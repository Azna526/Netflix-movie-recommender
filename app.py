import streamlit as st
from movie_loader import load_movies, load_similarity, fetch_movie_details, recommend

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters & Details)")

with st.spinner("Loading movies and similarity matrix..."):
    movies = load_movies()
    similarity = load_similarity()

movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Recommend"):
    rec_ids = recommend(selected_movie, movies, similarity, top_n=5)

    if not rec_ids:
        st.error("❌ No recommendations found. Please try another movie.")
    else:
        for movie_id in rec_ids:
            title, poster_url, rating, overview, tmdb_url = fetch_movie_details(movie_id)

            st.subheader(title)
            if poster_url:
                st.image(poster_url, width=200)
            st.write(f"⭐ Rating: {rating}")
            st.write("📖 Overview:")
            st.write(overview)
            st.markdown(f"[🔗 More details on TMDb]({tmdb_url})", unsafe_allow_html=True)
            st.markdown("---")

