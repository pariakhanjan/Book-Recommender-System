import pandas as pd
import numpy as np
import joblib
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from src.config import PROCESSED_DATA_PATH, TFIDF_MATRIX_PATH, VECTORIZER_PATH
from utils.logger import logger


class BookRecommender:
    """
    Core Recommendation Engine using Content-Based Filtering.
    Utilizes TF-IDF vectors and Cosine Similarity to match user profiles with books.
    """

    def __init__(self):
        self.df = None
        self.tfidf = None
        self.tfidf_matrix = None
        self.load_resources()

    def load_resources(self):
        """Loads the processed dataset and pre-computed TF-IDF matrix into memory."""
        logger.info("Loading recommender engine resources...")
        self.df = pd.read_csv(PROCESSED_DATA_PATH)
        self.df['bookId'] = self.df['bookId'].astype(str)
        self.tfidf = joblib.load(VECTORIZER_PATH)
        self.tfidf_matrix = joblib.load(TFIDF_MATRIX_PATH)
        logger.info("Resources loaded successfully.")

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

    def recommend_user_profile(self,
                               preferred_languages: List[str],
                               favorite_genres: List[str] = None,
                               favorite_authors: List[str] = None,
                               liked_book_ids: List[str] = None,
                               disliked_genres: List[str] = None,
                               disliked_authors: List[str] = None,
                               disliked_book_ids: List[str] = None,
                               top_n: int = 5) -> List[Dict[str, Any]]:

        liked_book_ids = [str(b) for b in (liked_book_ids or [])]
        disliked_book_ids = [str(b) for b in (disliked_book_ids or [])]
        favorite_authors = favorite_authors or []
        favorite_genres = favorite_genres or []
        disliked_authors = disliked_authors or []
        disliked_genres = disliked_genres or []

        logger.info(f"DEBUG: Processing preferences -> Genres: {favorite_genres}, Authors: {favorite_authors}, Liked Books: {len(liked_book_ids)}")

        profile_vectors, weights = [], []

        if liked_book_ids:
            idx = self.df[self.df['bookId'].isin(liked_book_ids)].index
            logger.info(f"DEBUG: Matched {len(idx)} books for liked_book_ids")
            if len(idx) > 0:
                profile_vectors.append(np.asarray(self.tfidf_matrix[idx].mean(axis=0)).flatten())
                weights.append(0.60) # وزن بالا برای کتاب‌های مشخص

        if favorite_genres:
            mask = self.df['clean_genres'].apply(lambda g: any(fg.lower() in str(g).lower() for fg in favorite_genres))
            idx = self.df[mask].index
            logger.info(f"DEBUG: Matched {len(idx)} books for liked_genres")
            if len(idx) > 0:
                profile_vectors.append(np.asarray(self.tfidf_matrix[idx].mean(axis=0)).flatten())
                weights.append(0.30)

        if favorite_authors:
            mask = self.df['clean_author'].apply(lambda a: any(fav_auth.lower() in str(a).lower() for fav_auth in favorite_authors))
            idx = self.df[mask].index
            if len(idx) > 0:
                profile_vectors.append(np.asarray(self.tfidf_matrix[idx].mean(axis=0)).flatten())
                weights.append(0.10)

        if not profile_vectors:
            logger.info("COLD START TRIGGERED: User profile empty. Falling back to popular books.")
            return self.get_popular_books(n=top_n, languages=preferred_languages)

        weights_arr = np.array(weights)
        user_vector = np.average(profile_vectors, axis=0, weights=weights_arr).reshape(1, -1)
        sim_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        rec_df = self.df.copy()
        rec_df['similarity_score'] = sim_scores

        if disliked_book_ids:
            rec_df = rec_df[~rec_df['bookId'].isin(disliked_book_ids)]

        penalty_mask = pd.Series(False, index=rec_df.index)

        if disliked_genres:
            penalty_mask |= rec_df['clean_genres'].apply(lambda g: any(fg.lower() in str(g).lower() for fg in disliked_genres))

        if disliked_authors:
            penalty_mask |= rec_df['clean_author'].apply(lambda a: any(dis_auth.lower() in str(a).lower() for dis_auth in disliked_authors))

        rec_df.loc[penalty_mask, 'similarity_score'] -= 0.5

        if preferred_languages:
            rec_df = rec_df[rec_df['language'].isin(preferred_languages)]

        rec_df['final_score'] = rec_df['similarity_score'] + (rec_df['rating'].fillna(0) * 0.05)

        results = rec_df.sort_values(by='final_score', ascending=False).head(top_n)
        return (results[['bookId', 'title', 'author', 'genres', 'rating', 'coverImg', 'language', 'similarity_score']]
                .to_dict(orient='records'))

    def get_popular_books(self, n: int = 10, languages: List[str] = None) -> List[Dict[str, Any]]:
        sim_df = self.df.copy()
        if languages:
            sim_df = sim_df[sim_df['language'].isin(languages)]
            logger.info(f"Fetching {n} popular books filtered by languages: {languages}")

        top = sim_df.nlargest(n, 'rating')
        results = top[['bookId', 'title', 'author', 'genres', 'rating', 'coverImg', 'language']].copy()
        results['similarity_score'] = 0.0
        return results.to_dict(orient='records')
