from datetime import datetime
from dateutil import parser as dateparser
import uuid
import json


class Message(object):

    HEADER_AUTHORIZATION = "autorisation"
    HEADER_MESSAGEID = "beskedID"
    HEADER_MESSAGETYPE = "beskedtype"
    HEADER_MESSAGEVERSION = "beskedversion"
    HEADER_OBJECTREFERENCE = "objektreference"
    HEADER_OBJECTTYPE = "objekttype"
    HEADER_OBJECTTYPE_VALUE_DOCUMENT = "dokument"
    HEADER_QUERY = "query"

    HEADER_TYPE = "type"
    HEADER_TYPE_VALUE_MANUAL = "Manuel"

    HEADER_OBJECTID = "objektID"
    HEADER_OPERATION = "operation"

    version = 1
    operation = ""
    authorization = None

    def __init__(self, authorization=None):
        self.authorization = authorization

    def getData(self):
        return {}

    def getHeaders(self):
        headers = {
            Message.HEADER_MESSAGEID: str(uuid.uuid4()),
            Message.HEADER_MESSAGEVERSION: self.version,
            Message.HEADER_OPERATION: self.operation
        }
        if self.authorization is not None:
            headers[Message.HEADER_AUTHORIZATION] = self.authorization
        return headers


class UploadedDocumentMessage(Message):

    KEY_UUID = "uuid"
    operation = "upload"

    def __init__(self, uuid, authorization):
        super(UploadedDocumentMessage, self).__init__(authorization)
        self.uuid = uuid

    def getData(self):
        object = super(UploadedDocumentMessage, self).getData()
        object[UploadedDocumentMessage.KEY_UUID] = str(self.uuid)
        return object

    def getHeaders(self):
        headers = super(UploadedDocumentMessage, self).getHeaders()
        headers[Message.HEADER_OBJECTTYPE] = \
            Message.HEADER_OBJECTTYPE_VALUE_DOCUMENT
        headers[Message.HEADER_TYPE] = Message.HEADER_TYPE_VALUE_MANUAL
        headers[Message.HEADER_OBJECTREFERENCE] = str(self.uuid)
        return headers

    @staticmethod
    def parse(headers, data):
        operation = headers[Message.HEADER_OPERATION]
        if operation == UploadedDocumentMessage.OPERATION:
            authorization = headers.get(Message.HEADER_AUTHORIZATION)
            uuid = headers.get(Message.HEADER_OBJECTREFERENCE)
            if authorization is not None and uuid is not None:
                return UploadedDocumentMessage(uuid, authorization)


class ObjectTypeMessage(Message):

    operation = None

    def __init__(self, objecttype, authorization=None):
        super(ObjectTypeMessage, self).__init__(authorization)
        self.objecttype = objecttype

    def getHeaders(self):
        headers = super(ObjectTypeMessage, self).getHeaders()
        headers[self.HEADER_OBJECTTYPE] = self.objecttype
        if self.operation is not None:
            headers[self.HEADER_OPERATION] = self.operation
        return headers


# A message pertaining to an object
class ObjectInstanceMessage(ObjectTypeMessage):

    def __init__(self, objectid, objecttype, authorization=None):
        super(ObjectInstanceMessage, self).__init__(objecttype, authorization)
        self.objectid = objectid

    def getHeaders(self):
        headers = super(ObjectInstanceMessage, self).getHeaders()
        headers[self.HEADER_OBJECTID] = self.objectid
        return headers


class ListDocumentMessage(ObjectTypeMessage):

    operation = 'list'

    def __init__(self, objecttype, uuids, authorization):
        super(ListDocumentMessage, self).__init__(objecttype, authorization)
        if not type(uuids) == list:
            uuids = [uuids]
        self.uuids = uuids

    def getHeaders(self):
        headers = super(ListDocumentMessage, self).getHeaders()
        headers[self.HEADER_QUERY] = json.dumps({'uuid': self.uuids})
        return headers


class CreateDocumentMessage(ObjectTypeMessage):

    operation = 'create'

    def __init__(self, objecttype, uuids, data, authorization):
        super(CreateDocumentMessage, self).__init__(objecttype, authorization)
        self.data = data

    def getData(self):
        return self.data


class SearchDocumentMessage(ObjectTypeMessage):

    operation = 'search'

    def __init__(self, objecttype, authorization):
        super(SearchDocumentMessage, self).__init__(objecttype, authorization)
        self.queryDict = {}

    def addQueryParam(self, key, value):
        if key not in self.queryDict:
            self.queryDict[key] = []
        self.queryDict[key].append(value)

    def getHeaders(self):
        headers = super(SearchDocumentMessage, self).getHeaders()
        headers[self.HEADER_QUERY] = json.dumps(self.queryDict)
        return headers


