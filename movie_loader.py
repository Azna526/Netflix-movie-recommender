import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_datasets():
    # Load dataset
    movies = pd.read_csv("movies_metadata.csv", low_memory=False)

    # Make sure we only keep valid titles
    movies = movies[['title', 'overview']].dropna()

    # --- Build TF-IDF model for overviews ---
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['overview'])

    # --- Compute cosine similarity matrix ---
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # ✅ Return only 2 values
    return movies, similarity


def build_text_model():
    """Optional helper if you want to expose TF-IDF + similarity separately"""
    movies, similarity = load_datasets()
    return movies, similarity


def similar_by_title(title, movies, similarity, top_n=5):
    """Find top_n similar movies by title."""
    if title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]

    return movies.iloc[movie_indices]['title'].tolist()


