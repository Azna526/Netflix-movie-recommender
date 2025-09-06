import os
import pickle
import pandas as pd
import requests
import kaggle
import streamlit as st

# ===============================
# Load API Keys from Streamlit Secrets
# ===============================
os.environ["KAGGLE_USERNAME"] = st.secrets["kaggle"]["username"]
os.environ["KAGGLE_KEY"] = st.secrets["kaggle"]["key"]
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "movies_metadata.csv"

    # If not present, download from Kaggle
    if not os.path.exists(dataset_path):
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
    sim_path = "similarity.pkl"
    if not os.path.exists(sim_path):
        raise FileNotFoundError(f"{sim_path} not found. Please upload it to your Streamlit app.")
    with open(sim_path, "rb") as f:
        return pickle.load(f)

# ===============================
# Fetch Poster & Details from TMDb
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
        homepage = data.get("homepage", "")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        return title, poster_url, rating, overview, homepage
    return "Unknown", "", "N/A", "Details not available.", ""

# ===============================
# Recommend Movies
# ===============================
def recommend(movie, movies, similarity):
    if movie not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]  # Top 5

    recommendations = []
    for i, _ in sim_scores:
        movie_id = movies.iloc[i].id
        details = fetch_movie_details(movie_id)
        recommendations.append(details)
    return recommendations

