package dk.magenta.mox.agent.messages;

import java.util.UUID;

/**
 * Created by lars on 09-01-17.
 */
public class NotificationMessage extends InstanceDocumentMessage {

    public static final String HEADER_LIFECYCLECODE = "livscykluskode";

    protected String lifecycleCode;

    public NotificationMessage(String objectType, UUID uuid, String lifecycleCode) {
        super(objectType, uuid);
        this.lifecycleCode = lifecycleCode;
    }

    public NotificationMessage(String objectType, String uuid, String lifecycleCode) {
        super(objectType, uuid);
        this.lifecycleCode = lifecycleCode;
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(NotificationMessage.HEADER_LIFECYCLECODE, this.lifecycleCode);
        return headers;
    }
}