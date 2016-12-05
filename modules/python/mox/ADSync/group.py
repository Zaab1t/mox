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
    )

    moxtype = 'OrganisationFunktion'

    USED_LDAP_ATTRS = (
        'description',
        'managedBy',
        'member',
        'name',
        'objectGUID',
        'sAMAccountName',
        'whenCreated',
    )

    _CLASS_NAMESPACE_ID = uuid.UUID('21CEAFDD-7B95-47CB-8749-BAA21E209D0D')

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)

        self.nest(GroupClass)

    @staticmethod
    def skip(entry):
        return abstract.Item.skip(entry) or entry['isCriticalSystemObject']

    @property
    def classid(self):
        return str(uuid.uuid5(self._CLASS_NAMESPACE_ID, self.uuid))

    def _relations(self):
        relations = collections.defaultdict(list, opgaver=[
            {
                'uuid': self.classid,
                'virkning': self.virkning,
            },
        ])

        typemap = {
            user.User: 'tilknyttedebrugere',
            computer.Computer: 'tilknyttedeitsystemer',
        }

        for member_edn in self.entry.get('member', []):
            info = util.unpack_extended_dn(member_edn)
            obj = self.domain.get_object(info.guid)
            relname = typemap.get(type(obj))
            if relname:
                relations[relname].append({
                    'uuid': obj.uuid,
                    'virkning': self.virkning,
                })
            elif obj:
                print('unhandled group member {}'.format(
                    obj
                ))

        for relname in typemap.values():
            relations.setdefault(relname, self.null_relation)

        return relations

    def data(self):
        return {
            'attributter': {
                'organisationfunktionegenskaber': [
                    {
                        'funktionsnavn': "Active Directory gruppemedlem",
                        'brugervendtnoegle': self.dn,
                        'virkning': self.virkning,
                    },
                ]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': self.virkning,
                    },
                ]
            },
            'relationer': self._relations(),
        }


class GroupClass(abstract.Item):
    __slots__ = (
    )

    moxtype = 'Klasse'

    @property
    def uuid(self):
        return self.parent.classid

    def data(self):
        relations = {
            'ansvarlig': []
        }

        if self.manager:
            relations['ansvarlig'].append({
                'uuid': self.manager,
                'virkning': self.virkning,
            })

        return {
            'note': self['description'],
            'attributter': {
                'klasseegenskaber': [
                    {
                        'titel': self['name'],
                        'brugervendtnoegle': self.dn,
                        'virkning': self.virkning,
                    },
                ],
            },
            'tilstande': {
                'klassepubliceret': [
                    {
                        'publiceret': 'Publiceret',
                        'virkning': self.virkning,
                    },
                ]
            },
            'relationer': relations,
        }
