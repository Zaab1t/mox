package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

/**
 * Created by lars on 25-01-16.
 */
public abstract class ObjectTypeMessage extends Message {

    public static final String HEADER_OBJECTTYPE = "objekttype";
    public static final String HEADER_OPERATION = "operation";
    public static final String HEADER_QUERY = "query";

    public String getOperationName() {
        return null;
    }

    protected String objectType = null;

    public ObjectTypeMessage(String objectType) {
        if (objectType != null) {
            this.objectType = objectType.trim().toLowerCase();
        }
    }

    public ObjectTypeMessage(String authorization, String objectType) {
        super(authorization);
        if (objectType != null) {
            this.objectType = objectType.trim().toLowerCase();
        }
    }

    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(ObjectTypeMessage.HEADER_OBJECTTYPE, this.objectType);
        String operation = this.getOperationName();
        if (operation != null) {
            headers.put(ObjectTypeMessage.HEADER_OPERATION, operation);
        }
        return headers;
    }

    public String getObjectType() {
        return objectType;
    }

    public static boolean matchType(Headers headers) {
        return (
                ListDocumentMessage.matchType(headers) || SearchDocumentMessage.matchType(headers) ||
                CreateDocumentMessage.matchType(headers) || ObjectInstanceMessage.matchType(headers)
        );
    }

    public static ObjectTypeMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (ListDocumentMessage.matchType(headers)) {
            return ListDocumentMessage.parse(headers, data);
        }
        if (SearchDocumentMessage.matchType(headers)) {
            return SearchDocumentMessage.parse(headers, data);
        }
        if (CreateDocumentMessage.matchType(headers)) {
            return CreateDocumentMessage.parse(headers, data);
        }
        if (ObjectInstanceMessage.matchType(headers)) {
            return ObjectInstanceMessage.parse(headers, data);
        }
        return null;
    }
}