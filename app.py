import streamlit as st
import pandas as pd
from movie_loader import load_movies, load_similarity, fetch_movie_details
import numpy as np

# -------------------------------
# Load Data
# -------------------------------
movies = load_movies()
similarity = load_similarity()

st.title("🍿 Netflix Movie Recommender ")

# Dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

# -------------------------------
# Recommend function
# -------------------------------
def recommend(movie_title, n=5):
    idx = movies[movies['title'] == movie_title].index[0]
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:n+1]
    recs = []
    for i, _ in distances:
        movie_id = movies.iloc[i]['id']
        title = movies.iloc[i]['title']
        poster, rating, overview, link = fetch_movie_details(movie_id)
        recs.append((title, poster, rating, overview, link))
    return recs

# -------------------------------
# UI
# -------------------------------
if st.button("Recommend"):
    results = recommend(selected_movie, 5)
    for title, poster, rating, overview, link in results:
        st.subheader(title)
        if poster:
            st.image(poster, width=250)
        st.write(f"⭐ Rating: {rating}")
        st.write(f"📖 Overview: {overview}")
        st.markdown(f"[🔗 More Info]({link})")
        st.markdown("---")
