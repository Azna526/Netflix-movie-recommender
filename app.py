import streamlit as st
from movie_loader import movies, similarity
import requests
import numpy as np

# ===============================
# Load Data
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

with st.spinner("Loading movies..."):
    movies = load_movies()
    similarity = load_similarity()

movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

# ===============================
# TMDb API Helpers
# ===============================
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url).json()
    
    poster = f"https://image.tmdb.org/t/p/w500{response.get('poster_path')}" if response.get("poster_path") else None
    title = response.get("title", "Unknown")
    rating = response.get("vote_average", "N/A")
    overview = response.get("overview", "No overview available")
    homepage = response.get("homepage", None)
    
    return title, poster, rating, overview, homepage

# ===============================
# Recommend Movies
# ===============================
def recommend(movie_title, top_n=6):
    idx = movies[movies['title'] == movie_title].index[0]
    distances = similarity[idx]
    recommended_indices = np.argsort(distances)[::-1][1:top_n+1]

    recommendations = []
    for i in recommended_indices:
        movie_id = movies.iloc[i]['id']
        recommendations.append(fetch_movie_details(movie_id))
    return recommendations

# ===============================
# Show Recommendations (Grid)
# ===============================
if st.button("🔍 Recommend"):
    recs = recommend(selected_movie, top_n=6)
    
    cols = st.columns(2)  # 2 cards per row
    for i, (title, poster, rating, overview, homepage) in enumerate(recs):
        with cols[i % 2]:
            st.subheader(title)
            if poster:
                st.image(poster, width=250)
            st.write(f"⭐ Rating: {rating}")
            st.write("📖 Overview:")
            st.write(overview[:200] + "..." if len(overview) > 200 else overview)
            if homepage:
                st.markdown(f"[🔗 More Info]({homepage})", unsafe_allow_html=True)
            st.markdown("---")
