import os
import kaggle
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=True)
def load_datasets():
    """
    Download dataset from Kaggle (if not already cached locally),
    then load the CSVs into Pandas DataFrames.
    """
    dataset = "rounakbanik/the-movies-dataset"
    data_dir = "data"

    # Create data dir if not exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Download only once
    if not os.path.exists(os.path.join(data_dir, "movies_metadata.csv")):
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(dataset, path=data_dir, unzip=True)

    # Load CSVs
    movies = pd.read_csv(os.path.join(data_dir, "movies_metadata.csv"), low_memory=False)
    credits = pd.read_csv(os.path.join(data_dir, "credits.csv"))
    keywords = pd.read_csv(os.path.join(data_dir, "keywords.csv"))
    links = pd.read_csv(os.path.join(data_dir, "links_small.csv"))

    return movies, credits, keywords, links
