from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd

from api.schemas import (
    UserCreate, UserResponse, PreferenceCreate, PreferenceResponse,
    FeedbackCreate, FeedbackResponse, BookSearchRequest, BookSearchResponse,
    UserProfileRequest, BookResponse
)
from src.database import get_db, UserModel, UserPreferenceModel, UserFeedbackModel
from src.recommender import BookRecommender

router = APIRouter(prefix="/api", tags=["API"])
recommender = BookRecommender()


@router.get("/", response_model=dict)
def health_check():
    return {"status": "online", "message": "Book Recommender API is running", "version": "2.0.0"}


def calculate_match_score(row, query: str) -> float:
    score = 0.0
    query_words = query.split()

    title_lower = str(row['title']).lower()
    if query in title_lower:
        score += 10.0
    else:
        score += sum(2.0 for word in query_words if word in title_lower)

    author_lower = str(row['author']).lower()
    if query in author_lower:
        score += 5.0
    else:
        score += sum(1.0 for word in query_words if word in author_lower)

    genres_lower = str(row['genres']).lower()
    if query in genres_lower:
        score += 3.0

    if pd.notna(row['rating']) and row['rating']:
        score += float(row['rating']) / 5.0

    return score


@router.post("/books/search", response_model=List[BookSearchResponse])
def search_books(request: BookSearchRequest):
    query = request.query.strip().lower()
    lang = request.lang
    limit = request.limit
    offset = request.offset
    try:
        df = recommender.df
        if lang:
            df = df[df['language'] == lang]

        mask = (
                df['title'].str.lower().str.contains(query, regex=False, na=False) |
                df['author'].str.lower().str.contains(query, regex=False, na=False) |
                df['clean_description'].str.lower().str.contains(query, regex=False, na=False)
        )
        results = df[mask].copy()
        results['match_score'] = results.apply(lambda row: calculate_match_score(row, query), axis=1)
        results = results.sort_values('match_score', ascending=False)
        results = results.iloc[offset:offset + limit]

        response = []
        for _, row in results.iterrows():
            response.append(BookSearchResponse(
                bookId=str(row['bookId']),
                title=str(row['title']),
                author=str(row['author']),
                genres=str(row['genres']),
                rating=float(row['rating']) if pd.notna(row['rating']) else 0.0,
                coverImg=str(row['coverImg']) if pd.notna(row['coverImg']) else "",
                language=str(row['language']),
                match_score=float(row['match_score'])
            ))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/recommend/profile", response_model=List[BookResponse])
def recommend_by_profile(profile: UserProfileRequest):
    try:
        return recommender.recommend_user_profile(
            favorite_genres=profile.favorite_genres,
            favorite_authors=profile.favorite_authors,
            liked_book_ids=profile.liked_book_ids,
            top_n=profile.top_n,
            lang=profile.lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/recommend/book/{book_id}", response_model=List[BookResponse])
def recommend_by_book(book_id: str, top_n: int = Query(5, ge=1, le=50), lang: Optional[str] = None):
    recommendations = recommender.recommend_by_book_id(book_id=book_id, top_n=top_n, lang_filter=lang)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Book not found")
    return recommendations


@router.get("/books/popular", response_model=List[BookResponse])
def get_popular_books(top_n: int = Query(10, ge=1, le=50), lang: Optional[str] = None):
    return recommender.get_popular_books(n=top_n, lang=lang)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user_in.email:
        db_email = db.query(UserModel).filter(UserModel.email == user_in.email).first()
        if db_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    new_user = UserModel(username=user_in.username, email=user_in.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    pref = UserPreferenceModel(user_id=new_user.id)
    db.add(pref)
    db.commit()
    return new_user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/{user_id}/preferences", response_model=PreferenceResponse)
def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref:
        pref = UserPreferenceModel(user_id=user_id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.put("/users/{user_id}/preferences", response_model=PreferenceResponse)
def update_user_preferences(user_id: int, pref_in: PreferenceCreate, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref:
        pref = UserPreferenceModel(user_id=user_id)
        db.add(pref)

    pref.liked_genres = pref_in.liked_genres
    pref.liked_authors = pref_in.liked_authors
    pref.liked_book_ids = pref_in.liked_book_ids
    pref.disliked_genres = pref_in.disliked_genres
    pref.disliked_authors = pref_in.disliked_authors
    pref.disliked_book_ids = pref_in.disliked_book_ids

    db.commit()
    db.refresh(pref)
    return pref


@router.post("/users/{user_id}/add-to-liked", response_model=PreferenceResponse)
def add_to_liked_books(user_id: int, book_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref:
        pref = UserPreferenceModel(user_id=user_id)
        db.add(pref)
        db.commit()
        db.refresh(pref)

    current_ids = pref.liked_book_ids or []
    if book_id not in current_ids:
        pref.liked_book_ids = current_ids + [book_id]
        db.commit()
        db.refresh(pref)
    return pref


@router.post("/users/{user_id}/remove-from-liked", response_model=PreferenceResponse)
def remove_from_liked_books(user_id: int, book_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found")

    current_ids = pref.liked_book_ids or []
    if book_id in current_ids:
        pref.liked_book_ids = [b for b in current_ids if b != book_id]
        db.commit()
        db.refresh(pref)
    return pref


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(feedback_in: FeedbackCreate, db: Session = Depends(get_db)):
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


@router.get("/users/{user_id}/feedbacks", response_model=List[FeedbackResponse])
def get_user_feedbacks(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(UserFeedbackModel).filter(UserFeedbackModel.user_id == user_id).all()


@router.get("/users/{user_id}/recommendations", response_model=List[BookResponse])
def get_personalized_recommendations(user_id: int, top_n: int = Query(10, ge=1, le=50), lang: Optional[str] = None,
                                     db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    pref = db.query(UserPreferenceModel).filter(UserPreferenceModel.user_id == user_id).first()
    if not pref or (not pref.liked_genres and not pref.liked_authors and not pref.liked_book_ids):
        return recommender.get_popular_books(n=top_n, lang=lang)

    try:
        return recommender.recommend_user_profile(
            favorite_genres=pref.liked_genres or [],
            favorite_authors=pref.liked_authors or [],
            liked_book_ids=pref.liked_book_ids or [],
            top_n=top_n,
            lang=lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")
