# movie_loader.py
import os
import json
import subprocess
import pandas as pd
import requests
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# -----------------------------
# Config
# -----------------------------
RAW_DATASET = "movies_metadata.csv"
SAMPLE_LIMIT = 3000  # adjust if Streamlit Cloud memory is tight

# ===============================
# Load API keys from Streamlit secrets
# ===============================
try:
    TMDB_API_KEY = st.secrets["tmdb"]["api_key"]
    KAGGLE_USERNAME = st.secrets["kaggle"]["username"]
    KAGGLE_KEY = st.secrets["kaggle"]["key"]

    os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
    os.environ["KAGGLE_KEY"] = KAGGLE_KEY
except Exception:
    TMDB_API_KEY = None


# -----------------------------
# Download dataset from Kaggle
# -----------------------------
def download_dataset_if_missing():
    if os.path.exists(RAW_DATASET):
        return

    st.info("📥 Dataset downloading from Kaggle...")
    cmd = [
        "kaggle", "datasets", "download", "-d",
        "rounakbanik/the-movies-dataset",
        "-p", ".", "--unzip"
    ]
    subprocess.run(cmd, check=True)


# -----------------------------
# Load movies
# -----------------------------
@st.cache_data(show_spinner=False)
def load_movies(sample_limit: int = SAMPLE_LIMIT) -> pd.DataFrame:
    if not os.path.exists(RAW_DATASET):
        download_dataset_if_missing()

    movies = pd.read_csv(RAW_DATASET, low_memory=False)

    # ensure required columns exist
    required = ["id", "title", "overview"]
    for col in required:
        if col not in movies.columns:
            raise FileNotFoundError(f"❌ Required column '{col}' not found in dataset.")

    movies = movies[required].dropna().drop_duplicates().reset_index(drop=True)

    # cast id to int if possible
    try:
        movies["id"] = movies["id"].astype(int)
    except Exception:
        pass

    # reduce size for safety
    if len(movies) > sample_limit:
        movies = movies.head(sample_limit).reset_index(drop=True)

    return movies


# -----------------------------
# Fetch movie details from TMDb
# -----------------------------
def fetch_movie_details(movie_id):
    if TMDB_API_KEY is None:
        raise RuntimeError("❌ TMDB API key missing. Set it in Streamlit secrets.")

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US", "append_to_response": "credits"}
    r = requests.get(url, params=params, timeout=10)

    if r.status_code != 200:
        return {
            "title": f"ID {movie_id}",
            "poster_url": "",
            "rating": "N/A",
            "overview": "Details not available.",
            "link": f"https://www.themoviedb.org/movie/{movie_id}",
            "credits": "Not available"
        }

    data = r.json()
    title = data.get("title") or data.get("original_title") or f"ID {movie_id}"
    poster_path = data.get("poster_path")
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview") or "No overview available."
    link = f"https://www.themoviedb.org/movie/{movie_id}"

    # credits
    credits_info = data.get("credits", {})
    cast = [c.get("name") for c in credits_info.get("cast", [])[:3] if c.get("name")]
    directors = [c.get("name") for c in credits_info.get("crew", []) if c.get("job") == "Director"]

    credits_text = []
    if cast:
        credits_text.append("Cast: " + ", ".join(cast))
    if directors:
        credits_text.append("Director: " + ", ".join(directors))
    credits_text = " | ".join(credits_text) if credits_text else "Not available"

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

    return {
        "title": title,
        "poster_url": poster_url,
        "rating": rating,
        "overview": overview,
        "link": link,
        "credits": credits_text
    }


# -----------------------------
# Recommend top N using TF-IDF
# -----------------------------
def recommend(selected_title: str, movies: pd.DataFrame, top_n: int = 5):
    if selected_title not in movies["title"].values:
        return []

    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    docs = movies["overview"].fillna("").astype(str).values
    tfidf_matrix = tfidf.fit_transform(docs)

    idx = movies[movies["title"] == selected_title].index
    if len(idx) == 0:
        return []
    idx = idx[0]

    sim = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()

    # top similar excluding itself
    top_indices = sim.argsort()[::-1]
    top_indices = [i for i in top_indices if i != idx][:top_n]

    recs = []
    for i in top_indices:
        movie_id = movies.iloc[i]["id"]
        recs.append(fetch_movie_details(movie_id))

    return recs


