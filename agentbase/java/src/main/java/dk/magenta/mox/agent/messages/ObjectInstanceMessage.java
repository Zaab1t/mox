package dk.magenta.mox.agent.messages;


import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public abstract class ObjectInstanceMessage extends ObjectTypeMessage {

    public static final String HEADER_OBJECTID = "objektID";

    protected UUID uuid;

    public ObjectInstanceMessage(String objectType, UUID uuid) {
        super(objectType);
        this.uuid = uuid;
    }

    public ObjectInstanceMessage(String objectType, String uuid) throws IllegalArgumentException {
        this(objectType, UUID.fromString(uuid));
    }

    public ObjectInstanceMessage(String authorization, String objectType, UUID uuid) {
        super(authorization, objectType);
        this.uuid = uuid;
    }

    public ObjectInstanceMessage(String authorization, String objectType, String uuid) throws IllegalArgumentException {
        this(authorization, objectType, UUID.fromString(uuid));
    }

    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(ObjectInstanceMessage.HEADER_OBJECTID, this.uuid.toString());
        return headers;
    }

    public static boolean matchType(Headers headers) {
        return (
                EffectUpdateMessage.matchType(headers) || NotificationMessage.matchType(headers) ||
                ReadDocumentMessage.matchType(headers) || UpdateDocumentMessage.matchType(headers) ||
                PassivateDocumentMessage.matchType(headers) || DeleteDocumentMessage.matchType(headers)
        );
    }

    public static ObjectInstanceMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (EffectUpdateMessage.matchType(headers)) {
            return EffectUpdateMessage.parse(headers, data);
        }
        if (NotificationMessage.matchType(headers)) {
            return NotificationMessage.parse(headers, data);
        }
        if (ReadDocumentMessage.matchType(headers)) {
            return ReadDocumentMessage.parse(headers, data);
        }
        if (UpdateDocumentMessage.matchType(headers)) {
            return UpdateDocumentMessage.parse(headers, data);
        }
        if (PassivateDocumentMessage.matchType(headers)) {
            return PassivateDocumentMessage.parse(headers, data);
        }
        if (DeleteDocumentMessage.matchType(headers)) {
            return DeleteDocumentMessage.parse(headers, data);
        }
        return null;
    }
}
