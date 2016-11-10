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

    USED_LDAP_ATTRS = (
        'accountExpires',
        'cn',
        'description',
        'objectGuid',
        'sAMAccountName',
        'userAccountControl',
        'userPrincipalName',
        'whenChanged',
    )

    def data(self):
        # userAccountControl is a bitfield, containing the 'account is
        # disabled' field, among others
        disabled = bool(self.entry.userAccountControl.value & 2)

        parent_dn = self.parent.entry.entry_dn
        parent_uuid = self.parent.entry.objectGuid.value

        return {
            'note': self.entry.description.value,
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
                        'uuid': parent_uuid,
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    }
                ] if parent_dn.startswith('OU=') else [],

                'tilknyttedeorganisationer': [
                    {
                        'uuid': parent_uuid,
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    }
                ] if parent_dn.startswith('DC=') else [],
            },
        }
