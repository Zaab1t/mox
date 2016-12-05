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
        '_dirsync',
        '_domain',
        '_base',
        '_parents',
    )

    moxtype = 'Organisation'

    USED_LDAP_ATTRS = (
        'description',
        'name',
        'objectClass',
        'objectGUID',
        'parentGUID',
    )

    def __init__(self, domain, host, user, password):
        self._conn = ldap3.Connection(host, user, password,
                                      read_only=True, auto_bind=True)
        self._conn.bind()

        # the search base is the domain, reformatted
        self._base = ','.join('dc=' + d for d in domain.split('.'))
        self._domain = domain
        self._parents = dict()

        if not self.connection.search(
                self._base, '(objectClass=domain)',
                ldap3.BASE, attributes=self.USED_LDAP_ATTRS,
                controls=(
                    ldap3.protocol.microsoft.extended_dn_control(True),
                    ldap3.protocol.microsoft.show_deleted_control(True),
                )
        ):
            raise Exception('search failed!')

        entry = self.connection.entries[0]

        query = '(&(|{})(!(showInAdvancedViewOnly=TRUE)))'.format(
            ''.join('(objectClass={})'.format(cls)
                    for cls in ('domain', 'group', 'organizationalUnit',
                                'user'))
        )

        attributes = set(itertools.chain(*(
            objcls.USED_LDAP_ATTRS
            for objcls in _LDAP_OBJECT_TYPES.values()
        )))

        self._dirsync = self.connection.extend.microsoft.dir_sync(
            self._base,
            query,
            attributes=attributes,
            object_security=True,
            incremental_values=False,
        )

        super(Domain, self).__init__(None, entry.entry_dn,
                                     entry.entry_attributes_as_dict)

    @property
    def connection(self):
        return self._conn

    @property
    def uuid(self):
        return self['objectGUID']

    @property
    def domain(self):
        return self

    @property
    def manager(self):
        return None

    @staticmethod
    def skip(entry):
        return True

    def _get_parent(self, attrs):
        if not attrs.get('parentGUID', None):
            return None

        parent_id = util.to_uuid(attrs['parentGUID'])

        while parent_id not in self._objects:
            parent_id = self._parents[parent_id]

        return self._objects[parent_id]

    def _process_item(self, item):
        def get_class(entry):
            for objcls in reversed(entry['objectClass']):
                if objcls in _LDAP_OBJECT_TYPES:
                    return _LDAP_OBJECT_TYPES[objcls]

            return None

        dn = item['dn']
        attrs = item['attributes']

        if attrs['parentGUID']:
            self._parents[attrs['objectGUID']] = \
                util.to_uuid(attrs['parentGUID'])

        obj = self.get_object(dn)

        if obj:
            return obj.update(item, self._get_parent(attrs))

        objtype = get_class(attrs)

        if not objtype or objtype.skip(attrs):
            return []

        obj = objtype(self._get_parent(attrs), dn, attrs)
        return [obj] + obj.nested_objects

    def poll(self):
        seen = []

        for item in self._dirsync.loop():
            seen += self._process_item(item)

        while self._dirsync.more_results:
            for item in self._dirsync.loop():
                seen += self._process_item(item)

        return seen

    def data(self):
        data = super(Domain, self).data()

        data['attributter'] = {
            'organisationegenskaber': [
                {
                    'organisationsnavn': self['description'],
                    'brugervendtnoegle': self._domain,
                    'virkning': self.virkning,
                },
            ],
        }

        data['tilstande'] = {
            'organisationgyldighed': [
                {
                    'gyldighed': 'Aktiv',
                    'virkning': self.virkning,
                },
            ],
        }

        return data

_LDAP_OBJECT_TYPES = {
    'computer': computer.Computer,
    'domainDNS': Domain,
    'group': group.Group,
    'organizationalUnit': orgunit.OrgUnit,
    'user': user.User,
}
