package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 25-01-16.
 */
public abstract class Message {

    public static final String HEADER_AUTHORIZATION = "autorisation";
    public static final String HEADER_MESSAGEID = "beskedID";
    public static final String HEADER_MESSAGEVERSION = "beskedversion";
    public static final String HEADER_OBJECTREFERENCE = "objektreference";
    public static final String HEADER_OBJECTTYPE = "objekttype";

    public static final String HEADER_TYPE = "type";
    public static final String HEADER_TYPE_VALUE_MANUAL = "Manuel";

    public static final String HEADER_OBJECTTYPE_VALUE_DOCUMENT = "dokument";

    public static final String HEADER_OBJECTID = "objektID";
    public static final String HEADER_OPERATION = "operation";
    public static final String HEADER_QUERY = "query";

    public static final long version = 1L;

    public Message() {
    }

    public JSONObject getJSON() {
        JSONObject object = new JSONObject();
        return object;
    }
    public Headers getHeaders() {
        Headers headers = new Headers();
        headers.put(HEADER_MESSAGEID, UUID.randomUUID().toString());
        headers.put(HEADER_MESSAGEVERSION, version);
        return headers;
    }
}
