import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

DATA_DIR = "data"

def download_dataset():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Kaggle credentials from Streamlit Secrets
    os.environ["KAGGLE_USERNAME"] = st.secrets["kaggle"]["username"]
    os.environ["KAGGLE_KEY"] = st.secrets["kaggle"]["key"]

    api = KaggleApi()
    api.authenticate()

    dataset = "rounakbanik/the-movies-dataset"
    api.dataset_download_files(dataset, path=DATA_DIR, unzip=True)

def load_datasets():
    if not os.path.exists(os.path.join(DATA_DIR, "movies_metadata.csv")):
        download_dataset()

    movies = pd.read_csv(os.path.join(DATA_DIR, "movies_metadata.csv"), low_memory=False)
    ratings = pd.read_csv(os.path.join(DATA_DIR, "ratings_small.csv"))
    credits = pd.read_csv(os.path.join(DATA_DIR, "credits.csv"))
    keywords = pd.read_csv(os.path.join(DATA_DIR, "keywords.csv"))
    links = pd.read_csv(os.path.join(DATA_DIR, "links_small.csv"))

    return movies, ratings, credits, keywords, links

def build_similarity(movies):
    # Ensure text features are present (for simplicity, use overview)
    movies["overview"] = movies["overview"].fillna("")
    cv = CountVectorizer(stop_words="english")
    count_matrix = cv.fit_transform(movies["overview"])
    similarity = cosine_similarity(count_matrix, count_matrix)
    return similarity
