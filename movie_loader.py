import os
import pickle
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# ===============================
# API Key from Streamlit Secrets
# ===============================
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

# ===============================
# Load Movies Dataset
# ===============================
def load_movies(dataset_path="movies_metadata.csv"):
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} not found. Please upload it to your repo or Kaggle.")

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Load or Rebuild Similarity Matrix
# ===============================
def load_similarity(movies, path="similarity.pkl"):
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"⚠️ similarity.pkl is corrupted. Rebuilding... ({e})")

    # --- Rebuild from movies_metadata.csv ---
    print("🔄 Building similarity matrix from movie overviews...")
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["overview"])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Save for future loads
    with open(path, "wb") as f:
        pickle.dump(similarity, f)

    return similarity

# ===============================
# Fetch TMDb Movie Details
# ===============================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
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
    return "Unknown", "", "N/A", "Details not available.", "#"

# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]  # skip itself

    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices][['id', 'title']].values.tolist()
