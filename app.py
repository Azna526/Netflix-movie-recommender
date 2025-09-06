import streamlit as st
from movie_loader import load_movies, load_similarity, recommend, fetch_movie_details

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

# Load dataset safely
with st.spinner("Loading movies..."):
    try:
        movies = load_movies()
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        st.stop()

# Load similarity safely
with st.spinner("Loading similarity data..."):
    try:
        similarity = load_similarity()
    except Exception as e:
        st.error(f"❌ Failed to load similarity data: {e}")
        st.stop()

# Dropdown to pick a movie
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

# Show recommendations
if st.button("Recommend"):
    try:
        recommended_movies = recommend(selected_movie, movies, similarity)

        for movie_id in recommended_movies:
            title, poster_url, rating, overview = fetch_movie_details(movie_id)

            st.subheader(title)
            if poster_url:
                st.image(poster_url, width=300)
            st.write(f"⭐ Rating: {rating}")
            st.write("📖 Overview:")
            st.write(overview)
            st.markdown(
                f"[🔗 More Info](https://www.themoviedb.org/movie/{movie_id})",
                unsafe_allow_html=True
            )
            st.markdown("---")
    except Exception as e:
        st.error(f"⚠️ Failed to generate recommendations: {e}")
