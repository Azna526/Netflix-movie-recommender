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

# Show recommendations
if st.button("Recommend"):
    st.subheader(f"🎬 Recommended movies similar to: {selected_movie}")
    recommendations = recommend(selected_movie, movies, similarity, top_n=5)

    if not recommendations:
        st.warning("No recommendations found. Try another movie.")
    else:
        for title, poster_url, rating, overview, link in recommendations:
            with st.container():
                st.image(poster_url, width=200)
                st.markdown(f"### [{title}]({link})")  # clickable link
                st.write(f"⭐ Rating: {rating}")
                st.write("📖 Overview:")
                st.write(overview)
                st.markdown("---")
