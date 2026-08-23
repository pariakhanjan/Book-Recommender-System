import pytest
import sys
from pathlib import Path
from src.preprocessing import TextCleaner
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

    def test_user_create_invalid_email(self):
        with pytest.raises(ValueError):
            UserCreate(username="testuser", email="invalid-email", password="SecurePass123!")

    def test_feedback_create_valid(self):
        feedback = FeedbackCreate(user_id=1, book_id="en_123", feedback_type="liked", rating=4.5)
        assert feedback.feedback_type == "liked"

    def test_feedback_create_invalid_type(self):
        with pytest.raises(ValueError):
            FeedbackCreate(user_id=1, book_id="en_123", feedback_type="invalid_type")


class TestDatabaseModels:
    def test_user_model_creation(self):
        from datetime import datetime
        user = UserModel(username="integration_test", email="test@integration.com", created_at=datetime.utcnow())
        assert user.username == "integration_test"

    def test_preference_model_creation(self):
        from datetime import datetime
        pref = UserPreferenceModel(user_id=1, liked_genres=["Fantasy"], liked_authors=["Author1"],
                                   liked_book_ids=["book1"], updated_at=datetime.utcnow())
        assert len(pref.liked_genres) == 1
