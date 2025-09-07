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
RAW_DATASET = "movies_metadata.csv"   # filename from Kaggle dataset
SAMPLE_LIMIT = 3000                   # reduce if memory is a concern
TMDB_API_KEY = None

# read TMDB key from Streamlit secrets
try:
    TMDB_API_KEY = st.secrets["tmdb"]["api_key"]
except Exception:
    TMDB_API_KEY = None


# -----------------------------
# Kaggle helpers
# -----------------------------
def _ensure_kaggle_json():
    """Writes ~/.kaggle/kaggle.json from Streamlit secrets."""
    try:
        kag = st.secrets["kaggle"]
        username = kag["username"]
        key = kag["key"]
    except Exception:
        raise RuntimeError("Missing Kaggle secrets (kaggle.username / kaggle.key).")

    kaggle_dir = os.path.expanduser("~/.kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    cred_path = os.path.join(kaggle_dir, "kaggle.json")

    data = {"username": username, "key": key}
    if not os.path.exists(cred_path):
        with open(cred_path, "w") as fh:
            json.dump(data, fh)
        os.chmod(cred_path, 0o600)


def _download_via_kaggle_api(dataset="rounakbanik/the-movies-dataset", path="."):
    """Try using Kaggle API client."""
    _ensure_kaggle_json()
    from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset, path=path, unzip=True)


def _download_via_cli(dataset="rounakbanik/the-movies-dataset"):
    """Fallback to Kaggle CLI."""
    cmd = ["kaggle", "datasets", "download", "-d", dataset, "-p", ".", "--unzip"]
    subprocess.run(cmd, check=True)


def download_dataset_if_missing():
    """Ensures RAW_DATASET exists - downloads using Kaggle API or CLI."""
    if os.path.exists(RAW_DATASET):
        return
    st.info("📥 Dataset attempting to download from Kaggle...")
    try:
        _download_via_kaggle_api()
    except Exception:
        _download_via_cli()
    if not os.path.exists(RAW_DATASET):
        raise FileNotFoundError(f"{RAW_DATASET} not found even after Kaggle download.")


# -----------------------------
# Load movies (cached)
# -----------------------------
@st.cache_data(show_spinner=False)
def load_movies(sample_limit: int = SAMPLE_LIMIT) -> pd.DataFrame:
    """Load movies with id, title, overview (limited for performance)."""
    if not os.path.exists(RAW_DATASET):
        download_dataset_if_missing()

    movies = pd.read_csv(RAW_DATASET, low_memory=False)
    movies = movies[["id", "title", "overview"]].dropna().drop_duplicates().reset_index(drop=True)

    try:
        movies["id"] = movies["id"].astype(int)
    except Exception:
        pass

    if len(movies) > sample_limit:
        movies = movies.head(sample_limit).reset_index(drop=True)

    return movies


# -----------------------------
# Fetch movie details from TMDb
# -----------------------------
def fetch_movie_details(movie_id: int):
    """Return dict with title, poster_url, rating, overview, link, credits."""
    if TMDB_API_KEY is None:
        raise RuntimeError("TMDB API key missing. Set secrets['tmdb']['api_key'].")

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
            "credits": "Not available",
        }

    data = r.json()
    title = data.get("title") or data.get("original_title") or f"ID {movie_id}"
    poster_path = data.get("poster_path")
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview") or "No overview available."
    link = f"https://www.themoviedb.org/movie/{movie_id}"

    credits_info = data.get("credits", {})
    cast = [c.get("name") for c in credits_info.get("cast", [])[:3] if c.get("name")]
    directors = [c.get("name") for c in credits_info.get("crew", []) if c.get("job") == "Director"]

    credits_text = ""
    if cast:
        credits_text += "Cast: " + ", ".join(cast)
    if directors:
        credits_text += (" | " if credits_text else "") + "Director: " + ", ".join(directors)
    if not credits_text:
        credits_text = "Not available"

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

    return {
        "title": title,
        "poster_url": poster_url,
        "rating": rating,
        "overview": overview,
        "link": link,
        "credits": credits_text,
    }


# -----------------------------
# Build TF-IDF matrix (cached once per session)
# -----------------------------
@st.cache_resource(show_spinner=False)
def build_tfidf_matrix(movies: pd.DataFrame):
    """Build and cache TF-IDF matrix for overviews."""
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    docs = movies["overview"].fillna("").astype(str).values
    tfidf_matrix = tfidf.fit_transform(docs)
    return tfidf_matrix


# -----------------------------
# Recommend top N movies
# -----------------------------
def recommend(selected_title: str, movies: pd.DataFrame, top_n: int = 5):
    """Return list of dicts for top_n similar movies."""
    if selected_title not in movies["title"].values:
        return []

    tfidf_matrix = build_tfidf_matrix(movies)

    idx = movies[movies["title"] == selected_title].index
    if len(idx) == 0:
        return []
    idx = idx[0]

    sim = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()
    top_indices = sim.argsort()[::-1]
    top_indices = [i for i in top_indices if i != idx][:top_n]

    recs = []
    for i in top_indices:
        movie_id = movies.iloc[i]["id"]
        recs.append(fetch_movie_details(movie_id))

    return recs
