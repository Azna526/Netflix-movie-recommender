import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

# ===============================
# Load Data
# ===============================
st.title("🍿 Netflix Movie Recommender (with NLP)")

with st.spinner("Loading movies..."):
    movies = load_movies()
    similarity = load_similarity()

# ===============================
# Select Movie
# ===============================
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

# ===============================
# Show Recommendations
# ===============================
if st.button("Recommend"):
    results = recommend(selected_movie, movies, similarity, top_n=5)

    if results:
        for movie in results:
            st.subheader(movie["title"])
            if movie["poster_url"]:
                st.image(movie["poster_url"], width=250)
            st.write(f"⭐ Rating: {movie['rating']}")
            st.write(f"👥 Cast: {movie['credits']}")
            st.write("📖 Overview:")
            st.write(movie["overview"])
            st.markdown(f"[🔗 View on TMDb]({movie['tmdb_url']})")
            st.markdown("---")
    else:
        st.warning("⚠️ No recommendations found.")
