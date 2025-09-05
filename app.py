import streamlit as st
import pickle
import pandas as pd
import os
import requests

# --- API Key ---
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"   # <-- Replace with your API key

# --- Load Data ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_FILE = os.path.join(BASE_DIR, "movies_metadata.csv")
SIM_FILE = os.path.join(BASE_DIR, "similarity.pkl")

movies = pd.read_csv(MOVIES_FILE, low_memory=False)

if "original_title" in movies.columns:
    title_col = "original_title"
elif "title" in movies.columns:
    title_col = "title"
else:
    st.error("No title column found in movies dataset!")
    st.stop()

with open(SIM_FILE, "rb") as f:
    similarity = pickle.load(f)

# --- Fetch Poster from TMDB ---
def fetch_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(url).json()
    if response["results"]:
        poster_path = response["results"][0].get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    return None

# --- Recommend Function ---
def recommend(movie, n=5):
    matches = movies[movies[title_col].str.lower() == movie.lower()]
    if matches.empty:
        return []
    idx = matches.index[0]
    if idx >= similarity.shape[0]:
        return []
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:n+1]
    rec_idxs = [i for i, _ in distances]
    rec_movies = movies.loc[rec_idxs, [title_col, "release_date", "vote_average"]]

    rec_movies["poster"] = rec_movies[title_col].apply(fetch_poster)
    return rec_movies

# --- Streamlit UI ---
st.title("🎬 Netflix Movie Recommender with Posters")

movie_list = movies[title_col].dropna().unique()
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = recommend(selected_movie, 5)
    if not recommendations.empty:
        st.write("### Recommended Movies:")
        for _, row in recommendations.iterrows():
            st.subheader(f"{row[title_col]} ({row['release_date'][:4]}) ⭐ {row['vote_average']}")
            if row["poster"]:
                st.image(row["poster"], width=150)
    else:
        st.warning("No recommendations found. Check similarity alignment.")
