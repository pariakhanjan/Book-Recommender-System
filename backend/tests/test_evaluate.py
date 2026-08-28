"""
Unit Tests for Book Recommender Evaluation System.

Test coverage:
1. Precision@k calculation
2. Recall@k calculation
3. Ground truth generation
4. Scenario evaluation
5. Edge cases and error handling

Run tests:
    pytest tests/test_evaluator.py -v

Or from command line:
    python -m pytest tests/test_evaluator.py --tb=short
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock
import sys
from pathlib import Path
from src.evaluation import RecommenderEvaluator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestPrecisionRecallCalculation(unittest.TestCase):
    """Test Precision and Recall metric calculations."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock recommender
        self.mock_recommender = Mock()
        self.mock_recommender.df = pd.DataFrame({
            'bookId': ['book_1', 'book_2', 'book_3', 'book_4', 'book_5'],
            'language': ['en', 'en', 'en', 'en', 'en'],
            'clean_genres': ['fantasy', 'mystery', 'fantasy', 'romance', 'thriller'],
            'clean_author': ['author_a', 'author_b', 'author_a', 'author_c', 'author_b']
        })
        self.mock_recommender.tfidf_matrix = Mock()

        # Initialize evaluator
        self.evaluator = RecommenderEvaluator(self.mock_recommender)

    def test_precision_at_k_perfect_recommendations(self):
        """Test Precision@k when all recommendations are relevant."""
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5']
        ground_truth = {'book_1', 'book_2', 'book_3', 'book_4', 'book_5'}

        precision = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=5)

        self.assertEqual(precision, 1.0)
        self.assertAlmostEqual(precision, 1.0, places=3)

    def test_precision_at_k_partial_match(self):
        """Test Precision@k with partial matches."""
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5',
                       'book_6', 'book_7', 'book_8', 'book_9', 'book_10']
        ground_truth = {'book_1', 'book_3', 'book_5', 'book_7', 'book_9'}

        # Top 10: 5 relevant out of 10
        precision = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=10)
        expected = 5 / 10

        self.assertAlmostEqual(precision, expected, places=3)

    def test_precision_at_k_no_relevant(self):
        """Test Precision@k when no recommendations are relevant."""
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5']
        ground_truth = {'book_99', 'book_100'}

        precision = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=5)

        self.assertEqual(precision, 0.0)

    def test_precision_at_different_k_values(self):
        """Test Precision@k at different cutoff values."""
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5',
                       'book_6', 'book_7', 'book_8', 'book_9', 'book_10']
        ground_truth = {'book_1', 'book_2', 'book_3', 'book_4', 'book_5',
                        'book_6', 'book_7', 'book_8', 'book_9', 'book_10'}

        # All relevant
        p_at_5 = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=5)
        p_at_10 = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=10)

        self.assertEqual(p_at_5, 1.0)
        self.assertEqual(p_at_10, 1.0)

    def test_recall_at_k_perfect_recommendations(self):
        """Test Recall@k when all relevant items are found."""
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5']
        ground_truth = {'book_1', 'book_2', 'book_3', 'book_4', 'book_5'}

        recall = self.evaluator.calculate_recall_at_k(recommended, ground_truth, k=5)

        self.assertEqual(recall, 1.0)

    def test_recall_at_k_partial_coverage(self):
        """Test Recall@k with partial coverage of relevant items."""
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5',
                       'book_6', 'book_7', 'book_8', 'book_9', 'book_10']
        ground_truth = {'book_1', 'book_3', 'book_5', 'book_7', 'book_9',
                        'book_11', 'book_12', 'book_13', 'book_14', 'book_15'}

        # Found 5 out of 10 relevant
        recall = self.evaluator.calculate_recall_at_k(recommended, ground_truth, k=10)
        expected = 5 / 10

        self.assertAlmostEqual(recall, expected, places=3)

    def test_recall_at_k_no_relevant_found(self):
        """Test Recall@k when no relevant items are found."""
        recommended = ['book_1', 'book_2', 'book_3']
        ground_truth = {'book_99', 'book_100', 'book_101'}

        recall = self.evaluator.calculate_recall_at_k(recommended, ground_truth, k=3)

        self.assertEqual(recall, 0.0)

    def test_recall_at_k_empty_ground_truth(self):
        """Test Recall@k with empty ground truth."""
        recommended = ['book_1', 'book_2', 'book_3']
        ground_truth = set()

        recall = self.evaluator.calculate_recall_at_k(recommended, ground_truth, k=3)

        self.assertEqual(recall, 0.0)

    def test_recall_increases_with_k(self):
        """Test that recall generally increases with higher k values."""
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5',
                       'book_6', 'book_7', 'book_8', 'book_9', 'book_10']
        ground_truth = {'book_1', 'book_3', 'book_5', 'book_7', 'book_9',
                        'book_11', 'book_12', 'book_13', 'book_14', 'book_15'}

        recall_at_5 = self.evaluator.calculate_recall_at_k(recommended, ground_truth, k=5)
        recall_at_10 = self.evaluator.calculate_recall_at_k(recommended, ground_truth, k=10)

        # More items searched = more likely to find relevant
        self.assertLessEqual(recall_at_5, recall_at_10)


