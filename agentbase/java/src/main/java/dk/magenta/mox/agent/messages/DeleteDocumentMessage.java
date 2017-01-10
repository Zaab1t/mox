package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public class DeleteDocumentMessage extends ObjectInstanceMessage {

    public static final String messageType = "DeleteDocumentMessage";

    public static final String KEY_NOTE = "Note";

    private String note = null;

    private static final String OPERATION = "delete";

    public DeleteDocumentMessage(String authorization, String objectType, UUID uuid, String note) {
        super(authorization, objectType, uuid);
        this.note = note;
    }

    public DeleteDocumentMessage(String authorization, String objectType, String uuid, String note) throws IllegalArgumentException {
        this(authorization, objectType, UUID.fromString(uuid), note);
    }

    public DeleteDocumentMessage(String authorization, String objectType, UUID uuid) {
        this(authorization, objectType, uuid, null);
    }

    public DeleteDocumentMessage(String authorization, String objectType, String uuid) throws IllegalArgumentException {
        this(authorization, objectType, uuid, null);
    }

    @Override
    public String getMessageType() {
        return DeleteDocumentMessage.messageType;
    }

    @Override
    public String getOperationName() {
        return DeleteDocumentMessage.OPERATION;
    }

    @Override
    public JSONObject getJSON() {
        JSONObject object = super.getJSON();
        object.put(DeleteDocumentMessage.KEY_NOTE, this.note);
        return object;
    }

    public static boolean matchType(Headers headers) {
        try {
            return DeleteDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE)) && DeleteDocumentMessage.OPERATION.equalsIgnoreCase(headers.getString(ObjectTypeMessage.HEADER_OPERATION));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static DeleteDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (DeleteDocumentMessage.matchType(headers)) {
            return new DeleteDocumentMessage(
                    headers.getString(Message.HEADER_AUTHORIZATION),
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    headers.getString(ObjectInstanceMessage.HEADER_OBJECTID),
                    data.optString(DeleteDocumentMessage.KEY_NOTE)
            );
        }
        return null;
    }

}
