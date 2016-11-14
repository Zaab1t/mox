from __future__ import print_function, absolute_import, unicode_literals

import ldap3

from . import abstract
from . import group
from . import user
from . import util

__all__ = (
    'OrgUnit',
)


class OrgUnit(abstract.Item):
    __slots__ = (
        '__base',
        '__groupdef',
        '__orgunitdef',
        '__userdef',
    )

    moxtype = 'OrganisationEnhed'

    USED_LDAP_ATTRS = (
        'cn',
        'description',
        'name',
        'objectGuid',
        'whenChanged',
    )

    def __init__(self, *args, **kwargs):
        super(OrgUnit, self).__init__(*args, **kwargs)

        self.__base = self.entry.entry_dn

        self.__userdef = ldap3.ObjectDef('user', self.connection)
        self.__groupdef = ldap3.ObjectDef('group', self.connection)

        # add missing attributes
        self.__userdef += 'cn', 'primaryGroupID', 'objectSid'
        self.__userdef += 'sAMAccountName', 'sAMAccountType'

        self.__groupdef += 'sAMAccountName', 'sAMAccountType', 'objectSid'

        # add relationships -- we only add them for member and not
        # memberOf; otherwise we'd get infinite recursions...
        self.__groupdef += ldap3.AttrDef('member', key='members',
                                         post_query=self._validate_group,
                                         dereference_dn=self.__userdef)
        self.__groupdef += ldap3.AttrDef('member', key='groupMembers',
                                         validate=self._validate_group,
                                         dereference_dn=self.__groupdef)
        self.__groupdef += ldap3.AttrDef('managedBy', key='managers',
                                         dereference_dn=self.__userdef)
        # self.__userdef += ldap3.AttrDef('memberOf', key='groups',
        #                                 dereference_dn=self.__groupdef)
        # self.__groupdef += ldap3.AttrDef('memberOf', key='groups',
        #                                  dereference_dn=self.__groupdef)

        self.__orgunitdef = ldap3.ObjectDef('organizationalUnit',
                                            self.connection)
        self.__orgunitdef = ldap3.ObjectDef('organizationalUnit',
                                            self.connection)

    def _is_user_group(self, dn):
        return (dn not in self.domain.entry.wellKnownObjects.values and
                dn not in self.domain.entry.otherWellKnownObjects)

    def _validate_group(self, attrname, group_dns):
        return filter(self._is_user_group, group_dns)

    @property
    def search_base(self):
        return self.__base

    @property
    def user_search_base(self):
        return self.search_base

    def data(self):
        relations = {
            'tilknyttedeenheder': [
                {
                    'uuid': subunit_id,
                    'virkning': util.virkning(self.entry.whenChanged),
                }
                for subunit_id in self.units('objectGuid')
            ],
            'tilknyttedefunktioner': [
                {
                    'uuid': group_id,
                    'virkning': util.virkning(self.entry.whenChanged),
                }
                for group_id in self.groups('objectGuid')
            ],
            'tilknyttedebrugere': [
                {
                    'uuid': user_id,
                    'virkning': util.virkning(self.entry.whenChanged),
                }
                for user_id in self.users('objectGuid')
            ],
        }

        if self.domain != self:
            relations['tilhoerer'] = [
                {
                    'uuid': self.domain.uuid,
                    'virkning': util.virkning(self.entry.whenChanged),
                },
            ]

        if isinstance(self.parent, OrgUnit):
            relations['overordnet'] = [
                {
                    'uuid': self.parent.uuid,
                    'virkning': util.virkning(self.entry.whenChanged),
                },
            ]

        return {
            'note': self.entry.entry_attributes_as_dict.get('description', ''),
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': self.name,
                        'brugervendtnoegle': self.entry.entry_dn,
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': util.virkning(self.entry.whenChanged),
                    },
                ],
            },
            'relationer': relations,
        }

    def units(self, attr=None, recurse=False):
        query = (
            '(&(objectClass=organizationalUnit)(!(isCriticalSystemObject=*)))'
        )

        reader = ldap3.Reader(self.domain.connection, self.__orgunitdef,
                              self.search_base, query, sub_tree=recurse)
        child_entries = reader.search(attr or
                                      ldap3.ALL_ATTRIBUTES)

        for child_entry in child_entries:
            if not child_entry:
                continue

            if attr:
                yield child_entry[attr].value
            else:
                yield OrgUnit(self, child_entry)

    def groups(self, attr=None):
        query = (
            '(&(sAMAccountType=268435456)'
            '(groupType:1.2.840.113556.1.4.803:=2147483648)'
            '(!(isCriticalSystemObject=*)))'
        )

        reader = ldap3.Reader(self.domain.connection, self.__groupdef,
                              self.user_search_base, query)
        group_entries = reader.search_level(attr or
                                            group.Group.USED_LDAP_ATTRS)

        for group_entry in group_entries:
            if not (group_entry and self._is_user_group(group_entry.entry_dn)):
                continue

            if attr:
                yield group_entry[attr].value
            else:
                yield group.Group(self, group_entry)

    def users(self, attr=None):
        query = '(&(sAMAccountType=805306368)(!(isCriticalSystemObject=*)))'

        reader = ldap3.Reader(self.domain.connection, self.__userdef,
                              self.user_search_base, query)
        user_entries = reader.search_level(attr or
                                           user.User.USED_LDAP_ATTRS)

        for user_entry in user_entries:
            if not user_entry:
                continue

            if attr:
                yield user_entry[attr].value
            else:
                yield user.User(self, user_entry)