class TestGroundTruthGeneration(unittest.TestCase):
    """Test ground truth generation logic."""

    def setUp(self):
        """Set up test data."""
        self.mock_recommender = Mock()

        # Create test dataframe
        self.test_df = pd.DataFrame({
            'bookId': ['book_1', 'book_2', 'book_3', 'book_4', 'book_5'],
            'language': ['en', 'en', 'fa', 'en', 'fa'],
            'clean_genres': ['fantasy', 'mystery', 'fantasy', 'romance', 'mystery'],
            'clean_author': ['author_a', 'author_b', 'author_a', 'author_c', 'author_b']
        })

        self.mock_recommender.df = self.test_df
        self.mock_recommender.tfidf_matrix = np.eye(5)  # Identity matrix for simplicity

        self.evaluator = RecommenderEvaluator(self.mock_recommender)

    def test_cold_start_returns_all_language_books(self):
        """Test Cold Start scenario returns all books in selected language."""
        # No preferences
        ground_truth = self.evaluator._get_ground_truth_ids(
            liked_genres=[],
            liked_authors=[],
            liked_books=[],
            lang='en'
        )

        # Should return all English books
        expected = {'book_1', 'book_2', 'book_4'}
        self.assertEqual(ground_truth, expected)

    def test_genre_based_ground_truth(self):
        """Test ground truth generation based on genres."""
        ground_truth = self.evaluator._get_ground_truth_ids(
            liked_genres=['fantasy'],
            lang='en'
        )

        # Should return English books with 'fantasy' genre
        self.assertIn('book_1', ground_truth)
        self.assertNotIn('book_2', ground_truth)  # mystery, not fantasy

    def test_author_based_ground_truth(self):
        """Test ground truth generation based on authors."""
        ground_truth = self.evaluator._get_ground_truth_ids(
            liked_authors=['author_b'],
            lang='en'
        )

        # Should return English books by 'author_b'
        self.assertIn('book_2', ground_truth)
        self.assertNotIn('book_1', ground_truth)

    def test_disliked_genres_filtering(self):
        """Test that disliked genres are excluded."""
        ground_truth = self.evaluator._get_ground_truth_ids(
            liked_genres=['fantasy', 'mystery'],
            disliked_genres=['mystery'],
            lang='en'
        )

        # Should have fantasy but not mystery
        self.assertIn('book_1', ground_truth)  # fantasy
        self.assertNotIn('book_2', ground_truth)  # mystery (disliked)

    def test_disliked_authors_filtering(self):
        """Test that disliked authors are excluded."""
        ground_truth = self.evaluator._get_ground_truth_ids(
            liked_authors=['author_a', 'author_b'],
            disliked_authors=['author_a'],
            lang='en'
        )

        # Should have author_b but not author_a
        self.assertIn('book_2', ground_truth)  # author_b
        self.assertNotIn('book_1', ground_truth)  # author_a (disliked)

    def test_language_filtering(self):
        """Test language filtering in ground truth."""
        ground_truth_en = self.evaluator._get_ground_truth_ids(
            liked_genres=['fantasy'],
            lang='en'
        )
        ground_truth_fa = self.evaluator._get_ground_truth_ids(
            liked_genres=['fantasy'],
            lang='fa'
        )

        # English should have book_1, Persian should have book_3
        self.assertIn('book_1', ground_truth_en)
        self.assertNotIn('book_3', ground_truth_en)

        self.assertIn('book_3', ground_truth_fa)
        self.assertNotIn('book_1', ground_truth_fa)


