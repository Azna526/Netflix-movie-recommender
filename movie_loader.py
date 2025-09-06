import os
import pickle
import pandas as pd
import subprocess

# ===============================
# Load Movies Dataset
# ===============================
def load_movies():
    dataset_path = "processed_movies.csv"

    if not os.path.exists(dataset_path):
        # Download dataset from Kaggle if not already present
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

        raise FileNotFoundError(
            f"{dataset_path} not found. Please generate it first "
            f"using your preprocessing script."
        )

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies


# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    with open("similarity.pkl", "rb") as f:
        return pickle.load(f)


# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    # Get index of selected movie
    idx = movies[movies['title'] == movie_title].index[0]

    # Get similarity scores
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Skip first (same movie) and take top_n
    recommended = []
    for i in sim_scores[1: top_n + 1]:
        movie_id = movies.iloc[i[0]].id
        title = movies.iloc[i[0]].title
        recommended.append((movie_id, title))

    return recommended
