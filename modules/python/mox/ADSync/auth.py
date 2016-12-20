from __future__ import print_function, absolute_import, unicode_literals

import base64
import datetime
import os
import zlib

from xml.dom import minidom

import dateutil
import pytz
import requests

ASS_NS = 'urn:oasis:names:tc:SAML:2.0:assertion'
SOAP_NS = 'http://www.w3.org/2003/05/soap-envelope'
TRUST_NS = 'http://docs.oasis-open.org/ws-sx/ws-trust/200512'


class SAMLTokenAuth(requests.auth.AuthBase):
    def __init__(self, host, username, passwd, endpoint):
        self.idp_url = 'https://%s/adfs/services/trust/13/UsernameMixed' % (
            host,
        )

        with open(os.path.join(os.path.dirname(__file__),
                               'soap-request.xml.in'), 'r') as fp:
            t = fp.read()

        self.token = None
        self.request_body = t.format(
            username=username,
            password=passwd,
            idp_url=self.idp_url,
            endpoint=endpoint,
        )

    @staticmethod
    def _encode_token(t):
        compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                      zlib.DEFLATED, 16 + zlib.MAX_WBITS)
        data = compressor.compress(t) + compressor.flush()

        return 'saml-gzipped ' + \
            base64.standard_b64encode(data)

    def get_token(self, r):
        '''Request a SAML authentication token from the given host and endpoint.

        Windows Server typically returns a 500 Internal Server Error on
        authentication errors; this function simply raises a
        httplib.HTTPError in these cases. In other cases, it returns a
        KeyError.

        '''

        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
        }

        resp = requests.post(self.idp_url, self.request_body, headers=headers)

        # quick-and-dirty error handling
        resp.raise_for_status()

        doc = minidom.parseString(resp.text)

        tokens = doc.getElementsByTagNameNS(TRUST_NS, 'RequestedSecurityToken')

        if len(tokens) == 0:
            raise KeyError('no tokens found - is the endpoint correct?')
        if len(tokens) > 1:
            raise KeyError('too many tokens found')

        assert len(tokens[0].childNodes) == 1

        token = tokens[0].firstChild

        expires = token.getElementsByTagNameNS(ASS_NS, 'Conditions')
        assert len(expires) == 1

        expiry = dateutil.parser.parse(
            expires[0].getAttribute('NotOnOrAfter')
        )
        authheader = self._encode_token(token.toxml())

        # just in case -- we don't want the token the token to expire
        # between now and when the server receives the request; one
        # second ought to be enough, and 10 is plenty
        expiry -= datetime.timedelta(seconds=10)

        return expiry, authheader

    def __call__(self, r):
        if not self.token or self.expiry <= datetime.datetime.now(pytz.utc):
            self.expiry, self.token = self.get_token(r)

        r.headers['Authorization'] = self.token

        return r
