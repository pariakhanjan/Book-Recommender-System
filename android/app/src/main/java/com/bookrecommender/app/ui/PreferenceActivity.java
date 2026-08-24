package com.bookrecommender.app.ui;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.bookrecommender.app.R;
import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.UserPreferences;
import com.bookrecommender.app.utils.UserManager;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PreferenceActivity extends AppCompatActivity {
    private static final String TAG = "PreferenceActivity";
    private ApiInterface apiService;
    private UserManager userManager;
    private ProgressBar progressBar;

    private CheckBox chkEn, chkFa;
    private AutoCompleteTextView actvLikedGenres, actvLikedAuthors, actvLikedBooks;
    private AutoCompleteTextView actvDislikedGenres, actvDislikedAuthors, actvDislikedBooks;
    private TextView tvSelLikedGenres, tvSelLikedAuthors, tvSelLikedBooks;
    private TextView tvSelDislikedGenres, tvSelDislikedAuthors, tvSelDislikedBooks;
    private Button btnSaveAndRecommend;

    private Set<String> selLikedGenres = new HashSet<>();
    private Set<String> selLikedAuthors = new HashSet<>();
    private Set<String> selLikedBooks = new HashSet<>();
    private Set<String> selDislikedGenres = new HashSet<>();
    private Set<String> selDislikedAuthors = new HashSet<>();
    private Set<String> selDislikedBooks = new HashSet<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_preference);

        apiService = RetrofitClient.getClient().create(ApiInterface.class);
        userManager = new UserManager(this);

        if (!userManager.isLoggedIn()) {
            startActivity(new Intent(this, AuthActivity.class));
            finish();
            return;
        }

        initViews();
        setupSearchListeners();

        btnSaveAndRecommend.setOnClickListener(v -> savePreferencesAndProceed());
    }

    private void initViews() {
        chkEn = findViewById(R.id.chkEn);
        chkFa = findViewById(R.id.chkFa);

        actvLikedGenres = findViewById(R.id.actvLikedGenres);
        actvLikedAuthors = findViewById(R.id.actvLikedAuthors);
        actvLikedBooks = findViewById(R.id.actvLikedBooks);
        actvDislikedGenres = findViewById(R.id.actvDislikedGenres);
        actvDislikedAuthors = findViewById(R.id.actvDislikedAuthors);
        actvDislikedBooks = findViewById(R.id.actvDislikedBooks);

        tvSelLikedGenres = findViewById(R.id.tvSelectedLikedGenres);
        tvSelLikedAuthors = findViewById(R.id.tvSelectedLikedAuthors);
        tvSelLikedBooks = findViewById(R.id.tvSelectedLikedBooks);
        tvSelDislikedGenres = findViewById(R.id.tvSelectedDislikedGenres);
        tvSelDislikedAuthors = findViewById(R.id.tvSelectedDislikedAuthors);
        tvSelDislikedBooks = findViewById(R.id.tvSelectedDislikedBooks);

        progressBar = findViewById(R.id.progressBar);
        btnSaveAndRecommend = findViewById(R.id.btnSaveAndRecommend);
    }

    private void setupSearchListeners() {
        setupAutoComplete(actvLikedGenres, "genres", selLikedGenres, tvSelLikedGenres);
        setupAutoComplete(actvLikedAuthors, "authors", selLikedAuthors, tvSelLikedAuthors);
        setupAutoComplete(actvLikedBooks, "books", selLikedBooks, tvSelLikedBooks);
        setupAutoComplete(actvDislikedGenres, "disliked-genres", selDislikedGenres, tvSelDislikedGenres);
        setupAutoComplete(actvDislikedAuthors, "disliked-authors", selDislikedAuthors, tvSelDislikedAuthors);
        setupAutoComplete(actvDislikedBooks, "disliked-books", selDislikedBooks, tvSelDislikedBooks);
    }

    private void setupAutoComplete(AutoCompleteTextView actv, String type, Set<String> selectedSet, TextView tvDisplay) {
        actv.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}

            @Override
            public void afterTextChanged(Editable s) {
                if (s.length() >= 2) {
                    searchBackend(type, s.toString(), actv, selectedSet, tvDisplay);
                }
            }
        });

        actv.setOnItemClickListener((parent, view, position, id) -> {
            String selectedItem = parent.getItemAtPosition(position).toString();
            if (selectedSet.add(selectedItem)) {
                updateDisplayText(selectedSet, tvDisplay);
                actv.setText("");
            }
        });
    }

    private void searchBackend(String type, String query, AutoCompleteTextView actv, Set<String> selectedSet, TextView tvDisplay) {
        Call<List<String>> call = null;
        switch (type) {
            case "genres":
                call = apiService.searchGenres(query);
                break;
            case "authors":
                call = apiService.searchAuthors(query);
                break;
            case "books":
                call = apiService.searchBooks(query);
                break;
            case "disliked-genres":
                call = apiService.searchGenres(query);
                break;
            case "disliked-authors":
                call = apiService.searchAuthors(query);
                break;
            case "disliked-books":
                call = apiService.searchBooks(query);
                break;
        }

        if (call != null) {
            call.enqueue(new Callback<List<String>>() {
                @Override
                public void onResponse(Call<List<String>> call, Response<List<String>> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        List<String> suggestions = new ArrayList<>();
                        for (String item : response.body()) {
                            if (!selectedSet.contains(item)) {
                                suggestions.add(item);
                            }
                        }

                        ArrayAdapter<String> adapter = new ArrayAdapter<>(PreferenceActivity.this,
                                android.R.layout.simple_dropdown_item_1line, suggestions);
                        actv.setAdapter(adapter);
                        actv.showDropDown();
                    }
                }
                @Override
                public void onFailure(Call<List<String>> call, Throwable t) {
                    Log.e(TAG, "Search failed: " + t.getMessage());
                }
            });
        }
    }

    private void updateDisplayText(Set<String> set, TextView tv) {
        if (set.isEmpty()) {
            tv.setText("Selected: None");
        } else {
            tv.setText("Selected: " + set.size() + " item(s)");
        }
    }

    private void savePreferencesAndProceed() {
        if (!chkEn.isChecked() && !chkFa.isChecked()) {
            Toast.makeText(this, "Please select at least one language", Toast.LENGTH_SHORT).show();
            return;
        }

        progressBar.setVisibility(View.VISIBLE);
        btnSaveAndRecommend.setEnabled(false);

        List<String> languages = new ArrayList<>();
        if (chkEn.isChecked()) languages.add("en");
        if (chkFa.isChecked()) languages.add("fa");

        UserPreferences prefs = new UserPreferences();
        prefs.setUserId(userManager.getUserId());
        prefs.setPreferredLanguages(languages);
        prefs.setLikedGenres(new ArrayList<>(selLikedGenres));
        prefs.setLikedAuthors(new ArrayList<>(selLikedAuthors));
        prefs.setLikedBookIds(new ArrayList<>(selLikedBooks));
        prefs.setDislikedGenres(new ArrayList<>(selDislikedGenres));
        prefs.setDislikedAuthors(new ArrayList<>(selDislikedAuthors));
        prefs.setDislikedBookIds(new ArrayList<>(selDislikedBooks));

        apiService.updateUserPreferences(userManager.getUserId(), prefs).enqueue(new Callback<UserPreferences>() {
            @Override
            public void onResponse(Call<UserPreferences> call, Response<UserPreferences> response) {
                progressBar.setVisibility(View.GONE);
                btnSaveAndRecommend.setEnabled(true);
                if (response.isSuccessful()) {
                    userManager.markSetupDone();
                    Toast.makeText(PreferenceActivity.this, "Preferences saved!", Toast.LENGTH_SHORT).show();
                    startActivity(new Intent(PreferenceActivity.this, MainActivity.class));
                    finish();
                } else {
                    Toast.makeText(PreferenceActivity.this, "Failed to save preferences", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<UserPreferences> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnSaveAndRecommend.setEnabled(true);
                Toast.makeText(PreferenceActivity.this, "Network error", Toast.LENGTH_SHORT).show();
            }
        });
    }
}