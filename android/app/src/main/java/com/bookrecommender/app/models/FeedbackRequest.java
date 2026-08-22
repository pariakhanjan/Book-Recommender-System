package com.bookrecommender.app.models;

public class FeedbackRequest {
    private int user_id;
    private String book_id;
    private String feedback_type;

    public FeedbackRequest(int user_id, String book_id, String feedback_type) {
        this.user_id = user_id;
        this.book_id = book_id;
        this.feedback_type = feedback_type;
    }
}