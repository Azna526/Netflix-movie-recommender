import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the big dataset (only once in Kaggle/local)
movies = pd.read_csv("movies_metadata.csv", low_memory=False)

# Keep only useful columns
movies = movies[['id', 'title', 'overview']].dropna().reset_index(drop=True)

# Create TF-IDF on overviews
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(movies['overview'])

# Cosine similarity
similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Save reduced dataset
movies[['id', 'title']].to_csv("processed_movies.csv", index=False)

# Save similarity matrix
with open("similarity.pkl", "wb") as f:
    pickle.dump(similarity, f)

print("✅ processed_movies.csv & similarity.pkl created")
