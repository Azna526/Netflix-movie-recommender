import streamlit as st
from movie_loader import load_movies, build_text_model, similar_by_title

st.title("🎬 Netflix Movie Recommender")
st.write("Find similar movies using metadata + NLP!")

movies_df = load_movies()
cosine_sim = build_text_model(movies_df)

movie_list = movies_df["title"].values
selected_movie = st.selectbox("🎥 Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = similar_by_title(selected_movie, movies_df, cosine_sim)
    if recommendations:
        st.write("### Recommended Movies:")
        for r in recommendations:
            st.write(f"- {r}")
    else:
        st.error("No recommendations found.")
