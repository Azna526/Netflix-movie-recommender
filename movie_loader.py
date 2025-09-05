import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def load_movies():
    # Load a smaller sample dataset
    df = pd.read_csv("movies_metadata_small.csv", low_memory=False)

    # Keep only useful columns
    df = df[['title', 'overview']].dropna()

    return df

def build_text_model(movies_df):
    # Use TF-IDF on movie overviews
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies_df["overview"])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def similar_by_title(title, movies_df, cosine_sim):
    indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()

    if title not in indices:
        return []

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # top 5
    movie_indices = [i[0] for i in sim_scores]
    return movies_df['title'].iloc[movie_indices].tolist()
