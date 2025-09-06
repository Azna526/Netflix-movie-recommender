import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ================================
# Paths for cached files
# ================================
MOVIES_PATH = "processed_movies.csv"
SIM_PATH = "similarity.pkl"
RAW_DATASET = "movies_metadata.csv"

# ================================
# Generate processed dataset if missing
# ================================
def generate_data():
    if not os.path.exists(RAW_DATASET):
        raise FileNotFoundError(
            f"{RAW_DATASET} not found. Please make sure it's downloaded via Kaggle or provided."
        )

    print("⚡ Generating processed_movies.csv and similarity.pkl ...")

    movies = pd.read_csv(RAW_DATASET, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().reset_index(drop=True)

    # TF-IDF vectorizer on overviews
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['overview'])

    # Compute similarity
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Save processed data
    movies.to_csv(MOVIES_PATH, index=False)
    with open(SIM_PATH, "wb") as f:
        pickle.dump(similarity, f)

    print("✅ Files generated successfully.")

# ================================
# Loaders
# ================================
def load_movies():
    if not os.path.exists(MOVIES_PATH):
        generate_data()
    return pd.read_csv(MOVIES_PATH)

def load_similarity():
    if not os.path.exists(SIM_PATH):
        generate_data()
    with open(SIM_PATH, "rb") as f:
        return pickle.load(f)

# ================================
# Recommend function
# ================================
def recommend(title, movies, similarity, top_n=5):
    if title not in movies['title'].values:
        return []
    idx = movies[movies['title'] == title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return movies.iloc[[i[0] for i in scores]]['title'].tolist()

