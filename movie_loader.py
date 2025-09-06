import os
import pickle
import pandas as pd
import requests
import subprocess
import streamlit as st

# ===============================
# Load API Keys from Streamlit Secrets
# ===============================
KAGGLE_USERNAME = st.secrets["kaggle"]["username"]
KAGGLE_KEY = st.secrets["kaggle"]["key"]
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
os.environ["KAGGLE_KEY"] = KAGGLE_KEY

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "movies_metadata.csv"

    if not os.path.exists(dataset_path):
        # Use Kaggle CLI instead of KaggleApi
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} not found after download.")

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies
