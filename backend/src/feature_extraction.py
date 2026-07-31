import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import PROCESSED_DATA_PATH, TFIDF_MATRIX_PATH, VECTORIZER_PATH


def build_features():
    print("Loading processed dataset...")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    df['soup'] = df['soup'].fillna('')

    print("Extracting TF-IDF features...")
    tfidf = TfidfVectorizer(max_features=20000, sublinear_tf=True)
    tfidf_matrix = tfidf.fit_transform(df['soup'])

    print("Saving TF-IDF vectorizer and sparse matrix...")
    VECTORIZER_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(tfidf, VECTORIZER_PATH)
    joblib.dump(tfidf_matrix, TFIDF_MATRIX_PATH)

    print("Feature extraction completed successfully!")


if __name__ == "__main__":
    build_features()
