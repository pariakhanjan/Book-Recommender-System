from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime


class PreferenceBase(BaseModel):
    preferred_languages: List[str] = Field(..., min_length=1, description="List of preferred languages (e.g., ['en', 'fa']). Mandatory for recommendations.")
    liked_genres: List[str] = Field(default_factory=list, description="List of genres the user likes.")
    liked_authors: List[str] = Field(default_factory=list, description="List of authors the user likes.")
    liked_book_ids: List[str] = Field(default_factory=list, description="List of specific book IDs the user has liked.")
    disliked_genres: List[str] = Field(default_factory=list, description="List of genres the user wants to avoid.")
    disliked_authors: List[str] = Field(default_factory=list, description="List of authors the user wants to avoid.")
    disliked_book_ids: List[str] = Field(default_factory=list, description="List of specific book IDs the user has disliked.")

class PreferenceCreate(PreferenceBase):
    pass


class PreferenceUpdate(BaseModel):
    preferred_languages: Optional[List[str]] = None
    liked_genres: Optional[List[str]] = None
    liked_authors: Optional[List[str]] = None
    liked_book_ids: Optional[List[str]] = None
    disliked_genres: Optional[List[str]] = None
    disliked_authors: Optional[List[str]] = None
    disliked_book_ids: Optional[List[str]] = None


class PreferenceResponse(PreferenceBase):
    id: int
    user_id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    email: Optional[str] = Field(None, description="Optional email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    hashed_password: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str = Field(..., description="User's username.")
    password: str = Field(..., description="User's plain text password.")

class FeedbackCreate(BaseModel):
    user_id: int = Field(..., description="ID of the user providing feedback.")
    book_id: str = Field(..., description="ID of the book being reviewed.")
    feedback_type: str = Field(..., description="Type of feedback: 'liked', 'disliked', 'read', or 'want_to_read'.")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Optional rating from 1.0 to 5.0.")
    comment: Optional[str] = Field(None, max_length=500, description="Optional text comment.")

    @field_validator('feedback_type')
    @classmethod
    def validate_feedback_type(cls, v: str) -> str:
        allowed_types = {"liked", "disliked", "read", "want_to_read"}
        if v not in allowed_types:
            raise ValueError(f"Feedback type must be one of: {allowed_types}")
        return v


class FeedbackResponse(FeedbackCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BookSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200, description="Search keyword.")
    lang: Optional[str] = Field(None, description="Filter by language.")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class BookSearchResponse(BaseModel):
    bookId: str
    title: str
    author: str
    genres: Optional[str]
    rating: Optional[float]
    coverImg: Optional[str]
    language: Optional[str]
    match_score: float


class UserProfileRequest(BaseModel):
    preferred_languages: List[str]
    favorite_genres: Optional[List[str]] = Field(default_factory=list)
    favorite_authors: Optional[List[str]] = Field(default_factory=list)
    liked_book_ids: Optional[List[str]] = Field(default_factory=list)
    disliked_genres: Optional[List[str]] = Field(default_factory=list)
    disliked_authors: Optional[List[str]] = Field(default_factory=list)
    disliked_book_ids: Optional[List[str]] = Field(default_factory=list)
    top_n: int = Field(default=5, ge=1, le=50, description="Number of recommendations to return.")

class BookResponse(BaseModel):
    bookId: str
    title: str
    author: str
    genres: Optional[str] = ""
    rating: Optional[float] = 0.0
    coverImg: Optional[str] = ""
    language: Optional[str] = "en"
    similarity_score: float