class TestScenarioEvaluation(unittest.TestCase):
    """Test complete scenario evaluation."""

    def setUp(self):
        """Set up mock for scenario testing."""
        self.mock_recommender = Mock()

        # Setup mock dataframe
        self.mock_df = pd.DataFrame({
            'bookId': [f'book_{i}' for i in range(1, 101)],
            'language': ['en'] * 100,
            'clean_genres': ['fantasy'] * 30 + ['mystery'] * 30 + ['romance'] * 40,
            'clean_author': ['author_a'] * 25 + ['author_b'] * 25 + ['author_c'] * 50
        })

        self.mock_recommender.df = self.mock_df
        self.mock_recommender.tfidf_matrix = np.eye(100)

        # Mock recommend_user_profile to return top 100 books
        self.mock_recommender.recommend_user_profile = Mock(
            return_value=[{'bookId': f'book_{i}', 'similarity_score': 1.0 - i / 100}
                          for i in range(1, 101)]
        )

        self.evaluator = RecommenderEvaluator(self.mock_recommender)

    def test_scenario_evaluation_structure(self):
        """Test that scenario evaluation returns correct structure."""
        user_profile = {
            'favorite_genres': ['fantasy'],
            'favorite_authors': [],
            'liked_book_ids': [],
            'disliked_genres': [],
            'disliked_authors': [],
            'disliked_book_ids': [],
            'language': 'en'
        }

        result = self.evaluator.evaluate_scenario('Test Scenario', user_profile, top_n=100)

        # Check all required keys exist
        required_keys = [
            'Scenario', 'Precision@10', 'Precision@50',
            'Recall@10', 'Recall@50', 'Ground_Truth_Size',
            'Recommendations', 'Relevant_in_Top10', 'Relevant_in_Top50'
        ]

        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_scenario_evaluation_metrics_range(self):
        """Test that metrics are in valid range."""
        user_profile = {
            'favorite_genres': ['fantasy'],
            'favorite_authors': [],
            'liked_book_ids': [],
            'language': 'en'
        }

        result = self.evaluator.evaluate_scenario('Test Scenario', user_profile, top_n=100)

        # Precision and Recall should be between 0 and 1
        self.assertGreaterEqual(result['Precision@10'], 0.0)
        self.assertLessEqual(result['Precision@10'], 1.0)

        self.assertGreaterEqual(result['Recall@10'], 0.0)
        self.assertLessEqual(result['Recall@10'], 1.0)

    def test_scenario_with_empty_user_profile(self):
        """Test scenario with empty user profile (Cold Start)."""
        user_profile = {
            'favorite_genres': [],
            'favorite_authors': [],
            'liked_book_ids': [],
            'language': 'en'
        }

        result = self.evaluator.evaluate_scenario('Cold Start', user_profile, top_n=100)

        # Cold Start should return something valid
        self.assertGreater(result['Ground_Truth_Size'], 0)
        self.assertGreater(result['Recommendations'], 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up minimal test data."""
        self.mock_recommender = Mock()
        self.mock_recommender.df = pd.DataFrame({
            'bookId': ['book_1'],
            'language': ['en'],
            'clean_genres': ['fiction'],
            'clean_author': ['author_a']
        })
        self.mock_recommender.tfidf_matrix = np.array([[1.0]])
        self.evaluator = RecommenderEvaluator(self.mock_recommender)

    def test_empty_recommendations_list(self):
        """Test handling of empty recommendations."""
        precision = self.evaluator.calculate_precision_at_k([], {'book_1'}, k=10)
        self.assertEqual(precision, 0.0)

    def test_k_larger_than_recommendations(self):
        """Test when k is larger than number of recommendations."""
        recommended = ['book_1', 'book_2']
        ground_truth = {'book_1', 'book_2'}

        # k=10 but only 2 recommendations
        precision = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=10)

        # Precision = 2/10 = 0.2
        self.assertAlmostEqual(precision, 0.2, places=3)

    def test_duplicate_recommendations(self):
        """Test handling of duplicate recommendations."""
        recommended = ['book_1', 'book_1', 'book_1']
        ground_truth = {'book_1'}

        # Should handle duplicates (count unique in top_k, but divide by k)
        precision = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=3)

        # 1 unique relevant book found, but k=3, so precision is 1/3
        self.assertAlmostEqual(precision, 1/3, places=3)

    def test_unicode_handling(self):
        """Test handling of unicode characters in book data."""
        self.mock_recommender.df = pd.DataFrame({
            'bookId': ['کتاب_۱', 'book_2'],  # Persian and English
            'language': ['fa', 'en'],
            'clean_genres': ['داستان', 'fiction'],  # Persian and English
            'clean_author': ['نویسنده', 'author']  # Persian and English
        })
        self.mock_recommender.tfidf_matrix = np.eye(2)

        evaluator = RecommenderEvaluator(self.mock_recommender)

        # Should handle unicode without errors
        ground_truth = evaluator._get_ground_truth_ids(lang='fa')

        self.assertIn('کتاب_۱', ground_truth)


class TestMetricInterpretation(unittest.TestCase):
    """Test interpretation and meaning of metrics."""

    def setUp(self):
        """Set up test data."""
        self.mock_recommender = Mock()
        self.mock_recommender.df = pd.DataFrame({
            'bookId': [f'book_{i}' for i in range(1, 101)],
            'language': ['en'] * 100,
            'clean_genres': ['fiction'] * 100,
            'clean_author': [f'author_{i % 10}' for i in range(100)]
        })
        self.mock_recommender.tfidf_matrix = np.eye(100)
        self.evaluator = RecommenderEvaluator(self.mock_recommender)

    def test_precision_measures_quality_of_top_k(self):
        """
        Precision measures: "How many top-k results are relevant?"
        This is USER-FACING metric (users see these first).
        """
        recommended = ['book_1', 'book_2', 'book_3', 'book_4', 'book_5',
                       'book_6', 'book_7', 'book_8', 'book_9', 'book_10']
        ground_truth = {'book_1', 'book_3', 'book_5'}

        precision = self.evaluator.calculate_precision_at_k(recommended, ground_truth, k=10)

        # 3 relevant out of 10 shown = 30% of user's views are relevant
        self.assertAlmostEqual(precision, 0.3, places=3)

    def test_recall_measures_coverage(self):
        """
        Recall measures: "How many relevant items did we find?"
        This is COMPLETENESS metric.
        """
        recommended = ['book_1', 'book_3', 'book_5', 'book_7', 'book_9']
        ground_truth = {'book_1', 'book_3', 'book_5', 'book_7', 'book_9',
                        'book_11', 'book_13', 'book_15', 'book_17', 'book_19'}

        recall = self.evaluator.calculate_recall_at_k(recommended, ground_truth, k=5)

        # Found 5 relevant items out of 10 total = 50% coverage
        self.assertAlmostEqual(recall, 0.5, places=3)

    def test_precision_vs_recall_tradeoff(self):
        """
        Show the precision-recall tradeoff.
        High precision = focused on quality
        High recall = focused on coverage
        """
        # Scenario 1: High Precision, Low Recall
        # Show only books we're very confident about
        recommended_high_precision = ['book_1', 'book_3', 'book_5']  # All relevant
        ground_truth = {'book_1', 'book_3', 'book_5', 'book_7', 'book_9'}

        precision = self.evaluator.calculate_precision_at_k(
            recommended_high_precision, ground_truth, k=3)
        recall = self.evaluator.calculate_recall_at_k(
            recommended_high_precision, ground_truth, k=3)

        self.assertEqual(precision, 1.0)  # All 3 are relevant
        self.assertEqual(recall, 0.6)  # Found 3 out of 5

        # Scenario 2: Lower Precision, Higher Recall
        # Show more books, some might not be as relevant
        recommended_high_recall = ['book_1', 'book_3', 'book_5', 'book_2', 'book_4']

        precision = self.evaluator.calculate_precision_at_k(
            recommended_high_recall, ground_truth, k=5)
        recall = self.evaluator.calculate_recall_at_k(
            recommended_high_recall, ground_truth, k=5)

        # 3 out of 5 recommended are relevant
        self.assertAlmostEqual(precision, 0.6, places=3)
        # Found 3 out of 5 ground truth items
        self.assertAlmostEqual(recall, 0.6, places=3)


def run_tests():
    """Run all tests with nice output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPrecisionRecallCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestGroundTruthGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestScenarioEvaluation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricInterpretation))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
