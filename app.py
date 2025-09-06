import streamlit as st
from movie_loader import load_movies, load_similarity, recommend

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender ")

with st.spinner("Loading movies & similarity data..."):
    movies = load_movies()
    similarity = load_similarity()

# Dropdown to pick a movie
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

# Show recommendations when button clicked
if st.button("Recommend"):
    recommendations = recommend(selected_movie, movies, similarity, top_n=5)

    if recommendations:
        for title, poster_url, rating, overview, homepage in recommendations:
            st.subheader(title)

            if poster_url:
                st.image(poster_url, width=250)

            st.write(f"⭐ **Rating:** {rating}")
            st.write("📖 **Overview:**")
            st.write(overview)

            if homepage:
                st.markdown(f"[🔗 More Info]({homepage})", unsafe_allow_html=True)

            st.markdown("---")
    else:
        st.warning("❌ No recommendations found. Try another movie!")
