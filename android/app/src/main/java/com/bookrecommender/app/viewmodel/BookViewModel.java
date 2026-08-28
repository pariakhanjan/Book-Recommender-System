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

/**
 * ViewModel responsible for fetching and managing book recommendation data.
 */
public class BookViewModel extends ViewModel {
    private static final String TAG = "BookViewModel";
    private final MutableLiveData<List<Book>> books = new MutableLiveData<>();
    private final MutableLiveData<Boolean> isLoading = new MutableLiveData<>();
    private final MutableLiveData<String> error = new MutableLiveData<>();
    private final ApiInterface apiService = RetrofitClient.getClient().create(ApiInterface.class);

    public LiveData<List<Book>> getBooks() { return books; }
    public LiveData<Boolean> getIsLoading() { return isLoading; }
    public LiveData<String> getError() { return error; }

    /**
     * Fetches personalized recommendations for a specific user.
     * @param userId The ID of the user.
     * @param topN The number of recommendations to fetch.
     */
    public void loadPersonalizedRecommendations(int userId, int topN) {
        Log.d(TAG, "Loading personalized recommendations for user: " + userId + ", top_n: " + topN);
        isLoading.setValue(true);
        error.setValue(null);

        apiService.getUserRecommendations(userId, topN).enqueue(new Callback<List<Book>>() {
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
}