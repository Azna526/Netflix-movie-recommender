import os
import pandas as pd
import requests
import subprocess
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# ===============================
# Load API Keys
# ===============================
try:
    KAGGLE_USERNAME = st.secrets["kaggle"]["username"]
    KAGGLE_KEY = st.secrets["kaggle"]["key"]
    TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

    os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
    os.environ["KAGGLE_KEY"] = KAGGLE_KEY
except Exception as e:
    st.error("❌ Missing secrets: Please set Kaggle + TMDb keys in Streamlit Cloud.")
    raise e

# ===============================
# Load Movies Dataset (cached)
# ===============================
@st.cache_data(show_spinner=False)
def load_movies():
    dataset_path = "movies_metadata.csv"

    if not os.path.exists(dataset_path):
        try:
            st.info("📥 Downloading dataset from Kaggle (first run only)...")
            subprocess.run([
                "kaggle", "datasets", "download", "-d",
                "rounakbanik/the-movies-dataset",
                "-p", ".", "--unzip"
            ], check=True)
        except Exception as e:
            st.error("❌ Failed to download dataset from Kaggle. Check Kaggle setup.")
            raise e

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Build Similarity Matrix (cached)
# ===============================
@st.cache_resource(show_spinner=False)
def build_similarity(movies):
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['overview'])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return similarity

