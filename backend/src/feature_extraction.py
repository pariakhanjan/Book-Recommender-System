import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import PROCESSED_DATA_PATH, TFIDF_MATRIX_PATH, VECTORIZER_PATH
from utils.logger import console


def build_features():
    console.print("[bold cyan]Loading processed dataset...[/bold cyan]")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    df['soup'] = df['soup'].fillna('')

    console.print("[bold cyan]Extracting TF-IDF features...[/bold cyan]")
    tfidf = TfidfVectorizer(max_features=20000, sublinear_tf=True)
    tfidf_matrix = tfidf.fit_transform(df['soup'])

    console.print("[bold cyan]Saving TF-IDF vectorizer and sparse matrix...[/bold cyan]")
    VECTORIZER_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(tfidf, VECTORIZER_PATH)
    joblib.dump(tfidf_matrix, TFIDF_MATRIX_PATH)
    console.print("[bold green]Feature extraction completed successfully![/bold green]")


if __name__ == "__main__":
    build_features()
