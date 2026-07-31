# Book-Recommender-System
Android-based smart book recommendation system using Content-Based Filtering (TF-IDF + Cosine Similarity) trained on the Goodreads Best Books Ever dataset. Python/FastAPI backend + Android (Java) frontend.
# 📚 Book Recommender System (Backend)

A Content-Based Filtering Book Recommendation System built with **Python**, **FastAPI**, **scikit-learn**, and **Pytest**. 

This system processes book metadata, computes text vectorizations using TF-IDF, calculates cosine similarities, and exposes RESTful API endpoints for client integrations.

---

## 📁 Project Structure

```text
Book-Recommender-System/
├── backend/
│   ├── data/
│   │   ├── raw/
│   │   │   └── books_1_Best_Books_Ever.csv
│   │   └── processed/
│   │       ├── books_clean.csv
│   │       ├── tfidf_matrix.pkl
│   │       └── similarity_matrix.pkl
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration & path constants
│   │   ├── preprocessing.py      # Data cleaning & normalization
│   │   ├── feature_extraction.py # TF-IDF Matrix calculation & pickling
│   │   └── recommender.py        # Recommender engine logic
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py               # FastAPI application & REST endpoints
│   │   swagger @ http://localhost:8000/docs           
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_recommender.py   # Unit tests for preprocessing & recommendations
│   └── pytest.ini                # Pytest configuration file
├── .venv/                        # Virtual environment
└── README.md