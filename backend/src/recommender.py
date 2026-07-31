import pandas as pd
import numpy as np
import joblib
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from src.config import PROCESSED_DATA_PATH, TFIDF_MATRIX_PATH, VECTORIZER_PATH


class BookRecommender:
    def __init__(self):
        self.df = None
        self.tfidf = None
        self.tfidf_matrix = None
        self.load_resources()

    def load_resources(self):
        print("Loading recommender engine resources...")
        self.df = pd.read_csv(PROCESSED_DATA_PATH)
        self.df['bookId'] = self.df['bookId'].astype(str)
        self.tfidf = joblib.load(VECTORIZER_PATH)
        self.tfidf_matrix = joblib.load(TFIDF_MATRIX_PATH)
        print("Resources loaded successfully.")

    def recommend_by_book_id(self, book_id: str, top_n: int = 5, lang: Optional[str] = None) -> List[Dict[str, Any]]:
        book_id = str(book_id)
        if book_id not in self.df['bookId'].values:
            return []

        idx = self.df[self.df['bookId'] == book_id].index[0]

        target_vector = self.tfidf_matrix[idx]
        sim_scores = cosine_similarity(target_vector, self.tfidf_matrix).flatten()

        sim_df = self.df.copy()
        sim_df['similarity_score'] = sim_scores
        sim_df = sim_df[sim_df['bookId'] != book_id]

        if lang:
            sim_df = sim_df[sim_df['language'] == lang]

        results = sim_df.sort_values(by='similarity_score', ascending=False).head(top_n)
        return (results[['bookId', 'title', 'author', 'genres', 'rating', 'coverImg', 'language', 'similarity_score']]
                .to_dict(orient='records'))

    def recommend_user_profile(self, favorite_genres: List[str] = None,
                               favorite_authors: List[str] = None,
                               liked_book_ids: List[str] = None,
                               top_n: int = 5,
                               lang: Optional[str] = None) -> List[Dict[str, Any]]:
        liked_book_ids = [str(b) for b in (liked_book_ids or [])]
        favorite_authors = favorite_authors or []
        favorite_genres = favorite_genres or []

        profile_vectors, weights = [], []

        if liked_book_ids:
            liked_indices = self.df[self.df['bookId'].isin(liked_book_ids)].index
            if len(liked_indices) > 0:
                liked_vec = np.asarray(self.tfidf_matrix[liked_indices].mean(axis=0)).flatten()
                profile_vectors.append(liked_vec)
                weights.append(3.0)

        if favorite_genres:
            mask = self.df['genres'].apply(
                lambda g: any(fg.lower() in str(g).lower() for fg in favorite_genres)
            )
            genre_indices = self.df[mask].index
            if len(genre_indices) > 0:
                genre_df = self.df.loc[genre_indices].nlargest(50, 'rating')
                genre_vec = np.asarray(self.tfidf_matrix[genre_df.index].mean(axis=0)).flatten()
                profile_vectors.append(genre_vec)
                weights.append(2.0)

        if favorite_authors:
            clean_fav = [a.replace(" ", "").lower() for a in favorite_authors]
            mask = self.df['clean_author'].apply(
                lambda a: any(ca in str(a) for ca in clean_fav)
            )
            author_indices = self.df[mask].index
            if len(author_indices) > 0:
                author_vec = np.asarray(self.tfidf_matrix[author_indices].mean(axis=0)).flatten()
                profile_vectors.append(author_vec)
                weights.append(1.5)

        if not profile_vectors:
            return self.get_popular_books(n=top_n, lang=lang)

        weights = np.array(weights) / np.sum(weights)
        user_vector = np.average(profile_vectors, axis=0, weights=weights).reshape(1, -1)

        sim_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        rec_df = self.df.copy()
        rec_df['similarity_score'] = sim_scores

        if liked_book_ids:
            rec_df = rec_df[~rec_df['bookId'].isin(liked_book_ids)]

        if lang:
            rec_df = rec_df[rec_df['language'] == lang]

        results = rec_df.sort_values(by='similarity_score', ascending=False).head(top_n)
        return (results[['bookId', 'title', 'author', 'genres', 'rating', 'coverImg', 'language', 'similarity_score']]
                .to_dict(orient='records'))

    def get_popular_books(self, n: int = 10, lang: Optional[str] = None) -> List[Dict[str, Any]]:
        sim_df = self.df.copy()
        if lang:
            sim_df = sim_df[sim_df['language'] == lang]

        top = sim_df.nlargest(n, 'rating')
        results = top[['bookId', 'title', 'author', 'genres', 'rating', 'coverImg', 'language']].copy()
        results['similarity_score'] = 0.0
        return results.to_dict(orient='records')
