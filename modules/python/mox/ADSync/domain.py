from __future__ import print_function, absolute_import, unicode_literals

import itertools

import ldap3

from . import orgunit
from . import util
from . import user
from . import computer
from . import group

__all__ = (
    'Domain',
)


class Domain(orgunit.OrgUnit):
    __slots__ = (
        '_conn',
        '_domain',
        '_base',
    )

    moxtype = 'Organisation'

    USED_LDAP_ATTRS = (
        'description',
        'distinguishedName',
        'name',
        'objectClass',
        'objectGuid',
        'whenChanged',
    )

    def __init__(self, domain, host, user, password):
        self._conn = ldap3.Connection(host, user, password,
                                      read_only=True, auto_bind=True)
        self._conn.bind()

        # the search base is the domain, reformatted
        self._base = ','.join('dc=' + d for d in domain.split('.'))
        self._domain = domain

        if not self.connection.search(self._base, '(objectClass=domain)',
                                      ldap3.BASE,
                                      attributes=self.USED_LDAP_ATTRS,
                                      controls=_LDAP_CONTROLS):
            raise Exception('search failed!')

        entry = self.connection.entries[0]

        print(self._base, entry.objectGuid.value)
        super(Domain, self).__init__(None, entry, entry.objectGuid.value)

    @property
    def connection(self):
        return self._conn

    @property
    def uuid(self):
        return self.entry.objectGuid.value

    @property
    def domain(self):
        return self

    def data(self):
        entry = self.entry
        data = super(Domain, self).data()

        data['attributter'] = {
            'organisationegenskaber': [
                {
                    'organisationsnavn': entry.description.value,
                    'brugervendtnoegle': self._domain,
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

    def objects(self):
        query = '(&(|{})(!(showInAdvancedViewOnly=TRUE)))'.format(
            ''.join('(objectClass={})'.format(cls)
                    for cls in ('domain', 'group', 'organizationalUnit',
                                'user'))
        )

        attributes = set(itertools.chain(*(
            objcls.USED_LDAP_ATTRS
            for objcls in _LDAP_OBJECT_TYPES.values()
        )))

        entries_by_dn = {
            self.dn: self.entry,
        }

        if not self.connection.search(self._base, query,
                                      attributes=attributes,
                                      controls=_LDAP_CONTROLS):
            raise Exception('search failed!')

        for entry in self.connection.entries:
            if entry is None:
                continue

            dn = util.unpack_extended_dn(entry.entry_dn)
            entries_by_dn[dn.dn] = entry

        def get_class(entry):
            for objcls in reversed(entry.objectClass.values):
                if objcls in _LDAP_OBJECT_TYPES:
                    return _LDAP_OBJECT_TYPES[objcls]

            return None

        def get_object(dn):
            entry = entries_by_dn[dn]

            obj = self.get_object(entry.objectGuid.value)

            if obj:
                return obj

            parent_dn = util.get_parent_dn(dn)
            parent = get_object(parent_dn) if parent_dn != dn else None

            objtype = get_class(entry)
            return objtype(parent, entry, entry.objectGuid.value)

        seen = []

        for dn, entry in entries_by_dn.items():
            if not get_class(entry) or get_class(entry).skip(entry):
                continue
            obj = get_object(dn)
            seen.append(obj)
            seen.extend(obj.nested_objects)

        return seen

_LDAP_CONTROLS = (
    ldap3.protocol.microsoft.extended_dn_control(criticality=True),
    ldap3.protocol.microsoft.show_deleted_control(criticality=True),
)

_LDAP_OBJECT_TYPES = {
    'computer': computer.Computer,
    'domainDNS': Domain,
    'group': group.Group,
    'organizationalUnit': orgunit.OrgUnit,
    'user': user.User,
}
