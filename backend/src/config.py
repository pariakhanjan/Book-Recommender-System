from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATA_PATH_EN = RAW_DATA_DIR / "books_1_Best_Books_Ever.csv"
RAW_DATA_PATH_FA = RAW_DATA_DIR / "data.csv"

PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "books_clean.csv"
TFIDF_MATRIX_PATH = PROCESSED_DATA_DIR / "tfidf_matrix.pkl"
SIMILARITY_MATRIX_PATH = PROCESSED_DATA_DIR / "similarity_matrix.pkl"
VECTORIZER_PATH = PROCESSED_DATA_DIR / "tfidf_vectorizer.pkl"


class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "book_recommender"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
