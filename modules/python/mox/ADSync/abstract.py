from __future__ import print_function, absolute_import, unicode_literals

__all__ = (
    'Item',
)


class Item(object):
    __slots__ = (
        '_entry',
        '_parent',
        '_uuid',
    )

    moxtype = None

    USED_LDAP_ATTRS = None

    def __init__(self, parent, entry, uuid=None):
        self._parent = parent
        self._entry = entry
        self._uuid = uuid

    def __str__(self):
        return "{} {!r} <{}>".format(
            type(self).__name__,
            self.name.encode('utf-8'),
            self.uuid,
        )

    @property
    def entry(self):
        return self._entry

    @property
    def name(self):
        return self._entry.name.value or self._entry.description.value

    @property
    def parent(self):
        return self._parent

    @property
    def search_base(self):
        return self._parent.search_base

    @property
    def connection(self):
        return self._parent.connection

    @property
    def uuid(self):
        return self._uuid or self.entry.objectGuid.value

    @property
    def domain(self):
        return self._parent.domain

    def dirty(self, lora):
        ''''''
        obj = lora.get_object(self.uuid, self.moxtype)

        if not obj or obj.current.livscykluskode == 'Slettet':
            return True

        assert len(obj.current.egenskaber) == 1

        whenChanged = self.entry.whenChanged.value

        for reg in reversed(obj.registreringer):
            if reg.from_time < whenChanged:
                # this registration predates our change
                continue

            for attr in reg.egenskaber:
                if attr.virkning.from_time == whenChanged:
                    # this change has been written to LoRA!
                    return False

        return True

    def load_from(self, lora):
        return lora.get_object(self.uuid, self.moxtype)

    def save_to(self, lora):
        if not self.moxtype:
            raise NotImplementedError

        lora.write_object(self.moxtype, self.uuid, json=self.data())

    def data(self):
        raise NotImplementedError
