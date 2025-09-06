import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

# ===============================
# Load Data
# ===============================
st.set_page_config(page_title="Netflix Movie Recommender", layout="wide")

movies = load_movies()
similarity = load_similarity()

# ===============================
# UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

movie_title = st.selectbox("🎬 Choose a movie:", movies['title'].values)

if st.button("🔍 Recommend"):
    recommendations = recommend(movie_title, movies, similarity)

    if not recommendations:
        st.error("No recommendations found. Try another movie.")
    else:
        st.subheader(f"Movies similar to **{movie_title}**:")

        cols = st.columns(5)  # Show 5 movies side by side
        for idx, movie in enumerate(recommendations):
            with cols[idx % 5]:
                if movie["poster"]:
                    st.image(movie["poster"], use_column_width=True)
                st.markdown(f"**{movie['title']}**")
                st.write(f"⭐ {movie['rating']}")
                st.caption(movie['overview'][:150] + "...")
                if movie["homepage"]:
                    st.markdown(f"[🔗 More Info]({movie['homepage']})")
