import streamlit as st
import pickle
import pandas as pd
import os
import requests

# --- Load Data ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_FILE = os.path.join(BASE_DIR, "movies_metadata.csv")
SIM_FILE = os.path.join(BASE_DIR, "similarity.pkl")

# Load movies
movies = pd.read_csv(MOVIES_FILE, low_memory=False)

# Ensure we have a title column
if "original_title" in movies.columns:
    title_col = "original_title"
elif "title" in movies.columns:
    title_col = "title"
else:
    st.error("No title column found in movies dataset!")
    st.stop()

# Load similarity matrix
if os.path.exists(SIM_FILE):
    with open(SIM_FILE, "rb") as f:
        similarity = pickle.load(f)
else:
    st.error("similarity.pkl not found! Run the notebook first to generate it.")
    st.stop()

# --- TMDB API ---
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

def fetch_poster(movie_id):
    """Fetch poster from TMDB API using movie_id"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/300x450?text=No+Image"

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

    recs = []
    for i in rec_idxs:
        movie_id = movies.loc[i, "id"] if "id" in movies.columns else None
        poster = fetch_poster(movie_id) if movie_id is not None else None
        recs.append({
            "title": movies.loc[i, title_col],
            "release_date": movies.loc[i].get("release_date", "N/A"),
            "vote_average": movies.loc[i].get("vote_average", "N/A"),
            "poster": poster
        })
    return recs

# --- Streamlit UI ---
st.title("🎬 Movie Recommender System with Posters")

movie_list = movies[title_col].dropna().unique()
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = recommend(selected_movie, 5)
    if recommendations:
        st.write("### Recommended Movies:")
        cols = st.columns(5)
        for i, rec in enumerate(recommendations):
            with cols[i]:
                st.image(rec["poster"], use_column_width=True)
                st.caption(f"**{rec['title']}** ({rec['release_date']}) ⭐ {rec['vote_average']}")
    else:
        st.warning("No recommendations found. Check similarity alignment.")

