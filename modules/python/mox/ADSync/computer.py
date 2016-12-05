from __future__ import print_function, absolute_import, unicode_literals

from . import abstract

__all__ = (
    'Computer',
)


class Computer(abstract.Item):
    __slots__ = (
    )

    moxtype = 'Itsystem'

    USED_LDAP_ATTRS = (
        'description',
        'name',
        'objectGUID',
        'operatingSystem',
        'dNSHostName',
        'userAccountControl',
    )

    def data(self):
        # userAccountControl is a bitfield, containing the 'account is
        # disabled' field, among others
        disabled = bool(self['userAccountControl'] & 2)

        parent_relation = {
            'DC': 'tilknyttedeorganisationer',
            'OU': 'tilknyttedeenheder',
        }[self.parent.dn.split('=', 1)[0].upper()]

        return {
            'note': self['description'],

            'attributter': {
                'itsystemegenskaber': [
                    {
                        'itsystemnavn': self.name,
                        'itsystemtype': self['operatingSystem'],
                        'brugervendtnoegle': self['dNSHostName'] or self.name,
                        'virkning': self.virkning,
                    },
                ],
            },

            'tilstande': {
                'itsystemgyldighed': [
                    {
                        'gyldighed': 'Aktiv' if not disabled else 'Inaktiv',
                        'virkning': self.virkning,
                    },
                ],
            },

            'relationer': {
                'tilhoerer': [
                    {
                        'uuid': self.domain.uuid,
                        'virkning': self.virkning,
                    }
                ],

                parent_relation: [
                    {
                        'uuid': self.parent.uuid,
                        'virkning': self.virkning,
                    }
                ],
            },
        }
