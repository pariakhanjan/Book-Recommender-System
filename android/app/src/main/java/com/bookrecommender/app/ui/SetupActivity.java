package com.bookrecommender.app.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.bookrecommender.app.R;
import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.User;
import com.bookrecommender.app.models.UserPreferences;
import com.bookrecommender.app.utils.UserManager;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class SetupActivity extends AppCompatActivity {

    private static final String TAG = "SetupActivity";
    private EditText etUsername;
    private Button btnSubmit;
    private ProgressBar progressBar;
    private ApiInterface apiService;
    private UserManager userManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_setup);

        apiService = RetrofitClient.getClient().create(ApiInterface.class);
        userManager = new UserManager(this);

        etUsername = findViewById(R.id.etUsername);
        btnSubmit = findViewById(R.id.btnSubmit);
        progressBar = findViewById(R.id.progressBar);

        btnSubmit.setOnClickListener(v -> submitPreferences());
    }

    private void submitPreferences() {
        String username = etUsername.getText().toString().trim();

        if (username.isEmpty()) {
            Toast.makeText(this, "Please enter a username", Toast.LENGTH_SHORT).show();
            return;
        }

        if (username.length() < 3) {
            Toast.makeText(this, "Username must be at least 3 characters", Toast.LENGTH_SHORT).show();
            return;
        }

        // جمع‌آوری ژانرهای انتخاب شده
        List<String> selectedGenres = new ArrayList<>();
        if (((CheckBox) findViewById(R.id.chkFiction)).isChecked()) selectedGenres.add("Fiction");
        if (((CheckBox) findViewById(R.id.chkMystery)).isChecked()) selectedGenres.add("Mystery");
        if (((CheckBox) findViewById(R.id.chkSciFi)).isChecked()) selectedGenres.add("Science Fiction");
        if (((CheckBox) findViewById(R.id.chkRomance)).isChecked()) selectedGenres.add("Romance");
        if (((CheckBox) findViewById(R.id.chkFantasy)).isChecked()) selectedGenres.add("Fantasy");
        if (((CheckBox) findViewById(R.id.chkThriller)).isChecked()) selectedGenres.add("Thriller");
        if (((CheckBox) findViewById(R.id.chkBiography)).isChecked()) selectedGenres.add("Biography");
        if (((CheckBox) findViewById(R.id.chkHistory)).isChecked()) selectedGenres.add("History");

        // جمع‌آوری نویسندگان انتخاب شده
        List<String> selectedAuthors = new ArrayList<>();
        if (((CheckBox) findViewById(R.id.chkAuthor1)).isChecked()) selectedAuthors.add("Stephen King");
        if (((CheckBox) findViewById(R.id.chkAuthor2)).isChecked()) selectedAuthors.add("J.K. Rowling");
        if (((CheckBox) findViewById(R.id.chkAuthor3)).isChecked()) selectedAuthors.add("Agatha Christie");
        if (((CheckBox) findViewById(R.id.chkAuthor4)).isChecked()) selectedAuthors.add("George Orwell");
        if (((CheckBox) findViewById(R.id.chkAuthor5)).isChecked()) selectedAuthors.add("Jane Austen");

        if (selectedGenres.isEmpty()) {
            Toast.makeText(this, "Please select at least one genre", Toast.LENGTH_SHORT).show();
            return;
        }

        // نمایش Loading
        btnSubmit.setVisibility(View.GONE);
        progressBar.setVisibility(View.VISIBLE);

        // مرحله ۱: ساخت کاربر
        createUser(username, selectedGenres, selectedAuthors);
    }

    private void createUser(String username, List<String> genres, List<String> authors) {
        User newUser = new User(username, username + "@example.com");

        apiService.createUser(newUser).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                if (response.isSuccessful() && response.body() != null) {
                    User createdUser = response.body();
                    Log.d(TAG, "User created with ID: " + createdUser.getId());

                    // ذخیره در SharedPreferences
                    userManager.saveUser(createdUser.getId(), username);

                    // مرحله ۲: ارسال Preferences
                    updatePreferences(createdUser.getId(), genres, authors);
                } else {
                    Log.e(TAG, "Create user failed: " + response.code());
                    Toast.makeText(SetupActivity.this, "Failed to create user", Toast.LENGTH_SHORT).show();
                    resetUI();
                }
            }

            @Override
            public void onFailure(Call<User> call, Throwable t) {
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(SetupActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
                resetUI();
            }
        });
    }

    private void updatePreferences(int userId, List<String> genres, List<String> authors) {
        Map<String, Object> prefMap = new HashMap<>();
        prefMap.put("liked_genres", genres);
        prefMap.put("liked_authors", authors);
        prefMap.put("liked_book_ids", new ArrayList<>());
        prefMap.put("disliked_genres", new ArrayList<>());
        prefMap.put("disliked_authors", new ArrayList<>());
        prefMap.put("disliked_book_ids", new ArrayList<>());

        apiService.updateUserPreferences(userId, prefMap).enqueue(new Callback<Map>() {
            @Override
            public void onResponse(Call<Map> call, Response<Map> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful()) {
                    Log.d(TAG, "Preferences updated successfully");
                    Toast.makeText(SetupActivity.this, "Setup complete! Welcome!", Toast.LENGTH_SHORT).show();

                    // انتقال به MainActivity
                    Intent intent = new Intent(SetupActivity.this, MainActivity.class);
                    startActivity(intent);
                    finish();
                } else {
                    Log.e(TAG, "Update preferences failed: " + response.code());
                    Toast.makeText(SetupActivity.this, "User created but preferences failed", Toast.LENGTH_LONG).show();

                    // حتی اگر preferences شکست خورد، به MainActivity برو
                    Intent intent = new Intent(SetupActivity.this, MainActivity.class);
                    startActivity(intent);
                    finish();
                }
            }

            @Override
            public void onFailure(Call<Map> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(SetupActivity.this, "Network error", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void resetUI() {
        btnSubmit.setVisibility(View.VISIBLE);
        progressBar.setVisibility(View.GONE);
    }
}