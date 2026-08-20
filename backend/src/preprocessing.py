import pandas as pd
import ast
import re
import string
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from src.config import RAW_DATA_PATH_EN, RAW_DATA_PATH_FA, PROCESSED_DATA_PATH
import logging

console = Console()

try:
    from hazm import Normalizer, StopwordRemover, Lemmatizer

    HAZM_AVAILABLE = True
    console.print("[bold green]Hazm library loaded successfully.[/bold green]")
except ImportError:
    HAZM_AVAILABLE = False
    console.print(
        "[bold yellow]WARNING: Hazm library not found. Persian text cleaning will use basic rules.[/bold yellow]")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    "هر", "است", "شد", "بود", "کرد", "می", "داشت", "وی", "و", "ای", "نه", "بله"
}


class TextCleaner:
    def __init__(self):
        if HAZM_AVAILABLE:
            self.normalizer = Normalizer()
            self.stopword_remover = StopwordRemover()
            self.lemmatizer = Lemmatizer()

    def clean_english_text(self, text: str) -> str:
        if pd.isna(text) or not text:
            return ""
        text = str(text).lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = text.split()
        tokens = [w for w in tokens if w not in ENGLISH_STOPWORDS and len(w) > 2]
        return " ".join(tokens)

    def clean_persian_text(self, text: str) -> str:
        if pd.isna(text) or not text:
            return ""
        text = str(text)
        if HAZM_AVAILABLE:
            text = self.normalizer.normalize(text)
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\d+', '', text)
            tokens = text.split()
            tokens = self.stopword_remover.remove(tokens)
            tokens = [self.lemmatizer.lemmatize(w) for w in tokens if len(w) > 2]
            return " ".join(tokens)
        else:
            text = text.replace("ي", "ی").replace("ك", "ک")
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\d+', '', text)
            tokens = text.split()
            tokens = [w for w in tokens if w not in PERSIAN_STOPWORDS and len(w) > 2]
            return " ".join(tokens)

    def clean_genres(self, genre_str: str) -> str:
        if pd.isna(genre_str) or not genre_str:
            return ""
        try:
            genres = ast.literal_eval(genre_str)
            if isinstance(genres, list):
                return " ".join([str(g).replace(" ", "").lower() for g in genres if g])
        except (ValueError, SyntaxError):
            return str(genre_str).replace(" ", "").lower().strip('[]')
        return ""


def load_and_standardize_datasets() -> tuple:
    dfs = []
    cleaner = TextCleaner()

    console.print(f"\n[cyan]Checking English dataset path:[/cyan] {RAW_DATA_PATH_EN}")
    if RAW_DATA_PATH_EN.exists():
        console.print("[green]Loading English raw dataset...[/green]")
        try:
            df_en = pd.read_csv(RAW_DATA_PATH_EN, encoding='utf-8')
            cols_en = {'bookId': 'bookId', 'title': 'title', 'author': 'author', 'genres': 'genres',
                       'description': 'description', 'rating': 'rating', 'coverImg': 'coverImg'}
            df_en = df_en[[c for c in cols_en.keys() if c in df_en.columns]].rename(columns=cols_en)
            df_en['language'] = 'en'
            df_en['bookId'] = "en_" + df_en['bookId'].astype(str)
            dfs.append(df_en)
            console.print(f"[green]Loaded {len(df_en)} English books.[/green]")
        except Exception as e:
            console.print(f"[bold red]Error loading English dataset: {e}[/bold red]")
    else:
        console.print("[yellow]English dataset NOT found at the specified path.[/yellow]")

    console.print(f"\n[cyan]Checking Persian dataset path:[/cyan] {RAW_DATA_PATH_FA}")
    if RAW_DATA_PATH_FA.exists():
        console.print("[green]Loading Persian raw dataset...[/green]")
        try:
            df_fa = pd.read_csv(RAW_DATA_PATH_FA, encoding='utf-8')
            cols_fa = {'book_id': 'bookId', 'title': 'title', 'author_name': 'author', 'categories': 'genres',
                       'description': 'description', 'rating': 'rating', 'coveruri': 'coverImg'}
            df_fa = df_fa[[c for c in cols_fa.keys() if c in df_fa.columns]].rename(columns=cols_fa)
            df_fa['language'] = 'fa'
            df_fa['bookId'] = "fa_" + df_fa['bookId'].astype(str)
            dfs.append(df_fa)
            console.print(f"[green]Loaded {len(df_fa)} Persian books.[/green]")
        except Exception as e:
            console.print(f"[bold red]Error loading Persian dataset: {e}[/bold red]")
    else:
        console.print("[yellow]Persian dataset NOT found at the specified path.[/yellow]")

    if not dfs:
        raise FileNotFoundError(
            f"No raw dataset files found. Please check these paths:\n1. {RAW_DATA_PATH_EN}\n2. {RAW_DATA_PATH_FA}")

    return pd.concat(dfs, ignore_index=True), cleaner


def preprocess_dataset(output_path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    console.print(Panel("[bold magenta]Starting Dataset Preprocessing[/bold magenta]", border_style="cyan", width=50))

    df, cleaner = load_and_standardize_datasets()
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

    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        console.print(f"[yellow]Dropped {dropped_count} invalid/duplicate rows.[/yellow]")

    clean_titles, clean_authors, clean_genres_list, clean_descriptions, soups = [], [], [], [], []

    console.print("\n[cyan]Processing text data...[/cyan]")
    with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            console=console,
            expand=True
    ) as progress:
        task = progress.add_task("Processing books", total=len(df))

        for idx, row in df.iterrows():
            lang = row['language']
            c_title = cleaner.clean_persian_text(row['title']) if lang == 'fa' else cleaner.clean_english_text(
                row['title'])
            c_author = cleaner.clean_persian_text(row['author']) if lang == 'fa' else row['author'].replace(" ",
                                                                                                            "").lower()
            c_genre = cleaner.clean_genres(row['genres'])
            c_desc = cleaner.clean_persian_text(row['description']) if lang == 'fa' else cleaner.clean_english_text(
                row['description'])

            clean_titles.append(c_title)
            clean_authors.append(c_author)
            clean_genres_list.append(c_genre)
            clean_descriptions.append(c_desc)

            soup_text = f"{(c_title + ' ') * 3}{(c_author + ' ') * 3}{(c_genre + ' ') * 2}{c_desc}"
            soups.append(soup_text.strip())

            progress.update(task, advance=1)

    df['clean_title'] = clean_titles
    df['clean_author'] = clean_authors
    df['clean_genres'] = clean_genres_list
    df['clean_description'] = clean_descriptions
    df['soup'] = soups

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')

    console.print("\n[bold green]Preprocessing finished successfully![/bold green]")
    console.print(f"[cyan]Total valid books ready:[/cyan] [bold]{len(df)}[/bold]")
    console.print(f"[cyan]Saved to:[/cyan] [underline]{output_path}[/underline]\n")

    return df


if __name__ == "__main__":
    console.print("[bold magenta]Starting preprocessing script...[/bold magenta]")
    preprocess_dataset()
    console.print("[bold magenta]Script execution completed.[/bold magenta]")
