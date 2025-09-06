def generate_data():
    raw_path = "movies_metadata.csv"
    processed_path = "processed_movies.csv"

    # If raw data not present, download from Kaggle
    if not os.path.exists(raw_path):
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "rounakbanik/the-movies-dataset",
            "-p", ".", "--unzip"
        ], check=True)

    # Preprocess to smaller dataset
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    movies = pd.read_csv(raw_path, low_memory=False)
    movies = movies[['id', 'title', 'overview']].dropna().reset_index(drop=True)

    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['overview'])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Save processed dataset
    movies.to_csv(processed_path, index=False)
    with open("similarity.pkl", "wb") as f:
        pickle.dump(similarity, f)

    return movies


def load_movies():
    dataset_path = "processed_movies.csv"
    if not os.path.exists(dataset_path):
        return generate_data()
    return pd.read_csv(dataset_path, low_memory=False)
