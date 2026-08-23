import pandas as pd
from typing import List, Dict, Any, Set
from src.recommender import BookRecommender
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RecommenderEvaluator:
    def __init__(self, recommender: BookRecommender):
        self.recommender = recommender
        self.df = recommender.df
        self.tfidf_matrix = recommender.tfidf_matrix

    def _get_ground_truth_ids(self,
                              liked_genres: List[str],
                              liked_authors: List[str],
                              liked_books: List[str],
                              disliked_genres: List[str],
                              disliked_authors: List[str],
                              disliked_books: List[str],
                              lang: str) -> Set[str]:
        """
        Finds all books in the dataset that match the user's positive preferences
        and do not match any negative preferences.

        Special handling:
        - If only language is set (Cold Start): returns all books in that language
        - If only books are liked: returns similar books to liked books (excluding liked books themselves)
        """
        mask = pd.Series(True, index=self.df.index)

        if lang:
            mask = mask & (self.df['language'] == lang)

        is_cold_start = (
            not liked_books and
            not liked_genres and
            not liked_authors
        )

        if is_cold_start:
            # For Cold Start, Ground Truth = all books in the selected language
            return set(self.df[mask]['bookId'].astype(str).tolist())

        positive_mask = pd.Series(False, index=self.df.index)

        if liked_books:
            liked_indices = self.df[self.df['bookId'].astype(str).isin([str(b) for b in liked_books])].index
            if len(liked_indices) > 0:
                avg_vector = np.asarray(self.tfidf_matrix[liked_indices].mean(axis=0)).flatten().reshape(1, -1)
                similarities = cosine_similarity(avg_vector, self.tfidf_matrix).flatten()
                similar_indices = np.argsort(similarities)[::-1][:1000]
                similar_book_ids = set(self.df.iloc[similar_indices]['bookId'].astype(str).tolist())
                similar_book_ids -= set([str(b) for b in liked_books])
                positive_mask = positive_mask | self.df['bookId'].astype(str).isin(similar_book_ids)

        if liked_genres:
            for genre in liked_genres:
                positive_mask = positive_mask | self.df['clean_genres'].str.contains(rf'\b{genre.lower()}\b',
                                                                                     regex=True, na=False)

        if liked_authors:
            for author in liked_authors:
                positive_mask = positive_mask | self.df['clean_author'].str.contains(author.lower().replace(" ", ""),
                                                                                     regex=False, na=False)

        # 3. Identify Negative Matches (to exclude)
        negative_mask = pd.Series(True, index=self.df.index)

        if disliked_books:
            negative_mask = negative_mask & ~self.df['bookId'].astype(str).isin([str(b) for b in disliked_books])

        if disliked_genres:
            for genre in disliked_genres:
                negative_mask = negative_mask & ~self.df['clean_genres'].str.contains(rf'\b{genre.lower()}\b',
                                                                                      regex=True, na=False)

        if disliked_authors:
            for author in disliked_authors:
                negative_mask = negative_mask & ~self.df['clean_author'].str.contains(author.lower().replace(" ", ""),
                                                                                      regex=False, na=False)

        # Final Ground Truth: Must be positive AND not negative
        final_mask = positive_mask & negative_mask
        return set(self.df[final_mask]['bookId'].astype(str).tolist())

    def evaluate_scenario(self, scenario_name: str, user_profile: Dict[str, Any], top_n: int = 50) -> Dict[str, Any]:
        """
        Evaluates a specific user scenario and returns Precision, Recall, and F1-Score.
        """
        # 1. Get Recommendations from the model
        recommendations = self.recommender.recommend_user_profile(
            preferred_languages=user_profile.get('preferred_languages', []),
            favorite_genres=user_profile.get('favorite_genres', []),
            favorite_authors=user_profile.get('favorite_authors', []),
            liked_book_ids=user_profile.get('liked_book_ids', []),
            disliked_genres=user_profile.get('disliked_genres', []),
            disliked_authors=user_profile.get('disliked_authors', []),
            disliked_book_ids=user_profile.get('disliked_book_ids', []),
            top_n=top_n
        )

        rec_ids = set([str(r['bookId']) for r in recommendations])

        lang = user_profile.get('preferred_languages', ['en'])[0] if user_profile.get('preferred_languages') else None
        gt_ids = self._get_ground_truth_ids(
            liked_genres=user_profile.get('favorite_genres', []),
            liked_authors=user_profile.get('favorite_authors', []),
            liked_books=user_profile.get('liked_book_ids', []),
            disliked_genres=user_profile.get('disliked_genres', []),
            disliked_authors=user_profile.get('disliked_authors', []),
            disliked_books=user_profile.get('disliked_book_ids', []),
            lang=lang
        )

        relevant_recs = rec_ids.intersection(gt_ids)

        precision = len(relevant_recs) / len(rec_ids) if len(rec_ids) > 0 else 0.0
        recall = len(relevant_recs) / len(gt_ids) if len(gt_ids) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "Scenario": scenario_name,
            "Precision": f"{precision:.2%}",
            "Recall": f"{recall:.2%}",
            "F1-Score": f"{f1_score:.2%}",
            "Recs Found": len(relevant_recs),
            "Total Recs": len(rec_ids),
            "Total Ground Truth": len(gt_ids)
        }