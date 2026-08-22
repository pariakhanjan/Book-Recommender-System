package com.bookrecommender.app.api;

import com.bookrecommender.app.models.Book;
import com.bookrecommender.app.models.FeedbackRequest;
import com.bookrecommender.app.models.User;
import com.bookrecommender.app.models.UserPreferences;
import java.util.List;
import java.util.Map;
import retrofit2.Call;
import retrofit2.http.*;

public interface ApiInterface {
    @GET("/") Call<Map<String, Object>> healthCheck();
    @GET("/api/books/popular") Call<List<Book>> getPopularBooks(@Query("top_n") int topN, @Query("lang") String lang);
    @POST("/api/books/search") Call<List<Book>> searchBooks(@Body Map<String, Object> searchRequest);
    @GET("/api/recommend/book/{book_id}") Call<List<Book>> getRecommendationsByBook(@Path("book_id") String bookId, @Query("top_n") int topN, @Query("lang") String lang);
    @POST("/api/recommend/profile") Call<List<Book>> getRecommendationsByProfile(@Body Map<String, Object> profileRequest);
    @GET("/api/users/{user_id}/recommendations") Call<List<Book>> getUserRecommendations(@Path("user_id") int userId, @Query("top_n") int topN, @Query("lang") String lang);
    @POST("/api/users") Call<User> createUser(@Body User user);
    @GET("/api/users/{user_id}") Call<User> getUser(@Path("user_id") int userId);
    @GET("/api/users/{user_id}/preferences") Call<UserPreferences> getUserPreferences(@Path("user_id") int userId);
    @PUT("/api/users/{user_id}/preferences") Call<UserPreferences> updateUserPreferences(@Path("user_id") int userId, @Body UserPreferences preferences);
    @POST("/api/users/{user_id}/add-to-liked") Call<UserPreferences> addToLikedBooks(@Path("user_id") int userId, @Body Map<String, String> bookRequest);
    @POST("/api/feedback") Call<Map<String, Object>> submitFeedback(@Body FeedbackRequest request);

}