#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd

print(pd.__version__)


# In[3]:


movies = pd.read_csv("data/movies_metadata.csv", low_memory=False)
ratings = pd.read_csv("data/ratings.csv")




# In[5]:


import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


# In[ ]:


from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(tag):
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV
    }
    return tag_dict.get(tag[0].upper(), wordnet.NOUN)

def lemmatize_sentence(sentence):
    tokens = word_tokenize(sentence)        # tokenize sentence
    pos_tags = pos_tag(tokens)              # part-of-speech tagging
    return " ".join([lemmatizer.lemmatize(word, get_wordnet_pos(pos)) 
                     for word, pos in pos_tags])


# In[ ]:


import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer  # Fixed: 'fasture'->'feature', 'TfIdFVectorizer'->'TfidfVectorizer'
from nltk import word_tokenize, pos_tag  # Fixed: 'top_tag'->'pos_tag'
from nltk.stem.wordnet import WordNetLemmatizer  # Fixed: 'nordnet'->'wordnet', 'NordNetImmersion'->'WordNetLemmatizer'
from sklearn.metrics.pairwise import cosine_similarity  # Fixed: 'palvoids'->'pairwise', 'cosine_dimilarity'->'cosine_similarity
import pickle  # Fixed: 'picks'->'pickle' (this was correct)


# In[6]:


movies = pd.read_csv('movies_metadata.csv')
ratings = pd.read_csv('ratings_small.csv')   # or ratings.csv depending on which one you want
credits = pd.read_csv('credits.csv')
keywords = pd.read_csv('keywords.csv')
links = pd.read_csv('links.csv')
links_small = pd.read_csv('links_small.csv')


# In[ ]:


movies.info()


# In[ ]:


movies.columns


# In[7]:


import ast

# The Kaggle movies_metadata.csv already has genres
movies['genres'] = movies['genres'].fillna('[]').apply(ast.literal_eval)
movies['genres'] = movies['genres'].apply(
    lambda x: [d['name'] for d in x] if isinstance(x, list) else []
)

print(movies[['title', 'genres']].head())


# In[8]:


movies['genres_str'] = movies['genres'].apply(lambda x: " ".join(x) + " ")


# In[10]:


import ast

# Fill NaNs first
movies['genres'] = movies['genres'].fillna('[]')

# Convert strings to list if needed
def parse_genres(x):
    if isinstance(x, str):
        return ast.literal_eval(x)
    elif isinstance(x, list):
        return x
    else:
        return []

movies['genres'] = movies['genres'].apply(parse_genres)

# Extract just the genre names (if it's a list of dicts)
movies['genres'] = movies['genres'].apply(
    lambda x: [d['name'] for d in x] if isinstance(x, list) and len(x) > 0 and isinstance(x[0], dict) else x
)

# Combine into single string
movies['genres_str'] = movies['genres'].apply(lambda x: " ".join(x))



# In[3]:


import pandas as pd

import ast

# Load movies_metadata.csv first
movies = pd.read_csv("movies_metadata.csv", low_memory=False)

# Parse the genres column
movies['genres'] = movies['genres'].fillna('[]').apply(ast.literal_eval)
movies['genres'] = movies['genres'].apply(
    lambda x: [d['name'] for d in x] if isinstance(x, list) else []
)

# Optional: create a string version of genres for text-based analysis
movies['genres_str'] = movies['genres'].apply(lambda x: " ".join(x))


# In[4]:


movies.info()


# In[5]:


movies.isna().sum()


# In[6]:


movies = movies.iloc[movies['overview'].dropna().index]


# In[7]:


movies = movies.fillna(' ')


# In[9]:


movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')


# In[10]:


movies = movies.sort_values(by=['release_date'], ascending=False)


# In[11]:


movies = movies.fillna(' ')
movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
movies = movies.sort_values(by=['release_date'], ascending=False)


# In[12]:


