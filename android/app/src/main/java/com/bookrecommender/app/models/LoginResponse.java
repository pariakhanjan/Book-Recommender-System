package com.bookrecommender.app.models;

import com.google.gson.annotations.SerializedName;

public class LoginResponse {
    @SerializedName("user_id")
    private int userId;

    @SerializedName("username")
    private String username;

    @SerializedName("message")
    private String message;

    public int getUserId() { return userId; }
    public String getUsername() { return username; }
    public String getMessage() { return message; }
}