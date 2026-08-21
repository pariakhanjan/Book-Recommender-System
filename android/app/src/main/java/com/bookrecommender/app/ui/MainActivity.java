package com.bookrecommender.app.ui;

import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import com.bookrecommender.app.R;
import com.bookrecommender.app.models.Book;
import com.bookrecommender.app.viewmodel.BookViewModel;

import java.util.List;

public class MainActivity extends AppCompatActivity {
    private BookViewModel viewModel;
    private BookAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        RecyclerView recyclerView = findViewById(R.id.recyclerViewBooks);
        ProgressBar progressBar = findViewById(R.id.progressBar);

        adapter = new BookAdapter();
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(adapter);

        viewModel = new ViewModelProvider(this).get(BookViewModel.class);

        viewModel.getIsLoading().observe(this, loading ->
                progressBar.setVisibility(loading ? View.VISIBLE : View.GONE)
        );

        viewModel.getBooks().observe(this, this::updateBookList);

        viewModel.loadPopularBooks(10, "en");
    }

    private void updateBookList(List<Book> newBooks) {
        adapter.setBooks(newBooks);
    }
}