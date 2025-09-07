import streamlit as st
from movie_loader import load_movies, recommend

# ==============================
# Page Config
# ==============================
st.set_page_config(page_title="Netflix Movie Recommender", layout="wide")

# ==============================
# Custom CSS for Netflix Style
# ==============================
st.markdown("""
<style>
/* Background */
.stApp {
    background-color: #141414;
    color: #fff;
    font-family: Arial, sans-serif;
}

/* Title */
.big-title {
    font-size: 42px !important;
    color: #E50914;
    text-align: center;
    font-weight: bold;
    margin-bottom: 20px;
}

/* Buttons */
div.stButton > button {
    background-color: #E50914;
    color: white;
    font-size: 18px;
    padding: 10px 25px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #b20710;
}

/* Movie Card */
.recommend-card {
    background-color: #1c1c1c;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.6);
    margin-bottom: 20px;
    transition: transform 0.3s;
}
.recommend-card:hover {
    transform: scale(1.05);
}

/* Poster */
.movie-poster {
    border-radius: 10px;
    margin-bottom: 10px;
    max-width: 100%;
}

/* Links */
a {
    color: #E50914;
    text-decoration: none;
    font-weight: bold;
}
a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# Title
# ==============================
st.markdown('<p class="big-title">🍿 Netflix Movie Recommender</p>', unsafe_allow_html=True)

# ==============================
# Load Movies
# ==============================
with st.spinner("📥 Loading movies dataset..."):
    try:
        movies = load_movies()
        st.success("✅ Movies loaded.")
    except Exception as e:
        st.error("❌ Failed to load movies dataset. Check logs or secrets.")
        st.stop()

# ==============================
# Movie Selection
# ==============================
movie_list = movies["title"].drop_duplicates().sort_values().tolist()
selected = st.selectbox("🎬 Choose a movie:", movie_list)

# ==============================
# Recommend Button
# ==============================
if st.button("🔍 Recommend Top 5"):
    with st.spinner("🔎 Finding similar movies..."):
        try:
            recs = recommend(selected, movies, top_n=5)
        except Exception as e:
            st.error("❌ Recommendation failed. See logs.")
            st.stop()

    if not recs:
        st.warning("⚠️ No recommendations found.")
    else:
        cols = st.columns(5)
        for i, rec in enumerate(recs):
            with cols[i % 5]:
                st.markdown(f"""
                <div class="recommend-card">
                    <h4>{rec.get("title", "Unknown")}</h4>
                    <img src="{rec.get("poster_url", "")}" class="movie-poster"><br>
                    ⭐ {rec.get("rating", "N/A")}<br
