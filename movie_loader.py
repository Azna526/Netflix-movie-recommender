import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import streamlit as st

# Download dataset from Kaggle if not already present
def download_data():
    if not os.path.exists("movies_metadata.csv"):
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(
            "rounakbanik/the-movies-dataset", 
            path=".", 
            unzip=True
        )

@st.cache_data
def load_movies():
    download_data()
    movies = pd.read_csv("movies_metadata.csv", low_memory=False)
    return movies

@st.cache_data
def load_ratings():
    download_data()
    ratings = pd.read_csv("ratings.csv")
    return ratings
