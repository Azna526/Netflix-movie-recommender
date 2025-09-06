import streamlit as st
import pandas as pd
from movie_loader import load_movies, fetch_movie_details
import os

# Load TMDb API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "0d309fbe7061ac46435369d2349288ba")  # replace with secret if needed

st.title("🍿 Netflix Style Movie Recommender ")

# Load movies
movies = load_movies()
movie_list = movies['title'].values

# Dropdown
selected_movie_name = st.selectbox("Choose a movie:", movie_list)

# Find movie_id from selected name
if st.button("Recommend"):
    movie_id = movies[movies['title'] == selected_movie_name]['id'].values[0]
    poster, rating, overview = fetch_movie_details(movie_id, TMDB_API_KEY)

    st.image(poster, width=300)
    st.markdown(f"**Rating:** ⭐ {rating}")
    st.markdown(f"**Overview:** {overview}")
