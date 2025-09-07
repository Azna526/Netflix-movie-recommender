import os
import pandas as pd
import requests
import subprocess
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# ===============================
# Load API Keys
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
    movies = movies[['id', 'title', 'overview']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Build Similarity Matrix
# ===============================
def build_similarity(movies):
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['overview'])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return similarity

# ===============================
# Recommend Top N Movies
# ===============================
def recommend(title, movies, similarity, top_n=5):
    if title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in scores]
    return movies.iloc[movie_indices]['id'].tolist()

# ===============================
# Fetch Movie Details from TMDb
# ===============================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=credits"
    response = requests.get(url)

    if response.status_code != 200:
        return "Unknown", "", "N/A", "Details not available.", "", []

    data = response.json()
    title = data.get("title", "Unknown Title")
    poster_path = data.get("poster_path")
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview", "No overview available.")
    link = f"https://www.themoviedb.org/movie/{movie_id}"

    # fetch cast (credits)
    credits = []
    if "credits" in data and "cast" in data["credits"]:
        credits = [c["name"] for c in data["credits"]["cast"][:5]]

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    return title, poster_url, rating, overview, link, credits
