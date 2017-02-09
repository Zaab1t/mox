package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public class PassivateDocumentMessage extends ObjectInstanceMessage {

    public static final String messageType = "PassivateDocumentMessage";

    public static final String KEY_NOTE = "Note";
    public static final String KEY_LIFECYCLE = "livscyklus";

    protected String note = "";

    public static final String OPERATION = "passivate";

    public PassivateDocumentMessage(String authorization, String objectType, UUID uuid, String note) {
        super(authorization, objectType, uuid);
        if (note == null) {
            note = "";
        }
        this.note = note;
    }

    public PassivateDocumentMessage(String authorization, String objectType, String uuid, String note) throws IllegalArgumentException {
        this(authorization, objectType, UUID.fromString(uuid), note);
    }

    public PassivateDocumentMessage(String authorization, String objectType, UUID uuid) {
        this(authorization, objectType, uuid, null);
    }

    public PassivateDocumentMessage(String authorization, String objectType, String uuid) throws IllegalArgumentException {
        this(authorization, objectType, uuid, null);
    }

    @Override
    public String getMessageType() {
        return PassivateDocumentMessage.messageType;
    }

    @Override
    public String getOperationName() {
        return PassivateDocumentMessage.OPERATION;
    }

    @Override
    public JSONObject getJSON() {
        JSONObject object = super.getJSON();
        object.put(PassivateDocumentMessage.KEY_NOTE, this.note);
        object.put(PassivateDocumentMessage.KEY_LIFECYCLE, "Passiv");
        return object;
    }

    public static boolean matchType(Headers headers) {
        try {
            return PassivateDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE)) && PassivateDocumentMessage.OPERATION.equalsIgnoreCase(headers.getString(ObjectTypeMessage.HEADER_OPERATION));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static PassivateDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (PassivateDocumentMessage.matchType(headers)) {
            return new PassivateDocumentMessage(
                    headers.getString(Message.HEADER_AUTHORIZATION),
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    headers.getString(ObjectInstanceMessage.HEADER_OBJECTID),
                    data.optString(PassivateDocumentMessage.KEY_NOTE)
            );
        }
        return null;
    }
}
