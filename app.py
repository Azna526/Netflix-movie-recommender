import streamlit as st
import pickle
import pandas as pd
import requests

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("🎬 Netflix Movie Recommender")

# TMDB API Key from Streamlit secrets
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# Function to fetch poster from TMDB
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    return "https://via.placeholder.com/300x450.png?text=No+Poster"

# Recommendation function
def recommend(movie):
    movie_index = movies[movies['original_title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].original_title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# UI
selected_movie_name = st.selectbox("🎥 Choose a movie:", movies['original_title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])


