# movie_loader.py
import os
import pandas as pd
import requests

TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # <- set this in Streamlit Secrets / env vars

def load_movies(csv_path="movies_metadata.csv"):
    """Return a DataFrame with 'id' and 'title' columns."""
    df = pd.read_csv(csv_path, low_memory=False)
    df = df[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return df

def fetch_movie_details(movie_id, api_key=None):
    """Return (title, poster_url, rating, overview). Never do network on import."""
    api_key = api_key or TMDB_API_KEY
    if not api_key:
        return "Unknown", "", "N/A", "TMDB_API_KEY not set."

    # Ensure movie_id is string or int that TMDB accepts
    try:
        movie_id_str = str(int(movie_id))
    except Exception:
        movie_id_str = str(movie_id)

    url = f"https://api.themoviedb.org/3/movie/{movie_id_str}?api_key={api_key}&language=en-US"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        title = data.get("title", "Unknown Title")
        poster_path = data.get("poster_path") or ""
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No overview available.")
        return title, poster_url, rating, overview
    except Exception as e:
        return "Unknown", "", "N/A", f"Details not available ({e})"
