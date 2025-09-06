import os
import pickle
import pandas as pd
import requests
import subprocess
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ===============================
# Load API Keys from Streamlit Secrets
# ===============================
KAGGLE_USERNAME = st.secrets["kaggle"]["username"]
KAGGLE_KEY = st.secrets["kaggle"]["key"]
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
os.environ["KAGGLE_KEY"] = KAGGLE_KEY

# ===============================
# File Paths
# ===============================
RAW_FILE = "movies_metadata.csv"
PROCESSED_FILE = "processed_movies.csv"
SIMILARITY_FILE = "similarity.pkl"

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    # If processed file exists, just load it
    if os.path.exists(PROCESSED_FILE):
        return pd.read_csv(PROCESSED_FILE)

    # If not, check raw file
    if not os.path.exists(RAW_FILE):
        # Download from Kaggle
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(f"{RAW_FILE} not found even after download.")

    # Preprocess and save
    movies = pd.read_csv(RAW_FILE, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().reset_index(drop=True)

    # Create TF-IDF matrix
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['overview'])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Save processed files
    movies[['id', 'title']].to_csv(PROCESSED_FILE, index=False)
    with open(SIMILARITY_FILE, "wb") as f:
        pickle.dump(similarity, f)

    return movies[['id', 'title']]

# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    if os.path.exists(SIMILARITY_FILE):
        with open(SIMILARITY_FILE, "rb") as f:
            return pickle.load(f)
    else:
        # Ensure preprocessing happens
        load_movies()
        with open(SIMILARITY_FILE, "rb") as f:
            return pickle.load(f)
