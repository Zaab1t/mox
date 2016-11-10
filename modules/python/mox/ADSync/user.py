from __future__ import print_function, absolute_import, unicode_literals

from . import abstract
from . import util

__all__ = (
    'User',
)


class User(abstract.Item):
    __slots__ = (
    )

    moxtype = 'Bruger'

    def dirty(self, lora):
        raise NotImplementedError

    def data(self):
        # userAccountControl is a bitfield, containing the 'account is
        # disabled' field, among others
        disabled = bool(self.entry.userAccountControl.value & 2)

        parentdn = self.parent.entry.distinguishedName

        return {
            'attributter': {
                'brugeregenskaber': [
                    {
                        'brugernavn':
                            self.entry.sAMAccountName.value,
                        'brugervendtnoegle':
                            self.entry.userPrincipalName.value,
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    },
                ],
            },
            'note':
                self.entry.self.entry_attributes_as_dict.get('description'),
            'tilstande': {
                'brugergyldighed': [
                    {
                        'gyldighed': 'Aktiv' if not disabled else 'Inaktiv',
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    },
                ],
            },
            'relationer': {
                # 'tilknyttedefunktioner': [
                #     {
                #         'uuid': group.uuid,
                #         'virkning': util.virkning(self.entry.whenChanged,
                #                                   self.entry.accountExpires),
                #     }
                # for group.entry.entry_dn in self.domain.groups()
                # ],

                'tilknyttedeenheder': [
                    {
                        'uuid': orgunits[parentdn].objectGuid.value,
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    }
                ] if parentdn.startswith('OU=') else [],

                'tilknyttedeorganisationer': [
                    {
                        'uuid': domains[parentdn].objectGuid.value,
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    }
                ] if parentdn.startswith('DC=') else [],
            },
        }
