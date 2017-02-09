package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.exceptions.MissingHeaderException;
import dk.magenta.mox.agent.json.JSONArray;
import dk.magenta.mox.agent.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Created by lars on 15-02-16.
 */
public class ListDocumentMessage extends ObjectTypeMessage {

    public static final String messageType = "ListDocumentMessage";

    protected ArrayList<UUID> uuids;

    public static final String OPERATION = "list";

    public ListDocumentMessage(String authorization, String objectType, List<UUID> uuids) {
        super(authorization, objectType);
        this.uuids = new ArrayList<UUID>(uuids);
    }

    public ListDocumentMessage(String authorization, String objectType, UUID uuid) {
        super(authorization, objectType);
        this.uuids = new ArrayList<UUID>();
        this.uuids.add(uuid);
    }

    public ListDocumentMessage(String authorization, String objectType, JSONArray uuids) {
        super(authorization, objectType);
        this.uuids = new ArrayList<UUID>();
        for (int i=0; i<uuids.length(); i++) {
            this.uuids.add(i, UUID.fromString(uuids.getString(i)));
        }
    }

    @Override
    public String getMessageType() {
        return ListDocumentMessage.messageType;
    }

    @Override
    public String getOperationName() {
        return ListDocumentMessage.OPERATION;
    }

    @Override
    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        JSONObject object = new JSONObject();
        JSONArray uuidList = new JSONArray();
        for (UUID uuid : uuids) {
            uuidList.put(uuid.toString());
        }
        object.put("uuid", uuidList);
        headers.put(ObjectTypeMessage.HEADER_QUERY, object.toString());
        return headers;
    }

    public static boolean matchType(Headers headers) {
        try {
            return ListDocumentMessage.messageType.equals(headers.getString(Message.HEADER_MESSAGETYPE)) && ListDocumentMessage.OPERATION.equalsIgnoreCase(headers.getString(ObjectTypeMessage.HEADER_OPERATION));
        } catch (MissingHeaderException e) {
            return false;
        }
    }

    public static ListDocumentMessage parse(Headers headers, JSONObject data) throws MissingHeaderException {
        if (ListDocumentMessage.matchType(headers)) {
            return new ListDocumentMessage(
                    headers.getString(Message.HEADER_AUTHORIZATION),
                    headers.getString(ObjectTypeMessage.HEADER_OBJECTTYPE),
                    new JSONObject(headers.getString(ObjectTypeMessage.HEADER_QUERY)).getJSONArray("uuid")
            );
        }
        return null;
    }
}
