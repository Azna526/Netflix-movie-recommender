import streamlit as st
import requests
from movie_loader import load_movies, build_text_model, similar_by_title

# --- Page setup
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="centered")
st.title("🎬 Movie Recommender with Posters")

# --- Load data + model
with st.spinner("Loading movies and building model..."):
    movies = load_movies()
    similarity = build_text_model(movies)

# --- Secrets: TMDB API key
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

def fetch_poster(tmdb_id: int) -> str:
    """Fetch poster from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("poster_path"):
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    except Exception:
        pass
    return "https://via.placeholder.com/500x750.png?text=No+Poster"

# --- UI
movie_list = movies["title"].tolist()
choice = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    idxs = similar_by_title(choice, movies, similarity, top_n=5)
    if not idxs:
        st.warning("No recommendations found.")
    else:
        cols = st.columns(len(idxs))
        for col, i in zip(cols, idxs):
            row = movies.iloc[i]
            with col:
                st.image(fetch_poster(int(row["id"])), use_column_width=True)
                st.caption(row["title"])

# --- Debug sanity check
with st.expander("Debug Info"):
    st.write("Movies shape:", movies.shape)
    st.write("Similarity shape:", similarity.shape)