movies.dropna(inplace=True)


# In[15]:


import pandas as pd
import ast

# 1) Load the Kaggle file (same folder as your notebook).
#    If your CSVs are inside a subfolder named "data", change to "data/movies_metadata.csv".
movies = pd.read_csv("movies_metadata.csv", low_memory=False)

# 2) Safe parser for the 'genres' column (handles strings like "[{'id': 28, 'name': 'Action'}, ...]").
def parse_genres(val):
    if pd.isna(val):
        return []
    if isinstance(val, list):
        # already parsed
        return [d.get('name', '') for d in val if isinstance(d, dict)]
    if isinstance(val, str):
        try:
            data = ast.literal_eval(val)
            if isinstance(data, list):
                return [d.get('name', '') for d in data if isinstance(d, dict)]
        except Exception:
            return []
    return []

movies["genres_list"] = movies["genres"].apply(parse_genres)
# Optional: squash spaces in genre names so they behave like tags (e.g., "Science Fiction" -> "ScienceFiction")
movies["genres_str"] = movies["genres_list"].apply(lambda lst: " ".join(g.replace(" ", "") for g in lst))

# 3) Ensure text columns exist, fill NaNs with empty strings
for col in ["overview", "tagline", "title"]:
    if col not in movies.columns:
        movies[col] = ""  # create empty if missing (rare)
    movies[col] = movies[col].fillna("").astype(str)

# 4) Build the Tags column (Kaggle version)
movies["Tags"] = (
    movies["genres_str"] + " " +
    movies["overview"] + " " +
    movies["tagline"] + " " +
    movies["title"]
).str.strip()

# 5) Dates: Kaggle uses 'release_date' (lowercase). Coerce bad/missing values.
if "release_date" in movies.columns:
    movies["release_date"] = pd.to_datetime(movies["release_date"], errors="coerce")
    movies = movies.sort_values("release_date", ascending=False)

# 6) Quick sanity check
print(movies[["title", "genres_list", "Tags"]].head(3).to_string(index=False))



# In[16]:


movies['Tags'] = movies['Tags'].str.lower()


# In[17]:


movies.reset_index(inplace=True)


# In[18]:


#work with first 10000 movies due to memory space
movies = movies[:10000]


# In[19]:


def lemmatize_sentence(sentence):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(sentence)
    pos_tags = pos_tag(tokens)

    def get_wordnet_pos(tag):
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag[0].upper(), wordnet.NOUN)

    return " ".join([lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in pos_tags])


# In[20]:


print(movies.columns)


# In[21]:


movies.columns = movies.columns.str.lower().str.strip()
print(movies.columns)


# In[25]:


from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
movies['tags_'] = movies['overview'].astype(str).fillna("").apply(lemmatize_sentence)


# In[26]:


from sklearn.feature_extraction.text import TfidfVectorizer  

vectorizer = TfidfVectorizer(max_features=7000, stop_words='english', lowercase=True)
 


# In[27]:


vectors = vectorizer.fit_transform(movies['tags']).toarray()


# In[28]:


# Step 1: Import everything you need
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Step 2: Vectorize your movie tags column
vectorizer = CountVectorizer(max_features=5000, stop_words='english')
vectors = vectorizer.fit_transform(movies['tags']).toarray()  # now 'vectors' exists

# Step 3: Build similarity matrix
similarity = cosine_similarity(vectors)

print("Vectors shape:", vectors.shape)
print("Similarity shape:", similarity.shape)


# In[29]:


similarity = cosine_similarity(vectors) 


# In[30]:


similarity.shape


# In[34]:


def recommendation(title, data): 
    try:
        movie_index = data[data['TITLE'] == title].index[0] 
    except:
        return "Movie not currently in the database"
    distances = similarity[movie_index] 
    movies_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:10]
    for i in movies_list:
        print(data.iloc[i[0]].TITLE) 


# In[33]:


