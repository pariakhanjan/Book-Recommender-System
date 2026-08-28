package com.bookrecommender.app.models;

import com.google.gson.annotations.SerializedName;

/**
 * Model class used for sending new user registration data to the backend.
 */
public class UserRegister {
    @SerializedName("username")
    private String username;

    @SerializedName("password")
    private String password;

    public UserRegister(String username, String password) {
        this.username = username;
        this.password = password;
    }
    public String getUsername() { return username; }
    public String getPassword() { return password; }
}