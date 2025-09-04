import streamlit as st
import pandas as pd
import pickle
from movie_loader import load_datasets

# --- Load Data ---
data = load_datasets()
movies = data["movies"]
similarity = data["similarity"]

# Ensure we have a title column
if "original_title" in movies.columns:
    title_col = "original_title"
elif "title" in movies.columns:
    title_col = "title"
else:
    st.error("No title column found in movies dataset!")
    st.stop()

# --- Recommend Function ---
def recommend(movie, n=5):
    matches = movies[movies[title_col].str.lower() == movie.lower()]
    if matches.empty:
        return []
    idx = matches.index[0]
    if similarity is None or idx >= similarity.shape[0]:
        return []
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:n+1]
    rec_idxs = [i for i, _ in distances]
    cols = [c for c in [title_col, "release_date", "vote_average"] if c in movies.columns]
    return movies.loc[rec_idxs, cols]

# --- Streamlit UI ---
st.title("🎬 Movie Recommender System")

movie_list = movies[title_col].dropna().unique()
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = recommend(selected_movie, 5)
    if isinstance(recommendations, pd.DataFrame) and not recommendations.empty:
        st.write("### Recommended Movies:")
        st.dataframe(recommendations)
    else:
        st.warning("No recommendations found. Check similarity alignment.")

