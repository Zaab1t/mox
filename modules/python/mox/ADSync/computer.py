from __future__ import print_function, absolute_import, unicode_literals

from . import abstract
from . import util

__all__ = (
    'Computer',
)


class Computer(abstract.Item):
    __slots__ = (
    )

    moxtype = 'Itsystem'

    USED_LDAP_ATTRS = (
        'cn',
        'description',
        'name',
        'objectGuid',
        'operatingSystem',
        'dNSHostName',
        'userAccountControl',
        'whenChanged',
    )

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
                'itsystemegenskaber': [
                    {
                        'itsystemnavn':
                            self.entry.dNSHostName.value,
                        'itsystemtype': self.entry.operatingSystem.value,
                        'brugervendtnoegle':
                            self.entry.cn.value,
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ],
            },

            'tilstande': {
                'itsystemgyldighed': [
                    {
                        'gyldighed': 'Aktiv' if not disabled else 'Inaktiv',
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ],
            },

            'relationer': {
                'tilhoerer': [
                    {
                        'uuid': self.domain.uuid,
                        'virkning': util.virkning(self.entry.whenChanged),
                    }
                ],

                parent_relation: [
                    {
                        'uuid': self.parent.uuid,
                        'virkning': util.virkning(self.entry.whenChanged),
                    }
                ],
            },
        }
