package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.json.JSONObject;

/**
 * Created by lars on 15-02-16.
 */
public class CreateDocumentMessage extends ObjectTypeMessage {

    protected JSONObject data;

    public static final String OPERATION = "create";

    public CreateDocumentMessage(String authorization, String objectType, JSONObject data) {
        super(authorization, objectType);
        this.data = data;
    }

    public CreateDocumentMessage(String authorization, String objectType, org.json.JSONObject data) {
        this(authorization, objectType, new JSONObject(data));
    }

    @Override
    public JSONObject getJSON() {
        return this.data;
    }

    @Override
    public String getOperationName() {
        return CreateDocumentMessage.OPERATION;
    }

    public static CreateDocumentMessage parse(Headers headers, JSONObject data) {
        String operationName = headers.optString(ObjectTypeMessage.HEADER_OPERATION);
        if (CreateDocumentMessage.OPERATION.equalsIgnoreCase(operationName)) {
            String authorization = headers.optString(Message.HEADER_AUTHORIZATION);
            String objectType = headers.optString(ObjectTypeMessage.HEADER_OBJECTTYPE);
            if (objectType != null) {
                return new CreateDocumentMessage(authorization, objectType, data);
            }
        }
        return null;
    }
}
