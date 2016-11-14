from __future__ import print_function, absolute_import, unicode_literals

import operator

import ldap3

from . import orgunit
from . import util

__all__ = (
    'Domain',
)


class Domain(orgunit.OrgUnit):
    __slots__ = (
        '_conn',
        '_domaindef',
    )

    moxtype = 'Organisation'

    def __init__(self, domain, host, user, password):
        self._conn = ldap3.Connection(host, user, password)
        self._conn.bind()

        # create basic type definitions
        self._domaindef = ldap3.ObjectDef('domain', self.connection)

        # add relationship for 'well known containers' -- i.e. system
        # groups which we want to discard
        self._domaindef += ldap3.AttrDef('wellKnownObjects',
                                         post_query=util.unpack_binary_dn)
        self._domaindef += ldap3.AttrDef('otherWellKnownObjects',
                                         post_query=util.unpack_binary_dn)

        # the search base is the domain, reformatted
        base = ','.join('dc=' + d for d in domain.split('.'))

        reader = ldap3.Reader(self._conn, self._domaindef, base)
        entry = reader.search_object(None)

        super(Domain, self).__init__(None, entry)

    @property
    def connection(self):
        return self._conn

    @property
    def uuid(self):
        return self.entry.objectGuid.value

    @property
    def domain(self):
        return self

    @property
    def user_search_base(self):
        return 'CN=Users,' + self.search_base

    def save_to(self, lora):
        lora.import_object(self.uuid, self.moxtype, json=self.data())

    def all_units(self):
        yield self

        for unit in self.units(recurse=True):
            yield unit

    def data(self):
        entry = self.entry
        data = super(Domain, self).data()

        domainname = '.'.join(
            map(operator.itemgetter(1),
                ldap3.utils.dn.parse_dn(self.entry.entry_dn))
        )

        data['attributter'] = {
            'organisationegenskaber': [
                {
                    'organisationsnavn': entry.description.value,
                    'brugervendtnoegle': domainname,
                    'virkning': util.virkning(entry.whenChanged),
                },
            ],
        }

        data['tilstande'] = {
            'organisationgyldighed': [
                {
                    'gyldighed': 'Aktiv',
                    'virkning': util.virkning(entry.whenChanged),
                },
            ],
        }

        return data
