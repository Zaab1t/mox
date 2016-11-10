from __future__ import print_function, absolute_import, unicode_literals

import uuid

from . import abstract
from . import util

__all__ = (
    'Group',
)


class Group(abstract.Item):
    __slots__ = (
        '_class_id',
    )

    moxtype = 'OrganisationFunktion'

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)

    def get_class(self, lora):
        if not getattr(self, '._class_id', None):
            self.load_from(lora)

        return GroupClass(self.parent, self.entry, self._class_id)

    def load_from(self, lora):
        orgfunktion = super(Group, self).load_from(lora)
        opgaver = orgfunktion and orgfunktion.current.relationer.get('opgaver')

        if orgfunktion and opgaver:
            assert len(opgaver) == 1
            self._class_id = opgaver[0]['uuid']
        else:
            self._class_id = str(uuid.uuid4())

        return orgfunktion

    def save_to(self, lora):
        self.get_class(lora).save_to(lora)
        super(Group, self).save_to(lora)

    def data(self):
        assert getattr(self, '_class_id', None), 'class id undetermined!'

        return {
            'attributter': {
                'organisationfunktionegenskaber': [
                    {
                        'funktionsnavn': "Active Directory gruppemedlem",
                        'brugervendtnoegle': self.entry.entry_dn,
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
            'relationer': {
                'tilknyttedebrugere': [
                    {
                        'uuid': member.objectGuid.value,
                        'virkning': util.virkning(self.entry.whenChanged),
                    }
                    for member in self.entry.members
                    # if member
                ] if 'members' in self.entry else [],
                'opgaver': [
                    {
                        'uuid': self._class_id,
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ]
            },
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
                        'klassetitel': self.entry.name.value,
                        'brugervendtnoegle': self.entry.entry_dn,
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
                        'uuid': manager.objectGuid.value,
                        'virkning': util.virkning(self.entry.whenChanged),
                    }
                    for manager in self.entry.managers
                ] if 'manager' in self.entry else [],
            },
        }
