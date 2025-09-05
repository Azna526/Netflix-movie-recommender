import pandas as pd
import numpy as np
import os
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = "data"  # make sure your pickle/csv files are inside /data

def load_datasets():
    """
    Load movies dataset.
    Returns a DataFrame with at least 'movie_id' and 'title' columns.
    """
    movies_path = os.path.join(DATA_DIR, "movies.pkl")

    if os.path.exists(movies_path):
        movies = pd.read_pickle(movies_path)
    else:
        raise FileNotFoundError(f"{movies_path} not found. Upload it to your repo under /data")

    return movies


def build_similarity(movies):
    """
    Build similarity matrix from movie metadata (tags).
    Returns a cosine similarity matrix.
    """
    if "tags" not in movies.columns:
        raise ValueError("Movies dataset must contain a 'tags' column for similarity calculation")

    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies["tags"]).toarray()
    similarity = cosine_similarity(vectors)

    # Optional: save for later use
    sim_path = os.path.join(DATA_DIR, "similarity.pkl")
    with open(sim_path, "wb") as f:
        pickle.dump(similarity, f)

    return similarity
