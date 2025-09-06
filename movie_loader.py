import os
import json
import pathlib
import pandas as pd
import streamlit as st

# -------------------------------
# Read secrets
# -------------------------------
K_USERNAME = st.secrets["kaggle"]["username"]
K_KEY = st.secrets["kaggle"]["key"]

# Optional: TMDb key if you use it elsewhere
TMDB_API_KEY = st.secrets["tmdb"]["api_key"]

DATASET_SLUG = "rounakbanik/the-movies-dataset"
CSV_NAME = "movies_metadata.csv"


def _ensure_kaggle_credentials():
    """Write ~/.kaggle/kaggle.json so KaggleApi can authenticate."""
    cred = {"username": K_USERNAME, "key": K_KEY}
    cfg_dir = pathlib.Path.home() / ".kaggle"
    cfg_dir.mkdir(exist_ok=True)
    cfg_path = cfg_dir / "kaggle.json"
    with open(cfg_path, "w") as f:
        json.dump(cred, f)
    os.chmod(cfg_path, 0o600)  # required by Kaggle
    os.environ["KAGGLE_CONFIG_DIR"] = str(cfg_dir)


def _download_movies_dataset():
    """Download and unzip the dataset using KaggleApi (no subprocess)."""
    from kaggle.api.kaggle_api_extended import KaggleApi

    _ensure_kaggle_credentials()
    api = KaggleApi()
    api.authenticate()
    # This produces a zip in the current directory and unzips it
    api.dataset_download_files(DATASET_SLUG, path=".", unzip=True)


def load_movies():
    """
    Ensure movies_metadata.csv exists, download if needed, then load a clean
    (id, title) dataframe.
    """
    dataset_path = CSV_NAME

    if not os.path.exists(dataset_path):
        try:
            _download_movies_dataset()
        except Exception as e:
            st.error(
                "Couldn't download from Kaggle. Check that your Kaggle secrets are correct "
                "and that the dataset is accessible to your account."
            )
            # Re-raise so Streamlit logs the traceback
            raise

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} not found after Kaggle download.")

    # Load and clean
    df = pd.read_csv(dataset_path, low_memory=False, usecols=["id", "title"])
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id", "title"]).astype({"id": "int64"})
    df = df.drop_duplicates().reset_index(drop=True)
    return df
