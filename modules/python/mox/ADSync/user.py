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
        'displayName',
        'distinguishedName',
        'isCriticalSystemObject',
        'isDeleted',
        'name',
        'objectGuid',
        'userAccountControl',
        'userPrincipalName',
        'whenChanged',
    )

    @staticmethod
    def skip(entry):
        return abstract.Item.skip(entry) or entry.isCriticalSystemObject.value

    def data(self):
        # userAccountControl is a bitfield, containing the 'account is
        # disabled' field, among others
        disabled = bool(self.entry.userAccountControl.value & 2)

        parent_relation = {
            'DC': 'tilknyttedeorganisationer',
            'OU': 'tilknyttedeenheder',
        }[self.parent.dn.split('=', 1)[0].upper()]

        return {
            'note': self.entry.description.value,
            'attributter': {
                'brugeregenskaber': [
                    {
                        'brugernavn':
                            self.entry.displayName.value,
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
                'tilknyttedefunktioner': [
                    {
                        'uuid': util.unpack_extended_dn(group_dn).guid,
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    }
                    for group_dn in self.entry.memberOf or []
                ],

                parent_relation: [
                    {
                        'uuid': self.parent.uuid,
                        'virkning': util.virkning(self.entry.whenChanged,
                                                  self.entry.accountExpires),
                    }
                ],
            },
        }
