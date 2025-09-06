import os
import subprocess
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATASET_FILE = "movies_metadata.csv"
KAGGLE_DATASET = "rounakbanik/the-movies-dataset"

@st.cache_data(show_spinner=False)
def load_movies():
    """
    Load movies from movies_metadata.csv (if present).
    If not present, try to download from Kaggle using Streamlit secrets.
    Returns a cleaned DataFrame with columns: id (TMDB id), title, overview
    """
    if not os.path.exists(DATASET_FILE):
        # optional fallback: download from Kaggle CLI if secrets are set
        try:
            os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
            os.environ["KAGGLE_KEY"] = st.secrets["KAGGLE_KEY"]
            subprocess.run(
                ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "--unzip", "-p", "."],
                check=True
            )
        except Exception as e:
            raise FileNotFoundError(
                f"{DATASET_FILE} not found in repo and Kaggle download failed. "
                f"Add the CSV to your repo or set KAGGLE_USERNAME/KAGGLE_KEY in secrets. Details: {e}"
            )

    df = pd.read_csv(DATASET_FILE, low_memory=False)

    # pick the available title column, standardize to 'title'
    title_col = "title" if "title" in df.columns else ("original_title" if "original_title" in df.columns else None)
    if title_col is None:
        raise ValueError("CSV must contain 'title' or 'original_title'.")
    if "overview" not in df.columns:
        raise ValueError("CSV must contain 'overview'.")
    if "id" not in df.columns:
        raise ValueError("CSV must contain 'id' (TMDB movie id).")

    df = df[["id", title_col, "overview"]].rename(columns={title_col: "title"}).dropna(subset=["title", "overview"])

    # Coerce TMDB ids -> integers, drop invalid rows
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    # Remove duplicate titles
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)
    return df

@st.cache_resource(show_spinner=False)
def build_text_model(movies):
    """Build TF-IDF + cosine similarity on overview; returns similarity matrix."""
    tfidf = TfidfVectorizer(stop_words="english")
    mat = tfidf.fit_transform(movies["overview"].astype(str))
    sim = cosine_similarity(mat, mat)
    return sim

def similar_by_title(title, movies, similarity, top_n=5):
    """Return indices (row numbers) of the top_n similar movies for a given title."""
    indexer = pd.Series(movies.index, index=movies["title"].str.lower()).drop_duplicates()
    key = str(title).lower()
    if key not in indexer:
        return []
    idx = indexer[key]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return [i for i, _ in scores]
