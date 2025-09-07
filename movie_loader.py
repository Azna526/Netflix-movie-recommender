import os
import pandas as pd
import pickle
import requests

# TMDB key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# -------------------------------
# Load preprocessed movies
# -------------------------------
def load_movies():
    return pd.read_csv("processed_movies.csv")

def load_similarity():
    with open("similarity.pkl", "rb") as f:
        return pickle.load(f)

# -------------------------------
# Fetch TMDb details
# -------------------------------
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        poster = f"https://image.tmdb.org/t/p/w500{data.get('poster_path','')}" if data.get("poster_path") else ""
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No overview available.")
        link = f"https://www.themoviedb.org/movie/{movie_id}"
        return poster, rating, overview, link
    return "", "N/A", "Details not available.", ""
