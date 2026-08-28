package com.bookrecommender.app.utils;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Utility class for managing user session state using SharedPreferences.
 */
public class UserManager {
    private static final String PREFS_NAME = "BookRecommenderPrefs";
    private static final String KEY_USER_ID = "user_id";
    private static final String KEY_USERNAME = "username";
    private static final String KEY_IS_LOGGED_IN = "is_logged_in";
    private static final String KEY_IS_SETUP_DONE = "is_setup_done";

    private final SharedPreferences prefs;

    public UserManager(Context context) {
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public void saveUser(int userId, String username) {
        prefs.edit()
                .putInt(KEY_USER_ID, userId)
                .putString(KEY_USERNAME, username)
                .putBoolean(KEY_IS_LOGGED_IN, true)
                .apply();
    }

    public void markSetupDone() {
        prefs.edit().putBoolean(KEY_IS_SETUP_DONE, true).apply();
    }

    public int getUserId() { return prefs.getInt(KEY_USER_ID, -1); }
    public String getUsername() { return prefs.getString(KEY_USERNAME, "Guest"); }
    public boolean isLoggedIn() { return prefs.getBoolean(KEY_IS_LOGGED_IN, false); }
    public boolean isSetupDone() { return prefs.getBoolean(KEY_IS_SETUP_DONE, false); }

    public void clearUser() {
        prefs.edit()
                .remove(KEY_USER_ID)
                .remove(KEY_USERNAME)
                .putBoolean(KEY_IS_LOGGED_IN, false)
                .putBoolean(KEY_IS_SETUP_DONE, false)
                .apply();
    }
}