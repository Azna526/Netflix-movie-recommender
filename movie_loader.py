import os
import pandas as pd
import pickle
from kaggle.api.kaggle_api_extended import KaggleApi

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SIM_FILE = os.path.join(BASE_DIR, "similarity.pkl")

def download_dataset():
    """Download The Movies Dataset from Kaggle if not available locally."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    api = KaggleApi()
    api.authenticate()

    dataset = "rounakbanik/the-movies-dataset"
    print("⬇️ Downloading dataset from Kaggle...")
    api.dataset_download_files(dataset, path=DATA_DIR, unzip=True)
    print("✅ Download complete!")

def load_datasets():
    """Load all datasets + similarity pickle (if available)."""
    movies_file = os.path.join(DATA_DIR, "movies_metadata.csv")

    # Download if missing
    if not os.path.exists(movies_file):
        download_dataset()

    # Load CSV datasets
    movies   = pd.read_csv(os.path.join(DATA_DIR, "movies_metadata.csv"), low_memory=False)
    ratings  = pd.read_csv(os.path.join(DATA_DIR, "ratings_small.csv"))
    credits  = pd.read_csv(os.path.join(DATA_DIR, "credits.csv"))
    keywords = pd.read_csv(os.path.join(DATA_DIR, "keywords.csv"))
    links    = pd.read_csv(os.path.join(DATA_DIR, "links_small.csv"))

    # Load similarity pickle if available
    similarity = None
    if os.path.exists(SIM_FILE):
        with open(SIM_FILE, "rb") as f:
            similarity = pickle.load(f)

    print("✅ Loaded datasets:")
    print("Movies:", movies.shape)
    print("Ratings:", ratings.shape)
    print("Credits:", credits.shape)
    print("Keywords:", keywords.shape)
    print("Links:", links.shape)
    if similarity is not None:
        print("Similarity matrix:", similarity.shape)
    else:
        print("⚠️ No similarity.pkl found. Run your notebook to generate it.")

    return {
        "movies": movies,
        "ratings": ratings,
        "credits": credits,
        "keywords": keywords,
        "links": links,
        "similarity": similarity
    }

# Example run (debug)
if __name__ == "__main__":
    data = load_datasets()
