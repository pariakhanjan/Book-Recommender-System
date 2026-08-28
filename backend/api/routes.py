"""
API Routes for the Book Recommender System.

Defines all endpoints for user management, authentication,
preferences, feedback, and book recommendations.
"""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import json
import bcrypt
from utils.logger import logger
from src.config import CLEAN_VOCABULARY_PATH

from api.schemas import (
    UserCreate, UserResponse, PreferenceCreate, PreferenceResponse,
    FeedbackCreate, FeedbackResponse, BookResponse, UserLogin
)
from src.database import get_db, UserModel, UserPreferenceModel, UserFeedbackModel
from src.recommender import BookRecommender

router = APIRouter(prefix="/api", tags=["API"])
recommender = BookRecommender()


def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.

    Args:
        plain_password (str): The plain text password to check.
        hashed_password (str): The stored hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.get("/", response_model=dict, tags=["System"])
def health_check() -> dict:
    """Simple health check endpoint to verify API is running."""
    return {"status": "online", "message": "Book Recommender API is running", "version": "2.0.0"}


@router.post("/auth/login", tags=["Authentication"])
def login_user(login_data: UserLogin, db: Session = Depends(get_db)) -> dict:
    """
    Authenticates a user and returns their ID and username.

    Args:
        login_data (UserLogin): The user's login credentials.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the user_id, username, and success message.

    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid.
    """
    user = db.query(UserModel).filter(UserModel.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return {"user_id": user.id, "username": user.username, "message": "Login successful"}


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserModel:
    """
    Registers a new user, hashes their password, and initializes an empty preference profile.

    Args:
        user_in (UserCreate): The new user's registration data.
        db (Session): The database session.

    Returns:
        UserModel: The created user object.

    Raises:
        HTTPException: 400 Bad Request if the username is already registered.
    """
    db_user = db.query(UserModel).filter(UserModel.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = get_password_hash(user_in.password)
    new_user = UserModel(username=user_in.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    pref = UserPreferenceModel(user_id=new_user.id, preferred_languages=[])
    db.add(pref)
    db.commit()
    return new_user


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserModel:
    """
    Retrieves a user by their ID.

    Args:
        user_id (int): The ID of the user.
        db (Session): The database session.

    Returns:
        UserModel: The user object.

    Raises:
        HTTPException: 404 Not Found if the user does not exist.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/{user_id}/preferences", response_model=PreferenceResponse, tags=["Users"])
def get_user_preferences(user_id: int, db: Session = Depends(get_db)) -> UserPreferenceModel:
    """
    Retrieves or initializes a user's preference profile.

    Args:
        user_id (int): The ID of the user.
        db (Session): The database session.

    Returns:
        UserPreferenceModel: The user's preference object.

    Raises:
        HTTPException: 404 Not Found if the user does not exist.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref:
        pref = UserPreferenceModel(user_id=user_id, preferred_languages=[])
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.put("/users/{user_id}/preferences", response_model=PreferenceResponse, tags=["Users"])
def update_user_preferences(user_id: int, pref_in: PreferenceCreate, db: Session = Depends(get_db)) -> UserPreferenceModel:
    """
    Updates the user's liked/disliked genres, authors, and books.

    Args:
        user_id (int): The ID of the user.
        pref_in (PreferenceCreate): The updated preference data.
        db (Session): The database session.

    Returns:
        UserPreferenceModel: The updated preference object.

    Raises:
        HTTPException: 404 Not Found if the user does not exist.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref:
        pref = UserPreferenceModel(user_id=user_id)
        db.add(pref)

    pref.preferred_languages = pref_in.preferred_languages
    pref.liked_genres = pref_in.liked_genres
    pref.liked_authors = pref_in.liked_authors
    pref.liked_book_ids = pref_in.liked_book_ids
    pref.disliked_genres = pref_in.disliked_genres
    pref.disliked_authors = pref_in.disliked_authors
    pref.disliked_book_ids = pref_in.disliked_book_ids

    db.commit()
    db.refresh(pref)
    return pref


@router.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
def submit_feedback(feedback_in: FeedbackCreate, db: Session = Depends(get_db)) -> UserFeedbackModel:
    """
    Records user feedback and dynamically updates their preference profile.

    Args:
        feedback_in (FeedbackCreate): The feedback data.
        db (Session): The database session.

    Returns:
        UserFeedbackModel: The created feedback object.

    Raises:
        HTTPException: 404 Not Found if the user does not exist.
    """
    user = db.query(UserModel).filter(UserModel.id == feedback_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_feedback = UserFeedbackModel(**feedback_in.model_dump())
    db.add(new_feedback)

    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == feedback_in.user_id).first()
    if pref:
        current_liked = pref.liked_book_ids or []
        current_disliked = pref.disliked_book_ids or []

        if feedback_in.feedback_type == "liked" and feedback_in.book_id not in current_liked:
            pref.liked_book_ids = current_liked + [feedback_in.book_id]
        elif feedback_in.feedback_type == "disliked" and feedback_in.book_id not in current_disliked:
            pref.disliked_book_ids = current_disliked + [feedback_in.book_id]

    db.commit()
    db.refresh(new_feedback)
    return new_feedback


@router.get(
    "/users/{user_id}/recommendations",
    response_model=List[BookResponse],
    tags=["Recommendations"],
    summary="Get Personalized Recommendations",
    description="Retrieves top N book recommendations based on the user's profile. "
                "Applies research-backed weights to liked/disliked items. "
                "Triggers Cold Start fallback to popular books if the profile is empty.",
    responses={
        200: {"description": "Successfully retrieved recommendations"},
        400: {"description": "User has not selected preferred languages yet"},
        404: {"description": "User not found"},
        500: {"description": "Internal recommendation engine error"}
    }
)
def get_personalized_recommendations(user_id: int, top_n: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)) -> List[dict]:
    """
    Generates personalized book recommendations for a specific user.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref or not pref.preferred_languages:
        logger.warning(f"COLD START BLOCKED: User {user_id} has not selected preferred languages.")
        raise HTTPException(status_code=400, detail="Preferred languages must be set to get recommendations")

    try:
        return recommender.recommend_user_profile(
            preferred_languages=pref.preferred_languages,
            favorite_genres=pref.liked_genres or [],
            favorite_authors=pref.liked_authors or [],
            liked_book_ids=pref.liked_book_ids or [],
            disliked_genres=pref.disliked_genres or [],
            disliked_authors=pref.disliked_authors or [],
            disliked_book_ids=pref.disliked_book_ids or [],
            top_n=top_n
        )
    except Exception as e:
        logger.error(f"Recommendation error for User {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/books/popular", response_model=List[BookResponse], tags=["Books"])
def get_popular_books(top_n: int = Query(10, ge=1, le=50), lang: Optional[str] = None) -> List[dict]:
    """Retrieves popular books, optionally filtered by language."""
    languages = [lang] if lang else None
    return recommender.get_popular_books(n=top_n, languages=languages)


@router.get("/search/unique-genres", tags=["Search"])
def get_unique_genres() -> List[str]:
    """Returns a sorted list of all unique genres from the dataset."""
    genres = recommender.df['clean_genres'].dropna().unique()
    all_genres = set()
    for genre_str in genres:
        if isinstance(genre_str, str):
            for g in genre_str.split():
                if g.strip():
                    all_genres.add(g.strip())
    return sorted(list(all_genres))


@router.get("/search/unique-authors", tags=["Search"])
def get_unique_authors() -> List[str]:
    """Returns a sorted list of all unique authors from the dataset."""
    authors = recommender.df['clean_author'].dropna().unique()
    return sorted([a for a in authors if isinstance(a, str) and a.strip()])


@router.get("/search/unique-books", tags=["Search"])
def get_unique_books() -> List[str]:
    """Returns a sorted list of all unique book titles from the dataset."""
    books = recommender.df['title'].dropna().unique()
    return sorted([b for b in books if isinstance(b, str) and b.strip()])


@router.get("/search/genres", tags=["Search"])
def search_genres(q: str = Query(..., min_length=1, max_length=100, description="Search query for genres")) -> List[str]:
    """
    Searches for genres from the clean vocabulary JSON file.

    Args:
        q (str): The search query string.

    Returns:
        List[str]: A list of matching genres (max 20).
    """
    try:
        vocab_file = Path(CLEAN_VOCABULARY_PATH)
        if not vocab_file.exists():
            logger.error(f"Vocabulary file not found: {vocab_file}")
            return []

        with open(vocab_file, 'r', encoding='utf-8') as f:
            vocabulary = json.load(f)

        genres = vocabulary.get('genres', [])
        query = q.lower().strip()
        matched = [g for g in genres if query in g.lower()]
        return sorted(matched)[:20]
    except Exception as e:
        logger.error(f"Error searching genres: {str(e)}")
        return []


@router.get("/search/authors", tags=["Search"])
def search_authors(q: str = Query(..., min_length=1, max_length=100, description="Search query for authors")) -> List[str]:
    """
    Searches for authors from the clean vocabulary JSON file.
    """
    try:
        vocab_file = Path(CLEAN_VOCABULARY_PATH)
        if not vocab_file.exists():
            logger.error(f"Vocabulary file not found: {vocab_file}")
            return []

        with open(vocab_file, 'r', encoding='utf-8') as f:
            vocabulary = json.load(f)

        authors = vocabulary.get('authors', [])
        query = q.lower().strip().replace(" ", "")
        matched = [a for a in authors if query in a]
        return sorted(matched)[:20]
    except Exception as e:
        logger.error(f"Error searching authors: {str(e)}")
        return []


@router.get("/search/books", tags=["Search"])
def search_books(q: str = Query(..., min_length=1, max_length=100, description="Search query for books")) -> List[str]:
    """
    Searches for book titles from the clean vocabulary JSON file.
    """
    try:
        vocab_file = Path(CLEAN_VOCABULARY_PATH)
        if not vocab_file.exists():
            logger.error(f"Vocabulary file not found: {vocab_file}")
            return []

        with open(vocab_file, 'r', encoding='utf-8') as f:
            vocabulary = json.load(f)

        titles = vocabulary.get('titles', [])
        query = q.lower().strip()
        matched = [t for t in titles if query in t.lower()]
        return sorted(matched)[:20]
    except Exception as e:
        logger.error(f"Error searching books: {str(e)}")
        return []
