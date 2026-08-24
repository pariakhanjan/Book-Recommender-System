package com.bookrecommender.app.api;

import com.bookrecommender.app.models.Book;
import com.bookrecommender.app.models.FeedbackRequest;
import com.bookrecommender.app.models.User;
import com.bookrecommender.app.models.UserLogin;
import com.bookrecommender.app.models.UserPreferences;
import com.bookrecommender.app.models.LoginResponse;
import com.bookrecommender.app.models.UserRegister;
import java.util.List;
import java.util.Map;
import retrofit2.Call;
import retrofit2.http.*;

public interface ApiInterface {
    @POST("/api/auth/login")
    Call<LoginResponse> loginUser(@Body UserLogin userLogin);

    @POST("/api/users")
    Call<User> createUser(@Body UserRegister userRegister);

    @GET("/api/users/{user_id}/preferences")
    Call<UserPreferences> getUserPreferences(@Path("user_id") int userId);

    @PUT("/api/users/{user_id}/preferences")
    Call<UserPreferences> updateUserPreferences(@Path("user_id") int userId, @Body UserPreferences preferences);

    @POST("/api/feedback")
    Call<Map<String, Object>> submitFeedback(@Body FeedbackRequest request);

    @GET("/api/users/{user_id}/recommendations")
    Call<List<Book>> getUserRecommendations(@Path("user_id") int userId, @Query("top_n") int topN);

    @GET("/api/search/genres")
    Call<List<String>> searchGenres(@Query("q") String query);

    @GET("/api/search/authors")
    Call<List<String>> searchAuthors(@Query("q") String query);

    @GET("/api/search/books")
    Call<List<String>> searchBooks(@Query("q") String query);

    @GET("/api/search/unique-genres")
    Call<List<String>> getUniqueGenres();

    @GET("/api/search/unique-authors")
    Call<List<String>> getUniqueAuthors();

    @GET("/api/search/unique-books")
    Call<List<String>> getUniqueBooks();
}