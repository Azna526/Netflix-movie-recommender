import streamlit as st
from movie_loader import load_movies, build_text_model, similar_by_title

# --- Load Data ---
movies = load_movies()
similarity = build_text_model(movies)

# --- UI ---
st.title("🎬 Movie Recommender with Posters (TMDb API)")

movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie to get recommendations:", movie_list)

if st.button("Recommend"):
    recommendations = similar_by_title(selected_movie, movies, similarity)
    if recommendations:
        for title, poster in recommendations:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(poster, width=150)
            with col2:
                st.subheader(title)
    else:
        st.warning("No recommendations found.")
