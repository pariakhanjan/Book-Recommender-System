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
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class SetupActivity extends AppCompatActivity {
    private static final String TAG = "SetupActivity";
    private EditText etUsername, etPassword;
    private CheckBox chkEn, chkFa, chkFiction, chkMystery, chkSciFi, chkRomance, chkFantasy, chkThriller, chkBiography, chkHistory;
    private CheckBox chkAuthor1, chkAuthor2, chkAuthor3, chkAuthor4, chkAuthor5;
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
        etPassword = findViewById(R.id.etPassword);
        chkEn = findViewById(R.id.chkEn);
        chkFa = findViewById(R.id.chkFa);

        chkFiction = findViewById(R.id.chkFiction);
        chkMystery = findViewById(R.id.chkMystery);
        chkSciFi = findViewById(R.id.chkSciFi);
        chkRomance = findViewById(R.id.chkRomance);
        chkFantasy = findViewById(R.id.chkFantasy);
        chkThriller = findViewById(R.id.chkThriller);
        chkBiography = findViewById(R.id.chkBiography);
        chkHistory = findViewById(R.id.chkHistory);

        chkAuthor1 = findViewById(R.id.chkAuthor1);
        chkAuthor2 = findViewById(R.id.chkAuthor2);
        chkAuthor3 = findViewById(R.id.chkAuthor3);
        chkAuthor4 = findViewById(R.id.chkAuthor4);
        chkAuthor5 = findViewById(R.id.chkAuthor5);

        btnSubmit = findViewById(R.id.btnSubmit);
        progressBar = findViewById(R.id.progressBar);

        btnSubmit.setOnClickListener(v -> submitData());
    }

    private void submitData() {
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        if (username.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Username and password are required", Toast.LENGTH_SHORT).show();
            return;
        }
        if (username.length() < 3) {
            Toast.makeText(this, "Username must be at least 3 characters", Toast.LENGTH_SHORT).show();
            return;
        }
        if (!chkEn.isChecked() && !chkFa.isChecked()) {
            Toast.makeText(this, "Please select at least one language", Toast.LENGTH_SHORT).show();
            return;
        }

        List<String> languages = new ArrayList<>();
        if (chkEn.isChecked()) languages.add("en");
        if (chkFa.isChecked()) languages.add("fa");

        List<String> likedGenres = new ArrayList<>();
        if (chkFiction.isChecked()) likedGenres.add("Fiction");
        if (chkMystery.isChecked()) likedGenres.add("Mystery");
        if (chkSciFi.isChecked()) likedGenres.add("Science Fiction");
        if (chkRomance.isChecked()) likedGenres.add("Romance");
        if (chkFantasy.isChecked()) likedGenres.add("Fantasy");
        if (chkThriller.isChecked()) likedGenres.add("Thriller");
        if (chkBiography.isChecked()) likedGenres.add("Biography");
        if (chkHistory.isChecked()) likedGenres.add("History");

        List<String> likedAuthors = new ArrayList<>();
        if (chkAuthor1.isChecked()) likedAuthors.add("Stephen King");
        if (chkAuthor2.isChecked()) likedAuthors.add("J.K. Rowling");
        if (chkAuthor3.isChecked()) likedAuthors.add("Agatha Christie");
        if (chkAuthor4.isChecked()) likedAuthors.add("George Orwell");
        if (chkAuthor5.isChecked()) likedAuthors.add("Jane Austen");

        btnSubmit.setVisibility(View.GONE);
        progressBar.setVisibility(View.VISIBLE);

        User newUser = new User(username, username + "@example.com", password);
        apiService.createUser(newUser).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                if (response.isSuccessful() && response.body() != null) {
                    User createdUser = response.body();
                    Log.d(TAG, "User created with ID: " + createdUser.getId());
                    userManager.saveUser(createdUser.getId(), username);
                    updatePreferences(createdUser.getId(), languages, likedGenres, likedAuthors);
                } else {
                    Log.e(TAG, "Create user failed: " + response.code());
                    Toast.makeText(SetupActivity.this, "Failed to create user. Username may exist.", Toast.LENGTH_SHORT).show();
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

    private void updatePreferences(int userId, List<String> languages, List<String> genres, List<String> authors) {
        UserPreferences prefs = new UserPreferences();
        prefs.setUserId(userId);
        prefs.setPreferredLanguages(languages);
        prefs.setLikedGenres(genres);
        prefs.setLikedAuthors(authors);
        prefs.setLikedBookIds(new ArrayList<>());
        prefs.setDislikedGenres(new ArrayList<>());
        prefs.setDislikedAuthors(new ArrayList<>());
        prefs.setDislikedBookIds(new ArrayList<>());

        apiService.updateUserPreferences(userId, prefs).enqueue(new Callback<UserPreferences>() {
            @Override
            public void onResponse(Call<UserPreferences> call, Response<UserPreferences> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful()) {
                    Log.d(TAG, "Preferences updated successfully");
                    Toast.makeText(SetupActivity.this, "Setup complete! Welcome!", Toast.LENGTH_SHORT).show();
                    startActivity(new Intent(SetupActivity.this, MainActivity.class));
                    finish();
                } else {
                    Log.e(TAG, "Update preferences failed: " + response.code());
                    startActivity(new Intent(SetupActivity.this, MainActivity.class));
                    finish();
                }
            }

            @Override
            public void onFailure(Call<UserPreferences> call, Throwable t) {
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