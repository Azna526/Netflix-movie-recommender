import os
import pickle
import pandas as pd
import streamlit as st

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "processed_movies.csv"

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} not found. Please generate it first.")

    movies = pd.read_csv(dataset_path)
    return movies

# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    similarity_path = "similarity.pkl"

    if not os.path.exists(similarity_path):
        raise FileNotFoundError(f"{similarity_path} not found. Please generate it first.")

    with open(similarity_path, "rb") as f:
        similarity = pickle.load(f)
    return similarity

# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommendations = movies.iloc[[i[0] for i in scores]][['id', 'title']]

    return recommendations
