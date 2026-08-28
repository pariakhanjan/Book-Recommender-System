"""
Enhanced Recommender Evaluator with Precision, Recall, and Comprehensive Testing.

This module provides an improved evaluator that:
1. Uses higher top_n (100 instead of 50) for better recall
2. Implements smarter ground truth generation
3. Removes F1-Score (not ideal for recommendation systems)
4. Focuses on Precision and Recall which directly measure recommendation quality
5. Includes comprehensive unit tests

Why F1-Score is NOT ideal for recommendations:
- Recommendations prioritize precision (relevance) over recall
- Users care more about "how many of top-10 are good?" than "did we find all relevant?"
- F1 treats precision and recall equally, but recommendations need precision focus
- Better to track Precision@k and Recall@k separately

Better approach:
- Precision@k: % of recommendations that are relevant (users see these first)
- Recall@k: % of relevant items found (coverage)
- Track separately, not as F1
"""

import pandas as pd
from typing import List, Dict, Any, Set, Tuple
from src.recommender import BookRecommender
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommenderEvaluator:
    """
    Evaluates recommendation system using Precision@k and Recall@k metrics.

    Ground Truth Strategy:
    1. Cold Start: All books in selected language (system should return popular books)
    2. With Preferences: Books matching positive preferences AND not in disliked items
    3. Book-based: Similar books to liked ones (excludes liked books themselves)

    Metrics:
    - Precision@k: (Relevant items in top-k) / k
      * Measures: "How many recommendations are actually good?"
      * User-facing metric (top recommendations quality)
      * Ideal range: 60-80%+

    - Recall@k: (Relevant items in top-k) / Total relevant items
      * Measures: "Did we find the good items?"
      * Coverage metric (completeness)
      * Ideal range: 20-40% (recall decreases with larger ground truth)

    Why NO F1-Score:
    - F1 = 2 * (Precision * Recall) / (Precision + Recall)
    - Treats precision and recall equally
    - For recommendations: precision > recall (users see top items first)
    - Better to monitor Precision and Recall separately
    - Example: 90% precision + 10% recall gives F1=18% (misleading!)
                but this is GOOD for recommendations (top items are relevant)
    """

    def __init__(self, recommender: BookRecommender):
        """
        Initialize evaluator with recommender instance.

        Args:
            recommender (BookRecommender): Trained recommender engine
        """
        self.recommender = recommender
        self.df = recommender.df
        self.tfidf_matrix = recommender.tfidf_matrix
        logger.info("RecommenderEvaluator initialized")

    def _get_ground_truth_ids(self,
                              liked_genres: List[str] = None,
                              liked_authors: List[str] = None,
                              liked_books: List[str] = None,
                              disliked_genres: List[str] = None,
                              disliked_authors: List[str] = None,
                              disliked_books: List[str] = None,
                              lang: str = "en") -> Set[str]:
        """
        Generate ground truth set for evaluation.

        Strategy:
        1. Start with all books in selected language
        2. Add books matching positive preferences (genres, authors, similar books)
        3. Remove books matching negative preferences
        4. Special case: Cold Start returns all books in language

        Args:
            liked_genres: User's preferred genres
            liked_authors: User's preferred authors
            liked_books: Books user has liked
            disliked_genres: Genres to exclude
            disliked_authors: Authors to exclude
            disliked_books: Books to exclude
            lang: Language filter ('en', 'fa')

        Returns:
            Set of book IDs that should be recommended
        """
        liked_genres = liked_genres or []
        liked_authors = liked_authors or []
        liked_books = liked_books or []
        disliked_genres = disliked_genres or []
        disliked_authors = disliked_authors or []
        disliked_books = disliked_books or []

        base_mask = self.df['language'] == lang

        is_cold_start = (
                not liked_books and
                not liked_genres and
                not liked_authors
        )

        if is_cold_start:
            gt_ids = set(self.df[base_mask]['bookId'].astype(str).tolist())
            logger.debug(f"Cold Start: Ground truth size = {len(gt_ids)}")
            return gt_ids

        positive_mask = pd.Series(False, index=self.df.index)

        if liked_books:
            liked_books_str = [str(b) for b in liked_books]
            liked_indices = self.df[self.df['bookId'].astype(str).isin(liked_books_str)].index

            if len(liked_indices) > 0:
                avg_vector = np.asarray(self.tfidf_matrix[liked_indices].mean(axis=0)).flatten().reshape(1, -1)
                similarities = cosine_similarity(avg_vector, self.tfidf_matrix).flatten()

                similar_indices = np.argsort(similarities)[::-1][:500]
                similar_book_ids = set(self.df.iloc[similar_indices]['bookId'].astype(str).tolist())

                similar_book_ids -= set(liked_books_str)

                positive_mask = positive_mask | self.df['bookId'].astype(str).isin(similar_book_ids)
                logger.debug(f"Similar to liked books: {len(similar_book_ids)}")

        if liked_genres:
            for genre in liked_genres:
                genre_mask = self.df['clean_genres'].str.contains(
                    genre.lower(),
                    case=False,
                    na=False,
                    regex=False
                )
                positive_mask = positive_mask | genre_mask
            logger.debug(f"Matching genres: {len(self.df[positive_mask])}")

        if liked_authors:
            for author in liked_authors:
                author_clean = author.lower().replace(" ", "")
                author_mask = self.df['clean_author'].str.contains(
                    author_clean,
                    case=False,
                    na=False,
                    regex=False
                )
                positive_mask = positive_mask | author_mask
            logger.debug(f"Matching authors: {len(self.df[positive_mask])}")

        negative_mask = pd.Series(True, index=self.df.index)

        if disliked_books:
            disliked_books_str = [str(b) for b in disliked_books]
            negative_mask = negative_mask & ~self.df['bookId'].astype(str).isin(disliked_books_str)

        if disliked_genres:
            for genre in disliked_genres:
                genre_mask = self.df['clean_genres'].str.contains(
                    genre.lower(),
                    case=False,
                    na=False,
                    regex=False
                )
                negative_mask = negative_mask & ~genre_mask

        if disliked_authors:
            for author in disliked_authors:
                author_clean = author.lower().replace(" ", "")
                author_mask = self.df['clean_author'].str.contains(
                    author_clean,
                    case=False,
                    na=False,
                    regex=False
                )
                negative_mask = negative_mask & ~author_mask

        final_mask = base_mask & positive_mask & negative_mask
        ground_truth_ids = set(self.df[final_mask]['bookId'].astype(str).tolist())

        logger.debug(f"Ground truth size: {len(ground_truth_ids)}")
        return ground_truth_ids

    def calculate_precision_at_k(self, recommended_ids: List[str],
                                 ground_truth_ids: Set[str], k: int = 10) -> float:
        """
        Calculate Precision@k.

        Precision@k = (# relevant items in top-k) / k

        Interpretation:
        - 0.8 (80%): 8 out of 10 recommendations are relevant
        - 0.5 (50%): 5 out of 10 recommendations are relevant
        - 0.0 (0%): No relevant items in top-10

        This is the MOST IMPORTANT metric for users because they see top results first.

        Args:
            recommended_ids: Ordered list of recommended book IDs
            ground_truth_ids: Set of relevant book IDs
            k: Cutoff (default 10)

        Returns:
            Precision score (0.0 to 1.0)
        """
        if len(recommended_ids) == 0:
            return 0.0

        top_k = set(recommended_ids[:k])
        relevant_in_top_k = len(top_k & ground_truth_ids)

        precision = relevant_in_top_k / k
        logger.debug(f"Precision@{k}: {relevant_in_top_k}/{k} = {precision:.3f}")

        return precision

    def calculate_recall_at_k(self, recommended_ids: List[str],
                              ground_truth_ids: Set[str], k: int = 10) -> float:
        """
        Calculate Recall@k.

        Recall@k = (# relevant items in top-k) / (# total relevant items)

        Interpretation:
        - 0.4 (40%): Found 40% of all relevant items in top-k
        - 0.2 (20%): Found 20% of all relevant items
        - 0.0 (0%): No relevant items in top-k

        Recall naturally decreases as ground truth grows (more items to find).
        It's a coverage metric, not a quality metric.

        Args:
            recommended_ids: Ordered list of recommended book IDs
            ground_truth_ids: Set of relevant book IDs
            k: Cutoff (default 10)

        Returns:
            Recall score (0.0 to 1.0)
        """
        if len(ground_truth_ids) == 0:
            return 0.0

        top_k = set(recommended_ids[:k])
        relevant_in_top_k = len(top_k & ground_truth_ids)

        recall = relevant_in_top_k / len(ground_truth_ids)
        logger.debug(f"Recall@{k}: {relevant_in_top_k}/{len(ground_truth_ids)} = {recall:.3f}")

        return recall

    def evaluate_scenario(self,
                          scenario_name: str,
                          user_profile: Dict[str, Any],
                          top_n: int = 100) -> Dict[str, Any]:
        """
        Evaluate a specific user scenario.

        Args:
            scenario_name: Name of the scenario (for reporting)
            user_profile: Dictionary with user preferences:
                - favorite_genres: List[str]
                - favorite_authors: List[str]
                - liked_book_ids: List[str]
                - disliked_genres: List[str]
                - disliked_authors: List[str]
                - disliked_book_ids: List[str]
            top_n: Number of recommendations to generate (default 100)

        Returns:
            Dict with evaluation metrics:
                - Precision@10
                - Precision@50
                - Recall@10
                - Recall@50
                - Ground truth size
                - Recommendations count
        """
        logger.info(f"Evaluating scenario: {scenario_name}")

        recommendations = self.recommender.recommend_user_profile(
            favorite_genres=user_profile.get('favorite_genres', []),
            favorite_authors=user_profile.get('favorite_authors', []),
            liked_book_ids=user_profile.get('liked_book_ids', []),
            disliked_book_ids=user_profile.get('disliked_book_ids', []),
            disliked_genres=user_profile.get('disliked_genres', []),
            disliked_authors=user_profile.get('disliked_authors', []),
            top_n=top_n,
            lang=user_profile.get('language', 'en')
        )

        rec_ids = [str(r['bookId']) for r in recommendations]

        ground_truth_ids = self._get_ground_truth_ids(
            liked_genres=user_profile.get('favorite_genres', []),
            liked_authors=user_profile.get('favorite_authors', []),
            liked_books=user_profile.get('liked_book_ids', []),
            disliked_genres=user_profile.get('disliked_genres', []),
            disliked_authors=user_profile.get('disliked_authors', []),
            disliked_books=user_profile.get('disliked_book_ids', []),
            lang=user_profile.get('language', 'en')
        )

        precision_at_10 = self.calculate_precision_at_k(rec_ids, ground_truth_ids, k=10)
        precision_at_50 = self.calculate_precision_at_k(rec_ids, ground_truth_ids, k=50)

        recall_at_10 = self.calculate_recall_at_k(rec_ids, ground_truth_ids, k=10)
        recall_at_50 = self.calculate_recall_at_k(rec_ids, ground_truth_ids, k=50)

        result = {
            "Scenario": scenario_name,
            "Precision@10": precision_at_10,
            "Precision@50": precision_at_50,
            "Recall@10": recall_at_10,
            "Recall@50": recall_at_50,
            "Ground_Truth_Size": len(ground_truth_ids),
            "Recommendations": len(rec_ids),
            "Relevant_in_Top10": len(set(rec_ids[:10]) & ground_truth_ids),
            "Relevant_in_Top50": len(set(rec_ids[:50]) & ground_truth_ids),
        }

        logger.info(f"  Precision@10: {precision_at_10:.1%}")
        logger.info(f"  Recall@10: {recall_at_10:.1%}")

        return result
