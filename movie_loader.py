import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cached files
MOVIES_PATH = "processed_movies.csv"
SIM_PATH = "similarity.pkl"
RAW_DATASET = "movies_metadata.csv"  # from Kaggle "The Movies Dataset"

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_PAGE_BASE = "https://www.themoviedb.org/movie/"

def _ensure_columns(df, cols_with_defaults):
    # make sure required columns exist; create empty ones if missing
    for col, default in cols_with_defaults.items():
        if col not in df.columns:
            df[col] = default
    return df

def generate_data():
    if not os.path.exists(RAW_DATASET):
        raise FileNotFoundError(
            f"{RAW_DATASET} not found. Add it to the repo OR provide {MOVIES_PATH} and {SIM_PATH}."
        )

    movies = pd.read_csv(RAW_DATASET, low_memory=False)

    # columns we’ll keep/use
    movies = _ensure_columns(
        movies,
        {
            "id": None,
            "title": "",
            "original_title": "",
            "overview": "",
            "poster_path": "",
            "vote_average": 0.0,
            "homepage": "",
        },
    )

    # clean/coerce
    movies["title"] = movies["title"].fillna(movies["original_title"]).fillna("")
    movies["overview"] = movies["overview"].fillna("")
    movies["vote_average"] = pd.to_numeric(movies["vote_average"], errors="coerce").fillna(0.0)

    # TMDb ids can be messy in this dataset; coerce to numeric and drop nulls
    movies["id"] = pd.to_numeric(movies["id"], errors="coerce")
    movies = movies.dropna(subset=["id"]).reset_index(drop=True)

    # build URLs
    def _poster_url(path):
        if isinstance(path, str) and path.strip():
            return f"{TMDB_IMAGE_BASE}{path}"
        return ""

    movies["poster_url"] = movies["poster_path"].apply(_poster_url)
    movies["tmdb_url"] = movies["id"].apply(lambda x: f"{TMDB_PAGE_BASE}{int(x)}")

    # compute TF-IDF similarity from overview text
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["overview"])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # persist a lean CSV the app needs
    out = movies[["id", "title", "overview", "poster_url", "vote_average", "tmdb_url"]].copy()
    out.rename(columns={"vote_average": "rating"}, inplace=True)
    out.to_csv(MOVIES_PATH, index=False)

    with open(SIM_PATH, "wb") as f:
        pickle.dump(similarity, f)

def load_movies():
    if not os.path.exists(MOVIES_PATH):
        generate_data()
    return pd.read_csv(MOVIES_PATH)

def load_similarity():
    if not os.path.exists(SIM_PATH):
        generate_data()
    with open(SIM_PATH, "rb") as f:
        return pickle.load(f)

def fetch_movie_details(title: str, movies: pd.DataFrame):
    """Return a dict with title, overview, poster_url, rating, link for a single movie."""
    if movies.empty:
        return None
    t = str(title).strip().lower()
    mask = movies["title"].str.lower() == t
    if not mask.any():
        # fallback: contains search
        mask = movies["title"].str.lower().str.contains(t, na=False)
        if not mask.any():
            return None
    row = movies[mask].iloc[0]
    return {
        "title": row["title"],
        "overview": row["overview"],
        "poster_url": row.get("poster_url", ""),
        "rating": float(row.get("rating", 0.0)),
        "link": row.get("tmdb_url", ""),
    }

def recommend(title: str, movies: pd.DataFrame, similarity, top_n: int = 5):
    """Return a list of dicts with details for the top-N similar movies."""
    if movies.empty:
        return []

    try:
        idx = movies[movies["title"].str.lower() == str(title).lower()].index[0]
    except IndexError:
        return []

    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1 : top_n + 1]

    recs = []
    for i, _ in scores:
        r = movies.iloc[i]
        recs.append(
            {
                "title": r["title"],
                "overview": r["overview"],
                "poster_url": r.get("poster_url", ""),
                "rating": float(r.get("rating", 0.0)),
                "link": r.get("tmdb_url", ""),
            }
        )
    return recs
