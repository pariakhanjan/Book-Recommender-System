"""
Feature extraction module for the Book Recommender System.

This module handles the generation of TF-IDF vectors from the
preprocessed book dataset and saves them for use by the recommender engine.
"""
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import PROCESSED_DATA_PATH, TFIDF_MATRIX_PATH, VECTORIZER_PATH
from utils.logger import console


def build_features() -> None:
    """
    Loads the processed dataset, extracts TF-IDF features, and saves the artifacts.

    Reads the 'soup' column from the processed CSV, applies a TF-IDF vectorizer
    with sublinear TF scaling and a maximum of 20,000 features, and persists
    both the vectorizer and the resulting sparse matrix to disk using joblib.
    """
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
