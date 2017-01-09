package dk.magenta.mox.agent.messages;

import dk.magenta.mox.agent.json.JSONObject;

import java.util.UUID;

/**
 * Created by lars on 25-01-16.
 */
public abstract class AuthorizedMessage extends Message {

    public static final long version = 1L;

    private String authorization;

    public AuthorizedMessage(String authorization) {
        this.authorization = authorization;
    }

    public Headers getHeaders() {
        Headers headers = super.getHeaders();
        headers.put(HEADER_AUTHORIZATION, this.authorization);
        return headers;
    }
}
