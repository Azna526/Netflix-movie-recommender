from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data
def load_datasets():
    api = KaggleApi()
    api.authenticate()
    dataset = "rounakbanik/the-movies-dataset"
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        api.dataset_download_files(dataset, path=data_dir, unzip=True)

    movies = pd.read_csv(os.path.join(data_dir, "movies_metadata.csv"), low_memory=False)

    # Clean IDs
    movies = movies.dropna(subset=["id"])
    movies["id"] = movies["id"].astype(str).str.replace(r"\D", "", regex=True)
    movies = movies[movies["id"] != ""]
    movies["id"] = movies["id"].astype(int)

    # Select only needed columns
    movies = movies[["id", "original_title", "overview", "release_date", "vote_average"]]
    movies = movies.dropna(subset=["overview"])

    # Build similarity matrix dynamically
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies["overview"])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return movies, similarity

