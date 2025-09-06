import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

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

# Show recommendations when button clicked
if st.button("Recommend"):
    recommendations = recommend(selected_movie, movies, similarity, top_n=6)  # 6 movies for grid

    if not recommendations:
        st.error("No recommendations found.")
    else:
        cols = st.columns(3)  # 3 movies per row

        for idx, (title, poster_url, rating, overview, link) in enumerate(recommendations):
            with cols[idx % 3]:
                st.image(poster_url, width=200, caption=title)
                st.markdown(f"⭐ **{rating}**")
                st.markdown(f"[🔗 View on TMDb]({link})")
                with st.expander("📖 Overview"):
                    st.write(overview)
