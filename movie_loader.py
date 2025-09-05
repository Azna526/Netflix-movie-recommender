import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

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
    movies = movies[['id', 'title', 'overview']].dropna()
    return movies

@st.cache_data
def build_text_model(movies):
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["overview"])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def similar_by_title(title, movies, cosine_sim):
    indices = pd.Series(movies.index, index=movies["title"]).drop_duplicates()
    if title not in indices:
        return []
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices]["title"].tolist()
