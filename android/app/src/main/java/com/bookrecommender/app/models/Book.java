package com.bookrecommender.app.models;

import com.google.gson.annotations.SerializedName;

public class Book {
    @SerializedName("bookId") private String bookId;
    @SerializedName("title") private String title;
    @SerializedName("author") private String author;
    @SerializedName("genres") private String genres;
    @SerializedName("rating") private double rating;
    @SerializedName("coverImg") private String coverImg;
    @SerializedName("language") private String language;
    @SerializedName("similarity_score") private double similarityScore;
    @SerializedName("match_score") private double matchScore;

    public Book() {}

    public String getBookId() { return bookId; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public String getGenres() { return genres; }
    public double getRating() { return rating; }
    public String getCoverImg() { return coverImg; }
    public String getLanguage() { return language; }
    public double getSimilarityScore() { return similarityScore; }
    public double getMatchScore() { return matchScore; }

    public void setBookId(String bookId) { this.bookId = bookId; }
    public void setTitle(String title) { this.title = title; }
    public void setAuthor(String author) { this.author = author; }
    public void setGenres(String genres) { this.genres = genres; }
    public void setRating(double rating) { this.rating = rating; }
    public void setCoverImg(String coverImg) { this.coverImg = coverImg; }
    public void setLanguage(String language) { this.language = language; }
    public void setSimilarityScore(double similarityScore) { this.similarityScore = similarityScore; }
    public void setMatchScore(double matchScore) { this.matchScore = matchScore; }
}