import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MOVIES_PATH = "processed_movies.csv"
SIM_PATH = "similarity.pkl"
RAW_DATASET = "movies_metadata.csv"

def generate_data():
    if not os.path.exists(RAW_DATASET):
        raise FileNotFoundError("movies_metadata.csv is missing! Please add it to your repo.")

    # Load metadata
    movies = pd.read_csv(RAW_DATASET, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().reset_index(drop=True)

    # TF-IDF on overview
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['overview'])

    # Similarity
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Save processed data
    movies.to_csv(MOVIES_PATH, index=False)
    with open(SIM_PATH, "wb") as f:
        pickle.dump(similarity, f)

    print("✅ Processed data & similarity saved.")


def load_movies():
    if not os.path.exists(MOVIES_PATH):
        generate_data()
    return pd.read_csv(MOVIES_PATH)


def load_similarity():
    if not os.path.exists(SIM_PATH):
        generate_data()
    with open(SIM_PATH, "rb") as f:
        return pickle.load(f)
