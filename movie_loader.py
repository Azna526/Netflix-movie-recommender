import os
import pandas as pd
import requests
import subprocess
import streamlit as st

# ===============================
# Load API Keys from Streamlit Secrets
# ===============================
try:
    KAGGLE_USERNAME = st.secrets["kaggle"]["username"]
    KAGGLE_KEY = st.secrets["kaggle"]["key"]
    TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

    os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
    os.environ["KAGGLE_KEY"] = KAGGLE_KEY
except Exception as e:
    st.error("❌ Missing secrets: Please set Kaggle + TMDb keys in Streamlit Cloud.")
    raise e

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "movies_metadata.csv"

    if not os.path.exists(dataset_path):
        try:
            st.info("📥 Downloading dataset from Kaggle...")
            subprocess.run([
                "kaggle", "datasets", "download", "-d",
                "rounakbanik/the-movies-dataset",
                "-p", ".", "--unzip"
            ], check=True)
        except Exception as e:
            st.error("❌ Failed to download dataset from Kaggle. Check Kaggle setup.")
            raise e

    if not os.path.exists(dataset_path):
        st.error(f"❌ {dataset_path} not found even after download.")
        raise FileNotFoundError(f"{dataset_path} not found.")

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Fetch Movie Details from TMDb
# ===============================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)

    if response.status_code != 200:
        return "Unknown", "", "N/A", "Details not available.", ""

    data = response.json()
    title = data.get("title", "Unknown Title")
    poster_path = data.get("poster_path")
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview", "No overview available.")
    link = f"https://www.themoviedb.org/movie/{movie_id}"

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    return title, poster_url, rating, overview, link
