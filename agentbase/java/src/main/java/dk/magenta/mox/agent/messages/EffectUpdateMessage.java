package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONObject;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.UUID;
import java.util.Date;
import java.util.regex.Pattern;

/**
 * Created by lars on 09-01-17.
 */
public class EffectUpdateMessage extends ObjectInstanceMessage {

    public static final String messageType = "EffectUpdateMessage";

    public static final String HEADER_UPDATETYPE = "updatetype";
    public static final String HEADER_EFFECTTIME = "effecttime";

    public static final String UPDATETYPE_START = "start";
    public static final String UPDATETYPE_END = "end";
    public static final String UPDATETYPE_BOTH = "both";

    private static SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd kk:mm:ssZ");

    protected String updateType;
    protected Date effectTime;

    public EffectUpdateMessage(String objectType, UUID uuid, String updateType, Date effectTime) {
        super(objectType, uuid);
        if (!EffectUpdateMessage.UPDATETYPE_START.equals(updateType) && !EffectUpdateMessage.UPDATETYPE_END.equals(updateType) && !EffectUpdateMessage.UPDATETYPE_BOTH.equals(updateType)) {
            throw IllegalArgumentException("updateType must be one of EffectUpdateMessage.UPDATETYPE_START, EffectUpdateMessage.UPDATETYPE_END or EffectUpdateMessage.UPDATETYPE_BOTH");
        }
        this.updateType = updateType;
        this.effectTime = effectTime;
    }

    public EffectUpdateMessage(String objectType, String uuid, String updateType, Date effectTime) {
        this(objectType, UUID.fromString(uuid), updateType, effectTime);
    }

    public EffectUpdateMessage(String objectType, String uuid, String updateType, String effectTime) throws ParseException {
        this(objectType, UUID.fromString(uuid), updateType, EffectUpdateMessage.parseDate(effectTime));
    }

    @Override
    public String getMessageType() {
        return EffectUpdateMessage.messageType;
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(EffectUpdateMessage.HEADER_UPDATETYPE, this.updateType);
        headers.put(EffectUpdateMessage.HEADER_EFFECTTIME, this.effectTime);
        return headers;
    }

    public static boolean matchType(Headers headers) {
        try {
            return EffectUpdateMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static EffectUpdateMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (EffectUpdateMessage.matchType(headers)) {
            try {
                return new EffectUpdateMessage(
                        headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                        headers.getString(ObjectInstanceMessage.HEADER_OBJECTID),
                        headers.getString(EffectUpdateMessage.HEADER_UPDATETYPE),
                        headers.getString(EffectUpdateMessage.HEADER_EFFECTTIME)
                );
            } catch (ParseException e) {
            }
        }
        return null;
    }

    private static Pattern timezoneFormatDetector = Pattern.compile("[+\\-]\\d\\d$");

    private static Date parseDate(String date) throws ParseException {
        if (EffectUpdateMessage.timezoneFormatDetector.matcher(date).find()) {
            date = date + "00";
        }
        return EffectUpdateMessage.dateFormat.parse(date);
    }
}