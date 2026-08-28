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

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.bookrecommender.app.R;
import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.UserPreferences;
import com.bookrecommender.app.utils.UserManager;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Activity for managing user reading preferences, including language selection
 * and dynamic search for liked/disliked genres, authors, and books.
 */
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

    private Call<List<String>> currentSearchCall = null;

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
        loadExistingPreferences();

        btnSaveAndRecommend.setOnClickListener(v -> savePreferencesAndProceed());
    }

    private void loadExistingPreferences() {
        progressBar.setVisibility(View.VISIBLE);

        apiService.getUserPreferences(userManager.getUserId()).enqueue(new Callback<UserPreferences>() {
            @Override
            public void onResponse(Call<UserPreferences> call, Response<UserPreferences> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    UserPreferences prefs = response.body();

                    if (prefs.getPreferredLanguages() != null) {
                        if (prefs.getPreferredLanguages().contains("en")) chkEn.setChecked(true);
                        if (prefs.getPreferredLanguages().contains("fa")) chkFa.setChecked(true);
                    }

                    // Load liked items
                    if (prefs.getLikedGenres() != null) {
                        selLikedGenres.addAll(prefs.getLikedGenres());
                        updateDisplayText(selLikedGenres, tvSelLikedGenres);
                    }
                    if (prefs.getLikedAuthors() != null) {
                        selLikedAuthors.addAll(prefs.getLikedAuthors());
                        updateDisplayText(selLikedAuthors, tvSelLikedAuthors);
                    }
                    if (prefs.getLikedBookIds() != null) {
                        selLikedBooks.addAll(prefs.getLikedBookIds());
                        updateDisplayText(selLikedBooks, tvSelLikedBooks);
                    }

                    if (prefs.getDislikedGenres() != null) {
                        selDislikedGenres.addAll(prefs.getDislikedGenres());
                        updateDisplayText(selDislikedGenres, tvSelDislikedGenres);
                    }
                    if (prefs.getDislikedAuthors() != null) {
                        selDislikedAuthors.addAll(prefs.getDislikedAuthors());
                        updateDisplayText(selDislikedAuthors, tvSelDislikedAuthors);
                    }
                    if (prefs.getDislikedBookIds() != null) {
                        selDislikedBooks.addAll(prefs.getDislikedBookIds());
                        updateDisplayText(selDislikedBooks, tvSelDislikedBooks);
                    }

                    Log.d(TAG, "Loaded existing preferences for user " + userManager.getUserId());
                }
            }

            @Override
            public void onFailure(Call<UserPreferences> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Log.e(TAG, "Failed to load preferences: " + t.getMessage());
            }
        });
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

        tvSelLikedGenres = findViewById(R.id.tvSelLikedGenres);
        tvSelLikedAuthors = findViewById(R.id.tvSelLikedAuthors);
        tvSelLikedBooks = findViewById(R.id.tvSelLikedBooks);
        tvSelDislikedGenres = findViewById(R.id.tvSelDislikedGenres);
        tvSelDislikedAuthors = findViewById(R.id.tvSelDislikedAuthors);
        tvSelDislikedBooks = findViewById(R.id.tvSelDislikedBooks);

        tvSelLikedGenres.setOnClickListener(v -> showEditDialog(selLikedGenres, tvSelLikedGenres, "Liked Genres"));
        tvSelLikedAuthors.setOnClickListener(v -> showEditDialog(selLikedAuthors, tvSelLikedAuthors, "Liked Authors"));
        tvSelLikedBooks.setOnClickListener(v -> showEditDialog(selLikedBooks, tvSelLikedBooks, "Liked Books"));
        tvSelDislikedGenres.setOnClickListener(v -> showEditDialog(selDislikedGenres, tvSelDislikedGenres, "Disliked Genres"));
        tvSelDislikedAuthors.setOnClickListener(v -> showEditDialog(selDislikedAuthors, tvSelDislikedAuthors, "Disliked Authors"));
        tvSelDislikedBooks.setOnClickListener(v -> showEditDialog(selDislikedBooks, tvSelDislikedBooks, "Disliked Books"));

        progressBar = findViewById(R.id.progressBar);
        btnSaveAndRecommend = findViewById(R.id.btnSaveAndRecommend);

        TextView tvCancelAndLogout = findViewById(R.id.tvCancelAndLogout);
        tvCancelAndLogout.setOnClickListener(v -> {
            userManager.clearUser();
            Intent intent = new Intent(this, AuthActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        });
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
        if (currentSearchCall != null && !currentSearchCall.isCanceled()) {
            currentSearchCall.cancel();
        }

        Call<List<String>> call = null;
        switch (type) {
            case "genres": case "disliked-genres": call = apiService.searchGenres(query); break;
            case "authors": case "disliked-authors": call = apiService.searchAuthors(query); break;
            case "books": case "disliked-books": call = apiService.searchBooks(query); break;
        }

        if (call != null) {
            currentSearchCall = call;
            currentSearchCall.enqueue(new Callback<List<String>>() {
                @Override
                public void onResponse(Call<List<String>> call, Response<List<String>> response) {
                    if (call.isCanceled()) return;

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
                    if (call.isCanceled()) return;
                    Log.e(TAG, "Search failed: " + t.getMessage());
                }
            });
        }
    }

    private void updateDisplayText(Set<String> set, TextView tv) {
        if (set.isEmpty()) {
            tv.setText("✦ Selected: None");
        } else {
            StringBuilder sb = new StringBuilder("✦ Selected: ");
            int count = 0;
            for (String item : set) {
                if (count > 0) sb.append(", ");
                sb.append(formatDisplayName(item));
                count++;
            }
            tv.setText(sb.toString());
        }
    }

    private String formatDisplayName(String name) {
        if (name == null || name.isEmpty()) return "";

        name = name.replaceAll("\\(.*?\\)", "").trim();

        String result = name.replaceAll("([a-z])([A-Z])", "$1 $2");

        StringBuilder sb = new StringBuilder();
        for (String word : result.split("\\s+")) {
            if (!word.isEmpty()) {
                sb.append(Character.toUpperCase(word.charAt(0)))
                        .append(word.substring(1).toLowerCase())
                        .append(" ");
            }
        }
        return sb.toString().trim();
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
                    String errorMsg = "Failed to save preferences";
                    if (response.errorBody() != null) {
                        try {
                            JSONObject errorJson = new JSONObject(response.errorBody().string());
                            errorMsg = errorJson.getString("detail");
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                    Toast.makeText(PreferenceActivity.this, errorMsg, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<UserPreferences> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnSaveAndRecommend.setEnabled(true);
                Toast.makeText(PreferenceActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    /**
     * Shows a dialog to edit selected items.
     */
    private void showEditDialog(Set<String> set, TextView tvDisplay, String type) {
        if (set.isEmpty()) {
            Toast.makeText(this, "No items selected", Toast.LENGTH_SHORT).show();
            return;
        }

        String[] items = set.toArray(new String[0]);
        boolean[] checkedItems = new boolean[items.length];
        Arrays.fill(checkedItems, true);

        new AlertDialog.Builder(this)
                .setTitle("✦ Edit " + type + " ✦")
                .setMultiChoiceItems(items, checkedItems, (dialog, which, isChecked) -> {
                    if (isChecked) {
                        set.add(items[which]);
                    } else {
                        set.remove(items[which]);
                    }
                })
                .setPositiveButton("Save", (dialog, which) -> {
                    updateDisplayText(set, tvDisplay);
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

}