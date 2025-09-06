import streamlit as st
import pickle
import pandas as pd
import requests

# Load the saved movie data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Your TMDb API key
TMDB_API_KEY = "0d309fbe7061ac46435369d2349288ba"

def fetch_movie_details(movie_id):
    """Fetch movie details from TMDb API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    data = requests.get(url).json()
    
    poster_path = data.get('poster_path')
    poster_url = "https://image.tmdb.org/t/p/w500" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "poster_url": poster_url,
        "rating": data.get("vote_average"),
        "release_date": data.get("release_date"),
        "genres": ", ".join([g['name'] for g in data.get("genres", [])]),
        "overview": data.get("overview", "No description available.")
    }

def recommend(movie):
    """Recommend similar movies with details."""
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    recommended_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    for i in recommended_list:
        movie_id = movies.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommended_movies.append(details)
    return recommended_movies

# Streamlit UI
st.title("🍿 Netflix-Style Movie Recommender")


selected_movie = st.selectbox(
    "Choose a movie:",
    movies['title'].values
)

if st.button("Recommend"):
    recommendations = recommend(selected_movie)

    for movie in recommendations:
        tmdb_url = f"https://www.themoviedb.org/movie/{movie['id']}"
        st.markdown(
            f"""
            <div style="display:flex; margin-bottom:30px;">
                <div style="margin-right:20px;">
                    <a href="{tmdb_url}" target="_blank">
                        <img src="{movie['poster_url']}" width="150">
                    </a>
                </div>
                <div>
                    <h3><a href="{tmdb_url}" target="_blank">{movie['title']}</a></h3>
                    <p><b>Rating:</b> {movie['rating']} ⭐</p>
                    <p><b>Release Date:</b> {movie['release_date']}</p>
                    <p><b>Genres:</b> {movie['genres']}</p>
                    <p style="max-width:600px;">{movie['overview']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
