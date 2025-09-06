import os
import pandas as pd
import requests

# ===============================
# TMDB API Key (hardcoded here)
# ===============================
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"

# ===============================
# Load Movies
# ===============================
def load_movies():
    movies = pd.read_csv("movies_metadata.csv", low_memory=False)
    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies

# ===============================
# Fetch Poster & Details
# ===============================
def fetch_movie_details(movie_id, api_key=TMDB_API_KEY):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        title = data.get("title", "Unknown Title")
        poster_path = data.get("poster_path", "")
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No overview available.")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        return title, poster_url, rating, overview
    return "Unknown", "", "N/A", "Details not available."

# ===============================
# Example Run
# ===============================
if __name__ == "__main__":
    movies = load_movies()
    print("✅ Loaded movies:", movies.shape)

    # Test with the first movie
    sample_id = movies['id'].values[0]
    title, poster, rating, overview = fetch_movie_details(sample_id)
    print("Title:", title)
    print("Poster:", poster)
    print("Rating:", rating)
    print("Overview:", overview[:200], "...")
