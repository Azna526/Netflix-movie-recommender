import pandas as pd
import os
from kaggle.api.kaggle_api_extended import KaggleApi
import streamlit as st

@st.cache_data
def load_datasets():
    """Download and load the TMDB dataset (movies + similarity)."""
    api = KaggleApi()
    api.authenticate()

    # Download dataset (only first time)
    dataset = "rounakbanik/the-movies-dataset"
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        api.dataset_download_files(dataset, path=data_dir, unzip=True)

    # Load movies
    movies = pd.read_csv(os.path.join(data_dir, "movies_metadata.csv"), low_memory=False)

    # Ensure movie IDs are integers (for TMDB API)
    movies = movies.dropna(subset=["id"])
    movies["id"] = movies["id"].astype(str).str.replace(r"\D", "", regex=True)
    movies = movies[movies["id"] != ""]
    movies["id"] = movies["id"].astype(int)

    # Use only relevant columns
    movies = movies[["id", "original_title", "overview", "release_date", "vote_average"]]

    # Load similarity (you generated this in Jupyter Notebook)
    similarity = pd.read_pickle(os.path.join(data_dir, "similarity.pkl"))

    return movies, similarity
