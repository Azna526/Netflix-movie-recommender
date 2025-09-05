import streamlit as st
from movie_loader import load_datasets, similar_by_title

# --- Load Data ---
st.set_page_config(page_title="Netflix Movie Recommender", layout="centered")

st.title("🍿 Netflix Movie Recommender")
st.write("Find similar movies using metadata + NLP!")

# Load movies + similarity
movies, similarity = load_datasets()

# --- Movie selection ---
movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = similar_by_title(selected_movie, movies, similarity, top_n=5)

    if recommendations:
        st.subheader("✨ Recommended Movies:")
        for rec in recommendations:
            st.write(f"- {rec}")
    else:
        st.error("❌ Could not find recommendations. Try another movie.")
