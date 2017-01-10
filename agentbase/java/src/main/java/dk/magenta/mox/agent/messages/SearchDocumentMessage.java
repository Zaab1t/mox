package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.ParameterMap;
import dk.magenta.mox.agent.json.JSONObject;

/**
 * Created by lars on 15-02-16.
 */
public class SearchDocumentMessage extends ObjectTypeMessage {

    protected ParameterMap<String, String> query;

    public static final String OPERATION = "search";

    public SearchDocumentMessage(String authorization, String objectType, ParameterMap<String, String> query) {
        super(authorization, objectType);
        this.query = query;
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(Message.HEADER_QUERY, this.query.toJSON().toString());
        return headers;
    }

    @Override
    public String getOperationName() {
        return SearchDocumentMessage.OPERATION;
    }

    public static SearchDocumentMessage parse(Headers headers, JSONObject data) {
        String operationName = headers.optString(ObjectTypeMessage.HEADER_OPERATION);
        if (SearchDocumentMessage.OPERATION.equalsIgnoreCase(operationName)) {
            String authorization = headers.optString(Message.HEADER_AUTHORIZATION);
            String objectType = headers.optString(ObjectTypeMessage.HEADER_OBJECTTYPE);
            if (objectType != null) {
                ParameterMap<String, String> query = new ParameterMap<String, String>();
                query.populateFromJSON(data);
                return new SearchDocumentMessage(authorization, objectType, query);
            }
        }
        return null;
    }
}
