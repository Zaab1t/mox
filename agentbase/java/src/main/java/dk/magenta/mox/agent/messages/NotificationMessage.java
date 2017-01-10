package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 09-01-17.
 */
public class NotificationMessage extends ObjectInstanceMessage {

    public static final String messageType = "NotificationMessage";

    public static final String HEADER_LIFECYCLECODE = "livscykluskode";

    protected String lifecycleCode;

    public NotificationMessage(String objectType, UUID uuid, String lifecycleCode) {
        super(objectType, uuid);
        this.lifecycleCode = lifecycleCode;
    }

    public NotificationMessage(String objectType, String uuid, String lifecycleCode) {
        this(objectType, UUID.fromString(uuid), lifecycleCode);
    }

    @Override
    public String getMessageType() {
        return NotificationMessage.messageType;
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(NotificationMessage.HEADER_LIFECYCLECODE, this.lifecycleCode);
        return headers;
    }

    public static boolean matchType(Headers headers) {
        try {
            return NotificationMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static NotificationMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (NotificationMessage.matchType(headers)) {
            return new NotificationMessage(
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    headers.getString(ObjectInstanceMessage.HEADER_OBJECTID),
                    headers.getString(NotificationMessage.HEADER_LIFECYCLECODE)
            );
        }
        return null;
    }
}