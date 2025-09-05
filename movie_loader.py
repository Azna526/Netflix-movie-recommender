import os
import subprocess
import pandas as pd
import streamlit as st

@st.cache_data
def load_movies():
    # Set Kaggle credentials from Streamlit secrets
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"] = st.secrets["KAGGLE_KEY"]

    dataset = "rounakbanik/the-movies-dataset"

    # Download dataset if not exists
    if not os.path.exists("movies_metadata.csv"):
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset, "--unzip"],
            check=True
        )

    # Load the dataset
    movies = pd.read_csv("movies_metadata.csv", low_memory=False)
    return movies
