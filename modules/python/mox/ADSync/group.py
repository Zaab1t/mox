from __future__ import print_function, absolute_import, unicode_literals

import collections
import uuid

from . import abstract
from . import computer
from . import user
from . import util

__all__ = (
    'Group',
)


class Group(abstract.Item):
    __slots__ = (
        '_classobj',
    )

    moxtype = 'OrganisationFunktion'

    USED_LDAP_ATTRS = (
        'cn',
        'description',
        'managedBy',
        'member',
        'memberOf',
        'name',
        'objectGuid',
        'sAMAccountName',
        'whenChanged',
        'whenCreated',
    )

    _CLASS_NAMESPACE_ID = uuid.UUID('21CEAFDD-7B95-47CB-8749-BAA21E209D0D')

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)

        self._classobj = GroupClass(self, self.entry, self.classid)

    @staticmethod
    def skip(entry):
        return abstract.Item.skip(entry) or entry.isCriticalSystemObject.value

    @property
    def classid(self):
        return str(uuid.uuid5(self._CLASS_NAMESPACE_ID, self.uuid))

    @property
    def nested_objects(self):
        r = super(Group, self).nested_objects
        r.append(self._classobj)
        return r

    def _relations(self):
        relations = collections.defaultdict(list, opgaver=[
            {
                'uuid': self.classid,
                'virkning': util.virkning(self.entry.whenChanged),
            },
        ])

        typemap = {
            user.User: 'tilknyttedebrugere',
            computer.Computer: 'tilknyttedeitsystemer',
        }

        for member_edn in self.entry.member:
            info = util.unpack_extended_dn(member_edn)
            obj = self.domain.get_object(info.guid)
            relname = typemap.get(type(obj))
            if relname:
                relations[relname].append({
                    'uuid': obj.uuid,
                    'virkning': util.virkning(self.entry.whenChanged),
                })
            elif obj:
                print('unhandled group member {}'.format(
                    obj
                ))

        return relations

    def data(self):
        return {
            'attributter': {
                'organisationfunktionegenskaber': [
                    {
                        'funktionsnavn': "Active Directory gruppemedlem",
                        'brugervendtnoegle': self.dn,
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ]
            },
            'relationer': self._relations(),
        }


class GroupClass(abstract.Item):
    __slots__ = (
    )

    moxtype = 'Klasse'

    def data(self):
        return {
            'note': self.entry.description.value,
            'attributter': {
                'klasseegenskaber': [
                    {
                        'titel': self.entry.name.value,
                        'brugervendtnoegle': self.dn,
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ],
            },
            'tilstande': {
                'klassepubliceret': [
                    {
                        'publiceret': 'Publiceret',
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ]
            },
            'relationer': {
                'ansvarlig': [
                    {
                        'uuid': util.unpack_extended_dn(manager).guid,
                        'virkning': util.virkning(self.entry.whenChanged),
                    }
                    for manager in (self.entry.managedBy or [])
                ],
            },
        }
