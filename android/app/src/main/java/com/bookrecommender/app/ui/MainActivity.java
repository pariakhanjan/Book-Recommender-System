package com.bookrecommender.app.ui;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.bookrecommender.app.R;
import com.bookrecommender.app.models.Book;
import com.bookrecommender.app.viewmodel.BookViewModel;

import java.util.List;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private BookViewModel viewModel;
    private BookAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        RecyclerView recyclerView = findViewById(R.id.recyclerViewBooks);
        ProgressBar progressBar = findViewById(R.id.progressBar);

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
                Toast.makeText(this, books.size() + " books loaded", Toast.LENGTH_SHORT).show();
            } else {
                Log.w(TAG, "No books received");
                Toast.makeText(this, "No books available", Toast.LENGTH_LONG).show();
            }
        });

        viewModel.getError().observe(this, error -> {
            if (error != null) {
                Log.e(TAG, "Error: " + error);
                Toast.makeText(this, "Error: " + error, Toast.LENGTH_LONG).show();
            }
        });

        Log.d(TAG, "Starting to load books...");
        viewModel.loadPopularBooks(10, "en");
    }

    private void updateBookList(List<Book> newBooks) {
        adapter.setBooks(newBooks);
    }
}