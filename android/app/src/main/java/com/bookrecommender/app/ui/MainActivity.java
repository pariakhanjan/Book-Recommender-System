package com.bookrecommender.app.ui;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ProgressBar;
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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        userManager = new UserManager(this);

        if (!userManager.isSetupDone()) {
            Intent intent = new Intent(this, SetupActivity.class);
            startActivity(intent);
            finish();
            return;
        }

        RecyclerView recyclerView = findViewById(R.id.recyclerViewBooks);
        ProgressBar progressBar = findViewById(R.id.progressBar);
        tvWelcome = findViewById(R.id.tvWelcome);

        if (tvWelcome != null) {
            tvWelcome.setText("Welcome, " + userManager.getUsername() + "!");
        }

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
                Toast.makeText(this, books.size() + " personalized recommendations loaded", Toast.LENGTH_SHORT).show();
            } else {
                Log.w(TAG, "No books received");
                Toast.makeText(this, "No recommendations available", Toast.LENGTH_LONG).show();
            }
        });

        viewModel.getError().observe(this, error -> {
            if (error != null) {
                Log.e(TAG, "Error: " + error);
                Toast.makeText(this, "Error: " + error, Toast.LENGTH_LONG).show();
            }
        });

        int userId = userManager.getUserId();
        Log.d(TAG, "Loading recommendations for user: " + userId);
        viewModel.loadPersonalizedRecommendations(userId, 10, "en");
    }

    // منوی بالا برای خروج و ریست
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_reset) {
            userManager.clearUser();
            Intent intent = new Intent(this, SetupActivity.class);
            startActivity(intent);
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}