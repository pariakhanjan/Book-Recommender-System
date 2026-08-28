import pytest
import sys
import json
import pandas as pd
from unittest.mock import patch
from pathlib import Path
from datetime import datetime, timezone

from src.preprocessing import TextCleaner, preprocess_dataset
from src.recommender import BookRecommender
from src.database import UserModel, UserPreferenceModel
from api.schemas import UserCreate, FeedbackCreate

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


class TestTextCleaner:
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()

    def test_clean_english_text(self, cleaner):
        text = "The Hunger Games: Catching Fire!"
        result = cleaner.clean_english_text(text)
        assert "hunger" in result
        assert "the" not in result

    def test_clean_persian_text(self, cleaner):
        text = "کتاب بوف کور، اثر صادق هدایت!"
        result = cleaner.clean_persian_text(text)
        assert "بوف" in result
        assert "هدایت" in result

    def test_clean_empty_text(self, cleaner):
        assert cleaner.clean_english_text("") == ""
        assert cleaner.clean_persian_text(None) == ""

    def test_clean_genres_valid_list_string(self, cleaner):
        genre_str = "['Fantasy', 'Science Fiction', 'Mystery']"
        result = cleaner.clean_genres(genre_str)
        assert "fantasy" in result
        assert "sciencefiction" in result
        assert "mystery" in result

    def test_clean_genres_invalid_string_fallback(self, cleaner):
        genre_str = "Fantasy, Mystery"
        result = cleaner.clean_genres(genre_str)
        assert "fantasy,mystery" in result

    def test_clean_genres_empty_or_none(self, cleaner):
        assert cleaner.clean_genres("") == ""
        assert cleaner.clean_genres(None) == ""


class TestBookRecommender:
    @pytest.fixture(scope="class")
    def recommender(self):
        return BookRecommender()

    def test_load_resources(self, recommender):
        assert recommender.df is not None
        assert recommender.tfidf_matrix is not None
        assert len(recommender.df) > 0

    def test_recommend_by_book_id(self, recommender):
        book_id = recommender.df.iloc[0]['bookId']
        recommendations = recommender.recommend_by_book_id(book_id, top_n=5)
        assert len(recommendations) <= 5
        assert all('similarity_score' in rec for rec in recommendations)

    def test_recommend_by_language(self, recommender):
        recommendations = recommender.get_popular_books(n=5, languages=['fa'])
        assert all(rec['language'] == 'fa' for rec in recommendations)


class TestSchemas:
    def test_user_create_valid(self):
        user = UserCreate(username="testuser", email="test@example.com", password="SecurePass123!")
        assert user.username == "testuser"

    def test_feedback_create_valid(self):
        feedback = FeedbackCreate(user_id=1, book_id="en_123", feedback_type="liked", rating=4.5)
        assert feedback.feedback_type == "liked"

    def test_feedback_create_invalid_type(self):
        with pytest.raises(ValueError):
            FeedbackCreate(user_id=1, book_id="en_123", feedback_type="invalid_type")


class TestDatabaseModels:
    def test_user_model_creation(self):
        user = UserModel(
            username="integration_test",
            hashed_password="dummy_hashed_password",
            created_at=datetime.now(timezone.utc)
        )
        assert user.username == "integration_test"

    def test_preference_model_creation(self):
        pref = UserPreferenceModel(
            user_id=1,
            liked_genres=["Fantasy"],
            liked_authors=["Author1"],
            liked_book_ids=["book1"],
            updated_at=datetime.now(timezone.utc)
        )
        assert len(pref.liked_genres) == 1

    def test_preprocess_generates_vocabulary_json(self, tmp_path):
        """
        Tests that preprocess_dataset correctly creates the clean_vocabulary.json file
        with unique and sorted lists of genres, authors, and titles.
        """
        dummy_csv = tmp_path / "dummy_en.csv"
        dummy_data = {
            'bookId': ['1', '2', '3'],
            'title': ['Book One', 'Book Two', 'Book One'],
            'author': ['Author A', 'Author B', 'Author A'],
            'genres': ["['Fantasy', 'Science Fiction']", "['Mystery']", "['Fantasy']"],
            'description': ['Good book', 'Bad book', 'Good book'],
            'rating': [4.5, 3.0, 4.5],
            'coverImg': ['url1', 'url2', 'url1']
        }
        pd.DataFrame(dummy_data).to_csv(dummy_csv, index=False)

        output_csv = tmp_path / "processed.csv"
        expected_json = tmp_path / "clean_vocabulary.json"

        with patch('src.preprocessing.RAW_DATA_PATH_EN', dummy_csv), \
                patch('src.preprocessing.RAW_DATA_PATH_FA', tmp_path / "nonexistent_fa.csv"), \
                patch('src.preprocessing.PROCESSED_DATA_PATH', output_csv):

            df = preprocess_dataset(output_path=output_csv)

        assert output_csv.exists(), "Processed CSV was not created"
        assert len(df) == 3, f"DataFrame should have 3 rows, but got {len(df)}"
        assert expected_json.exists(), "clean_vocabulary.json was not created"

        with open(expected_json, 'r', encoding='utf-8') as f:
            vocab = json.load(f)

        assert "genres" in vocab
        assert "authors" in vocab
        assert "titles" in vocab
        assert "metadata" in vocab

        assert vocab["genres"] == sorted(list(set(vocab["genres"]))), "Genres should be unique and sorted"
        assert vocab["authors"] == sorted(list(set(vocab["authors"]))), "Authors should be unique and sorted"
        assert vocab["titles"] == sorted(list(set(vocab["titles"]))), "Titles should be unique and sorted"

        assert "fantasy" in vocab["genres"]
        assert "sciencefiction" in vocab["genres"]
        assert "mystery" in vocab["genres"]

        assert "authora" in vocab["authors"]
        assert "authorb" in vocab["authors"]

        assert vocab["metadata"]["total_books"] == 3
        assert vocab["metadata"]["total_genres"] == 3
        assert vocab["metadata"]["total_authors"] == 2
        assert vocab["metadata"]["total_titles"] == 2
