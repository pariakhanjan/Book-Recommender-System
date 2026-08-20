# Book-Recommender-System
Android-based smart book recommendation system using Content-Based Filtering (TF-IDF + Cosine Similarity) trained on the Goodreads Best Books Ever dataset. Python/FastAPI backend + Android (Java) frontend.
# 📚 Book Recommender System (Backend)

A Content-Based Filtering Book Recommendation System built with **Python**, **FastAPI**, **scikit-learn**, and **Pytest**. 

This system processes book metadata, computes text vectorizations using TF-IDF, calculates cosine similarities, and exposes RESTful API endpoints for client integrations.

---

## 📁 Project Structure

```text
backend/
├── api/                      # FastAPI endpoints and schemas
│   ├── main.py               # Application entry point
│   ├── routes.py             # API route definitions
│   └── schemas.py            # Pydantic data models
├── data/
│   ├── raw/                  # Raw datasets (English & Persian)
│   └── processed/            # Cleaned datasets and saved models
├── src/                      # Core business logic
│   ├── config.py             # Environment and path configurations
│   ├── database.py           # SQLAlchemy ORM models
│   ├── preprocessing.py      # Data cleaning and NLP pipeline
│   ├── feature_extraction.py # TF-IDF vectorization
│   ├── recommender.py        # Recommendation engine logic
│   └── inspect_model.py      # Utility to inspect saved models
├── tests/                    # Unit and integration tests
├── utils/                    # Helper utilities
│   └── logger.py             # Rich-formatted logging
├── .env                      # Environment variables (DO NOT COMMIT)
└── setup_database.sql        # Database initialization script
```

# 🚀 Installation & Setup
## Prerequisites
```text
Python 3.9+
PostgreSQL 12+
pip and venv
```

## Step-by-Step Guide
### 1. Create and activate a virtual environment:
```text
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
```
### 2.Install dependencies:
```text
   pip install fastapi uvicorn pandas numpy scikit-learn sqlalchemy psycopg2-binary pydantic pydantic-settings rich hazm pytest
```
### 3.Configure Environment Variables:
```text
   DB_USER=postgres
   DB_PASSWORD=your_actual_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=book_recommender
```
### 4.Initialize the Database:
```text
Run the SQL script in pgAdmin, DBeaver, or via psql:
   psql -U postgres -h localhost -d book_recommender -f setup_database.sql
```
### 5.Preprocess Data & Extract Features:
```text
   python backend/src/preprocessing.py
   python backend/src/feature_extraction.py
```
### 6.Run the Server:
```text
   python backend/api/main.py
   # OR using uvicorn directly:
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
## 📚 API Documentation

Once the server is running, interactive API documentation is automatically generated and available at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### 📖 Books
- `GET /api/books/popular` - Retrieve top-rated popular books.
- `POST /api/books/search` - Search books by title, author, or description with relevance scoring.

#### 💡 Recommendations
- `POST /api/recommend/profile` - Get personalized recommendations based on user preferences (genres, authors, liked books).
- `GET /api/recommend/book/{book_id}` - Get books similar to a specific book (Content-Based).
- `GET /api/users/{user_id}/recommendations` - Get personalized recommendations for a registered user.

#### 👤 Users
- `POST /api/users` - Create a new user account.
- `GET /api/users/{user_id}` - Retrieve user details.
- `PUT /api/users/{user_id}/preferences` - Update user liked/disliked genres, authors, and books.

#### 💬 Feedback
- `POST /api/feedback` - Submit user feedback (liked, disliked, read, want_to_read) to improve future recommendations.
- `GET /api/users/{user_id}/feedbacks` - Retrieve a user's complete feedback history.

---

## 🧪 Testing

Run the unit and integration test suite using `pytest`:

```bash
pytest backend/tests/ -v
```
*(Current Status: 12/12 tests passing)*

---

## ✨ Key Features

- **🌐 Bilingual NLP Pipeline:** Advanced text cleaning for both English (stopword removal, tokenization) and Persian (using the `Hazm` library for normalization, lemmatization, and stopword removal).
- **🤖 Content-Based Filtering:** Utilizes TF-IDF vectorization and Cosine Similarity for highly accurate, explainable content matching.
- **⚖️ Weighted User Profiling:** Dynamically combines user preferences (liked books weighted highest, followed by genres and authors) to build a robust user vector.
- **🗄️ Robust Database:** PostgreSQL with SQLAlchemy ORM, utilizing JSON columns for flexible preference storage and indexed columns for optimized query performance.
- **🎨 Developer Experience:** Beautiful, color-coded console output and progress bars using the `Rich` library, alongside comprehensive Pydantic V2 data validation.

---

## 📊 Project Statistics

- **Total Books Processed:** 68,132 (52,478 English + 15,708 Persian)
- **TF-IDF Vocabulary Size:** 20,000 optimized features
- **Sparse Matrix Efficiency:** ~4.7 million non-zero elements (highly memory-efficient storage)
- **Test Coverage:** 100% of core utility and schema tests passing

---

## ⚠️ Important Notes

1. **IDE Type Warnings:** You might see minor type-checking warnings in PyCharm (e.g., regarding SQLAlchemy boolean types or CORS middleware). These are **IDE-level warnings only** and do not affect runtime execution.
2. **Hazm Library:** Installing `hazm` is highly recommended for optimal Persian text processing. If not installed, the system gracefully falls back to basic regex-based cleaning.
3. **Production Security:** Before deploying to production, change `allow_origins=["*"]` in `main.py` to your specific frontend domain, and ensure your `.env` file is never committed to version control.

---

## 📱 Android Integration Notes

When connecting your Android (Java/Kotlin) app to this backend:
- **Android Emulator Base URL:** `http://10.0.2.2:8000/api`
- **Physical Device Base URL:** `http://<YOUR_LOCAL_IP_ADDRESS>:8000/api`
- **Data Parsing:** Ensure your Retrofit/Gson setup correctly handles JSON arrays for the `liked_genres`, `liked_authors`, and `liked_book_ids` fields, as they are stored as JSON strings in the database but returned as arrays in the API response.

---

## 📄 License

This project is licensed under the MIT License.