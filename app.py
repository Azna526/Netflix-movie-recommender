import streamlit as st
from movie_loader import load_movies, fetch_movie_details

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

# Load dataset safely
try:
    with st.spinner("📥 Loading movies dataset..."):
        movies = load_movies()
except Exception as e:
    st.error("❌ Failed to load movies dataset. Please check Kaggle setup or dataset availability.")
    st.stop()

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

# Show movie details when button clicked
if st.button("🔍 Recommend"):
    try:
        movie_id = movies[movies['title'] == selected_movie]['id'].values[0]
        title, poster_url, rating, overview, link = fetch_movie_details(movie_id)

        st.subheader(title)
        if poster_url:
            st.image(poster_url, width=300)

        st.write(f"⭐ **Rating:** {rating}")
        st.write("📖 **Overview:**")
        st.write(overview)

        if link:
            st.markdown(f"[🔗 View on TMDb]({link})")

    except Exception as e:
        st.error("❌ Failed to fetch movie details. Please check TMDb API key.")

