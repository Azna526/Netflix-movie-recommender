import os
import pickle
import pandas as pd
import subprocess
import requests
import streamlit as st

# ===============================
# Load API Key from Streamlit Secrets
# ===============================
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "processed_movies.csv"

    if not os.path.exists(dataset_path):
        # Download dataset from Kaggle if not already present
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

        raise FileNotFoundError(
            f"{dataset_path} not found. Please generate it first "
            f"using your preprocessing script."
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
# Fetch Movie Details from TMDb
# ===============================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    poster_path = data.get("poster_path")
    rating = data.get("vote_average")
    link = f"https://www.themoviedb.org/movie/{movie_id}"

    return {
        "poster": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
        "rating": rating,
        "link": link
    }


# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i in sim_scores[1: top_n + 1]:
        movie_id = movies.iloc[i[0]].id
        title = movies.iloc[i[0]].title
        details = fetch_movie_details(movie_id)

        recommendations.append({
            "title": title,
            "poster": details["poster"] if details else None,
            "rating": details["rating"] if details else "N/A",
            "link": details["link"] if details else "#"
        })

    return recommendations
