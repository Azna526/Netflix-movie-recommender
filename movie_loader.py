import os
import pandas as pd
import pickle
import requests

# Your TMDB key
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"

# ===============================
# Load Movies
# ===============================
def load_movies():
    dataset_path = "movies_metadata.csv"

    # If file not present, download via Kaggle API
    if not os.path.exists(dataset_path):
        import kaggle
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            "rounakbanik/the-movies-dataset",
            path=".",
            unzip=True
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
# Fetch Poster, Details & Link
# ===============================
def fetch_movie_details(movie_id, api_key=TMDB_API_KEY):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        poster_path = data.get("poster_path", "")
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No overview available.")
        title = data.get("title", "Unknown Title")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        tmdb_url = f"https://www.themoviedb.org/movie/{movie_id}"
        return title, poster_url, rating, overview, tmdb_url

    return "Unknown", "", "N/A", "Details not available.", ""

# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity, top_n=5):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    distances = list(enumerate(similarity[idx]))
    similar_movies = sorted(distances, key=lambda x: x[1], reverse=True)[1:top_n+1]

    recommendations = []
    for i in similar_movies:
        rec_id = movies.iloc[i[0]]['id']
        recommendations.append(rec_id)
    return recommendations
