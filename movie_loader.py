# movie_loader.py
import os
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

POSTER_BASE = "https://image.tmdb.org/t/p/w342"
PLACEHOLDER = "https://via.placeholder.com/342x513?text=No+Image"

@st.cache_data(show_spinner="Loading movie CSVs…")
def load_movies() -> pd.DataFrame:
    """Load and clean the CSVs. Requires movies_metadata.csv and links_small.csv in repo root."""
    meta_path = "movies_metadata.csv"
    links_path = "links_small.csv"

    if not os.path.exists(meta_path) or not os.path.exists(links_path):
        raise FileNotFoundError(
            "CSV files not found. Make sure movies_metadata.csv and links_small.csv "
            "are committed to your repo (same folder as app.py)."
        )

    meta = pd.read_csv(meta_path, low_memory=False)[["id", "title", "overview", "poster_path"]]
    links = pd.read_csv(links_path)  # ~9k movies, perfect for Streamlit Cloud

    # numeric ids for a clean join
    meta["id"] = pd.to_numeric(meta["id"], errors="coerce")
    links["tmdbId"] = pd.to_numeric(links["tmdbId"], errors="coerce")

    # keep only titles that appear in links_small (smaller, faster)
    df = links.merge(meta, left_on="tmdbId", right_on="id", how="left")

    # basic cleanup
    df = df.dropna(subset=["title"]).drop_duplicates(subset=["title"]).reset_index(drop=True)
    df["overview"] = df["overview"].fillna("")
    df["poster_url"] = df["poster_path"].apply(
        lambda p: f"{POSTER_BASE}{p}" if isinstance(p, str) and p.strip() else PLACEHOLDER
    )

    # Index by lowercase title for reliable lookup
    df["title_lc"] = df["title"].str.lower()
    return df[["title", "title_lc", "overview", "poster_url"]]


@st.cache_resource(show_spinner="Building text model (first run only)…")
def build_text_model(df: pd.DataFrame):
    """Create TF-IDF vectors from overviews and cache the matrix/model."""
    vectorizer = TfidfVectorizer(stop_words="english", min_df=2)
    matrix = vectorizer.fit_transform(df["overview"])
    return vectorizer, matrix


def similar_by_title(df: pd.DataFrame, matrix, title: str, topn: int = 5):
    """Return a list of dicts: [{title, poster_url}, …] for the most similar movies."""
    if not title:
        return []

    title_lc = title.lower()
    matches = df.index[df["title_lc"] == title_lc].tolist()
    if not matches:
        return []

    idx = matches[0]
    sims = linear_kernel(matrix[idx], matrix).ravel()

    # top indices sorted by similarity (skip self)
    top = sims.argsort()[::-1]
    top = [i for i in top if i != idx][:topn]

    if not top:
        return []

    recs = df.loc[top, ["title", "poster_url"]].fillna(PLACEHOLDER)
    return recs.to_dict("records")
