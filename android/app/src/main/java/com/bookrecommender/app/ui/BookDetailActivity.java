package com.bookrecommender.app.ui;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.bookrecommender.app.R;
import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.Book;
import com.bookrecommender.app.models.FeedbackRequest;
import com.bumptech.glide.Glide;
import java.util.Map;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class BookDetailActivity extends AppCompatActivity {
    private static final String TAG = "BookDetailActivity";
    private Book book;
    private ApiInterface apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_book_detail);

        book = (Book) getIntent().getSerializableExtra("book", Book.class);
        if (book == null) {
            Toast.makeText(this, "Error loading book data", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        apiService = RetrofitClient.getClient().create(ApiInterface.class);
        initViews();
        setupClickListeners();
    }

    private void initViews() {
        ImageView ivCover = findViewById(R.id.ivBookCover);
        TextView tvTitle = findViewById(R.id.tvBookTitle);
        TextView tvAuthor = findViewById(R.id.tvBookAuthor);
        TextView tvRating = findViewById(R.id.tvBookRating);

        tvTitle.setText(book.getTitle());
        tvAuthor.setText(book.getAuthor());
        tvRating.setText(String.format("Rating: %.1f / 5.0", book.getRating()));

        if (book.getCoverImg() != null && !book.getCoverImg().isEmpty()) {
            Glide.with(this)
                    .load(book.getCoverImg())
                    .placeholder(R.drawable.ic_book_placeholder)
                    .error(R.drawable.ic_book_placeholder)
                    .into(ivCover);
        }
    }

    private void setupClickListeners() {
        Button btnLike = findViewById(R.id.btnLike);
        Button btnDislike = findViewById(R.id.btnDislike);

        btnLike.setOnClickListener(v -> sendFeedback("liked"));
        btnDislike.setOnClickListener(v -> sendFeedback("disliked"));
    }

    private void sendFeedback(String feedbackType) {
        Log.d(TAG, "Sending feedback: " + feedbackType + " for book: " + book.getBookId());

        TextView tvFeedback = findViewById(R.id.tvFeedbackMessage);

        FeedbackRequest request = new FeedbackRequest(1, book.getBookId(), feedbackType);

        apiService.submitFeedback(request).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful()) {
                    String msg = feedbackType.equals("liked")
                            ? "✅ Added to liked list"
                            : "❌ Added to disliked list";
                    Log.d(TAG, "Feedback success: " + msg);
                    tvFeedback.setText(msg);
                    tvFeedback.setVisibility(View.VISIBLE);
                    Toast.makeText(BookDetailActivity.this, msg, Toast.LENGTH_SHORT).show();
                } else {
                    try {
                        String errorBody = response.errorBody() != null ? response.errorBody().string() : "Unknown";
                        Log.e(TAG, "Feedback failed with code: " + response.code() + " Body: " + errorBody);
                    } catch (Exception e) {
                        Log.e(TAG, "Feedback failed with code: " + response.code());
                    }
                    Toast.makeText(BookDetailActivity.this, "Failed to submit feedback", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                Log.e(TAG, "Network error: " + t.getMessage());
                Toast.makeText(BookDetailActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }
}