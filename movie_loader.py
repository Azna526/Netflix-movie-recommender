import os
import pandas as pd
import requests
import subprocess
from sklearn.feature_extraction.text import CountVectorizer
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
except Exception:
    st.error("❌ Missing secrets: Please set Kaggle + TMDb keys in Streamlit Cloud.")
    raise

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
            st.error("❌ Failed to download dataset from Kaggle.")
            raise e

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Build Similarity Matrix
# ===============================
def build_similarity(movies):
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies["overview"].fillna("")).toarray()
    similarity = cosine_similarity(vectors)
    return similarity

# ===============================
# Fetch Movie Details from TMDb
# ===============================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=credits"
    response = requests.get(url)

    if response.status_code != 200:
        return {
            "title": "Unknown",
            "poster_url": "",
            "rating": "N/A",
            "overview": "Details not available.",
            "link": "",
            "credits": "Not available"
        }

    data = response.json()
    title = data.get("title", "Unknown Title")
    poster_path = data.get("poster_path")
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview", "No overview available.")
    link = f"https://www.themoviedb.org/movie/{movie_id}"

    # Credits (top 3 cast + director)
    credits_data = data.get("credits", {})
    cast = [c["name"] for c in credits_data.get("cast", [])[:3]]
    crew = [c["name"] for c in credits_data.get("crew", []) if c.get("job") == "Director"]
    credits = f"Cast: {', '.join(cast)} | Director: {', '.join(crew)}"

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

    return {
        "title": title,
        "poster_url": poster_url,
        "rating": rating,
        "overview": overview,
        "link": link,
        "credits": credits
    }

# ===============================
# Recommend Top 5 Movies
# ===============================
def recommend(movie_title, movies, similarity):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    distances = similarity[idx]
    movie_list = sorted(
        list(enumerate(distances)), key=lambda x: x[1], reverse=True
    )[1:6]  # Top 5 (excluding itself)

    recommendations = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].id
        details = fetch_movie_details(movie_id)
        recommendations.append(details)

    return recommendations
