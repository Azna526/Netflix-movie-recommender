import streamlit as st
import pandas as pd
import requests
from movie_loader import load_datasets, build_similarity

# --- TMDB API Key ---
TMDB_API_KEY = "your_tmdb_api_key_here"  # 🔴 Replace with your TMDB API key

st.title("🎬 Netflix Movie Recommender (with Posters)")

@st.cache_data(show_spinner=False)
def get_data_and_similarity():
    movies, ratings, credits, keywords, links = load_datasets()
    similarity = build_similarity(movies)
    return movies, similarity

with st.spinner("⏳ Downloading dataset from Kaggle and building similarity..."):
    movies, similarity = get_data_and_similarity()

# Pick title column
if "original_title" in movies.columns:
    title_col = "original_title"
elif "title" in movies.columns:
    title_col = "title"
else:
    st.error("No title column found in dataset!")
    st.stop()

# --- Helper: Fetch Poster ---
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    except Exception:
        return None
    return None

# --- Recommend Function ---
def recommend(movie, n=5):
    matches = movies[movies[title_col].str.lower() == movie.lower()]
    if matches.empty:
        return [], []
    idx = matches.index[0]
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:n+1]
    rec_idxs = [i for i, _ in distances]

    rec_movies = movies.iloc[rec_idxs]
    titles = rec_movies[title_col].tolist()
    ids = rec_movies["id"].astype(str).tolist() if "id" in rec_movies.columns else [None] * len(titles)
    posters = [fetch_poster(mid) if mid else None for mid in ids]

    return titles, posters

# --- Streamlit UI ---
movie_list = movies[title_col].dropna().unique()
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    titles, posters = recommend(selected_movie, 5)
    if titles:
        st.success("Here are some recommendations:")
        cols = st.columns(len(titles))
        for i, col in enumerate(cols):
            with col:
                st.text(titles[i])
                if posters[i]:
                    st.image(posters[i])
    else:
        st.warning("No recommendations found.")
