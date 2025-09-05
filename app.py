import streamlit as st
import requests
from movie_loader import load_datasets, similar_by_title

# --- Streamlit config ---
st.set_page_config(page_title="Netflix Movie Recommender", layout="centered")

st.title("🍿 Netflix Movie Recommender")
st.write("Find similar movies using metadata + NLP + Posters!")

# --- Load Data ---
movies, similarity = load_datasets()

# --- Fetch Poster ---
def fetch_poster(movie_id):
    api_key = st.secrets["TMDB_API_KEY"]   # put your TMDB key in Streamlit secrets
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    if "poster_path" in data and data["poster_path"]:
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    else:
        return "https://via.placeholder.com/500x750.png?text=No+Poster"

# --- UI Selection ---
movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = similar_by_title(selected_movie, movies, similarity, top_n=5)

    if recommendations:
        st.subheader("✨ Recommended Movies:")
        cols = st.columns(5)
        for idx, rec in enumerate(recommendations):
            movie_id = movies[movies['title'] == rec].iloc[0].id
            poster = fetch_poster(movie_id)
            with cols[idx]:
                st.image(poster, caption=rec, use_column_width=True)
    else:
        st.error("❌ Could not find recommendations. Try another movie.")
