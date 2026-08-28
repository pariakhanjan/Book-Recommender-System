"""
Pydantic schemas for request validation and response serialization.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime


class PreferenceBase(BaseModel):
    """Base schema for user reading preferences."""
    preferred_languages: List[str] = Field(..., min_length=1, description="List of preferred languages (e.g., ['en', 'fa']). Mandatory for recommendations.")
    liked_genres: List[str] = Field(default_factory=list, description="List of genres the user likes.")
    liked_authors: List[str] = Field(default_factory=list, description="List of authors the user likes.")
    liked_book_ids: List[str] = Field(default_factory=list, description="List of specific book IDs the user has liked.")
    disliked_genres: List[str] = Field(default_factory=list, description="List of genres the user wants to avoid.")
    disliked_authors: List[str] = Field(default_factory=list, description="List of authors the user wants to avoid.")
    disliked_book_ids: List[str] = Field(default_factory=list, description="List of specific book IDs the user has disliked.")


class PreferenceCreate(PreferenceBase):
    """Schema for creating a new preference profile."""
    pass


class PreferenceUpdate(BaseModel):
    """Schema for partially updating a preference profile."""
    preferred_languages: Optional[List[str]] = None
    liked_genres: Optional[List[str]] = None
    liked_authors: Optional[List[str]] = None
    liked_book_ids: Optional[List[str]] = None
    disliked_genres: Optional[List[str]] = None
    disliked_authors: Optional[List[str]] = None
    disliked_book_ids: Optional[List[str]] = None


class PreferenceResponse(PreferenceBase):
    """Schema for returning preference data in API responses."""
    id: int
    user_id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")


class UserResponse(BaseModel):
    """Schema for returning user data in API responses."""
    id: int
    username: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user authentication."""
    username: str = Field(..., description="User's username.")
    password: str = Field(..., description="User's plain text password.")


class FeedbackCreate(BaseModel):
    """Schema for submitting book feedback."""
    user_id: int = Field(..., description="ID of the user providing feedback.")
    book_id: str = Field(..., description="ID of the book being reviewed.")
    feedback_type: str = Field(..., description="Type of feedback: 'liked', 'disliked', 'read', or 'want_to_read'.")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Optional rating from 1.0 to 5.0.")
    comment: Optional[str] = Field(None, max_length=500, description="Optional text comment.")

    @field_validator('feedback_type')
    @classmethod
    def validate_feedback_type(cls, v: str) -> str:
        """Validates that the feedback type is one of the allowed values."""
        allowed_types = {"liked", "disliked", "read", "want_to_read"}
        if v not in allowed_types:
            raise ValueError(f"Feedback type must be one of: {allowed_types}")
        return v


class FeedbackResponse(FeedbackCreate):
    """Schema for returning feedback data in API responses."""
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BookSearchRequest(BaseModel):
    """Schema for book search queries."""
    query: str = Field(..., min_length=1, max_length=200, description="Search keyword.")
    lang: Optional[str] = Field(None, description="Filter by language.")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class BookSearchResponse(BaseModel):
    """Schema for book search results."""
    bookId: str
    title: str
    author: str
    genres: Optional[str]
    rating: Optional[float]
    coverImg: Optional[str]
    language: Optional[str]
    match_score: float


class UserProfileRequest(BaseModel):
    """Schema for requesting recommendations based on a raw profile."""
    preferred_languages: List[str]
    favorite_genres: Optional[List[str]] = Field(default_factory=list)
    favorite_authors: Optional[List[str]] = Field(default_factory=list)
    liked_book_ids: Optional[List[str]] = Field(default_factory=list)
    disliked_genres: Optional[List[str]] = Field(default_factory=list)
    disliked_authors: Optional[List[str]] = Field(default_factory=list)
    disliked_book_ids: Optional[List[str]] = Field(default_factory=list)
    top_n: int = Field(default=5, ge=1, le=50, description="Number of recommendations to return.")


class BookResponse(BaseModel):
    """Schema for returning book recommendation data."""
    bookId: str
    title: str
    author: str
    genres: Optional[str] = ""
    rating: Optional[float] = 0.0
    coverImg: Optional[str] = ""
    language: Optional[str] = "en"
    similarity_score: float
