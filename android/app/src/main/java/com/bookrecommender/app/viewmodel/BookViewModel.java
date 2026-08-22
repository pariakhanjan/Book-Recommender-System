package com.bookrecommender.app.viewmodel;

import android.util.Log;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

import com.bookrecommender.app.api.ApiInterface;
import com.bookrecommender.app.api.RetrofitClient;
import com.bookrecommender.app.models.Book;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class BookViewModel extends ViewModel {

    private static final String TAG = "BookViewModel";
    private final MutableLiveData<List<Book>> books = new MutableLiveData<>();
    private final MutableLiveData<Boolean> isLoading = new MutableLiveData<>();
    private final MutableLiveData<String> error = new MutableLiveData<>();
    private final ApiInterface apiService = RetrofitClient.getClient().create(ApiInterface.class);

    public LiveData<List<Book>> getBooks() { return books; }
    public LiveData<Boolean> getIsLoading() { return isLoading; }
    public LiveData<String> getError() { return error; }

    public void loadPersonalizedRecommendations(int userId, int topN, String lang) {
        Log.d(TAG, "Loading personalized recommendations for user: " + userId);
        isLoading.setValue(true);
        error.setValue(null);

        apiService.getUserRecommendations(userId, topN, lang).enqueue(new Callback<List<Book>>() {
            @Override
            public void onResponse(Call<List<Book>> call, Response<List<Book>> response) {
                isLoading.setValue(false);
                if (response.isSuccessful() && response.body() != null) {
                    Log.d(TAG, "Success: " + response.body().size() + " personalized books");
                    books.setValue(response.body());
                } else {
                    Log.e(TAG, "Failed with code: " + response.code());
                    error.setValue("Failed: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<List<Book>> call, Throwable t) {
                isLoading.setValue(false);
                Log.e(TAG, "Network error: " + t.getMessage());
                error.setValue("Network: " + t.getMessage());
            }
        });
    }

    // متد قدیمی: کتاب‌های محبوب (برای fallback)
    public void loadPopularBooks(int topN, String lang) {
        Log.d(TAG, "Loading popular books: topN=" + topN + ", lang=" + lang);
        isLoading.setValue(true);
        error.setValue(null);

        apiService.getPopularBooks(topN, lang).enqueue(new Callback<List<Book>>() {
            @Override
            public void onResponse(Call<List<Book>> call, Response<List<Book>> response) {
                isLoading.setValue(false);
                if (response.isSuccessful() && response.body() != null) {
                    Log.d(TAG, "Success: " + response.body().size() + " books");
                    books.setValue(response.body());
                } else {
                    Log.e(TAG, "Failed with code: " + response.code());
                    error.setValue("Failed: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<List<Book>> call, Throwable t) {
                isLoading.setValue(false);
                Log.e(TAG, "Network error: " + t.getMessage());
                error.setValue("Network: " + t.getMessage());
            }
        });
    }
}