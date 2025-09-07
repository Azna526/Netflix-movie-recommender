import streamlit as st
import requests
from movie_loader import load_movies, load_similarity

# ===============================
# TMDB API Key
# ===============================
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"

# ===============================
# Fetch Movie Details from TMDB
# ===============================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        title = data.get("title", "Unknown Title")
        poster_path = data.get("poster_path", "")
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No overview available.")
        link = f"https://www.themoviedb.org/movie/{movie_id}"
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        return title, poster_url, rating, overview, link
    return "Unknown", "", "N/A", "Details not available.", "#"


# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, movies, similarity):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]  # Top 5 (skip itself)

    recommendations = []
    for i, _ in scores:
        movie_id = movies.iloc[i]['id']
        title, poster_url, rating, overview, link = fetch_movie_details(movie_id)
        recommendations.append((title, poster_url, rating, overview, link))
    return recommendations


# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters & Details)")

with st.spinner("Loading movies..."):
    movies = load_movies()
    similarity = load_similarity()

movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Choose a movie:", movie_list)

if st.button("Recommend"):
    recommendations = recommend(selected_movie, movies, similarity)

    if recommendations:
        for title, poster_url, rating, overview, link in recommendations:
            st.subheader(title)
            if poster_url:
                st.image(poster_url, width=250)
            st.write(f"⭐ Rating: {rating}")
            st.write("📖 Overview:")
            st.write(overview)
            st.markdown(f"[🔗 More details]({link})", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.warning("No recommendations found.")
