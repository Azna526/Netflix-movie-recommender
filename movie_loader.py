import os
import pandas as pd
import pickle
import subprocess
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ===============================
# Prepare Files (Auto-generate if missing)
# ===============================
def prepare_files():
    dataset_path = "movies_metadata.csv"
    processed_path = "processed_movies.csv"
    similarity_path = "similarity.pkl"

    # If processed files already exist, skip
    if os.path.exists(processed_path) and os.path.exists(similarity_path):
        return

    # Download dataset from Kaggle if not exists
    if not os.path.exists(dataset_path):
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

    # Process dataset
    print("⚙️ Generating processed_movies.csv and similarity.pkl ...")
    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().reset_index(drop=True)

    # TF-IDF on overview
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['overview'])

    # Similarity matrix
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Save outputs
    movies.to_csv(processed_path, index=False)
    with open(similarity_path, "wb") as f:
        pickle.dump(similarity, f)

    print("✅ processed_movies.csv and similarity.pkl created successfully!")


# ===============================
# Load Movies
# ===============================
def load_movies():
    prepare_files()
    return pd.read_csv("processed_movies.csv")


# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    prepare_files()
    with open("similarity.pkl", "rb") as f:
        return pickle.load(f)
