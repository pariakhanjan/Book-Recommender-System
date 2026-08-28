package com.bookrecommender.app.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.ProgressBar;
import android.widget.Toast;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.bookrecommender.app.R;
import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.UserPreferences;
import com.bookrecommender.app.utils.UserManager;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Initial setup activity where users select their preferred languages,
 * favorite genres, and authors for the first time.
 */
public class SetupActivity extends AppCompatActivity {
    private static final String TAG = "SetupActivity";
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

        if (!userManager.isLoggedIn()) {
            startActivity(new Intent(this, AuthActivity.class));
            finish();
            return;
        }

        initViews();
        btnSubmit.setOnClickListener(v -> submitPreferences());
    }

    /** Initializes all CheckBox and Button views. */
    private void initViews() {
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

        TextView tvCancelAndLogout = findViewById(R.id.tvCancelAndLogout);
        tvCancelAndLogout.setOnClickListener(v -> {
            userManager.clearUser();
            Intent intent = new Intent(this, AuthActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        });
    }

    /** Validates UI inputs and triggers the preference update process. */
    private void submitPreferences() {
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

        updatePreferences(userManager.getUserId(), languages, likedGenres, likedAuthors);
    }

    /**
     * Sends the collected preferences to the backend.
     * @param userId The ID of the current user.
     * @param languages Selected languages.
     * @param genres Selected genres.
     * @param authors Selected authors.
     */
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
                    userManager.markSetupDone();
                    Toast.makeText(SetupActivity.this, "Setup complete! Welcome!", Toast.LENGTH_SHORT).show();
                    startActivity(new Intent(SetupActivity.this, MainActivity.class));
                    finish();
                } else {
                    Log.e(TAG, "Update preferences failed: " + response.code());
                    Toast.makeText(SetupActivity.this, "Failed to save preferences", Toast.LENGTH_SHORT).show();
                    resetUI();
                }
            }

            @Override
            public void onFailure(Call<UserPreferences> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(SetupActivity.this, "Network error", Toast.LENGTH_SHORT).show();
                resetUI();
            }
        });
    }

    /** Resets the UI to its initial state in case of an error. */
    private void resetUI() {
        btnSubmit.setVisibility(View.VISIBLE);
        progressBar.setVisibility(View.GONE);
    }
}