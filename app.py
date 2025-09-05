import streamlit as st
import pickle
import pandas as pd
import requests
import os
from movie_loader import load_datasets, build_similarity
import numpy as np

# -------------------------------
# TMDB API Key from Streamlit Secrets
# -------------------------------
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_poster(movie_id):
    """Fetch poster from TMDB API"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    data = response.json()
    if "poster_path" in data and data["poster_path"]:
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    else:
        return "https://via.placeholder.com/500x750.png?text=No+Poster"

def recommend(movie, movies, similarity):
    """Recommend top 5 similar movies"""
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# -------------------------------
# Streamlit App
# -------------------------------
st.title("🎬 Netflix Movie Recommender")
st.markdown("Find similar movies using metadata + NLP!")

# Load data
movies = load_datasets()
similarity = build_similarity(movies)

movie_list = movies['title'].values
selected_movie = st.selectbox("👤 Choose a movie:", movie_list)

if st.button("Recommend"):
    names, posters = recommend(selected_movie, movies, similarity)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.image(poster, use_container_width=True)
            st.caption(name)
