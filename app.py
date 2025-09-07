# app.py
import streamlit as st
from movie_loader import load_movies, recommend

st.set_page_config(page_title="Netflix Movie Recommender (Top 5)", layout="wide")
st.title("🍿 Netflix Movie Recommender")

# ===============================
# Load movies
# ===============================
with st.spinner("📥 Loading movies dataset..."):
    try:
        movies = load_movies()
        st.success("✅ Movies loaded.")
    except Exception as e:
        st.error("❌ Failed to load movies dataset. See Manage app logs or check Kaggle/TMDb secrets.")
        st.stop()

# ===============================
# Movie selection
# ===============================
movie_list = movies["title"].drop_duplicates().sort_values().tolist()
selected = st.selectbox("🎬 Choose a movie:", movie_list)

# ===============================
# Recommendations
# ===============================
if st.button("🔍 Recommend top 5"):
    with st.spinner("🔎 Finding similar movies..."):
        try:
            recs = recommend(selected, movies, top_n=5)
        except Exception as e:
            st.error("❌ Recommendation failed. See Manage app logs.")
            raise

    if not recs:
        st.warning("⚠️ No recommendations found.")
    else:
        # Dynamically adjust columns (desktop: 5, tablet: 3, mobile: 2)
        num_recs = len(recs)
        if num_recs >= 5:
            cols = st.columns(5)
        elif num_recs >= 3:
            cols = st.columns(3)
        else:
            cols = st.columns(2)

        for i, rec in enumerate(recs):
            col = cols[i % len(cols)]
            with col:
                st.subheader(rec.get("title", "Unknown"))
                poster = rec.get("poster_url", "")
                if poster:
                    st.image(poster, use_container_width=True)  # ✅ fixed warning
                st.write(f"⭐ **Rating:** {rec.get('rating', 'N/A')}")
                st.write(rec.get("overview", "")[:400] + ("..." if len(rec.get("overview", "")) > 400 else ""))
                st.write(f"🎭 **Credits:** {rec.get('credits','')}")
                link = rec.get("link", "")
                if link:
                    st.markdown(f"[🔗 View on TMDb]({link})")
