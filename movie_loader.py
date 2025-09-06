import pandas as pd
import requests
import os

# ===============================
# TMDB API Key (from Streamlit Secrets or fallback)
# ===============================
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "0d309fbe7061ac46435369d2349288ba")

# ===============================
# Load Movies
# ===============================
def load_movies():
    try:
        movies = pd.read_csv("movies_metadata.csv", low_memory=False)
    except FileNotFoundError:
        raise FileNotFoundError("❌ movies_metadata.csv not found. Make sure Kaggle dataset download works.")

    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Fetch Poster & Details
# ===============================
def fetch_movie_details(movie_id, api_key=TMDB_API_KEY):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get("poster_path", "")
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No overview available.")
        title = data.get("title", "Unknown Title")

        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        return title, poster_url, rating, overview

    return "Unknown", "", "N/A", "Details not available."

