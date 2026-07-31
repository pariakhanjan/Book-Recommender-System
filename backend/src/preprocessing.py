import string

import pandas as pd
import ast
import re
from src.config import RAW_DATA_PATH_EN, RAW_DATA_PATH_FA, PROCESSED_DATA_PATH

ENGLISH_STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "he", "him", "his", "she", "her", "it", "its", "they", "them",
    "their", "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and",
    "but", "if", "or", "because", "as", "until", "while", "of", "at", "by",
    "for", "with", "about", "against", "between", "into", "through", "during",
    "before", "after", "above", "below", "to", "from", "up", "down", "in",
    "out", "on", "off", "over", "under", "again", "further", "then", "once"
}

PERSIAN_STOPWORDS = {
    "از", "با", "به", "در", "را", "که", "این", "آن", "یک", "برای", "تا", "بر",
    "نیز", "خود", "هم", "بی", "اما", "یا", "اگر", "چون", "چه", "پس", "باید",
    "هر", "است", "شد", "بود", "کرد", "می", "داشت", "وی"
}


def clean_genres(genre_str: str) -> str:
    if pd.isna(genre_str):
        return ""
    try:
        genres = ast.literal_eval(genre_str)
        if isinstance(genres, list):
            return " ".join([str(g).replace(" ", "").lower() for g in genres])
    except Exception:
        return str(genre_str).replace(" ", "").lower()
    return ""


def clean_english_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [w for w in tokens if w not in ENGLISH_STOPWORDS and len(w) > 1]
    return " ".join(tokens)


def clean_persian_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text).replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    tokens = text.split()
    tokens = [w for w in tokens if w not in PERSIAN_STOPWORDS and len(w) > 1]
    return " ".join(tokens)


def load_and_standardize_datasets() -> pd.DataFrame:
    dfs = []

    # 1. Load English Dataset
    if RAW_DATA_PATH_EN.exists():
        print("Loading English raw dataset...")
        df_en = pd.read_csv(RAW_DATA_PATH_EN)
        cols_en = {'bookId': 'bookId', 'title': 'title', 'author': 'author',
                   'genres': 'genres', 'description': 'description',
                   'rating': 'rating', 'coverImg': 'coverImg'}
        df_en = df_en[[c for c in cols_en.keys() if c in df_en.columns]].rename(columns=cols_en)
        df_en['language'] = 'en'
        df_en['bookId'] = "en_" + df_en['bookId'].astype(str)
        dfs.append(df_en)
        print(f"Loaded {len(df_en)} English books.")

    # 2. Load Persian Dataset
    if RAW_DATA_PATH_FA.exists():
        print("Loading Persian raw dataset...")
        df_fa = pd.read_csv(RAW_DATA_PATH_FA)
        cols_fa = {'book_id': 'bookId', 'title': 'title', 'author_name': 'author',
                   'categories': 'genres', 'description': 'description',
                   'rating': 'rating', 'coveruri': 'coverImg'}
        df_fa = df_fa[[c for c in cols_fa.keys() if c in df_fa.columns]].rename(columns=cols_fa)
        df_fa['language'] = 'fa'
        df_fa['bookId'] = "fa_" + df_fa['bookId'].astype(str)
        dfs.append(df_fa)
        print(f"Loaded {len(df_fa)} Persian books.")

    if not dfs:
        raise FileNotFoundError("No raw dataset files found in backend/data/raw/")

    return pd.concat(dfs, ignore_index=True)


def preprocess_dataset(output_path=PROCESSED_DATA_PATH):
    print("--- Starting Dataset Preprocessing ---")
    df = load_and_standardize_datasets()

    required_cols = ['bookId', 'title', 'author', 'genres', 'description', 'rating', 'coverImg', 'language']
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[required_cols].copy()

    initial_count = len(df)
    df.dropna(subset=['title'], inplace=True)
    df.drop_duplicates(subset=['bookId'], inplace=True)

    df['title'] = df['title'].fillna('')
    df['author'] = df['author'].fillna('Unknown')
    df['genres'] = df['genres'].fillna('[]')
    df['description'] = df['description'].fillna('')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
    df['coverImg'] = df['coverImg'].fillna('')

    print(f"Dropped {initial_count - len(df)} invalid/duplicate rows.")

    clean_titles, clean_authors, clean_genres_list, clean_descriptions, soups = [], [], [], [], []

    for _, row in df.iterrows():
        lang = row['language']
        clean_fn = clean_persian_text if lang == 'fa' else clean_english_text

        c_title = clean_fn(row['title'])
        c_author = str(row['author']).replace(" ", "").lower() if lang == 'en' else clean_persian_text(row['author'])
        c_genre = clean_genres(row['genres'])
        c_desc = clean_fn(row['description'])

        clean_titles.append(c_title)
        clean_authors.append(c_author)
        clean_genres_list.append(c_genre)
        clean_descriptions.append(c_desc)

        soup_text = f"{(c_title + ' ') * 3}{(c_author + ' ') * 3}{(c_genre + ' ') * 2}{c_desc}"
        soups.append(soup_text.strip())

    df['clean_title'] = clean_titles
    df['clean_author'] = clean_authors
    df['clean_genres'] = clean_genres_list
    df['clean_description'] = clean_descriptions
    df['soup'] = soups

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Preprocessing finished successfully! Saved to: {output_path}")
    print(f"Total valid books ready: {len(df)}")
    return df


if __name__ == "__main__":
    preprocess_dataset()
