import streamlit as st
import pickle
import pandas as pd
import requests
import os

# --- Load Data ---
from movie_loader import load_datasets
movies, similarity = load_datasets()

# --- Fetch Poster Function ---
def fetch_poster(movie_id):
    api_key = st.secrets["TMDB_API_KEY"]   # get your key from Streamlit secrets
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    if "poster_path" in data and data["poster_path"]:
        return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
    else:
        return "https://via.placeholder.com/500x750?text=No+Poster"

# --- Recommend Function ---
def recommend(movie, n=5):
    matches = movies[movies['original_title'].str.lower() == movie.lower()]
    if matches.empty:
        return [], []
    idx = matches.index[0]
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:n+1]
    rec_idxs = [i for i, _ in distances]

    titles = movies.loc[rec_idxs, "original_title"].values
    ids = movies.loc[rec_idxs, "id"].values
    posters = [fetch_poster(mid) for mid in ids]

    return titles, posters

# --- Streamlit UI ---
st.title("🍿 Netflix Movie Recommender")
st.subheader("Find similar movies using metadata + NLP!")

movie_list = movies["original_title"].dropna().unique()
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

if st.button("Recommend"):
    titles, posters = recommend(selected_movie, 5)
    if titles:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(titles[idx])
                st.image(posters[idx])
    else:
        st.warning("No recommendations found.")
