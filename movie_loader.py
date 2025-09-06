import os
import pandas as pd
import pickle
import requests

# Your TMDB key
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"

# ===============================
# Load Movies
# ===============================
def load_movies():
    dataset_path = "movies_metadata.csv"

    # If file not present, download via Kaggle API
    if not os.path.exists(dataset_path):
        import kaggle
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            "rounakbanik/the-movies-dataset",
            path=".",
            unzip=True
        )

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    with open("similarity.pkl", "rb") as f:
        return pickle.load(f)

# ===============================
# Fetch Poster, Details & Link
# ===============================
def fetch_movie_details(movie_id, api_key=TMDB_API_KEY):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={
