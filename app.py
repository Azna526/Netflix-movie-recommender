import streamlit as st
from movie_loader import (
    load_movies,
    load_similarity,
    recommend,
    fetch_movie_details,
)

st.set_page_config(page_title="Netflix Movie Recommender", layout="wide")
st.title("🍿 Netflix Movie Recommender (with TMDb Posters, Ratings & Links)")

with st.spinner("Loading data..."):
    movies = load_movies()
    similarity = load_similarity()
st.success("✅ Data loaded successfully!")

# Movie picker
movie_list = movies["title"].dropna().drop_duplicates().sort_values().tolist()
selected_movie = st.selectbox("🎬 Choose a movie:", movie_list)

# Show selected movie brief
details = fetch_movie_details(selected_movie, movies)
if details:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        if details["poster_url"]:
            st.image(details["poster_url"], use_column_width=True)
        else:
            st.write("No poster available.")
    with col_b:
        st.subheader(details["title"])
        st.markdown(f"**⭐ Rating:** {details['rating']:.1f}")
        if details["link"]:
            st.markdown(f"[TMDb page]({details['link']})")
        if details["overview"]:
            st.caption(details["overview"])

st.write("---")

# Recommendations
if st.button("🔎 Recommend"):
    recs = recommend(selected_movie, movies, similarity, top_n=5)
    if not recs:
        st.warning("No recommendations found for this title.")
    else:
        st.subheader(f"Because you watched **{selected_movie}**, you might like:")
        for rec in recs:
            c1, c2 = st.columns([1, 3])
            with c1:
                if rec["poster_url"]:
                    st.image(rec["poster_url"], use_column_width=True)
                else:
                    st.write("No poster")
            with c2:
                st.markdown(f"### {rec['title']}")
                st.markdown(f"**⭐ Rating:** {rec['rating']:.1f}")
                if rec["link"]:
                    st.markdown(f"[TMDb link]({rec['link']})")
                if rec["overview"]:
                    st.caption(rec["overview"])

