import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

# ===============================
# Load Data
# ===============================
movies = load_movies()
similarity = load_similarity()

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

selected_movie = st.selectbox("🎬 Choose a movie:", movies['title'].values)

if st.button("🔍 Recommend"):
    recommendations = recommend(selected_movie, movies, similarity)

    if not recommendations:
        st.warning("No recommendations found.")
    else:
        st.subheader("Recommended Movies:")
        cols = st.columns(5)

        for idx, rec in enumerate(recommendations):
            with cols[idx % 5]:
                if rec["poster"]:
                    st.image(rec["poster"], use_container_width=True)
                st.markdown(f"**[{rec['title']}]({rec['link']})**")
                st.caption(f"⭐ {rec['rating']}")
