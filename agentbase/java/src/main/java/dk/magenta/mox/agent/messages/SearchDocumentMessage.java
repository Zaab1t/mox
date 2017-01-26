package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.ParameterMap;
import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

/**
 * Created by lars on 15-02-16.
 */
public class SearchDocumentMessage extends ObjectTypeMessage {

    public static final String messageType = "SearchDocumentMessage";

    protected ParameterMap<String, String> query;

    private static final String OPERATION = "search";

    public SearchDocumentMessage(String authorization, String objectType, ParameterMap<String, String> query) {
        super(authorization, objectType);
        this.query = query;
    }

    @Override
    public String getMessageType() {
        return SearchDocumentMessage.messageType;
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(ObjectTypeMessage.HEADER_QUERY, this.query.toJSON().toString());
        return headers;
    }

    @Override
    public String getOperationName() {
        return SearchDocumentMessage.OPERATION;
    }

    public static boolean matchType(Headers headers) {
        try {
            return SearchDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE)) && SearchDocumentMessage.OPERATION.equalsIgnoreCase(headers.getString(ObjectTypeMessage.HEADER_OPERATION));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static SearchDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (SearchDocumentMessage.matchType(headers)) {
            return new SearchDocumentMessage(
                    headers.getString(Message.HEADER_AUTHORIZATION),
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    ParameterMap.fromJSON(
                            new JSONObject(
                                    headers.getString(ObjectTypeMessage.HEADER_QUERY)
                            )
                    )
            );
        }
        return null;
    }
}
