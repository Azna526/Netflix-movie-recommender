import streamlit as st
import pandas as pd
from movie_loader import load_datasets

# --- App Title ---
st.title("🎬 Netflix Movie Recommender")

# --- Load Data ---
@st.cache_data(show_spinner=False)
def get_data():
    return load_datasets()

with st.spinner("⏳ Downloading and loading datasets from Kaggle... Please wait..."):
    movies, ratings, credits, keywords, links = get_data()

# --- Pick the title column ---
if "original_title" in movies.columns:
    title_col = "original_title"
elif "title" in movies.columns:
    title_col = "title"
else:
    st.error("No title column found in movies dataset!")
    st.stop()

# --- Simple Recommendation Function ---
def recommend(movie, n=5):
    matches = movies[movies[title_col].str.lower() == movie.lower()]
    if matches.empty:
        return []
    idx = matches.index[0]

    # Use a very simple similarity: same genres or top vote_average
    if "genres" in movies.columns:
        genre = movies.loc[idx, "genres"]
        recs = movies[movies["genres"] == genre].head(n)
    else:
        recs = movies.sort_values(by="vote_average", ascending=False).head(n)

    cols = [c for c in [title_col, "release_date", "vote_average"] if c in movies.columns]
    return recs[cols]

# --- Streamlit UI ---
movie_list = movies[title_col].dropna().unique()
selected_movie = st.selectbox("🎥 Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = recommend(selected_movie, 5)
    if isinstance(recommendations, pd.DataFrame) and not recommendations.empty:
        st.success("Here are some movies you might like:")
        st.dataframe(recommendations)
    else:
        st.warning("No recommendations found.")


