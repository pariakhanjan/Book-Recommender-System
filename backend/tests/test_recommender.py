import pytest
from src.preprocessing import clean_english_text, clean_persian_text, clean_genres
from src.recommender import BookRecommender


def test_clean_english_text():
    raw_text = "The Hunger Games: Catching Fire!"
    expected = "hunger games catching fire"
    assert clean_english_text(raw_text) == expected


def test_clean_persian_text():
    raw_text = "کتاب بوف کور، اثر صادق هدایت!"
    expected = "کتاب بوف کور اثر صادق هدایت"
    assert clean_persian_text(raw_text) == expected


def test_clean_genres():
    raw_genres = "['Young Adult', 'Science Fiction']"
    expected = "youngadult sciencefiction"
    assert clean_genres(raw_genres) == expected


@pytest.fixture(scope="module")
def recommender_engine():
    return BookRecommender()


def test_recommend_user_profile_empty(recommender_engine):
    recommendations = recommender_engine.recommend_user_profile(
        favorite_genres=[], favorite_authors=[], liked_book_ids=[], top_n=5
    )
    assert len(recommendations) == 5
    assert recommendations[0]["similarity_score"] == 0.0


def test_recommend_language_filtering(recommender_engine):
    recommendations_fa = recommender_engine.get_popular_books(n=3, lang='fa')
    for rec in recommendations_fa:
        assert rec['language'] == 'fa'
