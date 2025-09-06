import os
import pickle
import pandas as pd
import requests
import subprocess
import streamlit as st

# ===============================
# Load API Keys from Streamlit Secrets
# ===============================
KAGGLE_USERNAME = st.secrets["kaggle"]["username"]
KAGGLE_KEY = st.secrets["kaggle"]["key"]
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
os.environ["KAGGLE_KEY"] = KAGGLE_KEY


# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "movies_metadata.csv"

    if not os.path.exists(dataset_path):
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} not found after download.")

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
# Fetch Poster & Details from TMDB
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
        link = f"https://www.themoviedb.org/movie/{movie_id}"
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        return title, poster_url, rating, overview, link

    return "Unknown", "", "N/A", "Details not available.", ""


# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i in scores[1:top_n+1]:
        movie_id = movies.iloc[i[0]].id
        title, poster, rating, overview, link = fetch_movie_details(movie_id)
        recommendations.append((title, poster, rating, overview, link))

    return recommendations