class PassivateDocumentMessage(ObjectInstanceMessage):

    operation = 'passivate'

    def __init__(self, objectid, objecttype, authorization, note=None):
        super(PassivateDocumentMessage, self).__init__(objectid, objecttype, authorization)
        self.note = note

    def getData(self):
        return {'Note': self.note, 'livscyklus': 'Passiv'}


class DeleteDocumentMessage(ObjectInstanceMessage):

    operation = 'delete'

    def __init__(self, objectid, objecttype, authorization, note=None):
        super(DeleteDocumentMessage, self).__init__(objectid, objecttype, authorization)
        self.note = note

    def getData(self):
        if self.note is not None:
            return {'Note': self.note}
        return {}


# A message saying that an object has been updated in the database
class NotificationMessage(ObjectInstanceMessage):

    HEADER_LIFECYCLE_CODE = "livscykluskode"
    MESSAGE_TYPE = 'notification'

    def __init__(self, objectid, objecttype, lifecyclecode):
        super(NotificationMessage, self).__init__(objectid, objecttype)
        self.lifecyclecode = lifecyclecode

    def getHeaders(self):
        headers = super(NotificationMessage, self).getHeaders()
        headers[Message.HEADER_MESSAGETYPE] = self.MESSAGE_TYPE
        headers[NotificationMessage.HEADER_LIFECYCLE_CODE] = self.lifecyclecode
        return headers

    @staticmethod
    def parse(headers, data=None):
        type = headers[Message.HEADER_MESSAGETYPE]
        if type and type.lower() == NotificationMessage.MESSAGE_TYPE:
            try:
                objectid = headers[Message.HEADER_OBJECTID]
                objecttype = headers[Message.HEADER_OBJECTTYPE]
                lifecyclecode = headers[
                    NotificationMessage.HEADER_LIFECYCLE_CODE
                ]
                return NotificationMessage(objectid, objecttype, lifecyclecode)
            except:
                pass


# A message saying that an object's effective period has begun or ended
class EffectUpdateMessage(ObjectInstanceMessage):

    TYPE_BEGIN = 1
    TYPE_END = 2
    TYPE_BOTH = TYPE_BEGIN | TYPE_END

    HEADER_UPDATE_TYPE = "updatetype"
    HEADER_EFFECT_TIME = "effecttime"
    MESSAGE_TYPE = 'effectupdate'

    def __init__(self, objectid, objecttype, updatetype, effecttime):
        super(EffectUpdateMessage, self).__init__(objectid, objecttype)
        self.updatetype = updatetype
        self.effecttime = effecttime

    @property
    def updatetype(self):
        return self._updatetype

    @updatetype.setter
    def updatetype(self, updatetype):
        if type(updatetype) != int:
            raise TypeError
        elif updatetype not in [
            self.TYPE_BEGIN, self.TYPE_END, self.TYPE_BOTH
        ]:
            raise ValueError
        else:
            self._updatetype = updatetype

    @property
    def effecttime(self):
        return self._effecttime

    @effecttime.setter
    def effecttime(self, effecttime):
        if type(effecttime) == datetime:
            self._effecttime = effecttime
        elif isinstance(effecttime, basestring):
            self._effecttime = dateparser.parse(effecttime)
        else:
            raise TypeError

    def getHeaders(self):
        headers = super(EffectUpdateMessage, self).getHeaders()
        headers[self.HEADER_MESSAGETYPE] = self.MESSAGE_TYPE
        headers[self.HEADER_UPDATE_TYPE] = self.updatetype
        headers[self.HEADER_EFFECT_TIME] = self.effecttime
        return headers

    @staticmethod
    def parse(headers, data=None):
        type = headers[Message.HEADER_MESSAGETYPE]
        if type and type.lower() == EffectUpdateMessage.MESSAGE_TYPE:
            try:
                objectid = headers[Message.HEADER_OBJECTID]
                objecttype = headers[Message.HEADER_OBJECTTYPE]
                updatetype = headers[EffectUpdateMessage.HEADER_UPDATE_TYPE]
                effecttime = headers[EffectUpdateMessage.HEADER_EFFECT_TIME]
                return EffectUpdateMessage(
                    objectid, objecttype, updatetype, effecttime
                )
            except:
                pass


class ReadDocumentMessage(ObjectInstanceMessage):

    operation = 'read'


class UpdateDocumentMessage(ObjectTypeMessage):

    operation = 'update'

    def __init__(self, objecttype, data, authorization):
        super(UpdateDocumentMessage, self).__init__(objecttype, authorization)
        self.data = data

    def getData(self):
        return self.data
