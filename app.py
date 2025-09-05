# app.py
import streamlit as st
from movie_loader import load_movies, build_text_model, similar_by_title

st.set_page_config(page_title="Netflix Movie Recommender", page_icon="🎬", layout="wide")

st.title("🎬 Netflix Movie Recommender")
st.caption("Find similar movies using metadata + NLP (no external API required).")

# Load data and model (both cached)
movies_df = load_movies()
_, tfidf_matrix = build_text_model(movies_df)

# UI
title_choice = st.selectbox("Choose a movie:", sorted(movies_df["title"].tolist()))
if st.button("Recommend"):
    results = similar_by_title(movies_df, tfidf_matrix, title_choice, topn=5)

    if not results:
        st.info("No similar movies found. Try another title.")
    else:
        cols = st.columns(len(results))
        for col, item in zip(cols, results):
            with col:
                st.image(item["poster_url"], use_column_width=True)
                st.caption(item["title"])
