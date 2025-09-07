import streamlit as st
from movie_loader import load_movies, build_similarity, recommend, fetch_movie_details

st.title("🍿 Netflix Movie Recommender (Top 5 with Posters, Ratings, Links & Credits)")

try:
    with st.spinner("📥 Loading movies dataset..."):
        movies = load_movies()
        similarity = build_similarity(movies)
except Exception as e:
    st.error("❌ Failed to load dataset.")
    st.stop()

# Movie selection
movie_list = movies['title'].dropna().drop_duplicates().sort_values().tolist()
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

# Recommend
if st.button("🔍 Recommend"):
    rec_ids = recommend(selected_movie, movies, similarity, top_n=5)

    if rec_ids:
        st.subheader(f"📌 Top 5 recommendations for **{selected_movie}**:")

        for i, movie_id in enumerate(rec_ids, 1):
            try:
                title, poster_url, rating, overview, link, credits = fetch_movie_details(movie_id)

                st.markdown(f"### {i}. {title}")
                cols = st.columns([1, 2])
                with cols[0]:
                    if poster_url:
                        st.image(poster_url, width=200)
                with cols[1]:
                    st.write(f"⭐ **Rating:** {rating}")
                    st.write(f"🎭 **Cast:** {', '.join(credits) if credits else 'N/A'}")
                    st.write("📖 **Overview:**")
                    st.write(overview if overview else "No overview available.")
                    if link:
                        st.markdown(f"[🔗 View on TMDb]({link})")

                st.markdown("---")

            except Exception as inner_e:
                st.warning(f"⚠️ Could not fetch details for movie ID {movie_id}: {inner_e}")
    else:
        st.warning("⚠️ No recommendations found.")
