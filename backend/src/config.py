from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Paths to raw files
RAW_DATA_PATH_EN = RAW_DATA_DIR / "books_1_Best_Books_Ever.csv"
RAW_DATA_PATH_FA = RAW_DATA_DIR / "data.csv"

# Paths to processed output files
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "books_clean.csv"
TFIDF_MATRIX_PATH = PROCESSED_DATA_DIR / "tfidf_matrix.pkl"
SIMILARITY_MATRIX_PATH = PROCESSED_DATA_DIR / "similarity_matrix.pkl"
VECTORIZER_PATH = PROCESSED_DATA_DIR / "tfidf_vectorizer.pkl"

DATABASE_URL = f"sqlite:///{BASE_DIR}/recommender.db"
