# movie_loader.py
import os
import json
import pickle
import subprocess
import pandas as pd
import requests
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# -----------------------------
# Config - tweak SAMPLE_LIMIT to control memory/time
# -----------------------------
RAW_DATASET = "movies_metadata.csv"       # filename inside dataset zip
SAMPLE_LIMIT = 3000                       # reduce if memory/time is a concern
TMDB_API_KEY = None

# read TMDB key from Streamlit secrets (fail early)
try:
    TMDB_API_KEY = st.secrets["tmdb"]["api_key"]
except Exception:
    # We'll raise later where needed
    TMDB_API_KEY = None


# -----------------------------
# Kaggle helpers
# -----------------------------
def _ensure_kaggle_json():
    """
    Writes ~/.kaggle/kaggle.json from Streamlit secrets so Kaggle API can authenticate.
    """
    try:
        kag = st.secrets["kaggle"]
        username = kag["username"]
        key = kag["key"]
    except Exception:
        raise RuntimeError("Missing Kaggle secrets (kaggle.username / kaggle.key).")

    kaggle_dir = os.path.expanduser("~/.kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    cred_path = os.path.join(kaggle_dir, "kaggle.json")

    # only write if missing or different
    data = {"username": username, "key": key}
    if not os.path.exists(cred_path):
        with open(cred_path, "w") as fh:
            json.dump(data, fh)
        os.chmod(cred_path, 0o600)


def _download_via_kaggle_api(dataset="rounakbanik/the-movies-dataset", path="."):
    """
    Prefer KaggleApi python client if available.
    """
    _ensure_kaggle_json()
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore
    except Exception as e:
        raise RuntimeError("Kaggle package not installed in environment.") from e

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset, path=path, unzip=True)


def _download_via_cli(dataset="rounakbanik/the-movies-dataset"):
    """
    Try the kaggle CLI (if installed). May fail on Streamlit Cloud if CLI not available.
    """
    cmd = ["kaggle", "datasets", "download", "-d", dataset, "-p", ".", "--unzip"]
    subprocess.run(cmd, check=True)


def download_dataset_if_missing():
    """
    Ensures RAW_DATASET exists - downloads using Kaggle API or CLI.
    """
    if os.path.exists(RAW_DATASET):
        return

    st.info("📥 Dataset not found locally — attempting to download from Kaggle...")
    last_exc = None
    # try python API first
    try:
        _download_via_kaggle_api()
        if os.path.exists(RAW_DATASET):
            return
    except Exception as e:
        last_exc = e

    # fallback to CLI
    try:
        _download_via_cli()
        if os.path.exists(RAW_DATASET):
            return
    except Exception as e:
        last_exc = e

    # final: tell user what to do
    raise RuntimeError(
        "Failed to download the Kaggle dataset. "
        "Either install Kaggle and set secrets, or upload the processed CSV to the repo / Streamlit files."
    ) from last_exc


# -----------------------------
# Load movies (processed) - cached
# -----------------------------
@st.cache_data(show_spinner=False)
def load_movies(sample_limit: int = SAMPLE_LIMIT) -> pd.DataFrame:
    """
    Returns a dataframe with columns: id (int), title (str), overview (str).
    If the raw dataset is missing it will try to download it from Kaggle using secrets.
    We limit to sample_limit rows for cloud runtime safety.
    """
    # ensure dataset exists
    if not os.path.exists(RAW_DATASET):
        download_dataset_if_missing()

    # load and sanitize
    movies = pd.read_csv(RAW_DATASET, low_memory=False)
    # keep only basic columns and drop NA
    for col in ["id", "title", "overview"]:
        if col not in movies.columns:
            raise FileNotFoundError(f"Required column '{col}' not found in raw dataset.")

    movies = movies[["id", "title", "overview"]].dropna().drop_duplicates().reset_index(drop=True)

    # cast id as int when possible (TMDb expects id as integer)
    try:
        movies["id"] = movies["id"].astype(int)
    except Exception:
        # keep as-is if it fails
        pass

    # limit size for cloud runtime
    if len(movies) > sample_limit:
        movies = movies.head(sample_limit).reset_index(drop=True)

    return movies


# -----------------------------
# Fetch movie details from TMDb
# -----------------------------
def fetch_movie_details(movie_id):
    """
    Returns a dict with keys:
      title, poster_url, rating, overview, link, credits
    """
    if TMDB_API_KEY is None:
        raise RuntimeError("TMDB API key missing. Set secrets['tmdb']['api_key'].")

    # call TMDb movie endpoint with credits appended
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US", "append_to_response": "credits"}
    r = requests.get(url, params=params, timeout=10)

    if r.status_code != 200:
        # return a consistent structure on failure
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

    # credits (top 3 cast + director(s))
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
# Recommend top N using TF-IDF (computed on the loaded sample)
# -----------------------------
def recommend(selected_title: str, movies: pd.DataFrame, top_n: int = 5):
    """
    returns a list of dicts (each dict = fetch_movie_details output) for top_n similar movies.
    similarity calculated on the 'overview' column using TF-IDF + cosine similarity.
    """
    if selected_title not in movies["title"].values:
        return []

    # prepare tfidf matrix (fit on the sample)
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    docs = movies["overview"].fillna("").astype(str).values
    tfidf_matrix = tfidf.fit_transform(docs)

    # find the index of the selected movie (case-sensitive match used upstream)
    idx = movies[movies["title"] == selected_title].index
    if len(idx) == 0:
        return []
    idx = idx[0]

    # compute cosine similarities to the selected movie (fast with linear_kernel)
    sim = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()

    # get top indices excluding itself
    top_indices = sim.argsort()[::-1]  # descending
    # remove selected itself
    top_indices = [i for i in top_indices if i != idx][:top_n]

    recs = []
    for i in top_indices:
        movie_id = movies.iloc[i]["id"]
        recs.append(fetch_movie_details(movie_id))

    return recs
