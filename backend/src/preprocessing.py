import pandas as pd
import ast
import re
import string
import json
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from src.config import RAW_DATA_PATH_EN, RAW_DATA_PATH_FA, PROCESSED_DATA_PATH
from utils.logger import logger, console
from langdetect import detect, LangDetectException

try:
    from hazm import Normalizer, Lemmatizer, stopwords_list

    HAZM_AVAILABLE = True
    console.print("[bold green]Hazm library loaded successfully.[/bold green]")
except ImportError as e:
    HAZM_AVAILABLE = False
    logger.warning(f"Hazm import failed with error: {e}")
    logger.warning("Persian cleaning will use basic rules.")

ENGLISH_STOPWORDS = {"i", "me", "my", "we", "our", "you", "your", "he", "him", "his", "she", "her", "it", "its", "they",
                     "them", "their", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is",
                     "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did",
                     "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at",
                     "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after",
                     "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
                     "further", "then", "once"}
PERSIAN_STOPWORDS = {"از", "با", "به", "در", "را", "که", "این", "آن", "یک", "برای", "تا", "بر", "نیز", "خود", "هم",
                     "بی", "اما", "یا", "اگر", "چون", "چه", "پس", "باید", "هر", "است", "شد", "بود", "کرد", "می", "داشت",
                     "وی", "و", "ای", "نه", "بله"}


class TextCleaner:
    """Utility class for language-specific text normalization and cleaning."""
    def __init__(self):
        if HAZM_AVAILABLE:
            self.normalizer = Normalizer()
            self.lemmatizer = Lemmatizer()
            self.persian_stopwords = set(stopwords_list())

    def clean_english_text(self, text: str) -> str:
        """Cleans and tokenizes English text by removing punctuation and stopwords."""
        if pd.isna(text) or not text: return ""
        text = str(text).lower().translate(str.maketrans('', '', string.punctuation))
        return " ".join([w for w in text.split() if w not in ENGLISH_STOPWORDS and len(w) > 2])

    def clean_persian_text(self, text: str) -> str:
        """Cleans and tokenizes Persian text using Hazm or basic regex rules."""
        if pd.isna(text) or not text: return ""
        text = str(text)
        if HAZM_AVAILABLE:
            text = self.normalizer.normalize(text)
            text = re.sub(r'[^\w\s]', '', text)
            tokens = text.split()
            tokens = [w for w in tokens if w not in self.persian_stopwords and len(w) > 2]
            return " ".join([self.lemmatizer.lemmatize(w) for w in tokens])
        else:
            text = text.replace("ي", "ی").replace("ك", "ک")
            text = re.sub(r'[^\w\s]', '', text)
            return " ".join([w for w in text.split() if w not in PERSIAN_STOPWORDS and len(w) > 2])

    def clean_persian_text_simple(self, text: str) -> str:
        if pd.isna(text) or not text: return ""
        text = str(text)
        if HAZM_AVAILABLE:
            text = self.normalizer.normalize(text)
            text = re.sub(r'[^\w\s]', '', text)
            return " ".join([w for w in text.split() if len(w) > 1])
        else:
            text = text.replace("ي", "ی").replace("ك", "ک")
            text = re.sub(r'[^\w\s]', '', text)
            return " ".join([w for w in text.split() if len(w) > 1])

    def clean_genres(self, genre_str: str) -> str:
        """Parses and cleans genre strings, preserving spaces between words."""
        if pd.isna(genre_str) or not genre_str: return ""
        try:
            genres = ast.literal_eval(genre_str)
            if isinstance(genres, list):
                return " ".join([str(g).strip().lower() for g in genres if g])
        except (ValueError, SyntaxError):
            return str(genre_str).lower().strip('[]')
        return ""


def is_english_title(title: str) -> bool:
    """
    Checks whether a title is written in English using langdetect.
    Returns True for English titles, False otherwise.
    Short titles (less than 3 chars) are rejected to avoid false positives.
    """
    if pd.isna(title) or not title or len(str(title).strip()) < 3:
        return False
    try:
        detected = detect(str(title))
        return detected == 'en'
    except LangDetectException:
        return False


def fix_taaghche_image_urls(df: pd.DataFrame, column: str = 'coverImg') -> pd.DataFrame:
    old_domain = "https://img.taaghchecdn.com"
    new_domain = "https://img.taaghche.com"

    mask = df[column].astype(str).str.contains(old_domain, na=False)
    df.loc[mask, column] = df.loc[mask, column].str.replace(old_domain, new_domain, regex=False)

    return df


