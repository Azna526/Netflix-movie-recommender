import streamlit as st
import pandas as pd
import requests
from movie_loader import load_datasets

# Load data
st.title("🎬 Netflix Movie Recommender")
st.write("Find similar movies using metadata + NLP!")

movies, credits, keywords, links = load_datasets()

# Merge to get proper titles
movies = movies[['id', 'title', 'overview']].dropna()

# TMDB poster fetch function
def fetch_poster(movie_id):
    import os
    api_key = st.secrets["TMDB_API_KEY"]
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "poster_path" in data and data["poster_path"]:
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return "https://via.placeholder.com/500x750.png?text=No+Image"

# Recommendation function (placeholder: picks 5 random movies)
def recommend(movie_title):
    if movie_title not in movies['title'].values:
        return [], []
    movie_row = movies[movies['title'] == movie_title].iloc[0]
    sample = movies.sample(5)
    posters = [fetch_poster(mid) for mid in sample['id'].values]
    return sample['title'].values, posters

# UI
selected_movie = st.selectbox("👤 Choose a movie:", movies['title'].values[:5000])

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(names[i])
                st.image(posters[i])
    else:
        st.error("No recommendations found.")
