package dk.magenta.mox.agent.messages;


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
}
