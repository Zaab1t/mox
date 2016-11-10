from __future__ import print_function, absolute_import, unicode_literals

import operator

import ldap3

from . import abstract
from . import group
from . import user
from . import util

__all__ = (
    'Domain',
)


class Domain(abstract.Item):
    __slots__ = (
        '_base',
        '_conn',
        '_domaindef',
        '_groupdef',
        '_orgunitdef',
        '_userdef',
    )

    moxtype = 'Organisation'

    def __init__(self, domain, host, user, password):
        self._conn = ldap3.Connection(host, user, password)
        self._conn.bind()

        # the search base is the domain, reformatted
        self._base = ','.join('dc=' + d for d in domain.split('.'))

        # create basic type definitions
        self._domaindef = ldap3.ObjectDef('domain', self._conn)
        self._userdef = ldap3.ObjectDef('user', self._conn)
        self._groupdef = ldap3.ObjectDef('group', self._conn)

        # add missing attributes
        self._userdef += 'cn', 'primaryGroupID', 'objectSid'
        self._userdef += 'sAMAccountName', 'sAMAccountType'

        self._groupdef += 'sAMAccountName', 'sAMAccountType', 'objectSid'

        # add relationships -- we only add them for member and not
        # memberOf; otherwise we'd get infinite recursions...
        self._groupdef += ldap3.AttrDef('member', key='members',
                                        post_query=self._validate_group,
                                        dereference_dn=self._userdef)
        self._groupdef += ldap3.AttrDef('member', key='groupMembers',
                                        validate=self._validate_group,
                                        dereference_dn=self._groupdef)
        self._groupdef += ldap3.AttrDef('managedBy', key='managers',
                                        dereference_dn=self._userdef)
        # self._userdef += ldap3.AttrDef('memberOf', key='groups',
        #                                dereference_dn=self._groupdef)
        # self._groupdef += ldap3.AttrDef('memberOf', key='groups',
        #                                 dereference_dn=self._groupdef)

        # # add relationship for 'well known containers' -- i.e. system
        # # groups which we want to discard
        # self._domaindef += ldap3.AttrDef('wellKnownObjects', 'wellKnowns',
        #                                  post_query=util.unpack_binary_dn,
        #                                  dereference_dn=self._groupdef)
        # self._domaindef += ldap3.AttrDef('otherWellKnownObjects',
        #                                  'otherWellKnowns',
        #                                  post_query=util.unpack_binary_dn,
        #                                  dereference_dn=self._groupdef)
        self._domaindef += ldap3.AttrDef('wellKnownObjects',
                                         post_query=util.unpack_binary_dn)
        self._domaindef += ldap3.AttrDef('otherWellKnownObjects',
                                         post_query=util.unpack_binary_dn)

        reader = ldap3.Reader(self._conn, self._domaindef, self._base)
        entry = reader.search_object()

        super(Domain, self).__init__(None, entry)

    @property
    def connection(self):
        return self._conn

    def _is_user_group(self, group_dn):
        return (group_dn not in self.entry.wellKnownObjects.values and
                group_dn not in self.entry.otherWellKnownObjects)

    def _validate_group(self, attrname, group_dns):
        return filter(self._is_user_group, group_dns)

    @property
    def uuid(self):
        return self.entry.objectGuid.value

    @property
    def domain(self):
        return self

    def save_to(self, lora):
        lora.import_object(self.uuid, self.moxtype, json=self.data())

    def data(self):
        entry = self.entry
        domainname = '.'.join(
            map(operator.itemgetter(1),
                ldap3.utils.dn.parse_dn(self.entry.entry_dn))
        )

        return {
            'attributter': {
                'organisationegenskaber': [
                    {
                        'organisationsnavn': entry.description.value,
                        'brugervendtnoegle': domainname,
                        'virkning': util.virkning(entry.whenChanged),
                    },
                ],
            },
            'tilstande': {
                'organisationgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': util.virkning(entry.whenChanged),
                    },
                ],
            },
        }

    def users(self, recursive=True):
        query = '(&(sAMAccountType=805306368)(!(isCriticalSystemObject=*)))'

        if recursive:
            reader = ldap3.Reader(self._conn, self._userdef, self._base, query)
            user_entries = reader.search_subtree(user.User.USED_LDAP_ATTRS)

        else:
            reader = ldap3.Reader(self._conn, self._userdef,
                                  'CN=Users,' + self._base, query)
            user_entries = reader.search_level(user.User.USED_LDAP_ATTRS)

        for user_entry in user_entries:
            if not user_entry:
                continue
            yield user.User(self, user_entry)

    def groups(self, recursive=True):
        query = (
            '(&(sAMAccountType=268435456)'
            '(groupType:1.2.840.113556.1.4.803:=2147483648)'
            '(!(isCriticalSystemObject=*)))'
        )

        if recursive:
            reader = ldap3.Reader(self._conn, self._groupdef, self._base,
                                  query)
            group_entries = reader.search_subtree(group.Group.USED_LDAP_ATTRS)

        else:
            reader = ldap3.Reader(self._conn, self._groupdef,
                                  'CN=Users,' + self._base, query)
            group_entries = reader.search_level(group.Group.USED_LDAP_ATTRS)

        for group_entry in group_entries:
            if not (group_entry and self._is_user_group(group_entry.entry_dn)):
                continue
            yield group.Group(self, group_entry)