def preprocess_dataset(output_path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """
    Loads raw datasets, cleans text, and engineers the 'soup' feature for TF-IDF.
    The 'soup' combines title, author, genre, and description with specific weights
    to guide the TF-IDF vectorizer towards more important features.
    Also generates a clean vocabulary JSON for frontend autocomplete.
    Non-English titles in the English dataset are filtered out using langdetect.
    """
    console.print("[bold magenta]Starting Dataset Preprocessing...[/bold magenta]")
    dfs = []
    cleaner = TextCleaner()

    console.print(f"\n[cyan]Checking English dataset path:[/cyan] {RAW_DATA_PATH_EN}")
    if RAW_DATA_PATH_EN.exists():
        df_en = pd.read_csv(RAW_DATA_PATH_EN, encoding='utf-8')
        df_en = df_en[['bookId', 'title', 'author', 'genres', 'description', 'rating', 'coverImg']]

        console.print("[cyan]Filtering non-English titles with langdetect...[/cyan]")
        initial_en_count = len(df_en)
        df_en['is_english'] = df_en['title'].apply(is_english_title)
        df_en = df_en[df_en['is_english']].drop(columns=['is_english'])
        removed_en = initial_en_count - len(df_en)
        if removed_en > 0:
            console.print(f"[yellow]Removed {removed_en} non-English titles from English dataset.[/yellow]")

        df_en['language'] = 'en'
        df_en['bookId'] = "en_" + df_en['bookId'].astype(str)
        dfs.append(df_en)

    console.print(f"\n[cyan]Checking Persian dataset path:[/cyan] {RAW_DATA_PATH_FA}")
    if RAW_DATA_PATH_FA.exists():
        df_fa = pd.read_csv(RAW_DATA_PATH_FA, encoding='utf-8')
        df_fa = df_fa.rename(
            columns={'book_id': 'bookId', 'author_name': 'author', 'categories': 'genres', 'coveruri': 'coverImg'})
        df_fa = df_fa[['bookId', 'title', 'author', 'genres', 'description', 'rating', 'coverImg']]

        df_fa = fix_taaghche_image_urls(df_fa)

        df_fa['language'] = 'fa'
        df_fa['bookId'] = "fa_" + df_fa['bookId'].astype(str)
        dfs.append(df_fa)

    if not dfs:
        raise FileNotFoundError("No raw dataset files found.")

    df = pd.concat(dfs, ignore_index=True)
    initial_count = len(df)
    df.dropna(subset=['title'], inplace=True)
    df.drop_duplicates(subset=['bookId'], inplace=True)
    df = df[df['title'].notna() & (df['title'].str.strip() != '')]
    console.print(f"[yellow]Removed books with empty titles.[/yellow]")

    df['title'] = df['title'].fillna('')
    df['author'] = df['author'].fillna('Unknown')
    df['genres'] = df['genres'].fillna('[]')
    df['description'] = df['description'].fillna('')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
    df['coverImg'] = df['coverImg'].fillna('')

    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        console.print(f"[yellow]Dropped {dropped_count} invalid/duplicate rows.[/yellow]")

    valid_rows = []
    unique_titles = set()
    unique_authors = set()
    unique_genres = set()

    with Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}[/bold blue]"), BarColumn(),
                  TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("Processing books", total=len(df))
        for _, row in df.iterrows():
            lang = row['language']

            if lang == 'fa':
                c_title = cleaner.clean_persian_text_simple(row['title'])
                c_author = cleaner.clean_persian_text_simple(row['author'])
            else:
                c_title = cleaner.clean_english_text(row['title'])
                c_author = str(row['author']).strip().lower()

            c_genre = cleaner.clean_genres(row['genres'])
            c_desc = cleaner.clean_persian_text(row['description']) if lang == 'fa' else cleaner.clean_english_text(
                row['description'])

            if not c_desc and not c_genre:
                progress.update(task, advance=1)
                continue

            WEIGHTS = {'title': 2, 'author': 2, 'genre': 4, 'description': 1}
            soup_text = f"{(c_title + ' ') * WEIGHTS['title']} {(c_author + ' ') * WEIGHTS['author']} {(c_genre + ' ') * WEIGHTS['genre']} {c_desc}"

            if c_title: unique_titles.add(c_title)
            if c_author: unique_authors.add(c_author)
            if c_genre:
                unique_genres.update(c_genre.split())

            valid_rows.append({
                'bookId': row['bookId'],
                'title': row['title'],
                'author': row['author'],
                'genres': row['genres'],
                'description': row['description'],
                'rating': row['rating'],
                'coverImg': row['coverImg'],
                'language': lang,
                'clean_title': c_title,
                'clean_author': c_author,
                'clean_genres': c_genre,
                'clean_description': c_desc,
                'soup': soup_text.strip()
            })
            progress.update(task, advance=1)

    final_df = pd.DataFrame(valid_rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False, encoding='utf-8')
    console.print(f"[bold green]Preprocessing finished! Saved {len(final_df)} valid books to {output_path}[/bold green]")

    vocab_path = output_path.parent / "clean_vocabulary.json"
    vocabulary = {
        "genres": sorted(list(unique_genres)),
        "authors": sorted(list(unique_authors)),
        "titles": sorted(list(unique_titles)),
        "metadata": {
            "total_genres": len(unique_genres),
            "total_authors": len(unique_authors),
            "total_titles": len(unique_titles),
            "total_books": len(final_df)
        }
    }

    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocabulary, f, ensure_ascii=False, indent=2)

    console.print(f"[bold green]Clean vocabulary saved to {vocab_path}[/bold green]")

    return final_df


if __name__ == "__main__":
    console.print("[bold magenta]Starting preprocessing script...[/bold magenta]")
    preprocess_dataset()
    console.print("[bold magenta]Script execution completed.[/bold magenta]")
