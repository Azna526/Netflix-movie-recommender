import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import streamlit as st

@st.cache_data
def load_datasets():
    # Authenticate Kaggle
    api = KaggleApi()
    api.authenticate()

    # Download dataset if not already present
    if not os.path.exists("tmdb_5000_movies.csv") or not os.path.exists("tmdb_5000_credits.csv"):
        api.dataset_download_files('tmdb/tmdb-movie-metadata', path='.', unzip=True)

    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")

    # Merge datasets
    movies = movies.merge(credits, on='title')

    # Helper functions
    def convert(obj):
        try:
            L = []
            for i in ast.literal_eval(obj):
                L.append(i['name'])
            return L
        except:
            return []

    def fetch_director(obj):
        try:
            L = []
            for i in ast.literal_eval(obj):
                if i['job'] == 'Director':
                    L.append(i['name'])
            return L
        except:
            return []

    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(lambda x: convert(x)[:3])
    movies['crew'] = movies['crew'].apply(fetch_director)

    # Create tags column
    movies['tags'] = movies['overview'].fillna('') + " " + movies['genres'].astype(str) + " " + movies['keywords'].astype(str) + " " + movies['cast'].astype(str) + " " + movies['crew'].astype(str)

    # Feature extraction
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(movies['tags']).toarray()

    # Similarity matrix
    similarity = cosine_similarity(vectors)

    return movies, similarity


