from __future__ import print_function, absolute_import, unicode_literals

import itertools

import ldap3

from . import abstract
from . import computer
from . import group
from . import user
from . import util

__all__ = (
    'OrgUnit',
)


class OrgUnit(abstract.Item):
    __slots__ = (
        '__base',
        '__computerdef',
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
        self.__computerdef = ldap3.ObjectDef('computer', self.connection)

        # add missing attributes
        self.__userdef += user.User.USED_LDAP_ATTRS
        self.__groupdef += group.Group.USED_LDAP_ATTRS
        self.__computerdef += computer.Computer.USED_LDAP_ATTRS

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
        self.__groupdef += ldap3.AttrDef('managedBy', key='groupManagers',
                                         dereference_dn=self.__groupdef)
        # self.__userdef += ldap3.AttrDef('memberOf', key='groups',
        #                                 dereference_dn=self.__groupdef)
        # self.__groupdef += ldap3.AttrDef('memberOf', key='groups',
        #                                  dereference_dn=self.__groupdef)

        self.__orgunitdef = ldap3.ObjectDef('organizationalUnit',
                                            self.connection)

        self.__computerdef += ldap3.AttrDef('managedBy', key='managers',
                                            dereference_dn=self.__userdef)
        self.__computerdef += ldap3.AttrDef('managedBy', key='groupManagers',
                                            dereference_dn=self.__groupdef)

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

    @property
    def computer_search_base(self):
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
            'note': (self.entry.description.value
                     if 'description' in self.entry else None),
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': self.name,
                        'brugervendtnoegle': self.name,
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
        query = '(objectClass=organizationalUnit)'

        reader = ldap3.Reader(self.domain.connection, self.__orgunitdef,
                              self.search_base, query, sub_tree=recurse)
        child_entries = \
            reader.search(attr or ldap3.ALL_ATTRIBUTES)

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
        group_entries = \
            reader.search_level(attr or group.Group.USED_LDAP_ATTRS)

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

        user_entries = \
            reader.search_level(attr or user.User.USED_LDAP_ATTRS)

        for user_entry in user_entries:
            if not user_entry:
                continue

            if attr:
                yield user_entry[attr].value
            else:
                yield user.User(self, user_entry)

    def computers(self, attr=None):
        query = (
            '(&(sAMAccountType=805306369))'
        )

        reader = ldap3.Reader(self.domain.connection, self.__computerdef,
                              self.computer_search_base, query)
        computer_entries = \
            reader.search_level(attr or computer.Computer.USED_LDAP_ATTRS)

        for computer_entry in computer_entries:
            if not computer_entry:
                continue

            if attr:
                yield computer_entry[attr].value
            else:
                yield computer.Computer(self, computer_entry)

    def children(self, recurse=False):
        for child in itertools.chain(self.users(), self.groups(),
                                     self.computers()):
            yield child

        for unit in self.units():
            yield unit

            if recurse:
                for child in unit.children(True):
                    yield child
