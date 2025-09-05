import streamlit as st
from movie_loader import load_movies, build_text_model, similar_by_title

st.set_page_config(page_title="Netflix Movie Recommender", page_icon="🎬")

st.title("🎬 Netflix Movie Recommender")
st.write("Find similar movies using metadata + NLP (no API required).")

@st.cache_data
def load():
    movies = load_movies()
    cosine_sim = build_text_model(movies)
    return movies, cosine_sim

movies, cosine_sim = load()

movie_list = movies["title"].tolist()
selected_movie = st.selectbox("🎥 Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = similar_by_title(selected_movie, movies, cosine_sim)
    if recommendations:
        st.subheader("Recommended Movies:")
        for r in recommendations:
            st.write("- ", r)
    else:
        st.error("No recommendations found.")
