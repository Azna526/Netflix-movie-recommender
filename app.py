import streamlit as st
from movie_loader import load_movies, load_similarity, recommend, fetch_movie_details

# ===============================
# App Title
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

# ===============================
# Load Data
# ===============================
try:
    movies = load_movies()
    similarity = load_similarity(movies)
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie you like:", movie_list)

# ===============================
# Recommend Button
# ===============================
if st.button("Recommend"):
    recommendations = recommend(selected_movie, movies, similarity)

    if recommendations:
        st.write("### Recommended Movies:")
        cols = st.columns(5)  # display posters in a row

        for i, (mid, title) in enumerate(recommendations):
            title, poster_url, rating, overview, link = fetch_movie_details(mid)

            with cols[i % 5]:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                st.markdown(f"**[{title}]({link})**")
                st.caption(f"⭐ {rating}")
    else:
        st.warning("⚠️ No recommendations found.")
