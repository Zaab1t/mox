from __future__ import print_function, absolute_import, unicode_literals

import collections
import datetime
import itertools

import ldap3


def _dt2str(dt):
    '''Convert a datetime to string

    We consider anything before 1900 or after y9k as "infinity"

    '''

    if not dt or dt.year >= 9000 or dt.year < 1900:
        return 'infinity'
    assert isinstance(dt, datetime.datetime)

    return dt.isoformat()


def virkning(from_=None, to=None):
    '''Generate a LoRA 'virkning' object.

    The arguments may be either `ldap3.Attribute` resolving to
    `datetime` objects, or the `datetime` objects themselves. Assume
    'infinity' for any unspecified or out-of-bounds values.

    '''
    if isinstance(from_, ldap3.Attribute):
        from_ = from_.value
    if isinstance(to, ldap3.Attribute):
        to = to.value

    return {
        'from': _dt2str(from_),
        'to': _dt2str(to),
    }


def unpack_binary_dn(attr, values):
    r = []
    for v in values:
        assert v[:2] == b'B:', "{} isn't a binary DN: {}".format(attr, v)
        lenstr = v.split(b':', 2)[1]
        r.append(str(v[len(lenstr) + int(lenstr) + 4:]))
    return r


_extended_dn = collections.namedtuple('extended_dn', ('guid', 'sid', 'dn'))
_nulldn = _extended_dn(None, None, None)


def unpack_extended_dn(value):
    r = dict()

    while value[0] == '<':
        part, value = value.split(';', 1)

        assert part[-1] == '>'

        k, v = part[1:-1].split('=', 1)
        r[k.lower()] = v

    r['dn'] = value

    return _nulldn._replace(**r)


def unpack_extended_dns(attr, values):
    return [
        unpack_extended_dn(attr, v) for v in values
    ]


def get_parent_dn(dn):
    if dn.startswith('OU='):
        dn = ','.join(ldap3.utils.dn.to_dn(dn)[1:])

    return ','.join(
        itertools.dropwhile(lambda s: s.startswith('CN='),
                            ldap3.utils.dn.to_dn(dn))
    )


class cached_property(object):
    __slots__ = (
        'func',
        'value',
    )

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        try:
            return self.value
        except AttributeError:
            self.value = self.func(obj)

            try:
                obj.__dict__[self.func.__name__] = self.value
            except KeyError:
                # we cannot override slots
                pass

            return self.value


class cached_class_property(object):
    __slots__ = ('func')

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        try:
            return self.value
        except AttributeError:
            value = self.func(cls)

            setattr(cls, self.func.__name__, value)

            return value
