from __future__ import print_function, absolute_import, unicode_literals

import uuid
import weakref

from . import util

__all__ = (
    'Item',
)


class Item(object):
    __slots__ = (
        '__weakref__',
        '_children',
        '_entry',
        '_parent',
        '_uuid',
    )

    moxtype = None

    USED_LDAP_ATTRS = None

    __objects = dict()

    def __init__(self, parent, entry, uuid):
        self._parent = parent and weakref.ref(parent)
        self._children = set()
        self._entry = entry
        self._uuid = uuid

        self.__objects[uuid] = self

        if parent:
            parent._children.add(self)

    def __str__(self):
        return "{} {!r} <{}>".format(
            type(self).__name__,
            self.name.encode('utf-8'),
            self.uuid,
        )

    @property
    def entry(self):
        return self._entry

    @staticmethod
    def get_object(id):
        try:
            uuid.UUID(id)
        except ValueError:
            id = util.unpack_extended_dn(id).guid

        return Item.__objects.get(id)

    @staticmethod
    def skip(entry):
        return ('showInAdvancedViewOnly' in entry and
                entry.showInAdvancedViewOnly.value)

    @property
    def nested_objects(self):
        return []

    @property
    def dn(self):
        return util.unpack_extended_dn(self._entry.entry_dn).dn

    def get_children(self, objcls):
        for child in self._children:
            if isinstance(child, objcls):
                yield child

    def __iter__(self):
        return iter(self._children)

    @property
    def name(self):
        return self._entry.name.value or self._entry.description.value

    @property
    def parent(self):
        return self._parent and self._parent()

    @property
    def connection(self):
        return self.parent.connection

    @property
    def uuid(self):
        return self._uuid or self.entry.objectGuid.value

    @property
    def domain(self):
        return self.parent.domain

    def dirty(self, lora):
        obj = lora.get_object(self.uuid, self.moxtype)

        if 'isDeleted' in self.entry and self.entry.isDeleted:
            return obj and obj.current.livscykluskode != 'Slettet'

        if not obj or obj.current.livscykluskode == 'Slettet':
            return True

        return not obj.current.equivalent_to(self.data())

    def load_from(self, lora):
        return lora.get_object(self.uuid, self.moxtype)

    def save_to(self, lora):
        if not self.moxtype:
            raise NotImplementedError

        if 'isDeleted' in self.entry and self.entry.isDeleted:
            lora.write_object(self.moxtype, self.uuid, method='DELETE')
        else:
            lora.write_object(self.moxtype, self.uuid, json=self.data())

        for child in self.nested_objects:
            child.save_to(lora)

    @property
    def definition(self):
        raise NotImplementedError

    def data(self):
        raise NotImplementedError
