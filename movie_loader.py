import os
import pandas as pd
import requests
import pickle

# Your TMDB API key
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"

# ===============================
# Load Movies
# ===============================
def load_movies():
    dataset_path = "processed_movies.csv"   # preprocessed smaller dataset
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"{dataset_path} not found. Please upload it to your Streamlit app directory."
        )

    movies = pd.read_csv(dataset_path)
    return movies

# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    sim_path = "similarity.pkl"
    if not os.path.exists(sim_path):
        raise FileNotFoundError(
            f"{sim_path} not found. Please upload it to your Streamlit app directory."
        )

    with open(sim_path, "rb") as f:
        similarity = pickle.load(f)
    return similarity

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
