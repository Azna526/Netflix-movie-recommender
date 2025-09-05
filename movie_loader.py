import os
import subprocess
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

@st.cache_data
def load_movies():
    # Set Kaggle credentials
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"] = st.secrets["KAGGLE_KEY"]

    dataset = "rounakbanik/the-movies-dataset"

    # Download only once
    if not os.path.exists("movies_metadata.csv"):
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset, "--unzip"],
            check=True
        )

    movies = pd.read_csv("movies_metadata.csv", low_memory=False)
    movies = movies[["title", "overview"]].dropna()
    return movies

@st.cache_resource
def build_text_model(movies_df):
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies_df["overview"])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def similar_by_title(title, movies_df, cosine_sim, top_n=5):
    # Reset index to map titles to row indices
    indices = pd.Series(movies_df.index, index=movies_df["title"]).drop_duplicates()

    if title not in indices:
        return []

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]
    return movies_df["title"].iloc[movie_indices].tolist()