movies['original_title'][:100].values


# In[35]:


def recommendation(title, data, similarity=similarity):
    try:
        # find index of the movie
        movie_index = data[data['original_title'].str.lower() == title.lower()].index[0]
    except IndexError:
        return "Movie not currently in the database"
    
    # get similarity scores
    distances = list(enumerate(similarity[movie_index]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]
    
    # return top 5 similar movies
    return data['original_title'].iloc[[i[0] for i in distances]].tolist()


# In[57]:


recommendation("Jumanji", data=movies)


# In[58]:


recommendation("Copycat", data=movies)


# In[39]:


movies.to_csv('data.csv', index=False)


# In[40]:


import pickle
pickle.dump(similarity, open('similarity.pkl','wb'))


# In[41]:


import nltk
nltk.data.path.append(r"C:\Users\kazia\AppData\Roaming\nltk_data")



# In[41]:


import os
os.listdir("data")



# In[42]:


import pandas as pd

# Load the available CSV files
movies = pd.read_csv("data/movies_metadata.csv", low_memory=False)
credits = pd.read_csv("data/credits.csv")
keywords = pd.read_csv("data/keywords.csv")
ratings = pd.read_csv("data/ratings.csv")

print(movies.shape, credits.shape, keywords.shape, ratings.shape)


# In[44]:


import pandas as pd

# load the movie metadata
movies = pd.read_csv("data/movies_metadata.csv", low_memory=False)
print(movies.shape)
movies.head()


# In[45]:


ratings = pd.read_csv("data/ratings.csv")
print(ratings.shape)
ratings.head()


# In[46]:


keywords = pd.read_csv("data/keywords.csv")
print(keywords.shape)
keywords.head()


# In[43]:


import os
os.listdir("data")


# In[47]:


import pandas as pd

# Load metadata files
movies = pd.read_csv("data/movies_metadata.csv", low_memory=False)
credits = pd.read_csv("data/credits.csv")
keywords = pd.read_csv("data/keywords.csv")
links = pd.read_csv("data/links.csv")

# Load ratings
ratings = pd.read_csv("data/ratings.csv")

print("Movies:", movies.shape)
print("Credits:", credits.shape)
print("Keywords:", keywords.shape)
print("Ratings:", ratings.shape)
print("Links:", links.shape)


# In[48]:


import os
print(os.getcwd())


# In[53]:


import pandas as pd
df = pd.read_csv("movies_metadata.csv", low_memory=False)
print(df.shape)




# In[56]:


import os
import pandas as pd

BASE_DIR = os.getcwd()   # your project folder

# Define file paths
movies_file   = os.path.join(BASE_DIR, "movies_metadata.csv")
ratings_file  = os.path.join(BASE_DIR, "ratings.csv")
credits_file  = os.path.join(BASE_DIR, "credits.csv")
keywords_file = os.path.join(BASE_DIR, "keywords.csv")
links_file    = os.path.join(BASE_DIR, "links.csv")

# Load datasets
movies   = pd.read_csv(movies_file, low_memory=False)
ratings  = pd.read_csv(ratings_file)
credits  = pd.read_csv(credits_file)
keywords = pd.read_csv(keywords_file)
links    = pd.read_csv(links_file)

# Sanity check
print("Movies:", movies.shape)
print("Ratings:", ratings.shape)
print("Credits:", credits.shape)
print("Keywords:", keywords.shape)
print("links:", links.shape)


# In[54]:


links_file = os.path.join(BASE_DIR, "links.csv")
links = pd.read_csv(links_file)

print("Links:", links.shape)
print(links.head())


# In[ ]:

import pandas as pd

movies = pd.read_csv(r"C:\Users\kazia\Downloads\Netflix-movie-recommender\movies_metadata.csv")
ratings = pd.read_csv(r"C:\Users\kazia\Downloads\Netflix-movie-recommender\ratings_small.csv")




# In[ ]:




