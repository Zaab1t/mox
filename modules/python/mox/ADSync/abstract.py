from __future__ import print_function, absolute_import, unicode_literals

import collections
import uuid
import weakref

from . import util
from PyLoRA import LoRA

__all__ = (
    'Item',
)


class Item(object):
    __slots__ = (
        '__weakref__',
        '_children',
        '_nested_objects',
        '_dn',
        '_attrs',
        '_parent',
        '_uuid',
    )

    moxtype = None

    USED_LDAP_ATTRS = None

    _objects = dict()

    _groups = collections.defaultdict(set)
    _reports = collections.defaultdict(set)

    def __init__(self, parent, dn, attrs):
        self._parent = parent and weakref.ref(parent)
        self._children = set()
        self._nested_objects = list()
        self._dn = util.unpack_extended_dn(dn).dn
        self._attrs = dict(attrs)

        self._objects[self.uuid] = self

        self.update(attrs, parent)

        if parent:
            parent._children.add(self)

        assert self.domain == self or self.parent, \
            'missing parent for %s' % self

    def __str__(self):
        return "{} {!r} <{}>".format(
            type(self).__name__,
            self.name.encode('utf-8'),
            self.uuid,
        )

    @property
    def entry(self):
        return self._attrs

    @property
    def virkning(self):
        return util.virkning()

    @property
    def null_relation(self):
        return [{
            'virkning': self.virkning,
        }]

    @staticmethod
    def get_object(id):
        try:
            uuid.UUID(id)
        except ValueError:
            id = util.unpack_extended_dn(id).guid

        return Item._objects.get(id)

    @staticmethod
    def skip(entry):
        return ('showInAdvancedViewOnly' in entry and
                entry.showInAdvancedViewOnly.value)

    @property
    def nested_objects(self):
        return self._nested_objects

    def nest(self, objtype):
        self._nested_objects.append(objtype(self, self.dn, self.entry))

    def __getitem__(self, key):
        try:
            val = self.entry[key]
        except KeyError:
            return None

        if not isinstance(val, list):
            return val
        elif len(val) == 0:
            return None
        elif len(val) == 1:
            return val[0]
        else:
            return val

    @property
    def dn(self):
        return self._dn

    def get_children(self, objcls):
        for child in self._children:
            if isinstance(child, objcls):
                yield child

    def __iter__(self):
        return iter(self._children)

    @property
    def name(self):
        return self['name'] or self['description']

    @property
    def parent(self):
        return self._parent and self._parent()

    @parent.setter
    def parent(self, parent):
        if self._parent:
            self.parent._children.remove(self)
        if parent:
            parent._children.add(self)
        self._parent = weakref.ref(parent)

    @property
    def connection(self):
        return self.parent.connection

    @property
    def uuid(self):
        return self.entry['objectGUID']

    @property
    def domain(self):
        return self.parent.domain

    @property
    def manager(self):
        edn = self['managedBy']
        return util.unpack_extended_dn(edn).guid if edn else None

    @property
    def groups(self):
        return self._groups[self.uuid]

    @property
    def reports(self):
        return self._reports[self.uuid]

    def update(self, item, parent):
        prev_mgr = self.manager
        prev_groups = set(self.entry.get('member', []))

        # DirSync entries contain all of these attributes
        if {'dn', 'attributes', 'raw_attributes'} <= dict(item).viewkeys():
            self._dn = util.unpack_extended_dn(item['dn']).dn

            # yes, this is horrible, but necessary to detect deletions
            changes = {
                k: v
                for k, v in item['attributes'].iteritems()
                if v or item['raw_attributes'][k] is None
            }

            self._attrs.update(changes)

        else:
            self._attrs.update(item)

        cur_mgr = self.manager
        cur_groups = set(self.entry.get('member', []))

        # update group back references
        for removed_group in prev_groups - cur_groups:
            id = util.unpack_extended_dn(removed_group).guid
            self._groups[id].remove(self.uuid)

        for added_group in cur_groups:
            id = util.unpack_extended_dn(added_group).guid
            self._groups[id].add(self.uuid)

        touched_ids = prev_groups ^ cur_groups

        # and likewise for direct reports
        if prev_mgr != cur_mgr:
            if prev_mgr:
                id = util.unpack_extended_dn(prev_mgr).guid
                self._reports[id].remove(self.uuid)
                touched_ids.add(id)
            if cur_mgr:
                id = util.unpack_extended_dn(cur_mgr).guid
                self._reports[id].add(self.uuid)
                touched_ids.add(id)

        # update parent
        if parent != self.parent:
            touched_ids.update((parent.uuid, self.parent.uuid))
            self.parent = parent

        return [self] + self.nested_objects + map(self.get_object, touched_ids)

    def _dirty(self, lora):
        obj = lora.get_object(self.uuid, self.moxtype)

        if self['isDeleted']:
            return obj and obj.current.livscykluskode != 'Slettet'

        if not obj or obj.current.livscykluskode == 'Slettet':
            return True

        return not obj.current.equivalent_to(self.data())

    @property
    def relations(self):
        return LoRA.Lora.object_map[self.moxtype].relation_keys

    def load_from(self, lora):
        return lora.get_object(self.uuid, self.moxtype)

    def save_to(self, lora):
        if not self.moxtype:
            raise NotImplementedError

        if not self._dirty(lora):
            return False

        if self['isDeleted']:
            lora.write_object(self.moxtype, self.uuid, method='DELETE')

        else:
            lora.write_object(self.moxtype, self.uuid, json=self.data())

        return True

    @property
    def definition(self):
        raise NotImplementedError

    def data(self):
        raise NotImplementedError
