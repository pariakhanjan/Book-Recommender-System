"""
TF-IDF Vector Distinctiveness Analysis Script.

This script analyzes the quality of TF-IDF vectors by:
1. Finding exact duplicate vectors (books with identical content)
2. Calculating cosine similarity distribution to measure distinctiveness
3. Providing statistical insights about vector quality

Expected Results:
- Low number of exact duplicates (< 1% of dataset)
- Mean max similarity between 0.3-0.7 (indicating good distinctiveness)
- Most books should have unique semantic signatures
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import PROCESSED_DATA_PATH, TFIDF_MATRIX_PATH

console = Console()


def find_exact_duplicate_vectors(df, tfidf_matrix, sample_limit=2000):
    """
    Finds books that have exactly identical TF-IDF vectors.

    Uses hashing of non-zero elements to efficiently detect duplicates.
    Only checks first `sample_limit` books for performance.

    Args:
        df: DataFrame with book metadata
        tfidf_matrix: Sparse TF-IDF matrix
        sample_limit: Number of books to check (default 2000)

    Returns:
        Dictionary mapping vector hash to list of book indices
    """
    console.print(f"[cyan]Searching for exact duplicate TF-IDF vectors (checking first {sample_limit} books)...[/cyan]")

    duplicates = {}

    for i in range(min(sample_limit, tfidf_matrix.shape[0])):
        row = tfidf_matrix.getrow(i)
        # Create a hashable key from non-zero indices and rounded values
        key = (tuple(row.indices), tuple(np.round(row.data, 4)))

        if key in duplicates:
            duplicates[key].append(i)
        else:
            duplicates[key] = [i]

    # Filter to keep only groups with more than 1 book
    exact_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}

    return exact_duplicates


def analyze_similarity_distribution(df, tfidf_matrix, sample_size=500):
    """
    Calculates the distribution of cosine similarities for a random sample.

    For each book in the sample, finds the maximum similarity with any OTHER
    book in the dataset (excluding self-similarity).

    Args:
        df: DataFrame with book metadata
        tfidf_matrix: Sparse TF-IDF matrix
        sample_size: Number of books to sample (default 500)

    Returns:
        Array of max similarity scores for each sampled book
    """
    console.print(f"[cyan]Calculating cosine similarity distribution for {sample_size} random books...[/cyan]")

    # Set random seed for reproducibility
    np.random.seed(42)

    # Select a random sample of indices
    sample_indices = np.random.choice(tfidf_matrix.shape[0], sample_size, replace=False)
    sample_matrix = tfidf_matrix[sample_indices]

    # Calculate cosine similarity between sample and ALL books
    # Result shape: (sample_size, total_books)
    sim_matrix = cosine_similarity(sample_matrix, tfidf_matrix)

    # Find max similarity for each book against OTHER books
    max_sims = []
    for i in range(sample_size):
        # Get the row of similarities for this book
        sims = sim_matrix[i].copy()  # Make a copy to avoid modifying original

        # CRITICAL FIX: Set similarity with itself to -1
        # sample_indices[i] is the actual index in the full matrix
        sims[sample_indices[i]] = -1.0

        max_sims.append(np.max(sims))

    return np.array(max_sims)


def analyze_sample_books(df, tfidf_matrix, num_samples=5):
    """
    Shows detailed analysis for a few sample books.

    Args:
        df: DataFrame with book metadata
        tfidf_matrix: Sparse TF-IDF matrix
        num_samples: Number of sample books to analyze (default 5)
    """
    console.print(f"\n[cyan]Detailed analysis of {num_samples} sample books...[/cyan]\n")

    np.random.seed(123)
    sample_indices = np.random.choice(tfidf_matrix.shape[0], num_samples, replace=False)

    for idx in sample_indices:
        book = df.iloc[idx]
        vector = tfidf_matrix[idx]

        # Count non-zero elements
        num_features = vector.nnz

        # Find most similar book
        similarities = cosine_similarity(vector, tfidf_matrix).flatten()
        similarities[idx] = -1.0  # Exclude self
        most_similar_idx = np.argmax(similarities)
        most_similar_book = df.iloc[most_similar_idx]

        title = str(book.get('title', 'Unknown'))
        author = str(book.get('author', 'Unknown'))
        language = str(book.get('language', 'N/A'))
        genres = str(book.get('clean_genres', 'N/A'))
        similar_title = str(most_similar_book.get('title', 'Unknown'))

        # Replace string 'nan' with 'N/A' just in case
        if genres.lower() == 'nan':
            genres = 'N/A'

        console.print(f"📖 **{title}** by {author}")
        console.print(f"   ├─ Non-zero TF-IDF features: {num_features}")
        console.print(f"   ├─ Language: {language}")
        console.print(f"   ├─ Genres: {genres[:60]}...")
        console.print(
            f"   └─ Most similar: **{similar_title}** (similarity: {similarities[most_similar_idx]:.4f})")
        console.print()


def main():
    console.print("\n")
    console.print(Panel.fit(
        "[bold magenta]🔍 TF-IDF Vector Distinctiveness Analysis[/bold magenta]",
        border_style="magenta"
    ))
    console.print("\n")

    # 1. Load Data
    console.print("[cyan]Loading processed data and TF-IDF matrix...[/cyan]")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    tfidf_matrix = joblib.load(TFIDF_MATRIX_PATH)
    console.print(f"[green]Loaded {len(df)} books and matrix shape {tfidf_matrix.shape}.[/green]\n")

    # 2. Check for Exact Duplicates
    exact_dups = find_exact_duplicate_vectors(df, tfidf_matrix, sample_limit=2000)

    console.print(Panel.fit(
        f"[bold cyan]Exact Duplicate Vectors Found: {len(exact_dups)} groups (in first 2000 books)[/bold cyan]",
        border_style="cyan"
    ))

    if exact_dups:
        table = Table(title="Examples of Books with Identical Vectors", show_header=True, header_style="bold magenta")
        table.add_column("Group", style="cyan", width=5)
        table.add_column("Book Titles", width=80)

        for idx, (key, indices) in enumerate(list(exact_dups.items())[:5]):
            titles = [df.iloc[i]['title'] for i in indices]
            table.add_row(str(idx + 1), " | ".join(titles))

        console.print(table)
        console.print(
            "\n[yellow]Note: These books likely have identical or extremely similar cleaned descriptions.[/yellow]\n")
    else:
        console.print(
            "[bold green]No exact duplicate vectors found in sample! Every book has a unique TF-IDF signature.[/bold green]\n")

    # 3. Analyze Similarity Distribution
    max_sims = analyze_similarity_distribution(df, tfidf_matrix, sample_size=500)

    console.print(Panel.fit(
        "[bold cyan]Cosine Similarity Distribution (Max similarity to other books)[/bold cyan]",
        border_style="cyan"
    ))

    stats_table = Table(show_header=True, header_style="bold magenta")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", justify="right")
    stats_table.add_column("Interpretation", style="dim")

    mean_sim = np.mean(max_sims)
    median_sim = np.median(max_sims)

    stats_table.add_row(
        "Mean Max Similarity",
        f"{mean_sim:.4f}",
        "0.3-0.6 = Good distinctiveness" if 0.3 <= mean_sim <= 0.6 else "Check preprocessing"
    )
    stats_table.add_row(
        "Median Max Similarity",
        f"{median_sim:.4f}",
        "Should be < 0.7 for good separation"
    )
    stats_table.add_row(
        "Books with Sim > 0.90",
        f"{np.sum(max_sims > 0.90)} ({np.sum(max_sims > 0.90) / len(max_sims) * 100:.2f}%)",
        "Should be < 5% (likely duplicates)"
    )
    stats_table.add_row(
        "Books with Sim > 0.70",
        f"{np.sum(max_sims > 0.70)} ({np.sum(max_sims > 0.70) / len(max_sims) * 100:.2f}%)",
        "Related books/series"
    )
    stats_table.add_row(
        "Books with Sim < 0.50",
        f"{np.sum(max_sims < 0.50)} ({np.sum(max_sims < 0.50) / len(max_sims) * 100:.2f}%)",
        "Highly unique content"
    )

    console.print(stats_table)

    # 4. Detailed Sample Analysis
    analyze_sample_books(df, tfidf_matrix, num_samples=5)

    # 5. Final Assessment
    console.print("\n")
    if mean_sim < 0.7:
        console.print(Panel.fit(
            "[bold green]✅ TF-IDF vectors show GOOD distinctiveness![/bold green]\n"
            "Books are well-differentiated by their content.",
            border_style="green"
        ))
    elif mean_sim < 0.85:
        console.print(Panel.fit(
            "[bold yellow]⚠️ TF-IDF vectors show MODERATE distinctiveness.[/bold yellow]\n"
            "Consider improving text preprocessing or using more features.",
            border_style="yellow"
        ))
    else:
        console.print(Panel.fit(
            "[bold red]❌ TF-IDF vectors show POOR distinctiveness.[/bold red]\n"
            "Books are too similar. Check preprocessing and vectorizer parameters.",
            border_style="red"
        ))

    console.print("\n")


if __name__ == "__main__":
    main()
