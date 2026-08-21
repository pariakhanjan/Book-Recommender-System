package com.bookrecommender.app.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class UserPreferences {
    @SerializedName("id")
    private int id;

    @SerializedName("user_id")
    private int userId;

    @SerializedName("liked_genres")
    private List<String> likedGenres;

    @SerializedName("liked_authors")
    private List<String> likedAuthors;

    @SerializedName("liked_book_ids")
    private List<String> likedBookIds;

    @SerializedName("disliked_genres")
    private List<String> dislikedGenres;

    @SerializedName("disliked_authors")
    private List<String> dislikedAuthors;

    @SerializedName("disliked_book_ids")
    private List<String> dislikedBookIds;

    public UserPreferences() {}

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public int getUserId() { return userId; }
    public void setUserId(int userId) { this.userId = userId; }

    public List<String> getLikedGenres() { return likedGenres; }
    public void setLikedGenres(List<String> likedGenres) { this.likedGenres = likedGenres; }

    public List<String> getLikedAuthors() { return likedAuthors; }
    public void setLikedAuthors(List<String> likedAuthors) { this.likedAuthors = likedAuthors; }

    public List<String> getLikedBookIds() { return likedBookIds; }
    public void setLikedBookIds(List<String> likedBookIds) { this.likedBookIds = likedBookIds; }

    public List<String> getDislikedGenres() { return dislikedGenres; }
    public void setDislikedGenres(List<String> dislikedGenres) { this.dislikedGenres = dislikedGenres; }

    public List<String> getDislikedAuthors() { return dislikedAuthors; }
    public void setDislikedAuthors(List<String> dislikedAuthors) { this.dislikedAuthors = dislikedAuthors; }

    public List<String> getDislikedBookIds() { return dislikedBookIds; }
    public void setDislikedBookIds(List<String> dislikedBookIds) { this.dislikedBookIds = dislikedBookIds; }
}