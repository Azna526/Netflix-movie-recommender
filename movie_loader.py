import pandas as pd
import pickle

# ===============================
# Load Processed Movies
# ===============================
def load_movies():
    movies = pd.read_csv("processed_movies.csv")
    return movies

# ===============================
# Load Similarity Matrix
# ===============================
def load_similarity():
    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)
    return similarity

# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1: top_n + 1]

    recommendations = []
    for i, score in distances:
        movie = movies.iloc[i]
        recommendations.append({
            "title": movie["title"],
            "poster_url": movie["poster_url"],
            "rating": movie["vote_average"],
            "overview": movie["overview"],
            "credits": movie["credits"],
            "tmdb_url": movie["tmdb_url"]
        })
    return recommendations
