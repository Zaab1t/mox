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

    public static ObjectTypeMessage parse(Headers headers, JSONObject data) {
        String operationName = headers.optString(ObjectTypeMessage.HEADER_OPERATION);
        if (operationName != null) {
            operationName = operationName.trim().toLowerCase();
            if (operationName.equals(OPERATION_READ)) {
                return ReadDocumentMessage.parse(headers, data);
            }
            if (operationName.equals(OPERATION_LIST)) {
                return ListDocumentMessage.parse(headers, data);
            }
            if (operationName.equals(OPERATION_SEARCH)) {
                return SearchDocumentMessage.parse(headers, data);
            }
            if (operationName.equals(OPERATION_CREATE)) {
                return CreateDocumentMessage.parse(headers, data);
            }
            if (operationName.equals(OPERATION_UPDATE)) {
                return UpdateDocumentMessage.parse(headers, data);
            }
            if (operationName.equals(OPERATION_PASSIVATE)) {
                return PassivateDocumentMessage.parse(headers, data);
            }
            if (operationName.equals(OPERATION_DELETE)) {
                return PassivateDocumentMessage.parse(headers, data);
            }
        }
        return null;
    }
}