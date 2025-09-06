import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

# ===============================
# App Title
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

# ===============================
# Load Data
# ===============================
movies = load_movies()
similarity = load_similarity()

# ===============================
# User Input
# ===============================
movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

if st.button("🔍 Recommend"):
    recommendations = recommend(selected_movie, movies, similarity, top_n=5)

    if recommendations.empty:
        st.warning("No recommendations found.")
    else:
        for _, row in recommendations.iterrows():
            st.subheader(row['title'])
