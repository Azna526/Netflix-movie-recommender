import os
import pandas as pd
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi

@st.cache_data(show_spinner=True)
def load_datasets():
    """
    Download the Kaggle dataset if not already cached,
    then load the CSVs into Pandas DataFrames.
    """
    dataset = "rounakbanik/the-movies-dataset"
    data_dir = "data"

    # Create folder if not exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Authenticate with Kaggle using Streamlit secrets
    os.environ["KAGGLE_USERNAME"] = st.secrets["kaggle"]["username"]
    os.environ["KAGGLE_KEY"] = st.secrets["kaggle"]["key"]

    api = KaggleApi()
    api.authenticate()

    # Download only if missing
    if not os.path.exists(os.path.join(data_dir, "movies_metadata.csv")):
        api.dataset_download_files(dataset, path=data_dir, unzip=True)

    # Load CSVs
    movies = pd.read_csv(os.path.join(data_dir, "movies_metadata.csv"), low_memory=False)
    credits = pd.read_csv(os.path.join(data_dir, "credits.csv"))
    keywords = pd.read_csv(os.path.join(data_dir, "keywords.csv"))
    links = pd.read_csv(os.path.join(data_dir, "links_small.csv"))

    return movies, credits, keywords, links
