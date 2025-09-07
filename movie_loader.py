import pandas as pd
import pickle
import requests
import io

# GitHub raw URLs (replace with your repo username + branch)
MOVIES_URL = "https://raw.githubusercontent.com/Azna526/Netflix-movie-recommender/main/processed_movies.csv"
SIM_URL = "https://raw.githubusercontent.com/Azna526/Netflix-movie-recommender/main/similarity.pkl"

def load_movies():
    try:
        return pd.read_csv(MOVIES_URL)
    except Exception as e:
        raise FileNotFoundError(f"❌ Could not load processed_movies.csv from GitHub: {e}")

def load_similarity():
    try:
        response = requests.get(SIM_URL)
        response.raise_for_status()
        return pickle.load(io.BytesIO(response.content))
    except Exception as e:
        raise FileNotFoundError(f"❌ Could not load similarity.pkl from GitHub: {e}")

