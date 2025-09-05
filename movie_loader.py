import os
import pandas as pd
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi

@st.cache_data
def load_movies():
    # Set Kaggle credentials from secrets
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"] = st.secrets["KAGGLE_KEY"]

    api = KaggleApi()
    api.authenticate()

    # Create data directory if it doesn’t exist
    if not os.path.exists("data"):
        os.makedirs("data")

    # Download dataset if not already there
    file_path = "data/movies_metadata.csv"
    if not os.path.exists(file_path):
        api.dataset_download_files(
            "rounakbanik/the-movies-dataset",
            path="data",
            unzip=True
        )

    # Load only necessary columns to reduce memory usage
    df = pd.read_csv(file_path, low_memory=False)
    return df
