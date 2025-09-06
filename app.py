import streamlit as st
import numpy as np
from movie_loader import load_movies, fetch_movie_details, load_similarity

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

with st.spinner("Loading movies..."):
    movies = load_movies()
    similarity = load_similarity()

# Dropdown to pick a movie
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

# Function to recommend top 5 movies
def recommend(movie_title):
    idx = movies[movies['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in scores[1:6]]
    return movies.iloc[top_indices]

# Show recommendations
if st.button("Recommend"):
    recommended_movies = recommend(selected_movie)

    for _, row in recommended_movies.iterrows():
        movie_id = row['id']
        title, poster_url, rating, overview = fetch_movie_details(movie_id)

        st.subheader(title)
        if poster_url:
            st.image(poster_url, width=250)
        st.write(f"⭐ Rating: {rating}")
        st.write("📖 Overview:")
        st.write(overview)

        # 🔗 Add TMDb link
        tmdb_link = f"https://www.themoviedb.org/movie/{movie_id}"
        st.markdown(f"[🔗 View on TMDb]({tmdb_link})", unsafe_allow_html=True)

        st.markdown("---")

