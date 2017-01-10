package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public class UpdateDocumentMessage extends ObjectInstanceMessage {

    protected UUID uuid;

    public static final String OPERATION = "update";

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

    public JSONObject getJSON() {
        return this.data;
    }

    @Override
    public String getOperationName() {
        return UpdateDocumentMessage.OPERATION;
    }

    public static UpdateDocumentMessage parse(Headers headers, JSONObject data) {
        String operationName = headers.optString(ObjectTypeMessage.HEADER_OPERATION);
        if (UpdateDocumentMessage.OPERATION.equalsIgnoreCase(operationName)) {
            String authorization = headers.optString(Message.HEADER_AUTHORIZATION);
            String uuid = headers.optString(ObjectInstanceMessage.HEADER_OBJECTID);
            String objectType = headers.optString(ObjectTypeMessage.HEADER_OBJECTTYPE);
            if (uuid != null && objectType != null) {
                return new UpdateDocumentMessage(authorization, objectType, uuid, data);
            }
        }
        return null;
    }

}
