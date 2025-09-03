import pandas as pd
from pathlib import Path

DATA = Path.cwd() / "data"

# Preview first 5 rows of each Excel file
print("MOVIE.xlsx:")
print(pd.read_excel(DATA / "MOVIE.xlsx", engine="openpyxl").head(), "\n")

print("GENRE.xlsx:")
print(pd.read_excel(DATA / "GENRE.xlsx", engine="openpyxl").head(), "\n")

print("MOVIE_GENRE.xlsx:")
print(pd.read_excel(DATA / "MOVIE_GENRE.xlsx", engine="openpyxl").head(), "\n")
