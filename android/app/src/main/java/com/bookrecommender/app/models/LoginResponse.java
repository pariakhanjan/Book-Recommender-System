package com.bookrecommender.app.models;

import com.google.gson.annotations.SerializedName;

/**
 * Model class representing the response received after a successful user login.
 */
public class LoginResponse {
    @SerializedName("user_id")
    private int userId;

    @SerializedName("username")
    private String username;

    @SerializedName("message")
    private String message;

    /** @return The unique identifier of the logged-in user. */
    public int getUserId() { return userId; }

    /** @return The username of the logged-in user. */
    public String getUsername() { return username; }

    /** @return A success or informational message from the server. */
    public String getMessage() { return message; }
}