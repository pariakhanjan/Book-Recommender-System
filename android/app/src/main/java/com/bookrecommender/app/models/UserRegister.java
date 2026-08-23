package com.bookrecommender.app.models;

public class UserRegister {
    private String username;
    private String password;

    public UserRegister(String username, String password) {
        this.username = username;
        this.password = password;
    }
    public String getUsername() { return username; }
    public String getPassword() { return password; }
}