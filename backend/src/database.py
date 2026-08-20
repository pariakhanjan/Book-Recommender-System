from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import logging

from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    preference = relationship("UserPreferenceModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    feedbacks = relationship("UserFeedbackModel", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    __table_args__ = (Index('ix_users_username', 'username'), Index('ix_users_email', 'email'))


class UserPreferenceModel(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    liked_genres = Column(JSON, default=list, nullable=False)
    liked_authors = Column(JSON, default=list, nullable=False)
    liked_book_ids = Column(JSON, default=list, nullable=False)
    disliked_genres = Column(JSON, default=list, nullable=False)
    disliked_authors = Column(JSON, default=list, nullable=False)
    disliked_book_ids = Column(JSON, default=list, nullable=False)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user = relationship("UserModel", back_populates="preference")
    __table_args__ = (Index('ix_user_preferences_user_id', 'user_id'),)


class UserFeedbackModel(Base):
    __tablename__ = "user_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id = Column(String(100), nullable=False, index=True)
    feedback_type = Column(String(20), nullable=False)
    rating = Column(Float, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("UserModel", back_populates="feedbacks")
    __table_args__ = (
        Index('ix_user_feedbacks_user_book', 'user_id', 'book_id'), Index('ix_user_feedbacks_type', 'feedback_type'))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    logger.info("Checking database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables are ready.")


if __name__ == "__main__":
    init_db()
