package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

/**
 * Created by lars on 15-02-16.
 */
public class CreateDocumentMessage extends ObjectTypeMessage {

    public static final String messageType = "CreateDocumentMessage";

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
    public String getMessageType() {
        return CreateDocumentMessage.messageType;
    }

    @Override
    public JSONObject getJSON() {
        return this.data;
    }

    @Override
    public String getOperationName() {
        return CreateDocumentMessage.OPERATION;
    }

    public static boolean matchType(Headers headers) {
        try {
            return CreateDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE)) && CreateDocumentMessage.OPERATION.equalsIgnoreCase(headers.getString(ObjectTypeMessage.HEADER_OPERATION));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static CreateDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (CreateDocumentMessage.matchType(headers)) {
            return new CreateDocumentMessage(
                    headers.getString(Message.HEADER_AUTHORIZATION),
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    data
            );
        }
        return null;
    }
}
