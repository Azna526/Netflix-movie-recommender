# app.py
import streamlit as st
from movie_loader import load_movies, fetch_movie_details

st.set_page_config(page_title="Dynamic Movie Recommender", layout="centered")
st.title("🎬 Dynamic Movie Recommender (TMDb API)")

with st.spinner("Loading movies..."):
    try:
        movies = load_movies()
    except Exception as e:
        st.error(f"Failed to load movies_metadata.csv: {e}")
        st.stop()

movie_list = movies['title'].tolist()
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    movie_row = movies[movies['title'] == selected_movie]
    if movie_row.empty:
        st.error("Selected movie not found in dataset.")
    else:
        movie_id = movie_row['id'].values[0]
        title, poster_url, rating, overview = fetch_movie_details(movie_id)
        st.subheader(title)
        if poster_url:
            st.image(poster_url, width=300)
        st.write(f"⭐ Rating: {rating}")
        st.write("📖 Overview:")
        st.write(overview)
