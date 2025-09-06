import requests
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# TMDB API Key
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# --- Fetch movies dynamically from TMDb ---
def load_movies(pages=3):
    all_movies = []
    for page in range(1, pages + 1):  # Fetch multiple pages
        url = f"{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        response = requests.get(url).json()
        results = response.get("results", [])
        for movie in results:
            all_movies.append({
                "movie_id": movie["id"],
                "title": movie["title"],
                "overview": movie.get("overview", "")
            })
    return pd.DataFrame(all_movies)

# --- Build similarity model ---
def build_text_model(movies_df):
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(movies_df['overview'].fillna("")).toarray()
    similarity = cosine_similarity(vectors)
    return similarity

# --- Recommend similar movies ---
def similar_by_title(title, movies, similarity):
    if title not in movies['title'].values:
        return []
    idx = movies[movies['title'] == title].index[0]
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)
    recommendations = []
    for i in distances[1:6]:  # top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        rec_title = movies.iloc[i[0]].title
        poster = fetch_poster(movie_id)
        recommendations.append((rec_title, poster))
    return recommendations

# --- Fetch poster from TMDb ---
def fetch_poster(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url).json()
    if "poster_path" in response and response["poster_path"]:
        return f"https://image.tmdb.org/t/p/w500{response['poster_path']}"
    return "https://via.placeholder.com/300x450?text=No+Image"
