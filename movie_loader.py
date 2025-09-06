import os
import pandas as pd
import requests
from kaggle.api.kaggle_api_extended import KaggleApi

# ===============================
# Keys
# ===============================
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"
KAGGLE_USERNAME = "aznabanu"
KAGGLE_KEY = "efea932e6c849dc66edb596c04eb849d"

# ===============================
# Download Dataset (Kaggle)
# ===============================
def download_dataset():
    DATA_DIR = "data"
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Configure kaggle.json on the fly
    kaggle_dir = os.path.join(os.path.expanduser("~"), ".kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    kaggle_json = os.path.join(kaggle_dir, "kaggle.json")
    with open(kaggle_json, "w") as f:
        f.write(f'{{"username":"{KAGGLE_USERNAME}","key":"{KAGGLE_KEY}"}}')
    os.chmod(kaggle_json, 0o600)

    api = KaggleApi()
    api.authenticate()

    dataset = "rounakbanik/the-movies-dataset"
    api.dataset_download_files(dataset, path=DATA_DIR, unzip=True)

# ===============================
# Load Movies
# ===============================
def load_movies():
    DATA_DIR = "data"
    movies_path = os.path.join(DATA_DIR, "movies_metadata.csv")

    if not os.path.exists(movies_path):
        download_dataset()

    movies = pd.read_csv(movies_path, low_memory=False)
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
        title = data.get("title", "Unknown Title")
        poster_path = data.get("poster_path", "")
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No overview available.")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        return title, poster_url, rating, overview
    return "Unknown", "", "N/A", "Details not available."
