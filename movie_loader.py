import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ===============================
# Load Movies Dataset
# ===============================
def load_movies(dataset_path="movies_metadata.csv"):
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} not found. Please upload it to your repo or Kaggle.")

    movies = pd.read_csv(dataset_path, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Load or Rebuild Similarity Matrix
# ===============================
def load_similarity(movies, path="similarity.pkl"):
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"⚠️ similarity.pkl is corrupted. Rebuilding... ({e})")

    # --- Rebuild from movies_metadata.csv ---
    print("🔄 Building similarity matrix from movie overviews...")
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["overview"])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Save for future loads
    with open(path, "wb") as f:
        pickle.dump(similarity, f)

    return similarity

# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]  # skip itself

    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices][['id', 'title']].values.tolist()
