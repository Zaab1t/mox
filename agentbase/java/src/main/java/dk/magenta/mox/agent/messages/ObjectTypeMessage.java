package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.json.JSONObject;

/**
 * Created by lars on 25-01-16.
 */
public abstract class ObjectTypeMessage extends Message {

    public static final String HEADER_OBJECTTYPE = "objekttype";
    public static final String HEADER_OPERATION = "operation";

    public static final String OPERATION_CREATE = "create";
    public static final String OPERATION_READ = "read";
    public static final String OPERATION_SEARCH = "search";
    public static final String OPERATION_LIST = "list";
    public static final String OPERATION_UPDATE = "update";
    public static final String OPERATION_PASSIVATE = "passivate";
    public static final String OPERATION_DELETE = "delete";

    protected static String getOperationName() {
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
        headers.put(Message.HEADER_OBJECTTYPE, this.objectType);
        String operation = this.getOperationName();
        if (operation != null) {
            headers.put(Message.HEADER_OPERATION, operation);
        }
        return headers;
    }

    public String getObjectType() {
        return objectType;
    }

    public static DocumentMessage parse(Headers headers, JSONObject data) {
        String operationName = headers.optString(Message.HEADER_OPERATION);
        if (operationName != null) {
            switch (operationName.trim().toLowerCase()) {
                case OPERATION_READ:
                    return ReadDocumentMessage.parse(headers, data);
                case OPERATION_LIST:
                    return ListDocumentMessage.parse(headers, data);
                case OPERATION_SEARCH:
                    return SearchDocumentMessage.parse(headers, data);
                case OPERATION_CREATE:
                    return CreateDocumentMessage.parse(headers, data);
                case OPERATION_UPDATE:
                    return UpdateDocumentMessage.parse(headers, data);
                case OPERATION_PASSIVATE:
                    return PassivateDocumentMessage.parse(headers, data);
                case OPERATION_DELETE:
                    return PassivateDocumentMessage.parse(headers, data);
            }
        }
        return null;
    }

    public static DocumentMessage parse(Headers headers, org.json.JSONObject data) {
        return DocumentMessage.parse(headers, new JSONObject(data));
    }
}