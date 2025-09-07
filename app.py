import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

# ================================
# App Title
# ================================
st.set_page_config(page_title="Netflix Movie Recommender", layout="centered")
st.title("🍿 Netflix Movie Recommender (with TMDb)")

# ================================
# Load Data
# ================================
st.write("⏳ Loading data...")
movies = load_movies()
similarity = load_similarity()
st.success("✅ Data loaded successfully!")

# ================================
# Movie Selection
# ================================
movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

# ================================
# Recommend Movies
# ================================
if st.button("🔍 Recommend"):
    recommendations = recommend(selected_movie, movies, similarity, top_n=5)

    if recommendations:
        st.subheader(f"🎥 Because you watched **{selected_movie}**, you might like:")
        for i, rec in enumerate(recommendations, start=1):
            st.write(f"**{i}.** {rec}")
    else:
        st.warning("⚠️ No recommendations found for this movie.")
