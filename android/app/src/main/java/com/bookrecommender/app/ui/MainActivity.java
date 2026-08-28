package com.bookrecommender.app.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.bookrecommender.app.R;
import com.bookrecommender.app.models.Book;
import com.bookrecommender.app.utils.UserManager;
import com.bookrecommender.app.viewmodel.BookViewModel;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";
    private BookViewModel viewModel;
    private BookAdapter adapter;
    private UserManager userManager;
    private TextView tvWelcome;
    private Spinner spinnerTopN;
    private Button btnReload, btnEditPrefs, btnLogout;
    private int selectedTopN = 10;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        userManager = new UserManager(this);

        if (!userManager.isLoggedIn()) {
            startActivity(new Intent(this, AuthActivity.class));
            finish();
            return;
        }

        RecyclerView recyclerView = findViewById(R.id.recyclerViewBooks);
        ProgressBar progressBar = findViewById(R.id.progressBar);
        tvWelcome = findViewById(R.id.tvWelcome);
        spinnerTopN = findViewById(R.id.spinnerTopN);
        btnReload = findViewById(R.id.btnReload);
        btnEditPrefs = findViewById(R.id.btnEditPrefs);
        btnLogout = findViewById(R.id.btnLogout);

        if (tvWelcome != null) {
            tvWelcome.setText("Welcome, " + userManager.getUsername() + "!");
        }

        ArrayAdapter<CharSequence> adapterSpinner = ArrayAdapter.createFromResource(this,
                R.array.top_n_options, android.R.layout.simple_spinner_item);
        adapterSpinner.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerTopN.setAdapter(adapterSpinner);
        spinnerTopN.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selectedTopN = Integer.parseInt(parent.getItemAtPosition(position).toString());
            }
            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                selectedTopN = 10;
            }
        });

        btnReload.setOnClickListener(v -> {
            Log.d(TAG, "Reloading recommendations with top_n=" + selectedTopN);
            loadRecommendations();
        });

        btnEditPrefs.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, PreferenceActivity.class);
            startActivity(intent);
        });

        btnLogout.setOnClickListener(v -> {
            userManager.clearUser();
            Intent intent = new Intent(MainActivity.this, AuthActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
        });

        adapter = new BookAdapter(this);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(adapter);

        viewModel = new ViewModelProvider(this).get(BookViewModel.class);

        viewModel.getIsLoading().observe(this, loading -> {
            Log.d(TAG, "Loading state: " + loading);
            progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
        });

        viewModel.getBooks().observe(this, books -> {
            if (books != null && !books.isEmpty()) {
                Log.d(TAG, "Books received: " + books.size());
                adapter.setBooks(books);
                Toast.makeText(this, books.size() + " recommendations loaded", Toast.LENGTH_SHORT).show();
            } else {
                Log.w(TAG, "No books received");
                Toast.makeText(this, "No recommendations available", Toast.LENGTH_LONG).show();
            }
        });

        viewModel.getError().observe(this, error -> {
            if (error != null) {
                Log.e(TAG, "Error: " + error);
                Toast.makeText(this, getUserFriendlyError(error), Toast.LENGTH_LONG).show();
            }
        });

        loadRecommendations();
    }

    private void loadRecommendations() {
        int userId = userManager.getUserId();
        Log.d(TAG, "Loading recommendations for user: " + userId + " with top_n=" + selectedTopN);
        viewModel.loadPersonalizedRecommendations(userId, selectedTopN);
    }

    private String getUserFriendlyError(String error) {
        if (error.contains("Network") || error.contains("Unable to resolve host")) {
            return "Network error. Please check your connection or server status.";
        } else if (error.contains("404")) {
            return "User not found. Please log in again.";
        } else if (error.contains("400")) {
            return "Please complete your profile setup first.";
        } else {
            return "An unexpected error occurred: " + error;
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_reset) {
            userManager.clearUser();
            Intent intent = new Intent(this, AuthActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            startActivity(intent);
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}