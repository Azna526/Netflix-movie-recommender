def fetch_movie_details(movie_id):
    # Movie details
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)

    if response.status_code != 200:
        return "Unknown", "", "N/A", "Details not available.", "", "No credits available."

    data = response.json()
    title = data.get("title", "Unknown Title")
    poster_path = data.get("poster_path")
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview", "No overview available.")
    link = f"https://www.themoviedb.org/movie/{movie_id}"

    # Credits (actors, director)
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=en-US"
    credits_response = requests.get(credits_url)
    credits_data = credits_response.json() if credits_response.status_code == 200 else {}

    cast = [c['name'] for c in credits_data.get("cast", [])[:3]]
    director = [c['name'] for c in credits_data.get("crew", []) if c['job'] == "Director"]
    credits = f"Stars: {', '.join(cast)} | Director: {', '.join(director)}"

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    return title, poster_url, rating, overview, link, credits
