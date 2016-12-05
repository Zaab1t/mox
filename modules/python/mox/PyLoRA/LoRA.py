from __future__ import print_function

import itertools
import requests
import json
from uuid import UUID
from PyOIO.OIOCommon.entity import OIOEntity
from PyOIO import organisation, klassifikation
from PyOIO.OIOCommon.exceptions import InvalidUUIDException, InvalidObjectTypeException, TokenException, ItemNotFoundException, RestAccessException
import pylru

class Lora(object):
    """A Lora object represents a single running instance of the LoRa service.
    """
    objecttypes = list(
        val for val in itertools.chain(vars(organisation).itervalues(),
                                       vars(klassifikation).itervalues())
        if isinstance(val, type) and issubclass(val, OIOEntity)
    )
    object_map = {
        cls.ENTITY_CLASS: cls for cls in objecttypes
    }

    def __init__(self, host, username, password, verbose=False):
        """ Args:
        host:   string - the hostname of the LoRa instance
        username:   string - the username to authenticate as
        password:   string - the corresponding password
        verbose:   boolean - set to true to enable logging
        """
        self.host = host

        self.username = username
        self.password = password
        self.session = requests.Session()
        self.obtain_token()
        self._verbose = verbose
        self.all_items = pylru.lrucache(10000)

    def __repr__(self):
        return 'Lora("%s")' % (self.host)

    def __str__(self):
        return 'Lora: %s' % (self.host)

    @staticmethod
    def __check_uuid(uuid):
        try:
            UUID(uuid)
        except ValueError:
            raise InvalidUUIDException(uuid)

    @staticmethod
    def __check_response(response):
        if response:
            return

        try:
            msg = response.json()["message"]
        except:
            try:
                msg = response.text
            except:
                raise
            msg = '{} {}'.format(response.status_code, response.reason)

        if isinstance(msg, unicode):
            msg = msg.encode("utf-8")

        if response.status_code == requests.codes.not_found:
            raise KeyError(msg)

        raise RestAccessException(msg)

    def log(self, *args):
        if self._verbose:
            print(*args)

    def log_error(self, *args):
        print(*args)

    def obtain_token(self):
        response = self.session.post(
            self.host + "/get-token",
            data={
                'username': self.username,
                'password': self.password,
                'sts': self.host + ":9443/services/wso2carbon-sts?wsdl"
            }
        )
        if not response.text.startswith("saml-gzipped"):
            try:
                errormessage = json.loads(response.text)['message']
            except ValueError:
                errormessage = response.text
            raise TokenException(errormessage)
        self.session.headers['Authorization'] = response.text

    def request(self, url, method='GET', **kwargs):
        method = method.upper()
        response = self.session.request(method, url, **kwargs)
        if response.status_code == 401:
            # Token may be expired. Get a new one and try again
            self.obtain_token()
            response = self.session.request(method, url, **kwargs)
            if response.status_code == 401:
                # Failed with a new token. Bail
                raise RestAccessException(response.text)
        return response

    def get_uuids_of_type(self, objecttype):
        if issubclass(objecttype, OIOEntity):
            objecttype = objecttype.ENTITY_CLASS
        objectclass = self.object_map[objecttype]
        url = self.host + objectclass.basepath + "?search"
        response = self.request(url)
        return response.json()['results'][0]

    def load_all_of_type(self, objecttype):
        if issubclass(objecttype, OIOEntity):
            objecttype = objecttype.ENTITY_CLASS
        for guid in self.get_uuids_of_type(objecttype):
            self.get_object(guid, objecttype, True, True)

    def get_object(self, uuid, objecttype=None, force_refresh=False, refresh_cache=True):
        self.__check_uuid(uuid)

        if objecttype is None:
            objecttype = self.object_map.keys()
        elif type(objecttype) != list:
            objecttype = [objecttype]

        item = self.all_items.get(uuid, None)
        if item and not force_refresh:
            if not isinstance(item, tuple(self.object_map[otype]
                                          for otype in objecttype)):
                raise ItemNotFoundException(uuid, objecttype)

            return self.all_items[uuid]

        for otype in objecttype:
            self.log("get object of type %s" % otype)

            try:
                otypeobj = self.object_map[otype]
            except KeyError:
                raise InvalidObjectTypeException(otype)

            item = otypeobj(self, uuid)
            try:
                item.load()
            except ItemNotFoundException:
                # self.log("It's not a %s" % otype)
                continue

            if refresh_cache:
                self.all_items[uuid] = item
            return item
        self.log("Object %s not found" % uuid)

    def write_object(self, objecttype, uuid=None, **kwargs):
        '''write an object with the given UUID into the database
        '''
        self.__check_uuid(uuid)

        objcls = self.object_map[objecttype]

        if uuid:
            path = '/'.join((objcls.basepath, uuid))
            method = 'PUT'
        else:
            path = '/' + objcls.basepath
            method = 'POST'

        self.log('{} {}'.format('Import' if uuid else 'Create', path))

        response = self.request(self.host + path, method=method, **kwargs)

        self.__check_response(response)

        if uuid:
            # always invalidate the cache
            try:
                del self.all_items[uuid]
            except KeyError:
                pass

        return response.json()['uuid']
