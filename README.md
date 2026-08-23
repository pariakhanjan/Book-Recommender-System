```markdown
# 📚 Book Recommender System (Backend)

A Content-Based Filtering Book Recommendation System built with **Python**, **FastAPI**, **scikit-learn**, and **PostgreSQL**. 

This system processes bilingual book metadata, computes text vectorizations using TF-IDF, calculates dynamic weighted cosine similarities, and exposes robust RESTful API endpoints for client integrations (e.g., Android).

---

## 📁 Project Structure

```text
backend/
├── api/                      # FastAPI endpoints and schemas
│   ├── main.py               # Application entry point & lifespan
│   ├── routes.py             # API route definitions & business logic
│   └── schemas.py            # Pydantic V2 data models & validation
├── data/
│   ├── raw/                  # Raw datasets (English & Persian)
│   └── processed/            # Cleaned datasets and saved ML models
├── src/                      # Core business logic
│   ├── config.py             # Environment and path configurations
│   ├── database.py           # SQLAlchemy ORM models
│   ├── preprocess.py         # Data cleaning and NLP pipeline
│   ├── features.py           # TF-IDF vectorization pipeline
│   └── recommender.py        # Recommendation engine logic
├── utils/                    # Helper utilities
│   └── logger.py             # Rich-formatted logging
├── .env                      # Environment variables (DO NOT COMMIT)
└── setup_database.sql        # Database initialization script
```

---

## 🚀 Installation & Execution Order

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- `pip` and `venv`

### Step-by-Step Setup

**1. Create and activate a virtual environment:**
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure Environment Variables:**
Create a `.env` file in the `backend/` directory:
```env
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=book_recommender
```

**4. Initialize the Database:**
Run the SQL script in pgAdmin, DBeaver, or via terminal:
```bash
psql -U postgres -h localhost -d book_recommender -f setup_database.sql
```

**5. Preprocess Data & Extract Features (Must be done in this order):**
```bash
python -m src.preprocess
python -m src.features
```

**6. Run the Server:**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 API Documentation

Once the server is running, interactive API documentation is automatically generated:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Authenticate user and retrieve `user_id`. |
| `POST` | `/api/users` | Create a new user account (passwords are hashed via bcrypt). |
| `PUT` | `/api/users/{user_id}/preferences` | Update user liked/disliked genres, authors, books, and **required** preferred languages. |
| `GET` | `/api/users/{user_id}/recommendations` | Get personalized recommendations. Triggers **Cold Start** fallback if profile is empty. |
| `POST` | `/api/feedback` | Submit user feedback (`liked`, `disliked`, `read`, `want_to_read`) to dynamically update preferences. |
| `GET` | `/api/books/popular` | Retrieve top-rated popular books (supports `lang` query parameter). |

---

## 🧠 Algorithm & Architecture

The recommendation engine uses a **Weighted Content-Based Filtering** approach:

1. **Text Processing:** A bilingual NLP pipeline cleans text. English uses standard tokenization and stopword removal. Persian utilizes the `Hazm` library for advanced normalization, lemmatization, and stopword removal.
2. **Feature Extraction:** TF-IDF vectorization is applied to a weighted "soup" of book metadata (Genres x4, Title x2, Author x2, Description x1) to create a 20,000-feature sparse matrix.
3. **Dynamic User Profiling:** When a user requests recommendations, the system builds a composite user vector based on research-backed weights:
   - **Liked Books:** `0.50` (Strongest signal of exact taste)
   - **Liked Genres:** `0.25` (Moderate signal of thematic preference)
   - **Liked Authors:** `0.15` (Weaker signal to prevent author overfitting)
   - **Disliked Items:** Symmetrical negative weights (`-0.50`, `-0.25`, `-0.15`) to actively penalize and filter out unwanted content.
   - **Rating Boost:** A minor `+0.10` boost is applied to the final cosine similarity score based on the book's average rating.
4. **Cold Start Handling:** If a user has no preferences or the calculated weights sum to zero, the system gracefully falls back to returning the highest-rated popular books, strictly filtered by the user's explicitly selected `preferred_languages`.

---

## 📊 Project Statistics

| Metric | Value |
| :--- | :--- |
| **Total Books Processed** | ~68,000 (English & Persian combined) |
| **TF-IDF Vocabulary Size** | 20,000 optimized features |
| **Sparse Matrix Efficiency** | Highly memory-efficient storage via `joblib` |
| **Security** | Bcrypt password hashing, SQL injection prevention via SQLAlchemy ORM |

---

## ⚠️ Important Notes

1. **Hazm Library:** Installing `hazm` is highly recommended for optimal Persian text processing. If not installed, the system gracefully falls back to basic regex-based cleaning.
2. **Production Security:** Before deploying, change `allow_origins=["*"]` in `main.py` to your specific frontend domain, and ensure your `.env` file is never committed to version control.
3. **Language Enforcement:** The API strictly requires `preferred_languages` to be set in the user profile before generating personalized recommendations to prevent cross-language noise.

---

## 📱 Android Integration Notes

When connecting your Android (Java) app to this backend:
- **Android Emulator Base URL:** `http://10.0.2.2:8000`
- **Physical Device Base URL:** `http://<YOUR_LOCAL_IPV4_ADDRESS>:8000` (Ensure both devices are on the same Wi-Fi and Windows Firewall allows port 8000).
- **Data Parsing:** Ensure your Retrofit/Gson setup correctly handles JSON arrays for the `liked_genres`, `liked_authors`, and `preferred_languages` fields, as they are stored as JSON strings in the database but returned as arrays in the API response.
- **Feedback Payload:** When sending feedback, ensure the `feedback_type` string exactly matches: `"liked"` or `"disliked"` (not "like" or "dislike") to pass Pydantic validation.

---

## 📄 License

This project is licensed under the MIT License.
```