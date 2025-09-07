# app.py
import streamlit as st
from movie_loader import load_movies, recommend

# ===============================
# Streamlit Page Setup
# ===============================
st.set_page_config(page_title="Netflix Movie Recommender", layout="wide")
st.title("🍿 Netflix Movie Recommender (Top 5 with Posters, Ratings, Links & Credits)")

# ===============================
# Load Movies
# ===============================
with st.spinner("📥 Loading movies dataset..."):
    try:
        movies = load_movies()
        st.success("✅ Movies loaded successfully.")
    except Exception as e:
        st.error("❌ Failed to load movies dataset. Please check Kaggle/TMDb setup.")
        st.stop()

# ===============================
# Movie Selection
# ===============================
movie_list = movies["title"].drop_duplicates().sort_values().tolist()
selected = st.selectbox("🎬 Choose a movie:", movie_list)

# ===============================
# Recommend Button
# ===============================
if st.button("🔍 Recommend top 5"):
    with st.spinner("🔎 Finding similar movies..."):
        try:
            recs = recommend(selected, movies, top_n=5)
        except Exception as e:
            st.error("❌ Recommendation failed. Check logs for details.")
            st.stop()

    if not recs:
        st.warning("⚠️ No recommendations found.")
    else:
        # Show recommendations in 5 columns
        cols = st.columns(5)
        for i, rec in enumerate(recs):
            col = cols[i % 5]
            with col:
                title = rec.get("title", "Unknown")
                poster = rec.get("poster_url", "")
                rating = rec.get("rating", "N/A")
                overview = rec.get("overview", "")
                credits = rec.get("credits", "N/A")
                link = rec.get("link", "#")

                card_html = f"""
                <div style="text-align:center; padding:10px;">
                    <h4>{title}</h4>
                    <img src="{poster}" style="width:100%; border-radius:10px;"><br>
                    ⭐ {rating}<br>
                    <p>{overview[:120]}{"..." if len(overview) > 120 else ""}</p>
                    <p><b>Credits:</b> {credits}</p>
                    <a href="{link}" target="_blank">🔗 View on TMDb</a>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
