import streamlit as st
from movie_loader import load_movies, fetch_movie_details

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters & Links)")

with st.spinner("Loading movies..."):
    movies = load_movies()

movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    movie_id = movies[movies['title'] == selected_movie]['id'].values[0]
    title, poster_url, rating, overview, movie_url = fetch_movie_details(movie_id)

    st.subheader(title)
    if poster_url:
        st.image(poster_url, width=300)

    st.write(f"⭐ Rating: {rating}")
    st.write("📖 Overview:")
    st.write(overview)

    if movie_url:
        st.markdown(f"[🔗 View on TMDb]({movie_url})", unsafe_allow_html=True)
