# 📚 Book Recommender System

> An intelligent, bilingual (English & Persian) book recommendation system utilizing advanced Weighted Content-Based Filtering to deliver highly personalized and dynamic suggestions.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-005571?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Android-Java-3DDC84?logo=android" alt="Android">
  <img src="https://img.shields.io/badge/ML-TF--IDF-orange?logo=scikitlearn" alt="Machine Learning">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

---

## 📑 Table of Contents
- [📁 Project Structure](#-project-structure)
- [⚙️ Backend Setup](#️-backend-setup--execution)
- [📱 Android Setup](#-android-setup--execution)
- [🌐 API Documentation](#-api-documentation)
- [🧠 Algorithm & Architecture](#-algorithm--architecture)
- [📊 Statistics & Quality](#-statistics--quality-assurance)
- [⚠️ Important Notes](#️-important-notes)

---

## 📁 Project Structure

```text
Book-Recommender-System/
├── backend/                    # Python FastAPI Backend
│   ├── api/                    # Endpoints, Pydantic schemas, and main app
│   ├── data/                   # Raw and processed datasets, TF-IDF matrices
│   ├── src/                    # Core logic (preprocessing, recommender, database)
│   ├── tests/                  # Pytest unit and integration tests
│   ├── utils/                  # Helper utilities (e.g., rich logging)
│   ├── .env                    # Environment variables (DO NOT COMMIT)
│   ├── requirements.txt        # Python dependencies
│   └── analyze_tfidf.py        # Script for vector distinctiveness analysis
│
└── android/                    # Android Application (Java)
    ├── app/
    │   ├── src/main/
    │   │   ├── java/com/bookrecommender/app/
    │   │   │   ├── api/        # Retrofit interfaces and OkHttp clients
    │   │   │   ├── models/     # Data classes (Book, User, Feedback, etc.)
    │   │   │   ├── ui/         # Activities and Adapters (Auth, Preferences, Main)
    │   │   │   └── utils/      # Utilities (UserManager, Network helpers)
    │   │   ├── res/            # Layouts, colors, strings, themes, drawables
    │   │   └── AndroidManifest.xml
    │   └── build.gradle        # Android dependencies and build config
```

---

## ⚙️ Backend Setup & Execution

### Prerequisites
- Python 3.9+ (Recommended: **3.11**)
- PostgreSQL 12+ (or SQLite for local testing)
- `pip` and `venv`

### Step-by-Step Setup
1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Configure Environment Variables:**  
   Create a `.env` file in the `backend/` directory:
   ```env
   DATABASE_URL=sqlite:///./book_recommender.db
   # For PostgreSQL: postgresql://user:password@localhost:5432/book_recommender
   SECRET_KEY=your_super_secret_key_here
   ```
4. **Preprocess Data & Extract Features:**  
   *(This step cleans text, preserves multi-word genres, and builds the TF-IDF matrix)*
   ```bash
   python -m src.preprocessing
   python -m src.features
   ```
5. **Run the Server:**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## 📱 Android Setup & Execution

### Prerequisites
- Android Studio (latest stable version)
- JDK 17
- A physical Android device or emulator

### Step-by-Step Setup
1. **Open the Project:** Open the `android/` folder in Android Studio.
2. **Sync Gradle:** Allow Android Studio to download all dependencies (Retrofit2, OkHttp, Gson, Glide).
3. **Configure Network Connection:**  
   Open `android/app/build.gradle` and locate `currentApiUrl` in `defaultConfig`:
   - **For Local Demo (Recommended):** Set to your computer's local IP (e.g., `"http://192.168.43.XX:8000/api/"`). Connect your phone to your computer's Wi-Fi Hotspot for a stable, isolated network.
   - **For Cloud Deployment:** Set to your Render/Cloud URL (e.g., `"https://your-app.onrender.com/api/"`).
4. **Build and Run:** Click the **Run** button (▶️) or execute `.\gradlew installDebug` in the terminal.

### Key Android Features
- ✨ **Clean, Modern UI:** Soft purple/blue theme with explicit text labels and clear visual feedback.
- 🔍 **Dynamic AutoComplete:** Real-time search for genres, authors, and books with debounced backend queries.
- ⚡ **Interactive Feedback:** Like/Dislike buttons that instantly update the user's profile and trigger dynamic recalculations.
- 🛡️ **Robust Error Handling:** Graceful handling of network failures and API validation errors.

---

## 🌐 API Documentation

Once the backend server is running, interactive API documentation is automatically generated:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Authenticate user and retrieve `user_id`. |
| `POST` | `/api/users` | Create a new user account (passwords hashed via bcrypt). |
| `PUT` | `/api/users/{user_id}/preferences` | Update user preferences. *Includes backend validation to prevent like/dislike conflicts.* |
| `GET` | `/api/users/{user_id}/recommendations` | Get personalized recommendations. *Triggers **Cold Start** fallback if profile is empty.* |
| `POST` | `/api/feedback` | Submit feedback (`liked` or `disliked`) to dynamically update preferences in real-time. |

---

## 🧠 Algorithm & Architecture

The recommendation engine uses a **Positive-Only Profiling with Negative Filtering** approach to ensure stability, prevent weight cancellation, and eliminate author bias:

1. **Bilingual Text Processing:** English uses standard tokenization. Persian utilizes the `Hazm` library for normalization, lemmatization, and stopword removal. *Crucially, multi-word genres/authors preserve spaces for accurate matching.*
2. **Feature Extraction:** TF-IDF vectorization applied to a weighted "soup" of metadata (Genres ×4, Title ×2, Author ×2, Description ×1), creating a highly efficient 20,000-feature sparse matrix.
3. **Dynamic User Profiling (Positive Weights):**
   - **Liked Books:** `0.50` *(Strongest signal of exact taste)*
   - **Liked Genres:** `0.45` *(Promotes thematic diversity and discovery)*
   - **Liked Authors:** `0.05` *(Intentionally low weight to prevent author overfitting/bias)*
4. **Negative Filtering & Penalty (Dislikes):**
   - **Hard Filter:** Any book ID explicitly disliked is completely removed from the candidate pool.
   - **Similarity Penalty:** Books matching disliked genres or authors receive a `-0.50` penalty to their final cosine similarity score, pushing them to the bottom of the list.
5. **Cold Start Handling:** If user preferences are empty, the system gracefully falls back to returning the highest-rated popular books, strictly filtered by the user's selected `preferred_languages`.

---

## 📊 Statistics & Quality Assurance

| Metric | Value / Status |
| :--- | :--- |
| **Total Books Processed** | ~50,500+ (English & Persian combined) |
| **TF-IDF Vocabulary Size** | 20,000 optimized, distinct features |
| **Vector Distinctiveness** | **Excellent** (Mean Max Similarity: ~0.40, ensuring books are well-differentiated) |
| **Exact Duplicates** | 0% (Every book has a unique semantic signature) |
| **Security** | Bcrypt password hashing, SQL injection prevention via SQLAlchemy ORM |
| **Testing** | Comprehensive `pytest` suite covering preprocessing, schemas, and recommender logic |

---

## ⚠️ Important Notes

> [!IMPORTANT]
> **Demo Strategy:** For the most reliable presentation/defense, use the **Local Hotspot method**. Connect the laptop and phone to the same mobile hotspot, disable mobile data, and use the laptop's hotspot IP. This guarantees zero dependency on university Wi-Fi or external internet.

> [!WARNING]
> **Feedback Payload:** When sending feedback from Android, ensure `feedback_type` exactly matches `"liked"` or `"disliked"` (not "like"/"dislike") to pass Pydantic validation.

> [!NOTE]
> **Hazm Library:** Installing `hazm` is required for optimal Persian text processing. The system includes fallbacks, but full NLP capabilities depend on it.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
