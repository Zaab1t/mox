from __future__ import print_function, absolute_import, unicode_literals

from . import abstract
from . import group
from . import user

__all__ = (
    'OrgUnit',
)


class OrgUnit(abstract.Item):
    moxtype = 'OrganisationEnhed'

    USED_LDAP_ATTRS = (
        'description',
        'name',
        'objectGUID',
    )

    def data(self):
        relations = {
            'tilknyttedeenheder': [
                {
                    'uuid': subunit.uuid,
                    'virkning': self.virkning,
                }
                for subunit in self.get_children(OrgUnit)
            ] or self.null_relation,
            'tilknyttedefunktioner': [
                {
                    'uuid': contained_group.uuid,
                    'virkning': self.virkning,
                }
                for contained_group in self.get_children(group.Group)
            ] or self.null_relation,
            'tilknyttedebrugere': [
                {
                    'uuid': contained_user.uuid,
                    'virkning': self.virkning,
                }
                for contained_user in self.get_children(user.User)
            ] or self.null_relation,
        }

        if self.domain != self:
            relations['tilhoerer'] = [
                {
                    'uuid': self.domain.uuid,
                    'virkning': self.virkning,
                },
            ]

        if isinstance(self.parent, OrgUnit):
            relations['overordnet'] = [
                {
                    'uuid': self.parent.uuid,
                    'virkning': self.virkning,
                },
            ]

        return {
            'note': self['description'],
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': self.name,
                        'brugervendtnoegle': self.name,
                        'virkning': self.virkning,
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': self.virkning,
                    },
                ],
            },
            'relationer': relations,
        }
