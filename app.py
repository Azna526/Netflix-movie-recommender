import streamlit as st
from movie_loader import load_movies, build_text_model, similar_by_title

# App title
st.title("🎬 Netflix Movie Recommender")
st.write("Find similar movies using metadata + NLP (Kaggle dataset).")

# Load dataset
with st.spinner("Loading movies..."):
    movies_df = load_movies()
    cosine_sim = build_text_model(movies_df)

# Dropdown for movie selection
movie_list = movies_df["title"].values
selected_movie = st.selectbox("🎥 Choose a movie:", movie_list)

# Recommend button
if st.button("Recommend"):
    recommendations = similar_by_title(selected_movie, movies_df, cosine_sim)

    if recommendations:
        st.subheader("✨ Recommended Movies:")
        for r in recommendations:
            st.write(f"- {r}")
    else:
        st.error("No recommendations found.")

