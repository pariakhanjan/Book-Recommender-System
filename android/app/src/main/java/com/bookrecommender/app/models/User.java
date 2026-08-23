package com.bookrecommender.app.models;

import com.google.gson.annotations.SerializedName;

public class User {
    @SerializedName("id") private int id;
    @SerializedName("username") private String username;
    @SerializedName("password") private String password;

    public User() {}

    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public int getId() { return id; }
    public String getUsername() { return username; }
    public String getPassword() { return password; }

    public void setId(int id) { this.id = id; }
    public void setUsername(String username) { this.username = username; }
    public void setPassword(String password) { this.password = password; }
}