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
    @POST("/api/users")
    Call<User> createUser(@Body User user);

    @GET("/api/users/{user_id}/preferences")
    Call<UserPreferences> getUserPreferences(@Path("user_id") int userId);

    @PUT("/api/users/{user_id}/preferences")
    Call<UserPreferences> updateUserPreferences(@Path("user_id") int userId, @Body UserPreferences preferences);

    @POST("/api/feedback")
    Call<Map<String, Object>> submitFeedback(@Body FeedbackRequest request);

    @GET("/api/users/{user_id}/recommendations")
    Call<List<Book>> getUserRecommendations(
            @Path("user_id") int userId,
            @Query("top_n") int topN
    );
}