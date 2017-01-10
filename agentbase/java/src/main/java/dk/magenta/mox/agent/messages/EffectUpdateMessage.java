package dk.magenta.mox.agent.messages;

import java.util.UUID;
import java.util.Date;

/**
 * Created by lars on 09-01-17.
 */
public class EffectUpdateMessage extends ObjectInstanceMessage {

    public static final String HEADER_UPDATETYPE = "updatetype";
    public static final String HEADER_EFFECTTIME = "effecttime";

    protected String updateType;
    protected Date effectTime;

    public EffectUpdateMessage(String objectType, UUID uuid, String updateType, Date effectTime) {
        super(objectType, uuid);
        this.updateType = updateType;
        this.effectTime = effectTime;
    }

    public EffectUpdateMessage(String objectType, String uuid, String updateType, Date effectTime) {
        super(objectType, uuid);
        this.updateType = updateType;
        this.effectTime = effectTime;
    }

    @Override
    public String getMessageType() {
        return "";
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(EffectUpdateMessage.HEADER_UPDATETYPE, this.updateType);
        headers.put(EffectUpdateMessage.HEADER_EFFECTTIME, this.effectTime);
        return headers;
    }
}