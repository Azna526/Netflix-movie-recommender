import streamlit as st
import pickle
import pandas as pd
import requests
import tmdbsimple as tmdb

# -----------------------------
# Setup TMDB
# -----------------------------
tmdb.API_KEY = "YOUR_TMDB_API_KEY"  # <-- Replace with your TMDB API key

# -----------------------------
# Load Data
# -----------------------------
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# -----------------------------
# Poster Fetcher
# -----------------------------
def fetch_poster(movie_id):
    try:
        movie = tmdb.Movies(movie_id).info()
        if "poster_path" in movie and movie["poster_path"]:
            return "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Poster+Available"
    except:
        return "https://via.placeholder.com/500x750.png?text=Error"

# -----------------------------
# Recommendation Function
# -----------------------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    recommended_movies = []
    recommended_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎬 Netflix Movie Recommender with Posters")

selected_movie_name = st.selectbox(
    "Type or select a movie:",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
