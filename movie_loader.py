import os
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess

DATASET_FILE = "movies_metadata.csv"
KAGGLE_DATASET = "rounakbanik/the-movies-dataset"

@st.cache_data(show_spinner=False)
def load_movies():
    """Load and clean movies metadata from CSV (local or Kaggle)."""
    if not os.path.exists(DATASET_FILE):
        # Download from Kaggle if not found locally
        try:
            os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
            os.environ["KAGGLE_KEY"] = st.secrets["KAGGLE_KEY"]
            subprocess.run(
                ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "--unzip", "-p", "."],
                check=True
            )
        except Exception as e:
            raise FileNotFoundError(
                f"{DATASET_FILE} missing and Kaggle download failed: {e}"
            )

    df = pd.read_csv(DATASET_FILE, low_memory=False)

    # Pick title column
    title_col = "title" if "title" in df.columns else "original_title"
    df = df[["id", title_col, "overview"]].rename(columns={title_col: "title"}).dropna()

    # Ensure TMDB IDs are integers
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    # Remove duplicate titles
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)
    return df

@st.cache_resource(show_spinner=False)
def build_text_model(movies):
    """Build TF-IDF + cosine similarity model."""
    tfidf = TfidfVectorizer(stop_words="english")
    mat = tfidf.fit_transform(movies["overview"].astype(str))
    return cosine_similarity(mat, mat)

def similar_by_title(title, movies, similarity, top_n=5):
    """Return indices of similar movies given a title."""
    indexer = pd.Series(movies.index, index=movies["title"].str.lower()).drop_duplicates()
    key = str(title).lower()
    if key not in indexer:
        return []
    idx = indexer[key]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return [i for i, _ in scores]
