from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
import bcrypt
from utils.logger import logger

from api.schemas import (
    UserCreate, UserResponse, PreferenceCreate, PreferenceResponse,
    FeedbackCreate, FeedbackResponse, BookSearchRequest, BookSearchResponse,
    UserProfileRequest, BookResponse, UserLogin
)
from src.database import get_db, UserModel, UserPreferenceModel, UserFeedbackModel
from src.recommender import BookRecommender

router = APIRouter(prefix="/api", tags=["API"])
recommender = BookRecommender()


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.get("/", response_model=dict, tags=["System"])
def health_check():
    """Simple health check endpoint to verify API is running."""
    return {"status": "online", "message": "Book Recommender API is running", "version": "2.0.0"}


@router.post("/auth/login", tags=["Authentication"])
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticates a user and returns their ID and username."""
    user = db.query(UserModel).filter(UserModel.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return {"user_id": user.id, "username": user.username, "message": "Login successful"}


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user, hashes their password, and initializes an empty preference profile."""
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
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/{user_id}/preferences", response_model=PreferenceResponse, tags=["Users"])
def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
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
def update_user_preferences(user_id: int, pref_in: PreferenceCreate, db: Session = Depends(get_db)):
    """Updates the user's liked/disliked genres, authors, and books."""
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
def submit_feedback(feedback_in: FeedbackCreate, db: Session = Depends(get_db)):
    """Records user feedback and dynamically updates their preference profile."""
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
def get_personalized_recommendations(user_id: int, top_n: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
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
def get_popular_books(top_n: int = Query(10, ge=1, le=50), lang: Optional[str] = None):
    languages = [lang] if lang else None
    return recommender.get_popular_books(n=top_n, languages=languages)


@router.get("/search/genres", tags=["Search"])
def search_genres(q: str = Query(..., min_length=1, description="Search query for genres")):
    # بازگرداندن ژانرهای یکتا که شامل کوئری هستند
    genres = recommender.df['clean_genres'].dropna().unique()
    matched = [g for g in genres if q.lower() in str(g).lower()]
    return list(set(matched))[:20]  # محدود به 20 مورد برای پرفورمنس


@router.get("/search/authors", tags=["Search"])
def search_authors(q: str = Query(..., min_length=1, description="Search query for authors")):
    authors = recommender.df['clean_author'].dropna().unique()
    matched = [a for a in authors if q.lower() in str(a).lower()]
    return list(set(matched))[:20]


@router.get("/search/books", tags=["Search"])
def search_books(q: str = Query(..., min_length=1, description="Search query for books")):
    titles = recommender.df['title'].dropna().unique()
    matched = [t for t in titles if q.lower() in str(t).lower()]
    return list(set(matched))[:20]


@router.get("/search/unique-genres", tags=["Search"])
def get_unique_genres():
    """Returns a list of all unique genres from the dataset"""
    genres = recommender.df['clean_genres'].dropna().unique()
    # Split compound genres and get unique ones
    all_genres = set()
    for genre_str in genres:
        if isinstance(genre_str, str):
            for g in genre_str.split():
                if g.strip():
                    all_genres.add(g.strip())
    return sorted(list(all_genres))


@router.get("/search/unique-authors", tags=["Search"])
def get_unique_authors():
    """Returns a list of all unique authors from the dataset"""
    authors = recommender.df['clean_author'].dropna().unique()
    return sorted([a for a in authors if isinstance(a, str) and a.strip()])


@router.get("/search/unique-books", tags=["Search"])
def get_unique_books():
    """Returns a list of all unique book titles from the dataset"""
    books = recommender.df['title'].dropna().unique()
    return sorted([b for b in books if isinstance(b, str) and b.strip()])
