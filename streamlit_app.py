import streamlit as st
import pandas as pd

st.title("🎬 Netflix Movie Recommender")

# Load small dataset to avoid GitHub file size issues
movies = pd.read_csv("movies_metadata.csv", low_memory=False, nrows=5000)

st.write("Sample data from movies dataset:")
st.write(movies.head())

# TODO: Hook your recommender functions here
