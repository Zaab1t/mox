package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public class ReadDocumentMessage extends ObjectInstanceMessage {

    public static final String OPERATION = "read";

    public ReadDocumentMessage(String authorization, String objectType, UUID uuid) {
        super(authorization, objectType, uuid);
    }

    public ReadDocumentMessage(String authorization, String objectType, String uuid) throws IllegalArgumentException {
        super(authorization, objectType, uuid);
    }

    @Override
    public String getOperationName() {
        return ReadDocumentMessage.OPERATION;
    }

    public static ReadDocumentMessage parse(Headers headers, JSONObject data) throws IllegalArgumentException {
        String operationName = headers.optString(ObjectTypeMessage.HEADER_OPERATION);
        if (ReadDocumentMessage.OPERATION.equalsIgnoreCase(operationName)) {
            String authorization = headers.optString(Message.HEADER_AUTHORIZATION);
            String objectType = headers.optString(ObjectTypeMessage.HEADER_OBJECTTYPE);
            String uuid = headers.optString(ObjectInstanceMessage.HEADER_OBJECTID);
            if (uuid != null && objectType != null) {
                return new ReadDocumentMessage(authorization, objectType, uuid);
            }
        }
        return null;
    }

}
