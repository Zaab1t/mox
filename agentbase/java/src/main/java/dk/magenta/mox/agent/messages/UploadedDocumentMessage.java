package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.lang.IllegalArgumentException;
import java.util.UUID;

/**
 * Created by lars on 22-01-16.
 */
public class UploadedDocumentMessage extends Message {

    public static final String messageType = "UploadedDocumentMessage";

    public static final String HEADER_OBJECTREFERENCE = "objektreference";

    public static final String KEY_UUID = "uuid";

    private UUID retrievalUUID;

    public UploadedDocumentMessage(UUID retrievalUUID, String authorization) {
        super(authorization);
        this.retrievalUUID = retrievalUUID;
    }

    public UploadedDocumentMessage(String retrievalUUID, String authorization) throws IllegalArgumentException {
        this(UUID.fromString(retrievalUUID), authorization);
    }

    @Override
    public String getMessageType() {
        return UploadedDocumentMessage.messageType;
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
//        headers.put(Message.HEADER_OBJECTTYPE, HEADER_OBJECTTYPE_VALUE_DOCUMENT);
//        headers.put(Message.HEADER_OPERATION, OPERATION);
        headers.put(Message.HEADER_TYPE, Message.HEADER_TYPE_VALUE_MANUAL);
        headers.put(UploadedDocumentMessage.HEADER_OBJECTREFERENCE, this.retrievalUUID.toString());
        return headers;
    }

    public JSONObject getJSON() {
        JSONObject object = super.getJSON();
        object.put(KEY_UUID, this.retrievalUUID.toString());
        return object;
    }

    public static boolean matchType(Headers headers) {
        try {
            return UploadedDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static UploadedDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (UploadedDocumentMessage.matchType(headers)) {
            return new UploadedDocumentMessage(
                    headers.getString(UploadedDocumentMessage.HEADER_OBJECTREFERENCE),
                    headers.getString(Message.HEADER_AUTHORIZATION)
            );
        }
        return null;
    }
}
