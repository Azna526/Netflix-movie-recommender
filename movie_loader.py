import os
import pandas as pd

# Base directory = where your script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define file paths (make sure files are in the same folder as this script)
MOVIES_FILE   = os.path.join(BASE_DIR, "movies_metadata.csv")
RATINGS_FILE  = os.path.join(BASE_DIR, "ratings.csv")
CREDITS_FILE  = os.path.join(BASE_DIR, "credits.csv")
KEYWORDS_FILE = os.path.join(BASE_DIR, "keywords.csv")

# Load datasets
movies   = pd.read_csv(MOVIES_FILE, low_memory=False)
ratings  = pd.read_csv(RATINGS_FILE)
credits  = pd.read_csv(CREDITS_FILE)
keywords = pd.read_csv(KEYWORDS_FILE)

# Sanity check
print("Movies:", movies.shape)
print("Ratings:", ratings.shape)
print("Credits:", credits.shape)
print("Keywords:", keywords.shape)
