import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi

DATA_DIR = "data"

def download_dataset():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    api = KaggleApi()
    api.authenticate()  # needs kaggle.json secret

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



