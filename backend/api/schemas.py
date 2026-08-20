from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime


class PreferenceBase(BaseModel):
    liked_genres: List[str] = Field(default_factory=list)
    liked_authors: List[str] = Field(default_factory=list)
    liked_book_ids: List[str] = Field(default_factory=list)
    disliked_genres: List[str] = Field(default_factory=list)
    disliked_authors: List[str] = Field(default_factory=list)
    disliked_book_ids: List[str] = Field(default_factory=list)


class PreferenceCreate(PreferenceBase):
    pass


class PreferenceUpdate(BaseModel):
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
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None)

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
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FeedbackCreate(BaseModel):
    user_id: int
    book_id: str
    feedback_type: str
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, max_length=500)

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
    query: str = Field(..., min_length=1, max_length=200)
    lang: Optional[str] = Field(None)
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
    favorite_genres: Optional[List[str]] = Field(default_factory=list)
    favorite_authors: Optional[List[str]] = Field(default_factory=list)
    liked_book_ids: Optional[List[str]] = Field(default_factory=list)
    top_n: int = Field(default=5, ge=1, le=50)
    lang: Optional[str] = Field(None)


class BookResponse(BaseModel):
    bookId: str
    title: str
    author: str
    genres: Optional[str] = ""
    rating: Optional[float] = 0.0
    coverImg: Optional[str] = ""
    language: Optional[str] = "en"
    similarity_score: float
