package com.bookrecommender.app.viewmodel;

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
    private final MutableLiveData<List<Book>> books = new MutableLiveData<>();
    private final MutableLiveData<Boolean> isLoading = new MutableLiveData<>();
    private final ApiInterface apiService = RetrofitClient.getClient().create(ApiInterface.class);

    public LiveData<List<Book>> getBooks() { return books; }
    public LiveData<Boolean> getIsLoading() { return isLoading; }

    public void loadPopularBooks(int topN, String lang) {
        isLoading.setValue(true);
        apiService.getPopularBooks(topN, lang).enqueue(new Callback<List<Book>>() {
            @Override
            public void onResponse(Call<List<Book>> call, Response<List<Book>> response) {
                isLoading.setValue(false);
                if (response.isSuccessful() && response.body() != null) {
                    books.setValue(response.body());
                }
            }
            @Override
            public void onFailure(Call<List<Book>> call, Throwable t) {
                isLoading.setValue(false);
                // برای دیباگ: t.printStackTrace();
            }
        });
    }
}