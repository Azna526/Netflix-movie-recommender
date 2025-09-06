import os
import pandas as pd
import requests
import kaggle

# ===============================
# API Keys (from Streamlit secrets)
# ===============================
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")

DATASET_PATH = "movies_metadata.csv"

# ===============================
# Download Kaggle Dataset
# ===============================
def download_dataset():
    if not os.path.exists(DATASET_PATH):
        print("📥 Downloading dataset from Kaggle...")

        # Set Kaggle credentials dynamically
        os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
        os.environ["KAGGLE_KEY"] = KAGGLE_KEY

        kaggle.api.authenticate()

        kaggle.api.dataset_download_files(
            "rounakbanik/the-movies-dataset",
            path=".",
            unzip=True
        )
        print("✅ Dataset downloaded and extracted.")

# ===============================
# Load Movies
# ===============================
def load_movies():
    if not os.path.exists(DATASET_PATH):
        download_dataset()

    movies = pd.read_csv(DATASET_PATH, low_memory=False)
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
