package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public class UpdateDocumentMessage extends ObjectInstanceMessage {

    public static final String messageType = "UpdateDocumentMessage";

    protected UUID uuid;

    private static final String OPERATION = "update";

    protected JSONObject data;

    public UpdateDocumentMessage(String authorization, String objectType, UUID uuid, JSONObject data) {
        super(authorization, objectType, uuid);
        this.data = data;
    }

    public UpdateDocumentMessage(String authorization, String objectType, UUID uuid, org.json.JSONObject data) {
        super(authorization, objectType, uuid);
        this.data = new JSONObject(data);
    }

    public UpdateDocumentMessage(String authorization, String objectType, String uuid, JSONObject data) throws IllegalArgumentException {
        this(authorization, objectType, UUID.fromString(uuid), data);
    }

    public UpdateDocumentMessage(String authorization, String objectType, String uuid, org.json.JSONObject data) throws IllegalArgumentException {
        this(authorization, objectType, UUID.fromString(uuid), data);
    }

    @Override
    public String getMessageType() {
        return UpdateDocumentMessage.messageType;
    }

    public JSONObject getJSON() {
        return this.data;
    }

    @Override
    public String getOperationName() {
        return UpdateDocumentMessage.OPERATION;
    }

    public static boolean matchType(Headers headers) {
        try {
            return UpdateDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE)) && UpdateDocumentMessage.OPERATION.equalsIgnoreCase(headers.getString(ObjectTypeMessage.HEADER_OPERATION));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static UpdateDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (UpdateDocumentMessage.matchType(headers)) {
            return new UpdateDocumentMessage(
                    headers.getString(Message.HEADER_AUTHORIZATION),
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    headers.getString(ObjectInstanceMessage.HEADER_OBJECTID),
                    data
            );
        }
        return null;
    }

}
