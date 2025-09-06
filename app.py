import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

# ===============================
# Load movies + similarity matrix
# ===============================
with st.spinner("Loading data..."):
    movies = load_movies()
    similarity = load_similarity()

# ===============================
# User Input
# ===============================
movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

if st.button("🔍 Recommend"):
    recommendations = recommend(selected_movie, movies, similarity, top_n=6)

    if recommendations:
        st.subheader(f"🎯 Top Recommendations for *{selected_movie}*:")

        # Show movies in grid (3 per row)
        cols = st.columns(3)

        for idx, (title, poster, rating, overview, link) in enumerate(recommendations):
            with cols[idx % 3]:
                st.image(poster, width=180)
                st.markdown(f"**{title}**")
                st.write(f"⭐ {rating}")
                st.markdown(f"[🔗 View on TMDb]({link})", unsafe_allow_html=True)
                st.caption(overview[:120] + "..." if len(overview) > 120 else overview)

    else:
        st.error("❌ No recommendations found.")
