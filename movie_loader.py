import os
import pandas as pd
import numpy as np
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

DATA_DIR = "data"
DATASET = "rounakbanik/the-movies-dataset"


def download_dataset():
    """Download dataset from Kaggle if not already present."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(DATASET, path=DATA_DIR, unzip=True)


@st.cache_data
def load_datasets():
    """Load datasets from Kaggle or local storage."""
    if not os.path.exists(os.path.join(DATA_DIR, "movies_metadata.csv")):
        download_dataset()

    movies = pd.read_csv(os.path.join(DATA_DIR, "movies_metadata.csv"), low_memory=False)

    # Keep only useful columns
    movies = movies[["id", "title", "overview"]].dropna()

    return movies


@st.cache_data
def build_similarity(movies):
    """Compute similarity matrix from movie overviews."""
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["overview"])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return similarity


def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API."""
    api_key = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

