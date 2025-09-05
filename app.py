import streamlit as st
import pandas as pd
from movie_loader import load_datasets

st.title("🎬 Netflix Movie Recommender")

# Load data
with st.spinner("Loading dataset from Kaggle..."):
    movies, ratings, credits, keywords, links = load_datasets()

st.success("✅ Dataset loaded successfully!")

st.write("Movies dataset shape:", movies.shape)
st.write("Ratings dataset shape:", ratings.shape)

# (your recommendation logic here)


