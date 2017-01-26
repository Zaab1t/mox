package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public class ReadDocumentMessage extends ObjectInstanceMessage {

    public static final String messageType = "ReadDocumentMessage";

    private static final String OPERATION = "read";

    public ReadDocumentMessage(String authorization, String objectType, UUID uuid) {
        super(authorization, objectType, uuid);
    }

    public ReadDocumentMessage(String authorization, String objectType, String uuid) throws IllegalArgumentException {
        super(authorization, objectType, uuid);
    }

    @Override
    public String getMessageType() {
        return ReadDocumentMessage.messageType;
    }

    @Override
    public String getOperationName() {
        return ReadDocumentMessage.OPERATION;
    }

    public static boolean matchType(Headers headers) {
        try {
            return ReadDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE)) && ReadDocumentMessage.OPERATION.equalsIgnoreCase(headers.getString(ObjectTypeMessage.HEADER_OPERATION));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static ReadDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (ReadDocumentMessage.matchType(headers)) {
            return new ReadDocumentMessage(
                    headers.getString(Message.HEADER_AUTHORIZATION),
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    headers.getString(ObjectInstanceMessage.HEADER_OBJECTID)
            );
        }
        return null;
    }

}
