import streamlit as st
from movie_loader import load_movies, load_similarity, recommend, fetch_movie_details

# ===============================
# Streamlit UI
# ===============================
st.title("🍿 Netflix Movie Recommender (Top 5 with Posters, Ratings, Links & Credits)")

# Load dataset & similarity
try:
    with st.spinner("📥 Loading movies dataset..."):
        movies = load_movies()
        similarity = load_similarity()
except Exception as e:
    st.error("❌ Failed to load dataset or similarity. Check Kaggle setup or files.")
    st.stop()

# Movie selection
movie_list = movies['title'].dropna().drop_duplicates().sort_values().tolist()
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

# Show recommendations
if st.button("🔍 Recommend"):
    try:
        recs = recommend(selected_movie, movies, similarity, top_n=5)

        if recs:
            st.subheader(f"📌 Top 5 recommendations for **{selected_movie}**:")

            for i, rec_title in enumerate(recs, 1):
                try:
                    movie_id = movies[movies['title'] == rec_title]['id'].values[0]
                    title, poster_url, rating, overview, link, credits = fetch_movie_details(movie_id)

                    st.markdown(f"### {i}. {title}")

                    cols = st.columns([1, 2])  # poster left, details right
                    with cols[0]:
                        if poster_url:
                            st.image(poster_url, width=200)
                    with cols[1]:
                        st.write(f"⭐ **Rating:** {rating}")
                        st.write(f"🎭 **Cast:** {', '.join(credits[:5]) if credits else 'N/A'}")
                        st.write("📖 **Overview:**")
                        st.write(overview if overview else "No overview available.")
                        if link:
                            st.markdown(f"[🔗 View on TMDb]({link})")

                    st.markdown("---")

                except Exception as inner_e:
                    st.warning(f"⚠️ Failed to fetch details for {rec_title}: {inner_e}")

        else:
            st.warning("⚠️ No recommendations found for this movie.")

    except Exception as e:
        st.error(f"❌ Recommendation failed: {e}")
