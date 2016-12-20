from __future__ import print_function, absolute_import, unicode_literals

import datetime

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
        'description',
        'displayName',
        'isCriticalSystemObject',
        'isDeleted',
        'manager',
        'name',
        'objectGUID',
        'userAccountControl',
        'userPrincipalName',
        'whenCreated',
    )

    @staticmethod
    def skip(entry):
        return abstract.Item.skip(entry) or entry['isCriticalSystemObject']

    @property
    def virkning(self):
        expires = self['accountExpires']

        # why yes, AD, an early expiry can indeed mean never -- which
        # makes zero sense...
        if expires.year <= 1900 or expires.year >= 9000:
            expires = datetime.datetime.max
        elif expires <= util.now():
            return super(User, self).virkning

        return util.virkning(to=expires)

    def data(self):
        # userAccountControl is a bitfield, containing the 'account is
        # disabled' field, among others
        disabled = bool(self['userAccountControl'] & 2)

        return {
            'note': self['description'],
            'attributter': {
                'brugeregenskaber': [
                    {
                        'brugernavn': self['displayName'],
                        'brugervendtnoegle': self['userPrincipalName'],
                        'virkning': self.virkning,
                    },
                ],
            },
            'tilstande': {
                'brugergyldighed': [
                    {
                        'gyldighed': 'Aktiv' if not disabled else 'Inaktiv',
                        'virkning': self.virkning,
                    },
                ],
            },
            'relationer': {
                'tilknyttedefunktioner': [
                    {
                        'uuid': group_id,
                        'virkning': self.virkning,
                    }
                    for group_id in self.groups
                ] or self.null_relation,

                'tilknyttedeorganisationer': [
                    {
                        'uuid': (self.parent.uuid if self.parent == self.domain
                                 else ''),
                        'virkning': self.virkning,
                    }
                ],

                'tilknyttedeenheder': [
                    {
                        'uuid': (self.parent.uuid if self.parent != self.domain
                                 else ''),
                        'virkning': self.virkning,
                    }
                ],
            },
        }
