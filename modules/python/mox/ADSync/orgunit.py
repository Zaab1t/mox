from __future__ import print_function, absolute_import, unicode_literals

from . import abstract
from . import group
from . import user
from . import util

__all__ = (
    'OrgUnit',
)


class OrgUnit(abstract.Item):
    moxtype = 'OrganisationEnhed'

    USED_LDAP_ATTRS = (
        'cn',
        'description',
        'name',
        'objectGuid',
        'whenChanged',
    )

    def _is_user_group(self, dn):
        return (dn not in self.domain.entry.wellKnownObjects.values and
                dn not in self.domain.entry.otherWellKnownObjects)

    def _validate_group(self, attrname, group_dns):
        return filter(self._is_user_group, group_dns)

    def data(self):
        relations = {
            'tilknyttedeenheder': [
                {
                    'uuid': subunit.uuid,
                    'virkning': util.virkning(self.entry.whenChanged),
                }
                for subunit in self.get_children(OrgUnit)
            ],
            'tilknyttedefunktioner': [
                {
                    'uuid': contained_group.uuid,
                    'virkning': util.virkning(self.entry.whenChanged),
                }
                for contained_group in self.get_children(group.Group)
            ],
            'tilknyttedebrugere': [
                {
                    'uuid': contained_user.uuid,
                    'virkning': util.virkning(self.entry.whenChanged),
                }
                for contained_user in self.get_children(user.User)
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
