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
    dataset_path = "processed_movies.csv"

    if not os.path.exists(dataset_path):
        # Download from Kaggle if missing
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"{dataset_path} not found. Please generate it first.")

    movies = pd.read_csv(dataset_path, low_memory=False)
    return movies


# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)
    return similarity


# ===============================
# Fetch Poster, Rating & Overview from TMDb
# ===============================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    poster_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview", "No overview available.")
    homepage = data.get("homepage", None)

    return {
        "title": data.get("title", "Unknown"),
        "poster": poster_url,
        "rating": rating,
        "overview": overview,
        "homepage": homepage
    }


# ===============================
# Recommendation Function
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i in scores[1:top_n+1]:
        movie_id = movies.iloc[i[0]]['id']
        details = fetch_movie_details(movie_id)
        if details:
            recommendations.append(details)

    return recommendations


