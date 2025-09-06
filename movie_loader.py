import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_FILE = os.path.join(BASE_DIR, "movies_metadata.csv")

def load_movies():
    """Load the movies dataset with required preprocessing."""
    movies = pd.read_csv(MOVIES_FILE, low_memory=False)

    # Ensure title column
    if "title" not in movies.columns:
        raise ValueError("❌ No 'title' column found in movies_metadata.csv")

    # Keep minimal useful columns
    keep_cols = ["id", "title", "overview", "genres"]
    movies = movies[[c for c in keep_cols if c in movies.columns]]

    # Fill blanks
    for col in ["overview", "genres"]:
        if col in movies.columns:
            movies[col] = movies[col].fillna("")

    # Tags = overview + genres (lightweight bag of words)
    movies["tags"] = movies["overview"].astype(str) + " " + movies["genres"].astype(str)

    print("✅ Movies loaded:", movies.shape)
    return movies

def build_text_model(movies):
    """Build text similarity model (bag-of-words + cosine similarity)."""
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies["tags"].astype(str)).toarray()
    similarity = cosine_similarity(vectors)

    print("✅ Similarity matrix shape:", similarity.shape)
    if similarity.shape[0] != movies.shape[0]:
        print("⚠️ Shape mismatch between movies and similarity!")
    else:
        print("✅ Shapes match correctly 🎉")
    return similarity

def similar_by_title(title, movies, similarity, top_n=5):
    """Return indices of most similar movies given a title."""
    matches = movies[movies["title"].str.lower() == title.lower()]
    if matches.empty:
        return []
    idx = matches.index[0]
    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return [i for i, _ in distances]

# Debug run
if __name__ == "__main__":
    movies = load_movies()
    similarity = build_text_model(movies)
    print("Sanity check → Movies:", movies.shape, "| Similarity:", similarity.shape)
