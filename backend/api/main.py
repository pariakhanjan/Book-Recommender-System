from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from src.recommender import BookRecommender

app = FastAPI(
    title="Book Recommender System API",
    description="REST API connecting frontend with multi-language recommendation engine.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = BookRecommender()


class UserProfileRequest(BaseModel):
    favorite_genres: Optional[List[str]] = Field(default=[], example=["Fantasy", "Young Adult"])
    favorite_authors: Optional[List[str]] = Field(default=[], example=["Suzanne Collins"])
    liked_book_ids: Optional[List[str]] = Field(default=[], example=["2767052-the-hunger-games"])
    top_n: Optional[int] = Field(default=5, ge=1, le=20, description="Number of recommendations to return (K)")


class BookResponse(BaseModel):
    bookId: str
    title: str
    author: str
    genres: Optional[str] = ""
    rating: Optional[float] = 0.0
    coverImg: Optional[str] = ""
    language: Optional[str] = "en"
    similarity_score: float


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/", tags=["Health Check"])
def root():
    """API Health Check Endpoint"""
    return {"status": "online", "message": "Book Recommender API is running successfully."}


@app.post("/api/recommend/profile", response_model=List[BookResponse], tags=["Recommendations"])
def recommend_by_profile(profile: UserProfileRequest):
    """
    Generate recommendations based on user profile:
    Calculates weighted average vector of interests (genres, authors, liked books)
    and retrieves top K most similar books.
    """
    try:
        recommendations = recommender.recommend_user_profile(
            favorite_genres=profile.favorite_genres,
            favorite_authors=profile.favorite_authors,
            liked_book_ids=profile.liked_book_ids,
            top_n=profile.top_n,
            lang=profile.lang
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@app.get("/api/recommend/book/{book_id}", response_model=List[BookResponse], tags=["Recommendations"])
def recommend_by_book(book_id: str, top_n: int = Query(default=5, ge=1, le=20),
                      lang: Optional[str] = Query(default=None)):
    recommendations = recommender.recommend_by_book_id(book_id=book_id, top_n=top_n, lang=lang)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Book ID not found in dataset.")
    return recommendations


@app.get("/api/books/popular", response_model=List[BookResponse], tags=["Books"])
def get_popular_books(top_n: int = Query(default=10, ge=1, le=50), lang: Optional[str] = Query(default=None)):
    return recommender.get_popular_books(n=top_n, lang=lang)


@app.get("/api/recommend/title/{title}", response_model=List[BookResponse], tags=["Recommendations"])
def recommend_by_title(
        title: str,
        top_n: int = Query(10, ge=1, le=50),
        lang: Optional[str] = Query(None, description="fa, en, or None for all")
):
    clean_search_title = title.strip().lower()
    matched_books = recommender.df[
        recommender.df['title'].str.strip().str.lower() == clean_search_title
        ]
    if matched_books.empty:
        matched_books = recommender.df[
            recommender.df['title'].str.strip().str.lower().str.contains(clean_search_title, regex=False)
        ]
    if matched_books.empty:
        raise HTTPException(
            status_code=404,
            detail=f"کتابی با عنوان '{title}' یافت نشد."
        )

    book_id = matched_books.iloc[0]['bookId']

    recommendations = recommender.recommend_by_book_id(
        book_id=book_id,
        top_n=top_n,
        lang_filter=lang
    )

    return recommendations
