from __future__ import print_function, absolute_import, unicode_literals

import datetime

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
        assert v[:2] == 'B:', "{} isn't a binary DN: {}".format(attr, v)
        lenstr = v.split(':', 2)[1]
        r.append(v[len(lenstr) + int(lenstr) + 4:])
    return r
