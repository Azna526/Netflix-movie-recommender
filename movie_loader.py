import os
import pandas as pd

def load_movies():
    file_path = "movies_metadata.csv"

    # If file doesn't exist, download from Kaggle
    if not os.path.exists(file_path):
        # Authenticate with Kaggle (you must set Kaggle username & key in Streamlit Secrets)
        kaggle_username = os.getenv("KAGGLE_USERNAME")
        kaggle_key = os.getenv("KAGGLE_KEY")

        if kaggle_username is None or kaggle_key is None:
            raise ValueError("Kaggle API credentials not found. Please set them in Streamlit secrets.")

        # Save kaggle.json for API use
        with open("kaggle.json", "w") as f:
            f.write(f'{{"username":"{kaggle_username}","key":"{kaggle_key}"}}')

        os.system("mkdir -p ~/.kaggle")
        os.system("mv kaggle.json ~/.kaggle/")
        os.system("chmod 600 ~/.kaggle/kaggle.json")

        # Download the dataset
        os.system("kaggle datasets download -d rounakbanik/the-movies-dataset -p .")
        os.system("unzip -o the-movies-dataset.zip -d .")

    # Load movies
    movies = pd.read_csv(file_path, low_memory=False)
    movies = movies[['id', 'title']].dropna().drop_duplicates().reset_index(drop=True)
    return movies
