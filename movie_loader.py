import os
import pandas as pd
import pickle
import requests
import json
import streamlit as st

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_FILE = os.path.join(BASE_DIR, "movies_metadata.csv")
SIMILARITY_FILE = os.path.join(BASE_DIR, "similarity.pkl")
POSTERS_CACHE = os.path.join(BASE_DIR, "posters_cache.json")

# --- TMDB API ---
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

def fetch_poster(movie_id):
    """Fetch poster URL from TMDB API"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

def load_posters_cache():
    """Load cached poster URLs if available"""
    if os.path.exists(POSTERS_CACHE):
        with open(POSTERS_CACHE, "r") as f:
            return json.load(f)
    return {}

def save_posters_cache(cache):
    """Save poster URLs cache to file"""
    with open(POSTERS_CACHE, "w") as f:
        json.dump(cache, f)

def load_datasets():
    """Load movies, similarity matrix, and poster URLs"""
    # Movies
    movies = pd.read_csv(MOVIES_FILE, low_memory=False)

    # Similarity
    with open(SIMILARITY_FILE, "rb") as f:
        similarity = pickle.load(f)

    # Posters cache
    posters_cache = load_posters_cache()

    # Ensure poster URLs for all movies
    if "id" in movies.columns:
        for _, row in movies.iterrows():
            movie_id = str(row["id"])
            if movie_id not in posters_cache:
                poster_url = fetch_poster(movie_id)
                if poster_url:
                    posters_cache[movie_id] = poster_url
        save_posters_cache(posters_cache)

    print("✅ Datasets loaded")
    print("Movies:", movies.shape)
    print("Similarity:", similarity.shape)
    print("Posters cached:", len(posters_cache))

    return movies, similarity, posters_cache


if __name__ == "__main__":
    movies, similarity, posters = load_datasets()
    print("Sample poster:", list(posters.items())[:5])
