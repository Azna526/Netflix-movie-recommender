import os
import pickle
import pandas as pd
import requests
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi

# ===============================
# Setup Kaggle API credentials
# ===============================
def setup_kaggle():
    kaggle_dir = os.path.join(os.path.expanduser("~"), ".kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    kaggle_path = os.path.join(kaggle_dir, "kaggle.json")

    if not os.path.exists(kaggle_path):
        with open(kaggle_path, "w") as f:
            f.write(
                '{"username":"%s","key":"%s"}' % (
                    st.secrets["kaggle"]["username"],
                    st.secrets["kaggle"]["key"]
                )
            )
    os.chmod(kaggle_path, 0o600)

setup_kaggle()
api = KaggleApi()
api.authenticate()

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "movies_metadata.csv"
    if not os.path.exists(dataset_path):
        api.dataset_download_files(
            "rounakbanik/the-movies-dataset",
            path=".",
            unzip=True
        )

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies
