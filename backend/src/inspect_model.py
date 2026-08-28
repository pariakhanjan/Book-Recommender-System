"""
Inspection utility for saved TF-IDF artifacts.

This script loads the pre-computed TF-IDF vectorizer and matrix
to verify their integrity and display key statistics about the
feature space.
"""
import joblib
from src.config import TFIDF_MATRIX_PATH, VECTORIZER_PATH


def inspect_saved_files() -> None:
    """
    Loads and inspects the saved TF-IDF vectorizer and matrix.

    Prints the total vocabulary size, a sample of feature names,
    the shape of the TF-IDF matrix, the number of non-zero elements,
    and a sample of the first book's sparse vector representation.
    """
    print("--- Loading Saved Files ---")
    tfidf = joblib.load(VECTORIZER_PATH)
    tfidf_matrix = joblib.load(TFIDF_MATRIX_PATH)

    print("\n1. Inspecting TF-IDF Vectorizer:")
    feature_names = tfidf.get_feature_names_out()
    print(f"- Total vocabulary size: {len(feature_names)}")
    print(f"- Sample features: {list(feature_names[100:120])}")

    print("\n2. Inspecting TF-IDF Matrix:")
    print(f"- Matrix shape (Books, Features): {tfidf_matrix.shape}")
    print(f"- Total non-zero elements (stored values): {tfidf_matrix.nnz}")

    print("\n- First book sparse vector sample:")
    print(tfidf_matrix[0])


if __name__ == "__main__":
    inspect_saved_files()
