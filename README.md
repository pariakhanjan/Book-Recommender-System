# 📚 Book Recommender System

A comprehensive, smart book recommendation system featuring a **Python/FastAPI backend** and an **Android (Java) frontend**. The system utilizes Content-Based Filtering with TF-IDF and Cosine Similarity, trained on a bilingual (English & Persian) dataset, to deliver personalized, dynamic book recommendations.

---

## 📁 Project Structure

```text
Book-Recommender-System/
├── backend/                    # Python FastAPI Backend
│   ├── api/                    # Endpoints, schemas, and main app
│   ├── data/                   # Raw and processed datasets
│   ├── src/                    # Core logic (preprocess, features, recommender, db)
│   ├── utils/                  # Helper utilities (e.g., rich logging)
│   ├── .env                    # Environment variables (DO NOT COMMIT)
│   ├── requirements.txt        # Python dependencies
│   └── setup_database.sql      # PostgreSQL initialization script
│
└── android/                    # Android Application (Java)
    ├── app/
    │   ├── src/main/
    │   │   ├── java/com/bookrecommender/app/
    │   │   │   ├── api/        # Retrofit interfaces and clients
    │   │   │   ├── models/     # Data classes (Book, User, Feedback, etc.)
    │   │   │   ├── ui/         # Activities and Adapters (Main, Setup, Detail)
    │   │   │   ├── utils/      # Utilities (NetworkUtils, UserManager)
    │   │   │   └── viewmodel/  # ViewModel for state management
    │   │   ├── res/            # Layouts, colors, strings, themes
    │   │   └── AndroidManifest.xml
    │   └── build.gradle        # Android dependencies
    └── gradle.properties
```

---

## ⚙️ Backend Setup & Execution

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
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
   DB_USER=postgres
   DB_PASSWORD=your_actual_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=book_recommender
   ```
4. **Initialize the Database:**
   ```bash
   psql -U postgres -h localhost -d book_recommender -f backend/setup_database.sql
   ```
5. **Preprocess Data & Extract Features:**
   ```bash
   python -m backend.src.preprocess
   python -m backend.src.features
   ```
6. **Run the Server:**
   ```bash
   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## 📱 Android Setup & Execution

### Prerequisites
- Android Studio (latest stable version)
- JDK 11 or 17
- A physical Android device or emulator

### Step-by-Step Setup
1. **Open the Project:** Open the `android/` folder in Android Studio.
2. **Sync Gradle:** Allow Android Studio to download all dependencies (Retrofit2, OkHttp, Gson, Glide, Lifecycle).
3. **Configure Network:** 
   - The app automatically detects the host machine's local IPv4 address using `NetworkUtils.java`.
   - Ensure your Android device and computer are on the **same Wi-Fi network**.
   - Ensure Windows Firewall allows inbound connections on port `8000`.
4. **Run the App:** Click the **Run** button (green triangle) or use `Shift + F10`.

### Key Android Features
- **Dynamic IP Resolution:** Automatically finds the host machine's IP, eliminating hardcoded URLs and Wi-Fi switching issues.
- **Auth & Onboarding:** Secure Signup/Login with mandatory language selection (EN/FA) and optional preference selection (genres/authors).
- **Personalized UI:** Soft purple and blue theme with smooth transitions and user-friendly error handling.
- **Interactive Feedback:** Like/Dislike buttons that instantly update the user's profile and trigger dynamic recommendation recalculations.
- **Reload Control:** Users can choose the number of recommendations (5, 10, 20, 50) and refresh the list on demand.

---

## 🌐 API Documentation

Once the backend server is running, interactive API documentation is automatically generated:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Authenticate user and retrieve `user_id`. |
| `POST` | `/api/users` | Create a new user account (passwords hashed via bcrypt). |
| `PUT` | `/api/users/{user_id}/preferences` | Update user preferences (languages, liked/disliked items). |
| `GET` | `/api/users/{user_id}/recommendations` | Get personalized recommendations (triggers **Cold Start** fallback if empty). |
| `POST` | `/api/feedback` | Submit feedback (`liked` or `disliked`) to dynamically update preferences. |
| `GET` | `/api/books/popular` | Retrieve top-rated popular books (supports `lang` query). |

---

## 🧠 Algorithm & Architecture

The recommendation engine uses a **Weighted Content-Based Filtering** approach:

1. **Text Processing:** Bilingual NLP pipeline. English uses standard tokenization/stopword removal. Persian utilizes the `Hazm` library for normalization, lemmatization, and stopword removal.
2. **Feature Extraction:** TF-IDF vectorization applied to a weighted "soup" of metadata (Genres x4, Title x2, Author x2, Description x1) creating a 20,000-feature sparse matrix.
3. **Dynamic User Profiling:** Composite user vector built using research-backed weights:
   - **Liked Books:** `0.50` (Strongest signal of exact taste)
   - **Liked Genres:** `0.25` (Moderate signal of thematic preference)
   - **Liked Authors:** `0.15` (Weaker signal to prevent author overfitting)
   - **Disliked Items:** Symmetrical negative weights (`-0.50`, `-0.25`, `-0.15`) to actively filter unwanted content.
   - **Rating Boost:** `+0.10` boost applied to the final cosine similarity score based on average rating.
4. **Cold Start Handling:** If user preferences are empty, the system gracefully falls back to returning the highest-rated popular books, strictly filtered by the user's selected `preferred_languages`.

---

## 📊 Project Statistics

| Metric | Value |
| :--- | :--- |
| **Total Books Processed** | ~68,000 (English & Persian combined) |
| **TF-IDF Vocabulary Size** | 20,000 optimized features |
| **Sparse Matrix Efficiency** | Highly memory-efficient storage via `joblib` |
| **Security** | Bcrypt password hashing, SQL injection prevention via SQLAlchemy ORM |
| **Android Architecture** | MVVM (Model-View-ViewModel) with LiveData |

---

## ⚠️ Important Notes

1. **Hazm Library:** Installing `hazm` is highly recommended for optimal Persian text processing. The system falls back to regex-based cleaning if unavailable.
2. **Production Security:** Before deploying, change `allow_origins=["*"]` in `main.py` to your specific frontend domain, and never commit the `.env` file.
3. **Language Enforcement:** The API strictly requires `preferred_languages` to be set before generating personalized recommendations to prevent cross-language noise.
4. **Feedback Payload:** When sending feedback from Android, ensure `feedback_type` exactly matches `"liked"` or `"disliked"` (not "like"/"dislike") to pass Pydantic validation.

---

## 📄 License

This project is licensed under the MIT License.
