package com.bookrecommender.app.models;
import com.google.gson.annotations.SerializedName;

public class FeedbackRequest {
    @SerializedName("user_id") private int userId;
    @SerializedName("book_id") private String bookId;
    @SerializedName("feedback_type") private String feedbackType;

    public FeedbackRequest(int userId, String bookId, String feedbackType) {
        this.userId = userId;
        this.bookId = bookId;
        this.feedbackType = feedbackType;
    }
}