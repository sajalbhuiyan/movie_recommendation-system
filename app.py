import os
import requests

def download_from_gdrive(gdrive_url, dest_path):
    import re
    session = requests.Session()
    file_id_match = re.search(r'/d/([\w-]+)', gdrive_url)
    if not file_id_match:
        raise ValueError(f"Invalid Google Drive URL: {gdrive_url}")
    file_id = file_id_match.group(1)
    base_url = "https://drive.google.com/uc?export=download"
    response = session.get(base_url, params={"id": file_id}, stream=True)
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
    if token:
        response = session.get(base_url, params={"id": file_id, "confirm": token}, stream=True)
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)

# Download required .pkl files if not present
files_to_download = [
    ("https://drive.google.com/file/d/1aUNbwWu3gOhb2rPQJacu1yAJoNZfHfAC/view?usp=sharing", "movie_list.pkl"),
    ("https://drive.google.com/file/d/1vNeQkY_GfAh6xfWLydssSvh6ErRSi4Ep/view?usp=sharing", "similarity.pkl"),
    ("https://drive.google.com/file/d/1ILsFbv8WWf-5ElXV7B37oj3PwJR3-gPJ/view?usp=sharing", "svd_model.pkl"),
]
for url, filename in files_to_download:
    if not os.path.exists(filename):
        print(f"Downloading {filename} from Google Drive...")
        download_from_gdrive(url, filename)

import streamlit as st




# Sidebar navigation
with st.sidebar:
    nav = st.radio("Navigation", ["Home", "Discover", "Mood-Based", "Watchlist", "History", "Analytics", "Profile", "Sign In"], key="nav_radio")
    if st.session_state.get("current_username"):
        if st.button("Sign Out"):
            st.session_state.current_user = None
            st.session_state.current_username = None
            st.session_state.page = "Home"      

# Main page routing
if nav == "Profile":
    st.title("User Profile")
    if st.session_state.get("current_user"):
        user_id = st.session_state.current_user
        username = st.session_state.get("current_username", str(user_id))
        st.markdown(f"**Username:** {username}")
        st.markdown(f"**User ID:** {user_id}")
        import pandas as pd, os
        ratings_count = 0
        avg_rating = None
        if os.path.exists("user_reviews.csv"):
            reviews_df = pd.read_csv("user_reviews.csv", header=0)
            user_reviews = reviews_df[reviews_df["user"].astype(str) == str(user_id)]
            ratings_count = len(user_reviews)
            if ratings_count > 0:
                avg_rating = user_reviews["rating"].astype(float).mean()
        st.markdown(f"**Number of Ratings:** {ratings_count}")
        if avg_rating is not None:
            st.markdown(f"**Average Rating:** {avg_rating:.2f}")
        if st.button("Edit Info"):
            st.info("Feature coming soon: Edit profile info.")
    else:
        st.warning("Please sign in to view your profile.")
    st.stop()
elif nav == "Analytics":
    st.title("Analytics & Insights")
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os
    # Rating histogram
    if os.path.exists("user_reviews.csv"):
        reviews_df = pd.read_csv("user_reviews.csv", header=0)
        st.subheader("Rating Distribution")
        fig, ax = plt.subplots()
        sns.histplot(reviews_df["rating"].astype(float), bins=5, kde=True, ax=ax)
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        # Ratings per user (top raters)
        st.subheader("Ratings per User (Top Raters)")
        user_counts = reviews_df["user"].value_counts().head(10)
        fig_user, ax_user = plt.subplots()
        ax_user.bar(user_counts.index.astype(str), user_counts.values)
        ax_user.set_xlabel("User")
        ax_user.set_ylabel("Number of Ratings")
        plt.xticks(rotation=45)
        st.pyplot(fig_user)

        # Number of reviews per movie (top reviewed movies)
        st.subheader("Number of Reviews per Movie (Top Reviewed)")
        movie_counts = reviews_df["title"].value_counts().head(10)
        fig_movie, ax_movie = plt.subplots()
        ax_movie.bar(movie_counts.index.astype(str), movie_counts.values)
        ax_movie.set_xlabel("Movie Title")
        ax_movie.set_ylabel("Number of Reviews")
        plt.xticks(rotation=45)
        st.pyplot(fig_movie)

        # Top genres bar chart & average rating per genre
        if os.path.exists("movies.csv") and "movie_id" in reviews_df:
            movies_df = pd.read_csv("movies.csv")
            # Map movie_id to genres
            genre_counts = {}
            genre_ratings = {}
            for _, row in reviews_df.iterrows():
                mid = int(row["movie_id"])
                genres = []
                if "genres" in movies_df.columns:
                    genres_str = movies_df[movies_df["id"] == mid]["genres"].values
                    if len(genres_str) > 0:
                        import ast #Abstract Syntax Trees.
                        try:
                            genres = [g["name"] for g in ast.literal_eval(genres_str[0]) if "name" in g]
                        except Exception:
                            pass
                for g in genres:
                    genre_counts[g] = genre_counts.get(g, 0) + 1
                    genre_ratings.setdefault(g, []).append(float(row["rating"]))
            if genre_counts:
                st.subheader("Top Genres by Ratings")
                fig2, ax2 = plt.subplots()
                genres_sorted = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
                ax2.bar([g for g, _ in genres_sorted], [c for _, c in genres_sorted])
                ax2.set_xlabel("Genre")
                ax2.set_ylabel("Number of Ratings")
                plt.xticks(rotation=45)
                st.pyplot(fig2)
            if genre_ratings:
                st.subheader("Average Rating per Genre")
                avg_ratings = {g: sum(r)/len(r) for g, r in genre_ratings.items() if len(r) > 0}
                genres_sorted = sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)
                fig3, ax3 = plt.subplots()
                ax3.bar([g for g, _ in genres_sorted], [r for _, r in genres_sorted])
                ax3.set_xlabel("Genre")
                ax3.set_ylabel("Average Rating")
                plt.xticks(rotation=45)
                st.pyplot(fig3)

    else:
        st.info("No ratings data found. Please rate some movies first.")
    st.stop()

elif nav == "Sign In" or st.session_state.get("page") == "Sign In":
    st.title("Sign In / Sign Up")
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    with tab1:
        st.subheader("Sign In")
        signin_email = st.text_input("Email", key="signin_email")
        signin_password = st.text_input("Password", type="password", key="signin_password")
        if st.button("Sign In", key="signin_btn"):
            users = load_users_from_csv()
            user = users.get(signin_email)
            if user and bcrypt.checkpw(signin_password.encode(), user["password"].encode()):
                st.session_state.current_user = user["user_id"]
                st.session_state.current_username = signin_email
                st.session_state.page = "home"
                st.success("Signed in successfully!")
            else:
                st.error("Invalid email or password.")
    with tab2:
        st.subheader("Sign Up")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up", key="signup_btn"):
            users = load_users_from_csv()
            if signup_email in users:
                st.error("Email already registered. Please sign in.")
            else:
                new_user_id = max([u["user_id"] for u in users.values()], default=0) + 1
                save_user_to_csv(signup_email, signup_password, new_user_id)
                st.success("Account created! Please sign in.")
    st.stop()

# ...existing code for other sections (Home, Discover, Mood-Based, Watchlist, History)...
import streamlit as st
import pandas as pd
import pickle
import requests
import os
import csv
from datetime import datetime
import uuid
import numpy as np
import scipy.sparse as sp
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import bcrypt

# TMDB API Key (use environment variable for security)
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "9ef5ae6fc8b8f484e9295dc97d8d32ea")


@st.cache_resource
def load_pickles():
    import time
    def robust_pickle_load(filename, url):
        # Check file exists and is not empty
        if not os.path.exists(filename) or os.path.getsize(filename) < 1000:
            st.warning(f"{filename} missing or too small, attempting to download...")
            download_from_gdrive(url, filename)
            time.sleep(1)
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            # Print first 100 bytes for debugging
            try:
                with open(filename, 'rb') as f:
                    first_bytes = f.read(100)
                st.error(f"Failed to load {filename}: {e}. First bytes: {first_bytes}")
            except Exception as e2:
                st.error(f"Failed to load {filename}: {e}. Also failed to read file: {e2}")
            return None

    files = [
        ("movie_list.pkl", "https://drive.google.com/file/d/1aUNbwWu3gOhb2rPQJacu1yAJoNZfHfAC/view?usp=sharing"),
        ("similarity.pkl", "https://drive.google.com/file/d/1vNeQkY_GfAh6xfWLydssSvh6ErRSi4Ep/view?usp=sharing"),
        ("svd_model.pkl", "https://drive.google.com/file/d/1ILsFbv8WWf-5ElXV7B37oj3PwJR3-gPJ/view?usp=sharing"),
    ]
    loaded = [robust_pickle_load(fname, url) for fname, url in files]
    if any(x is None for x in loaded):
        st.error("One or more model files could not be loaded. See above for details.")
    return tuple(loaded)

movies, similarity, svd_model = load_pickles()

# Custom CSS for dark theme, styling, and watchlist/history cards
st.markdown("""
<style>
body {
    background-color: #121212;
    color: white;
    margin: 0;
    padding: 0;
}
.stApp {
    background-color: #121212;
    color: white;
}
h1, h2, h3 {
    color: white;
}
.stButton>button {
    background-color: #4a4a4a;
    color: white;
    border-radius: 5px;
    width: 100%;
    min-width: 80px;
    font-size: 1em;
}
.stTextInput>div>input, .stSelectbox>div>select {
    background-color: #2a2a2a;
    color: white;
    border-radius: 5px;
    width: 100%;
    font-size: 1em;
}
.genre-button {
    background-color: #2a2a2a;
    color: white;
    border-radius: 15px;
    padding: 5px 15px;
    margin: 5px;
    display: inline-block;
    font-size: 1em;
}
.movie-card {
    background-color: #1e1e1e;
    border-radius: 10px;
    padding: 10px;
    margin: 10px auto;
    width: 100%;
    max-width: 320px;
    display: block;
    vertical-align: top;
    box-sizing: border-box;
}
.movie-card img {
    width: 100%;
    height: auto;
    border-radius: 10px;
}
.watchlist-container, .history-container {
    display: flex;
    flex-wrap: wrap;
    overflow-x: auto;
    white-space: normal;
    padding: 10px 0;
}
.nav-bar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: #1a1a1a;
}
.nav-links button {
    background: none;
    border: none;
    color: white;
    margin: 0 15px;
    text-decoration: none;
    cursor: pointer;
    font-size: 1em;
}
.sign-in-btn {
    background-color: #333;
    color: white;
    padding: 5px 15px;
    border-radius: 5px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    font-size: 1em;
}
@media (max-width: 900px) {
    .movie-card {
        max-width: 90vw;
        margin: 10px auto;
    }
    .nav-bar {
        flex-direction: column;
        align-items: flex-start;
    }
    .nav-links button {
        margin: 5px 0;
    }
}
@media (max-width: 600px) {
    .movie-card {
        max-width: 98vw;
        margin: 10px auto;
        font-size: 0.95em;
    }
    h1, h2, h3 {
        font-size: 1.2em;
    }
    .nav-bar {
        padding: 5px;
    }
    .stButton>button, .sign-in-btn {
        font-size: 0.95em;
        padding: 8px 10px;
    }
}
</style>
""", unsafe_allow_html=True)

# Cache TMDB API calls for performance
@st.cache_data
def fetch_popular_movies():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(f"Failed to fetch popular movies: HTTP {response.status_code}")
            return []
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            st.warning("Invalid popular movies response")
            return []
        movies_list = []
        for movie in data.get("results", []):
            movies_list.append({
                "id": movie.get("id", 0),
                "title": movie.get("title", "Unknown"),
                "rating": movie.get("vote_average", 0.0),
                "description": movie.get("overview", "No description available"),
                "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}" if movie.get("poster_path") else "https://via.placeholder.com/200x300?text=No+Poster",
                "runtime": movie.get("runtime", 120),
                "release_date": movie.get("release_date", "2000-01-01"),
                "genres": movie.get("genre_ids", [])
            })
        return movies_list
    except requests.exceptions.RequestException as e:
        st.warning(f"Network error fetching popular movies: {e}")
        return []
    except Exception as e:
        st.warning(f"Error fetching popular movies: {e}")
        return []

@st.cache_data
def fetch_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(f"Failed to fetch genres: HTTP {response.status_code}")
            return {}
        data = response.json()
        if not isinstance(data, dict) or "genres" not in data:
            st.warning("Invalid genres response")
            return {}
        return {genre["id"]: genre["name"] for genre in data.get("genres", [])}
    except Exception as e:
        st.warning(f"Error fetching genres: {e}")
        return {}

@st.cache_data
def fetch_movies_by_genre(genre_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&language=en-US&page=1"
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(f"Failed to fetch movies for genre: HTTP {response.status_code}")
            return []
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            st.warning("Invalid genre movies response")
            return []
        movies_list = []
        for movie in data.get("results", []):
            movies_list.append({
                "id": movie.get("id", 0),
                "title": movie.get("title", "Unknown"),
                "rating": movie.get("vote_average", 0.0),
                "description": movie.get("overview", "No description available"),
                "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}" if movie.get("poster_path") else "https://via.placeholder.com/200x300?text=No+Poster",
                "runtime": movie.get("runtime", 120),
                "release_date": movie.get("release_date", "2000-01-01"),
                "genres": movie.get("genre_ids", [])
            })
        return movies_list
    except Exception as e:
        st.warning(f"Error fetching movies for genre: {e}")
        return []

@st.cache_data
def fetch_poster(movie_id):
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = session.get(url, timeout=5)
        
        if response.status_code == 204:
            st.warning(f"No poster available for movie ID {movie_id} (HTTP 204)")
            return "https://via.placeholder.com/200x300?text=No+Poster"
        elif response.status_code != 200:
            st.warning(f"Failed to fetch poster for movie ID {movie_id}: HTTP {response.status_code}")
            return "https://via.placeholder.com/200x300?text=Error"
        
        data = response.json()
        if not isinstance(data, dict):
            st.warning(f"Invalid poster response for movie ID {movie_id}")
            return "https://via.placeholder.com/200x300?text=Error"
        
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/200x300?text=No+Poster"
    except requests.exceptions.ConnectionError as e:
        st.warning(f"Network error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/200x300?text=Network+Error"
    except requests.exceptions.Timeout:
        st.warning(f"Request timed out fetching poster for movie ID {movie_id}")
        return "https://via.placeholder.com/200x300?text=Timeout"
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/200x300?text=Error"
    except Exception as e:
        st.warning(f"Unexpected error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/200x300?text=Error"

@st.cache_data
def fetch_trailer(movie_id):
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}&language=en-US"
        response = session.get(url, timeout=5)
        
        if response.status_code == 204:
            st.warning(f"No trailer available for movie ID {movie_id} (HTTP 204)")
            return None
        elif response.status_code != 200:
            st.warning(f"Failed to fetch trailer for movie ID {movie_id}: HTTP {response.status_code}")
            return None
        
        data = response.json()
        if not isinstance(data, dict) or "results" not in data:
            st.warning(f"Invalid trailer response for movie ID {movie_id}")
            return None
        
        for video in data.get('results', []):
            if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                return f"https://www.youtube.com/watch?v={video['key']}"
        return None
    except requests.exceptions.ConnectionError as e:
        st.warning(f"Network error fetching trailer for movie ID {movie_id}. Please check internet connection.")
        return None
    except requests.exceptions.Timeout:
        st.warning(f"Request timed out fetching trailer for movie ID {movie_id}. Please try again later.")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching trailer for movie ID {movie_id}: {e}")
        return None
    except Exception as e:
        st.warning(f"Unexpected error fetching trailer for movie ID {movie_id}: {e}")
        return None

@st.cache_data
def fetch_movie_details(movie_id):
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = session.get(url, timeout=5)
        
        if response.status_code == 204:
            st.warning(f"No details available for movie ID {movie_id} (HTTP 204)")
            return {"rating": 0.0, "description": "No description available"}
        elif response.status_code != 200:
            st.warning(f"Failed to fetch details for movie ID {movie_id}: HTTP {response.status_code}")
            return {"rating": 0.0, "description": "No description available"}
        
        data = response.json()
        if not isinstance(data, dict):
            st.warning(f"Invalid details response for movie ID {movie_id}")
            return {"rating": 0.0, "description": "No description available"}
        
        return {
            "rating": data.get("vote_average", 0.0),
            "description": data.get("overview", "No description available")
        }
    except Exception as e:
        st.warning(f"Error fetching movie details for movie ID {movie_id}: {e}")
        return {"rating": 0.0, "description": "No description available"}

@st.cache_data
def fetch_movie_metadata(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=keywords"
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(f"Failed to fetch metadata for movie ID {movie_id}: HTTP {response.status_code}")
            return {"genres": [], "keywords": [], "title": "Unknown"}
        data = response.json()
        return {
            "genres": [g['id'] for g in data.get('genres', [])],
            "keywords": [k['id'] for k in data.get('keywords', {}).get('keywords', [])[:5]],
            "title": data.get('title', 'Unknown'),
            "rating": data.get('vote_average', 0.0),
            "description": data.get('overview', 'No description available')
        }
    except Exception as e:
        st.warning(f"Error fetching metadata for movie ID {movie_id}: {e}")
        return {"genres": [], "keywords": [], "title": "Unknown", "rating": 0.0, "description": "No description available"}

@st.cache_data
def fetch_mood_based_movies(_cache_key, genre_ids, max_runtime=None, min_year=None, max_year=None, keywords=None, adult=False):
    movies_list = []
    base_url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US&sort_by=vote_average.desc&vote_count.gte=100"
    
    # Construct query parameters
    query_params = []
    if genre_ids:
        query_params.append(f"with_genres={','.join(map(str, genre_ids))}")
    query_params.append(f"include_adult={adult}")
    
    # Try multiple query variations for diversity
    attempts = [
        # Full query
        query_params + (
            ([f"with_runtime.lte={max_runtime}"] if max_runtime else []) +
            ([f"primary_release_date.gte={min_year}-01-01"] if min_year else []) +
            ([f"primary_release_date.lte={max_year}-12-31"] if max_year else []) +
            ([f"with_keywords={keywords}"] if keywords else []) +
            ["page=1"]
        ),
        # Relax runtime and keywords
        query_params + (
            ([f"primary_release_date.gte={min_year}-01-01"] if min_year else []) +
            ([f"primary_release_date.lte={max_year}-12-31"] if max_year else []) +
            ["page=1"]
        ),
        # Random page for diversity
        query_params + (
            ([f"primary_release_date.gte={min_year}-01-01"] if min_year else []) +
            ([f"primary_release_date.lte={max_year}-12-31"] if max_year else []) +
            [f"page={np.random.randint(1, 5)}"]
        ),
        # Broad query
        query_params + ["page=1"],
    ]
    
    for params in attempts:
        url = base_url + "&" + "&".join(params)
        try:
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[204, 429, 500, 502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))
            response = session.get(url, timeout=5)
            if response.status_code != 200:
                continue
            data = response.json()
            if not isinstance(data, dict) or "results" not in data:
                continue
            for movie in data.get("results", [])[:5]:
                movies_list.append({
                    "id": movie.get("id", 0),
                    "title": movie.get("title", "Unknown"),
                    "rating": movie.get("vote_average", 0.0),
                    "description": movie.get("overview", "No description available"),
                    "poster": f"https://image.tmdb.org/t/p/w500/{movie.get('poster_path')}" if movie.get("poster_path") else "https://via.placeholder.com/200x300?text=No+Poster",
                    "runtime": movie.get("runtime", 120),
                    "release_date": movie.get("release_date", "2000-01-01"),
                    "genres": movie.get("genre_ids", [])
                })
            if movies_list:
                # Shuffle for diversity
                np.random.shuffle(movies_list)
                return movies_list[:5]
        except Exception as e:
            continue
    
    # Fallback to popular movies with warning
    st.warning("No movies found matching your mood-based criteria. Showing popular movies.")
    return fetch_popular_movies()

# Content-based recommendation
def recommend_content_based(movie_title):
    if similarity is None or movies.empty:
        st.error("Content-based recommendations unavailable due to missing data.")
        return [], []
    try:
        index = movies[movies['title'] == movie_title].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_names = []
        recommended_posters = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].id
            recommended_names.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))
        return recommended_names, recommended_posters
    except IndexError:
        st.error(f"Movie '{movie_title}' not found in the database.")
        return [], []
    except Exception as e:
        st.error(f"Error generating content-based recommendations: {e}")
        return [], []

# Fallback content-based recommendation using TMDB genres
def recommend_content_based_tmdb(movie_title, num_recommendations=5):
    if movies.empty:
        st.error("Content-based recommendations unavailable due to missing movie data.")
        return [], []
    
    try:
        movie_id = movies[movies['title'] == movie_title]['id'].iloc[0] if movie_title in movies['title'].values else None
        if not movie_id:
            st.error(f"Movie '{movie_title}' not found.")
            return [], []
        
        # Fetch metadata for the target movie
        target_metadata = fetch_movie_metadata(movie_id)
        target_genres = set(target_metadata['genres'])
        
        # Compute similarities with other movies
        similarities = []
        for movie in movies.itertuples():
            if movie.title == movie_title:
                continue
            metadata = fetch_movie_metadata(movie.id)
            genres = set(metadata['genres'])
            # Jaccard similarity for genres
            intersection = len(target_genres & genres)
            union = len(target_genres | genres)
            sim = intersection / union if union > 0 else 0
            similarities.append((movie.id, movie.title, sim))
        
        # Sort by similarity and select top recommendations
        similarities = sorted(similarities, key=lambda x: x[2], reverse=True)[:num_recommendations]
        recommended_names = [title for _, title, _ in similarities]
        recommended_posters = [fetch_poster(movie_id) for movie_id, _, _ in similarities]
        return recommended_names, recommended_posters
    
    except IndexError:
        st.error(f"Movie '{movie_title}' not found in the database.")
        return [], []
    except Exception as e:
        st.error(f"Error generating TMDB-based content recommendations: {e}")
        return [], []

# Collaborative filtering recommendation (using SVD)
def recommend_collaborative(user_id):
    if svd_model is None or movies.empty:
        st.error("Collaborative recommendations unavailable due to missing data.")
        return [], []
    try:
        # Get movies already rated by the user
        rated_movie_ids = set()
        if os.path.exists("user_reviews.csv"):
            reviews_df = pd.read_csv("user_reviews.csv", header=0)
            reviews_df['user'] = reviews_df['user'].astype(str)
            uid = str(user_id)
            rated_movie_ids = set(reviews_df[reviews_df['user'] == uid]['movie_id'].astype(int).tolist())

        # Predict ratings for movies not yet rated
        predictions = [(movie_id, svd_model.predict(user_id, movie_id).est)
                       for movie_id in movies['id'] if movie_id not in rated_movie_ids]
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
        recommended_names = []
        recommended_posters = []
        for movie_id, _ in predictions[:3]:
            movie_title = movies[movies['id'] == movie_id]['title'].iloc[0]
            recommended_names.append(movie_title)
            recommended_posters.append(fetch_poster(movie_id))
        return recommended_names, recommended_posters
    except Exception as e:
        st.error(f"Error generating collaborative recommendations: {e}")
        return [], []

# Hybrid recommendation (combining content-based and SVD-based collaborative filtering)
def recommend_hybrid(movie_title, user_id, num_recommendations=3, content_weight=0.5):
    if movies.empty:
        st.error("Hybrid recommendations unavailable due to missing movie data.")
        return [], []
    
    try:
        # Get content-based recommendations
        if similarity is not None:
            content_names, content_posters = recommend_content_based(movie_title)
        else:
            content_names, content_posters = recommend_content_based_tmdb(movie_title, num_recommendations * 2)
        content_scores = {name: score for name, score in zip(content_names, np.linspace(1.0, 0.5, len(content_names)))}
        
        # Get collaborative recommendations (SVD-based)
        collab_names, collab_posters = recommend_collaborative(user_id)
        collab_scores = {name: score for name, score in zip(collab_names, np.linspace(1.0, 0.5, len(collab_names)))}
        
        # Combine scores
        combined_scores = {}
        all_names = set(content_names) | set(collab_names)
        
        for name in all_names:
            content_score = content_scores.get(name, 0.0) * content_weight
            collab_score = collab_scores.get(name, 0.0) * (1.0 - content_weight)
            combined_scores[name] = content_score + collab_score
        
        # Sort by combined score and exclude the input movie
        filtered_scores = [(name, score) for name, score in combined_scores.items() if name != movie_title]
        top_movies = sorted(filtered_scores, key=lambda x: x[1], reverse=True)[:num_recommendations]
        recommended_names = []
        recommended_posters = []
        for name, _ in top_movies:
            if name in content_names:
                idx = content_names.index(name)
                recommended_names.append(name)
                recommended_posters.append(content_posters[idx])
            elif name in collab_names:
                idx = collab_names.index(name)
                recommended_names.append(name)
                recommended_posters.append(collab_posters[idx])
            else:
                movie_id = movies[movies['title'] == name]['id'].iloc[0] if name in movies['title'].values else None
                if movie_id:
                    recommended_names.append(name)
                    recommended_posters.append(fetch_poster(movie_id))
        
        if not recommended_names:
            st.warning("No hybrid recommendations found. Falling back to mood-based or popular movies.")
            if st.session_state.mood_answers:
                movies_list = recommend_mood_based(st.session_state.mood_answers, fetch_genres())
                return [m['title'] for m in movies_list[:num_recommendations]], [m['poster'] for m in movies_list[:num_recommendations]]
            popular_movies = fetch_popular_movies()
            return [m['title'] for m in popular_movies[:num_recommendations]], [m['poster'] for m in popular_movies[:num_recommendations]]
        
        return recommended_names, recommended_posters
    
    except IndexError:
        st.error(f"Movie '{movie_title}' not found in the database.")
        popular_movies = fetch_popular_movies()
        return [m['title'] for m in popular_movies[:num_recommendations]], [m['poster'] for m in popular_movies[:num_recommendations]]
    except Exception as e:
        st.error(f"Error generating hybrid recommendations: {e}")
        popular_movies = fetch_popular_movies()
        return [m['title'] for m in popular_movies[:num_recommendations]], [m['poster'] for m in popular_movies[:num_recommendations]]

# Mood-based recommendation
def recommend_mood_based(answers, genre_map):
    genre_ids = []
    max_runtime = None
    min_year = None
    max_year = None
    keywords = None
    adult = False

    mood_genres = {
        "Happy": [35, 16, 12],  # Comedy, Animation, Adventure
        "Sad": [18, 10749, 99],  # Drama, Romance, Documentary
        "Stressed": [35, 10749, 10751],  # Comedy, Romance, Family
        "Excited": [28, 53, 878],  # Action, Thriller, Sci-Fi
        "Relaxed": [18, 10749, 99],  # Drama, Romance, Documentary
        "Bored": [28, 35, 12],  # Action, Comedy, Adventure
        "Angry": [53, 28, 18]  # Thriller, Action, Drama
    }
    secondary_genres = {
        "Happy": [10751],  # Family
        "Sad": [36],  # History
        "Stressed": [16],  # Animation
        "Excited": [12],  # Adventure
        "Relaxed": [35],  # Comedy
        "Bored": [878],  # Sci-Fi
        "Angry": [80]  # Crime
    }
    
    if answers.get("mood"):
        genre_ids.extend(mood_genres.get(answers["mood"], []))
        genre_ids.extend(secondary_genres.get(answers["mood"], []))
    
    if answers.get("motivation") == "Yes":
        genre_ids.extend([18, 99])  # Drama, Documentary
        keywords = "inspirational,motivational"
    
    if answers.get("watching_with") in ["Kids", "Family"] or answers.get("occasion") == "Family Night":
        genre_ids.extend([16, 10751])  # Animation, Family
        adult = False
    elif answers.get("occasion") == "Date Night" or answers.get("romantic") == "Yes":
        genre_ids.extend([10749, 35])  # Romance, Comedy
    
    if answers.get("time"):
        if answers["time"] == "Less than 1 hour":
            max_runtime = 90
        elif answers["time"] == "1-2 hours":
            max_runtime = 120
        elif answers["time"] == "2+ hours":
            max_runtime = 180
    
    if answers.get("genre"):
        genre_id = [k for k, v in genre_map.items() if v == answers["genre"]]
        if genre_id:
            genre_ids.append(genre_id[0])
    
    tone_genres = {
        "Light-hearted": [35, 10749],  # Comedy, Romance
        "Serious": [18, 36],  # Drama, History
        "Emotional": [18, 10749],  # Drama, Romance
        "Fun": [35, 12],  # Comedy, Adventure
        "Epic": [12, 28],  # Adventure, Action
        "Thought-provoking": [18, 99]  # Drama, Documentary
    }
    if answers.get("tone"):
        genre_ids.extend(tone_genres.get(answers["tone"], []))
    
    if answers.get("release"):
        if answers["release"] == "New (post-2010)":
            min_year = 2010
        elif answers["release"] == "Classics (pre-2010)":
            max_year = 2010
    
    if answers.get("mature") == "No":
        adult = False
    elif answers.get("mature") == "Yes":
        adult = True
    
    # Remove duplicates and limit genres
    genre_ids = list(set(genre_ids))[:3]
    
    # Fallback genres if none selected
    if not genre_ids:
        genre_ids = [35, 18]  # Comedy, Drama
    
    # Unique cache key for diversity
    cache_key = str(uuid.uuid4()) + str(answers)
    
    return fetch_mood_based_movies(cache_key, genre_ids, max_runtime, min_year, max_year, keywords, adult)

# Save user activity
def save_user_activity(user_id, action, movie_title, movie_id, rating=None):
    try:
        file_exists = os.path.exists("user_activity.csv")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        activity_data = pd.DataFrame([[user_id, action, movie_title, movie_id, rating, timestamp]], 
                                    columns=["user_id", "action", "title", "movie_id", "rating", "timestamp"])
        activity_data.to_csv("user_activity.csv", mode='a', index=False, header=not file_exists, quoting=csv.QUOTE_NONNUMERIC)
    except Exception as e:
        st.warning(f"Error saving user activity: {e}")

# Save user to CSV
def save_user_to_csv(username, password, user_id):
    try:
        file_exists = os.path.exists("users.csv")
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_data = pd.DataFrame([{
            "username": str(username),
            "password": hashed_password,
            "user_id": int(user_id)
        }])
        user_data.to_csv("users.csv", mode='a', index=False, header=not file_exists, quoting=csv.QUOTE_NONNUMERIC)
    except Exception as e:
        st.error(f"Error saving user to CSV: {e}")

# Load users from CSV
def load_users_from_csv():
    if os.path.exists("users.csv"):
        try:
            users_df = pd.read_csv(
                "users.csv",
                dtype={"username": str, "password": str, "user_id": int},
                quoting=csv.QUOTE_NONNUMERIC
            )
            users = {}
            for _, row in users_df.iterrows():
                users[row['username']] = {"password": row['password'], "user_id": row['user_id']}
            return users
        except Exception as e:
            st.warning(f"Error loading users: {e}. Starting with empty user list.")
            return {}
    return {}

# Save watchlist to CSV
def save_watchlist_to_csv(user_id, movie_title, movie_id):
    filename = f"watchlist_{user_id}.csv"
    file_exists = os.path.exists(filename)
    try:
        movie_id = int(movie_id)
        watchlist_data = pd.DataFrame([[movie_title, movie_id]], columns=["title", "movie_id"])
        watchlist_data.to_csv(filename, mode='a', index=False, header=not file_exists, quoting=csv.QUOTE_NONNUMERIC)
    except Exception as e:
        st.error(f"Error saving watchlist for user {user_id}: {e}")

# Load watchlist from CSV
def load_watchlist_from_csv(user_id):
    filename = f"watchlist_{user_id}.csv"
    if os.path.exists(filename):
        try:
            watchlist_df = pd.read_csv(
                filename,
                names=["title", "movie_id"],
                skiprows=1 if os.path.getsize(filename) > 0 else 0,
                on_bad_lines='skip',
                quoting=csv.QUOTE_NONNUMERIC
            )
            watchlist_df = watchlist_df.dropna(subset=["title", "movie_id"])
            watchlist_df["movie_id"] = pd.to_numeric(watchlist_df["movie_id"], errors='coerce', downcast='integer')
            watchlist_df = watchlist_df.dropna(subset=["movie_id"])
            return watchlist_df[["title", "movie_id"]].to_dict('records')
        except Exception as e:
            st.warning(f"Error loading watchlist for user {user_id}: {e}")
            try:
                corrupted_filename = f"watchlist_{user_id}_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                os.rename(filename, corrupted_filename)
                st.info(f"Corrupted watchlist file renamed to {corrupted_filename}. Starting with an empty watchlist.")
            except Exception as rename_e:
                st.error(f"Failed to rename corrupted watchlist file: {rename_e}")
            return []
    return []

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = None
if "show_recommendations" not in st.session_state:
    st.session_state.show_recommendations = False
if "recommendation_type" not in st.session_state:
    st.session_state.recommendation_type = None
if "genre_movies" not in st.session_state:
    st.session_state.genre_movies = []
if "users" not in st.session_state:
    st.session_state.users = load_users_from_csv()
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_username" not in st.session_state:
    st.session_state.current_username = None
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "mood_answers" not in st.session_state:
    st.session_state.mood_answers = {}
if "mood_recommendations" not in st.session_state:
    st.session_state.mood_recommendations = []

# Load watchlist for the current user
if st.session_state.current_user and not st.session_state.watchlist:
    st.session_state.watchlist = load_watchlist_from_csv(st.session_state.current_user)

# Navigation Bar
st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
col_logo, col_links, col_signin = st.columns([1, 4, 1])
# No branding/logo
with col_links:
    col_home, col_discover, col_mood, col_watchlist, col_history = st.columns(5)
    with col_home:
        if st.button("Home", key="nav_home"):
            st.session_state.page = "home"
            st.session_state.show_recommendations = False
            st.session_state.selected_genre = None
    with col_discover:
        if st.button("Discover", key="nav_discover"):
            st.session_state.page = "discover"
    with col_mood:
        if st.button("Mood-Based", key="nav_mood"):
            st.session_state.page = "mood"
    with col_watchlist:
        if st.button("Watchlist", key="nav_watchlist"):
            st.session_state.page = "watchlist"
    with col_history:
        if st.button("History", key="nav_history"):
            st.session_state.page = "history"
with col_signin:
    if st.session_state.current_user:
        if st.button(f"Sign Out ({st.session_state.current_username})", key="nav_signout"):
            st.session_state.current_user = None
            st.session_state.current_username = None
            st.session_state.watchlist = []
            st.session_state.mood_answers = {}
            st.session_state.mood_recommendations = []
            st.session_state.page = "home"
            st.success("Signed out successfully!")
    else:
        if st.button("Sign In", key="nav_signin"):
            st.session_state.page = "signin"
st.markdown("</div>", unsafe_allow_html=True)

# Page Content
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align: center;'>Discover Movies You'll Love</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0;'>Let our AI find your perfect next watch based on your unique taste</p>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center;'>Popular Movies</h2>", unsafe_allow_html=True)
    popular_movies = fetch_popular_movies()
    if popular_movies:
        cols = st.columns(3)
        for idx, movie in enumerate(popular_movies[:3]):
            with cols[idx % 3]:
                trailer_url = fetch_trailer(movie['id'])
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{movie['poster']}" style="width: 100%; border-radius: 10px;">
                        <h3>{movie['title']}</h3>
                        <p>⭐ {movie['rating']:.1f}</p>
                        <p>{movie['description'][:100]}...</p>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Watch Now", key=f"watch_pop_{movie['id']}"):
                        if st.session_state.current_user:
                            save_user_activity(st.session_state.current_user, "watched", movie['title'], movie['id'])
                            st.session_state[f"rating_movie_{movie['id']}"] = movie['title']
                            st.session_state[f"show_rating_{movie['id']}"] = True
                            st.session_state[f"rating_movie_id_{movie['id']}"] = movie['id']
                        else:
                            st.warning("Please sign in to watch movies.")
                with col2:
                    if st.button("Add to Watchlist", key=f"watchlist_pop_{movie['id']}"):
                        if st.session_state.current_user:
                            if not any(item["title"] == movie['title'] for item in st.session_state.watchlist):
                                st.session_state.watchlist.append({"title": movie['title'], "movie_id": movie['id']})
                                save_watchlist_to_csv(st.session_state.current_user, movie['title'], movie['id'])
                                save_user_activity(st.session_state.current_user, "added_to_watchlist", movie['title'], movie['id'])
                                st.success(f"Added {movie['title']} to watchlist!")
                        else:
                            st.warning("Please sign in to add movies to your watchlist.")
                with col3:
                    if trailer_url:
                        if st.button("Watch Trailer", key=f"trailer_pop_{movie['id']}"):
                            st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                if st.session_state.get(f"show_rating_{movie['id']}", False):
                    rating = st.slider(f"Rate {movie['title']} (1-5)", 1, 5, key=f"rating_pop_{movie['id']}")
                    review = st.text_area(f"Write a review for {movie['title']}", key=f"review_pop_{movie['id']}")
                    if st.button("Submit Rating & Review", key=f"submit_rating_pop_{movie['id']}"):
                        if st.session_state.current_user:
                            save_user_activity(st.session_state.current_user, "rated", movie['title'], movie['id'], rating)
                            import csv, os
                            file_exists = os.path.exists("user_reviews.csv")
                            with open("user_reviews.csv", "a", newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                if not file_exists:
                                    writer.writerow(["user","movie_id","title","rating","review"])
                                writer.writerow([st.session_state.current_user, movie['id'], movie['title'], rating, review])
                            st.success(f"Rated {movie['title']} with {rating} stars and review submitted!")
                            st.session_state[f"show_rating_{movie['id']}"] = False
                        else:
                            st.warning("Please sign in to rate movies.")
    else:
        st.info("Could not fetch popular movies. Please check your API key or internet connection.")

elif st.session_state.page == "discover":
    if not movies.empty:
        user_id = st.session_state.current_user if st.session_state.current_user else 1
        movie_list = movies['title'].dropna().unique()
        selected_movie = st.selectbox("🎥 Pick a movie for recommendations", movie_list)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Get Content-Based Recommendations", key="content_based"):
                if selected_movie in movie_list:
                    recommended_names, recommended_posters = recommend_content_based(selected_movie)
                    if recommended_names:
                        st.session_state.show_recommendations = True
                        st.session_state.recommended_names = recommended_names
                        st.session_state.recommended_posters = recommended_posters
                        st.session_state.recommendation_type = "content"
                    else:
                        st.error("Could not generate content-based recommendations.")
                else:
                    st.error(f"Movie '{selected_movie}' not found in the database.")
        with col2:
            if st.button("Get Collaborative Recommendations", key="collaborative"):
                recommended_names, recommended_posters = recommend_collaborative(user_id)
                if recommended_names:
                    st.session_state.show_recommendations = True
                    st.session_state.recommended_names = recommended_names
                    st.session_state.recommended_posters = recommended_posters
                    st.session_state.recommendation_type = "collaborative"
                else:
                    st.error("Could not generate collaborative recommendations.")
        with col3:
            if st.button("Get Hybrid Recommendations", key="hybrid"):
                recommended_names, recommended_posters = recommend_hybrid(selected_movie, user_id)
                if recommended_names:
                    st.session_state.show_recommendations = True
                    st.session_state.recommended_names = recommended_names
                    st.session_state.recommended_posters = recommended_posters
                    st.session_state.recommendation_type = "hybrid"
                else:
                    st.error("Could not generate hybrid recommendations.")
        with col4:
            if st.button("Get Personalized Recommendations", key="personalized"):
                try:
                    import pandas as pd
                    import os
                    top_rated = []
                    csv_path = "user_reviews.csv"
                    if os.path.exists(csv_path):
                        reviews_df = pd.read_csv(csv_path, header=0)
                        # Normalize user id comparison (string/int)
                        reviews_df['user'] = reviews_df['user'].astype(str)
                        uid = str(st.session_state.current_user) if st.session_state.get('current_user') is not None else None
                        if uid:
                            user_reviews = reviews_df[reviews_df['user'] == uid]
                            if not user_reviews.empty:
                                top_rated = user_reviews.sort_values('rating', ascending=False).head(5)['title'].tolist()

                    if not top_rated:
                        st.warning("No ratings found for your account. Please rate some movies first.")
                        st.session_state.show_recommendations = True
                        popular = fetch_popular_movies()[:5]
                        st.session_state.recommended_names = [m['title'] for m in popular]
                        st.session_state.recommended_posters = [m['poster'] for m in popular]
                        st.session_state.recommendation_type = "popular"
                    else:
                        personalized_names = []
                        personalized_posters = []
                        for title in top_rated:
                            names, posters = recommend_content_based(title)
                            for n, p in zip(names, posters):
                                if n not in personalized_names:
                                    personalized_names.append(n)
                                    personalized_posters.append(p)
                        if personalized_names:
                            st.session_state.show_recommendations = True
                            st.session_state.recommended_names = personalized_names
                            st.session_state.recommended_posters = personalized_posters
                            st.session_state.recommendation_type = "personalized"
                        else:
                            st.warning("No personalized recommendations found. Showing popular movies instead.")
                            st.session_state.show_recommendations = True
                            popular = fetch_popular_movies()[:5]
                            st.session_state.recommended_names = [m['title'] for m in popular]
                            st.session_state.recommended_posters = [m['poster'] for m in popular]
                            st.session_state.recommendation_type = "popular"
                except Exception as e:
                    st.error(f"Error loading ratings from CSV: {e}")
    else:
        st.warning("No movies loaded from .pkl file. Please ensure the file is correct.")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>Recommended for You</h2>", unsafe_allow_html=True)

    search_query = st.text_input("", placeholder="Search movies...")

    genre_map = fetch_genres()
    genre_names = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance", "Thriller", "Adventure"]
    genre_ids = {name: gid for gid, name in genre_map.items() if name in genre_names}

    cols = st.columns(len(genre_names))
    for idx, genre in enumerate(genre_names):
        with cols[idx]:
            if st.button(genre, key=f"genre_{genre}"):
                genre_id = genre_ids.get(genre)
                if genre_id:
                    st.session_state.selected_genre = genre
                    st.session_state.genre_movies = fetch_movies_by_genre(genre_id)
                    st.session_state.show_recommendations = False

    if st.session_state.selected_genre and st.session_state.genre_movies:
        st.subheader(f"{st.session_state.selected_genre} Movies")
        cols = st.columns(3)
        for idx, movie in enumerate(st.session_state.genre_movies[:3]):
            with cols[idx % 3]:
                trailer_url = fetch_trailer(movie['id'])
                st.markdown(f"""
                    <div class='movie-card' style='padding-bottom: 0;'>
                        <img src='{movie['poster']}' style='width: 100%; border-radius: 10px;'>
                        <h3>{movie['title']}</h3>
                        <p>⭐ {movie['rating']:.1f}</p>
                        <p>{movie['description'][:100]}...</p>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button('Watch Now', key=f'watch_genre_{movie["id"]}')
                with col2:
                    st.button('Add to Watchlist', key=f'watchlist_genre_{movie["id"]}')
                with col3:
                    if trailer_url:
                        st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                if st.session_state.get(f"show_rating_{movie['id']}", False):
                    rating = st.slider(f"Rate {movie['title']} (1-5)", 1, 5, key=f"rating_genre_{movie['id']}")
                    review = st.text_area(f"Write a review for {movie['title']}", key=f"review_genre_{movie['id']}")
                    if st.button("Submit Rating & Review", key=f"submit_rating_genre_{movie['id']}"):
                        if st.session_state.current_user:
                            save_user_activity(st.session_state.current_user, "rated", movie['title'], movie['id'], rating)
                            import csv
                            import os
                            file_exists = os.path.exists("user_reviews.csv")
                            with open("user_reviews.csv", "a", newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                if not file_exists:
                                    writer.writerow(["user","movie_id","title","rating","review"])
                                writer.writerow([st.session_state.current_user, movie['id'], movie['title'], rating, review])
                            st.success(f"Rated {movie['title']} with {rating} stars and review submitted!")
                            st.session_state[f"show_rating_{movie['id']}"] = False
                        else:
                            st.warning("Please sign in to rate movies.")
                    # Display recent reviews and average rating
                    import pandas as pd
                    try:
                        reviews_df = pd.read_csv("user_reviews.csv", header=0)
                        movie_reviews = reviews_df[reviews_df["movie_id"] == movie['id']]
                        if not movie_reviews.empty:
                            avg_rating = movie_reviews["rating"].astype(float).mean()
                            st.markdown(f"**Average Rating:** {avg_rating:.1f} ⭐")
                            st.markdown("**Recent Reviews:**")
                            for _, row in movie_reviews.tail(3).iterrows():
                                st.markdown(f"- *{row['user']}*: {row['review']} ({row['rating']}⭐)")
                    except Exception:
                        pass

    if search_query and not movies.empty:
        st.session_state.show_recommendations = False
        st.session_state.selected_genre = None
        # remember last search and provide recommendations based on it
        st.session_state.last_search = search_query
        filtered_movies = movies[movies['title'].str.contains(search_query, case=False, na=False)]
        if not filtered_movies.empty:
            cols = st.columns(3)
            for idx, movie in enumerate(filtered_movies.head(3).itertuples()):
                with cols[idx % 3]:
                    trailer_url = fetch_trailer(movie.id)
                    poster = fetch_poster(movie.id)
                    rating = movie.vote_average if hasattr(movie, 'vote_average') and pd.notna(movie.vote_average) else fetch_movie_details(movie.id)['rating']
                    description = movie.overview if hasattr(movie, 'overview') and pd.notna(movie.overview) else fetch_movie_details(movie.id)['description']
                    st.markdown(f"""
                        <div class='movie-card' style='padding-bottom: 0;'>
                            <img src='{poster}' style='width: 100%; border-radius: 10px;'>
                            <h3>{movie.title}</h3>
                            <p>⭐ {rating:.1f}</p>
                            <p>{description[:100]}...</p>
                        </div>
                    """, unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button('Watch Now', key=f'watch_search_{movie.id}'):
                            if st.session_state.current_user:
                                save_user_activity(st.session_state.current_user, "watched", movie.title, movie.id)
                                st.session_state[f"rating_movie_{movie.id}"] = movie.title
                                st.session_state[f"show_rating_{movie.id}"] = True
                                st.session_state[f"rating_movie_id_{movie.id}"] = movie.id
                            else:
                                st.warning("Please sign in to watch movies.")
                    with col2:
                        st.button('Add to Watchlist', key=f'watchlist_search_{movie.id}')
                    with col3:
                        if trailer_url:
                            st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                    if st.session_state.get(f"show_rating_{movie.id}", False):
                        rating = st.slider(f"Rate {movie.title} (1-5)", 1, 5, key=f"rating_search_{movie.id}")
                        review = st.text_area(f"Write a review for {movie.title}", key=f"review_search_{movie.id}")
                        if st.button("Submit Rating & Review", key=f"submit_rating_search_{movie.id}"):
                            if st.session_state.current_user:
                                save_user_activity(st.session_state.current_user, "rated", movie.title, movie.id, rating)
                                import csv, os
                                file_exists = os.path.exists("user_reviews.csv")
                                with open("user_reviews.csv", "a", newline='', encoding='utf-8') as f:
                                    writer = csv.writer(f)
                                    if not file_exists:
                                        writer.writerow(["user","movie_id","title","rating","review"])
                                    writer.writerow([st.session_state.current_user, movie.id, movie.title, rating, review])
                                st.success(f"Rated {movie.title} with {rating} stars and review submitted!")
                                st.session_state[f"show_rating_{movie.id}"] = False
                            else:
                                st.warning("Please sign in to rate movies.")

            # Generate recommendations based on first matched search result
            try:
                first_title = filtered_movies.head(1)['title'].iloc[0]
                names, posters = recommend_content_based(first_title)
                if names:
                    st.session_state.show_recommendations = True
                    st.session_state.recommended_names = names
                    st.session_state.recommended_posters = posters
                    st.session_state.recommendation_type = "search"
            except Exception:
                pass
    if st.session_state.show_recommendations:
        recommended_names = st.session_state.recommended_names
        recommended_posters = st.session_state.recommended_posters
        recommendation_type = st.session_state.recommendation_type
        st.subheader(f"{recommendation_type.capitalize()}-Based Recommendations")
        cols = st.columns(3)
        for idx, (name, poster) in enumerate(zip(recommended_names, recommended_posters)):
            with cols[idx % 3]:
                movie_id = movies[movies['title'] == name]['id'].iloc[0] if not movies.empty and name in movies['title'].values else None
                trailer_url = fetch_trailer(movie_id) if movie_id else None
                rating = movies[movies['title'] == name]['vote_average'].iloc[0] if not movies.empty and name in movies['title'].values and 'vote_average' in movies and pd.notna(movies[movies['title'] == name]['vote_average'].iloc[0]) else fetch_movie_details(movie_id)['rating'] if movie_id else 0.0
                description = movies[movies['title'] == name]['overview'].iloc[0] if not movies.empty and name in movies['title'].values and 'overview' in movies and pd.notna(movies[movies['title'] == name]['overview'].iloc[0]) else fetch_movie_details(movie_id)['description'] if movie_id else "No description available"
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{poster}" style="width: 100%; border-radius: 10px;">
                        <h3>{name}</h3>
                        <p>⭐ {rating:.1f}</p>
                        <p>{description[:100]}...</p>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Watch Now", key=f"watch_rec_{idx}_{movie_id}"):
                        if st.session_state.current_user:
                            if movie_id:
                                save_user_activity(st.session_state.current_user, "watched", name, movie_id)
                                st.session_state[f"rating_movie_{movie_id}"] = name
                                st.session_state[f"show_rating_{movie_id}"] = True
                                st.session_state[f"rating_movie_id_{movie_id}"] = movie_id
                            else:
                                st.error("Cannot watch this movie: Movie ID not found.")
                        else:
                            st.warning("Please sign in to watch movies.")
                with col2:
                    if st.button("Add to Watchlist", key=f"watchlist_rec_{idx}_{movie_id}"):
                        if st.session_state.current_user:
                            if movie_id and not any(item["title"] == name for item in st.session_state.watchlist):
                                st.session_state.watchlist.append({"title": name, "movie_id": movie_id})
                                save_watchlist_to_csv(st.session_state.current_user, name, movie_id)
                                save_user_activity(st.session_state.current_user, "added_to_watchlist", name, movie_id)
                                st.success(f"Added {name} to watchlist!")
                            elif not movie_id:
                                st.error("Cannot add to watchlist: Movie ID not found.")
                        else:
                            st.warning("Please sign in to add movies to your watchlist.")
                with col3:
                    if trailer_url:
                        if st.button("Watch Trailer", key=f"trailer_rec_{idx}_{movie_id}"):
                            st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                if st.session_state.get(f"show_rating_{movie_id}", False):
                    rating = st.slider(f"Rate {name} (1-5)", 1, 5, key=f"rating_rec_{movie_id}")
                    review = st.text_area(f"Write a review for {name}", key=f"review_rec_{movie_id}")
                    if st.button("Submit Rating & Review", key=f"submit_rating_rec_{movie_id}"):
                        if st.session_state.current_user:
                            if movie_id:
                                save_user_activity(st.session_state.current_user, "rated", name, movie_id, rating)
                                import csv, os
                                file_exists = os.path.exists("user_reviews.csv")
                                with open("user_reviews.csv", "a", newline='', encoding='utf-8') as f:
                                    writer = csv.writer(f)
                                    if not file_exists:
                                        writer.writerow(["user","movie_id","title","rating","review"])
                                    writer.writerow([st.session_state.current_user, movie_id, name, rating, review])
                                st.success(f"Rated {name} with {rating} stars and review submitted!")
                                st.session_state[f"show_rating_{movie_id}"] = False
                            else:
                                st.error("Cannot rate this movie: Movie ID not found.")
                        else:
                            st.warning("Please sign in to rate movies.")
    else:
        if not movies.empty and not st.session_state.selected_genre and not search_query:
            cols = st.columns(3)
            for idx, movie in enumerate(movies.head(3).itertuples()):
                with cols[idx % 3]:
                    trailer_url = fetch_trailer(movie.id)
                    poster = fetch_poster(movie.id)
                    rating = movie.vote_average if hasattr(movie, 'vote_average') and pd.notna(movie.vote_average) else fetch_movie_details(movie.id)['rating']
                    description = movie.overview if hasattr(movie, 'overview') and pd.notna(movie.overview) else fetch_movie_details(movie.id)['description']
                    st.markdown(f"""
                        <div class="movie-card">
                            <img src="{poster}" style="width: 100%; border-radius: 10px;">
                            <h3>{movie.title}</h3>
                            <p>⭐ {rating:.1f}</p>
                            <p>{description[:100]}...</p>
                        </div>
                    """, unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Watch Now", key=f"watch_{movie.id}"):
                            if st.session_state.current_user:
                                save_user_activity(st.session_state.current_user, "watched", movie.title, movie.id)
                                st.session_state[f"rating_movie_{movie.id}"] = movie.title
                                st.session_state[f"show_rating_{movie.id}"] = True
                                st.session_state[f"rating_movie_id_{movie.id}"] = movie.id
                            else:
                                st.warning("Please sign in to watch movies.")
                    with col2:
                        if st.button("Add to Watchlist", key=f"watchlist_{movie.id}"):
                            if st.session_state.current_user:
                                if not any(item["title"] == movie.title for item in st.session_state.watchlist):
                                    st.session_state.watchlist.append({"title": movie.title, "movie_id": movie.id})
                                    save_watchlist_to_csv(st.session_state.current_user, movie.title, movie.id)
                                    save_user_activity(st.session_state.current_user, "added_to_watchlist", movie.title, movie.id)
                                    st.success(f"Added {movie.title} to watchlist!")
                            else:
                                st.warning("Please sign in to add movies to your watchlist.")
                    with col3:
                        if trailer_url:
                            if st.button("Watch Trailer", key=f"trailer_{movie.id}"):
                                st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                    if st.session_state.get(f"show_rating_{movie.id}", False):
                        rating = st.slider(f"Rate {movie.title} (1-5)", 1, 5, key=f"rating_default_{movie.id}")
                        review = st.text_area(f"Write a review for {movie.title}", key=f"review_default_{movie.id}")
                        if st.button("Submit Rating & Review", key=f"submit_rating_default_{movie.id}"):
                            if st.session_state.current_user:
                                save_user_activity(st.session_state.current_user, "rated", movie.title, movie.id, rating)
                                import csv, os
                                file_exists = os.path.exists("user_reviews.csv")
                                with open("user_reviews.csv", "a", newline='', encoding='utf-8') as f:
                                    writer = csv.writer(f)
                                    if not file_exists:
                                        writer.writerow(["user","movie_id","title","rating","review"])
                                    writer.writerow([st.session_state.current_user, movie.id, movie.title, rating, review])
                                st.success(f"Rated {movie.title} with {rating} stars and review submitted!")
                                st.session_state[f"show_rating_{movie.id}"] = False
                            else:
                                st.warning("Please sign in to rate movies.")

elif st.session_state.page == "mood":
    st.markdown("<h2>Mood-Based Recommendations</h2>", unsafe_allow_html=True)
    st.markdown("<p>Answer a few questions to get movie recommendations tailored to your mood and preferences. All fields are optional.</p>", unsafe_allow_html=True)
    
    with st.form("mood_form"):
        mood = st.selectbox("What’s your current mood?", ["", "Happy", "Sad", "Stressed", "Excited", "Relaxed", "Bored", "Angry"], index=0)
        motivation = st.selectbox("Are you looking for something motivational or uplifting?", ["", "Yes", "No", "Neutral"], index=0)
        watching_with = st.selectbox("Who are you watching with?", ["", "Alone", "Friends", "Family", "Partner", "Kids"], index=0)
        occasion = st.selectbox("Is this for a special occasion?", ["", "Date Night", "Casual", "Party", "Family Night", "None"], index=0)
        time = st.selectbox("How much time do you have?", ["", "Less than 1 hour", "1-2 hours", "2+ hours"], index=0)
        genre = st.selectbox("What genre are you in the mood for?", [""] + list(fetch_genres().values()), index=0)
        tone = st.selectbox("What kind of tone do you prefer?", ["", "Light-hearted", "Serious", "Emotional", "Fun", "Epic", "Thought-provoking"], index=0)
        romantic = st.selectbox("Are you looking for something romantic?", ["", "Yes", "No", "Maybe"], index=0)
        pace = st.selectbox("Do you want something fast-paced or slow-paced?", ["", "Fast-paced", "Slow-paced", "Balanced"], index=0)
        release = st.selectbox("Do you prefer newer releases or classics?", ["", "New (post-2010)", "Classics (pre-2010)", "No preference"], index=0)
        mature = st.selectbox("Are you okay with intense or mature themes?", ["", "Yes", "No", "Neutral"], index=0)
        
        submit_button = st.form_submit_button("Get Recommendations")
        
        if submit_button:
            answers = {
                "mood": mood if mood else None,
                "motivation": motivation if motivation else None,
                "watching_with": watching_with if watching_with else None,
                "occasion": occasion if occasion else None,
                "time": time if time else None,
                "genre": genre if genre else None,
                "tone": tone if tone else None,
                "romantic": romantic if romantic else None,
                "pace": pace if pace else None,
                "release": release if release else None,
                "mature": mature if mature else None
            }
            st.session_state.mood_answers = answers
            st.session_state.mood_recommendations = recommend_mood_based(answers, fetch_genres())
            if st.session_state.mood_recommendations:
                st.success("Recommendations generated based on your mood!")
            else:
                st.warning("No movies found for your preferences. Showing popular movies instead.")

    if st.session_state.mood_recommendations:
        st.subheader("Movies for Your Mood")
        cols = st.columns(3)
        for idx, movie in enumerate(st.session_state.mood_recommendations):
            with cols[idx % 3]:
                trailer_url = fetch_trailer(movie['id'])
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{movie['poster']}" style="width: 100%; border-radius: 10px;">
                        <h3>{movie['title']}</h3>
                        <p>⭐ {movie['rating']:.1f}</p>
                        <p>{movie['description'][:100]}...</p>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Watch Now", key=f"watch_mood_{movie['id']}"):
                        if st.session_state.current_user:
                            save_user_activity(st.session_state.current_user, "watched", movie['title'], movie['id'])
                            st.session_state[f"rating_movie_{movie['id']}"] = movie['title']
                            st.session_state[f"show_rating_{movie['id']}"] = True
                            st.session_state[f"rating_movie_id_{movie['id']}"] = movie['id']
                        else:
                            st.warning("Please sign in to watch movies.")
                with col2:
                    if st.button("Add to Watchlist", key=f"watchlist_mood_{movie['id']}"):
                        if st.session_state.current_user:
                            if not any(item["title"] == movie['title'] for item in st.session_state.watchlist):
                                st.session_state.watchlist.append({"title": movie['title'], "movie_id": movie['id']})
                                save_watchlist_to_csv(st.session_state.current_user, movie['title'], movie['id'])
                                save_user_activity(st.session_state.current_user, "added_to_watchlist", movie['title'], movie['id'])
                                st.success(f"Added {movie['title']} to watchlist!")
                        else:
                            st.warning("Please sign in to add movies to your watchlist.")
                with col3:
                    if trailer_url:
                        if st.button("Watch Trailer", key=f"trailer_mood_{movie['id']}"):
                            st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                if st.session_state.get(f"show_rating_{movie['id']}", False):
                    rating = st.slider(f"Rate {movie['title']} (1-5)", 1, 5, key=f"rating_mood_{movie['id']}")
                    review = st.text_area(f"Write a review for {movie['title']}", key=f"review_mood_{movie['id']}")
                    if st.button("Submit Rating & Review", key=f"submit_rating_mood_{movie['id']}"):
                        if st.session_state.current_user:
                            save_user_activity(st.session_state.current_user, "rated", movie['title'], movie['id'], rating)
                            import csv, os
                            file_exists = os.path.exists("user_reviews.csv")
                            with open("user_reviews.csv", "a", newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                if not file_exists:
                                    writer.writerow(["user","movie_id","title","rating","review"])
                                writer.writerow([st.session_state.current_user, movie['id'], movie['title'], rating, review])
                            st.success(f"Rated {movie['title']} with {rating} stars and review submitted!")
                            st.session_state[f"show_rating_{movie['id']}"] = False
                        else:
                            st.warning("Please sign in to rate movies.")
    else:
        st.info("No mood-based recommendations available. Please submit your preferences or adjust filters.")

elif st.session_state.page == "watchlist":
    st.markdown("<h2>Watchlist</h2>", unsafe_allow_html=True)
    # Notification feature: alert for new movies matching interests
    import pandas as pd
    import os
    if st.session_state.current_user:
        # Get user's favorite genres from top-rated movies
        try:
            reviews_df = pd.read_csv("user_reviews.csv", header=0)
            user_reviews = reviews_df[reviews_df["user"] == st.session_state.current_user]
            top_rated_ids = user_reviews.sort_values("rating", ascending=False).head(5)["movie_id"].tolist()
            favorite_genres = set()
            for mid in top_rated_ids:
                details = fetch_movie_details(mid)
                genre = details.get("genre")
                if genre:
                    favorite_genres.add(genre)
            # Check for new movies in those genres
            notified_file = f"notified_{st.session_state.current_user}.txt"
            notified_ids = set()
            if os.path.exists(notified_file):
                with open(notified_file) as f:
                    notified_ids = set(f.read().splitlines())
            new_movies = movies[movies["genre"].isin(favorite_genres) & ~movies["id"].astype(str).isin(notified_ids)]
            if not new_movies.empty:
                st.info(f"New movies added in your favorite genres: {', '.join(new_movies['title'].head(3))}")
                # Mark as notified
                with open(notified_file, "a") as f:
                    for mid in new_movies["id"].astype(str).head(3):
                        f.write(mid + "\n")
        except Exception:
            pass
        if st.session_state.watchlist:
            st.markdown("<div class='watchlist-container'>", unsafe_allow_html=True)
            # Social sharing feature
            watchlist_titles = [item["title"] for item in st.session_state.watchlist]
            share_text = "My Watchlist: " + ", ".join(watchlist_titles)
            st.text_area("Share your watchlist:", value=share_text, height=50)
            st.button("Copy to Clipboard", on_click=lambda: st.session_state.update({"copied": True}))
            if st.session_state.get("copied"):
                st.success("Watchlist copied! You can share it with friends.")
            cols = st.columns(3)
            for idx, item in enumerate(st.session_state.watchlist):
                with cols[idx % 3]:
                    movie = item["title"]
                    movie_id = item["movie_id"]
                    poster = fetch_poster(movie_id) if movie_id else "https://via.placeholder.com/200x300?text=No+Poster"
                    trailer_url = fetch_trailer(movie_id) if movie_id else None
                    rating = movies[movies['id'] == movie_id]['vote_average'].iloc[0] if not movies.empty and movie_id in movies['id'].values and 'vote_average' in movies and pd.notna(movies[movies['id'] == movie_id]['vote_average'].iloc[0]) else fetch_movie_details(movie_id)['rating']
                    description = movies[movies['id'] == movie_id]['overview'].iloc[0] if not movies.empty and movie_id in movies['id'].values and 'overview' in movies and pd.notna(movies[movies['id'] == movie_id]['overview'].iloc[0]) else fetch_movie_details(movie_id)['description']
                    # Movie Details Link
                    if st.button(f"Details: {movie}", key=f"details_wl_{movie_id}_{idx}"):
                        st.session_state.selected_movie_details = movie_id
                    st.markdown(f"""
                        <div class="movie-card">
                            <img src="{poster}" style="width: 100%; border-radius: 10px;">
                            <h3>{movie}</h3>
                            <p>⭐ {rating:.1f}</p>
                            <p>{description[:100]}...</p>
                        </div>
                    """, unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Watch Now", key=f"watch_wl_{movie_id}_{idx}"):
                            save_user_activity(st.session_state.current_user, "watched", movie, movie_id)
                            st.session_state[f"rating_movie_{movie_id}"] = movie
                            st.session_state[f"show_rating_{movie_id}"] = True
                            st.session_state[f"rating_movie_id_{movie_id}"] = movie_id
                    with col2:
                        if st.button("Remove", key=f"remove_wl_{movie_id}_{idx}"):
                            st.session_state.watchlist = [item for item in st.session_state.watchlist if item["movie_id"] != movie_id]
                            filename = f"watchlist_{st.session_state.current_user}.csv"
                            if st.session_state.watchlist:
                                pd.DataFrame(st.session_state.watchlist).to_csv(filename, index=False, quoting=csv.QUOTE_NONNUMERIC)
                            else:
                                if os.path.exists(filename):
                                    os.remove(filename)
                            st.success(f"Removed {movie} from watchlist!")
                    with col3:
                        if trailer_url:
                            if st.button("Trailer", key=f"trailer_wl_{movie_id}_{idx}"):
                                st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                    if st.session_state.get(f"show_rating_{movie_id}", False):
                        rating = st.slider(f"Rate {movie} (1-5)", 1, 5, key=f"rating_wl_{movie_id}_{idx}")
                        review = st.text_area(f"Write a review for {movie}", key=f"review_wl_{movie_id}_{idx}")
                        if st.button("Submit Rating & Review", key=f"submit_rating_wl_{movie_id}_{idx}"):
                            save_user_activity(st.session_state.current_user, "rated", movie, movie_id, rating)
                            import csv, os
                            file_exists = os.path.exists("user_reviews.csv")
                            with open("user_reviews.csv", "a", newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                if not file_exists:
                                    writer.writerow(["user","movie_id","title","rating","review"])
                                writer.writerow([st.session_state.current_user, movie_id, movie, rating, review])
                            st.success(f"Rated {movie} with {rating} stars and review submitted!")
                            st.session_state[f"show_rating_{movie_id}"] = False
            st.markdown("</div>", unsafe_allow_html=True)
            # Movie Details Page
            if st.session_state.get("selected_movie_details"):
                movie_id = st.session_state.selected_movie_details
                details = fetch_movie_details(movie_id)
                st.markdown(f"## Movie Details")
                st.image(fetch_poster(movie_id), width=200)
                st.markdown(f"**Title:** {details.get('title', '')}")
                st.markdown(f"**Release Date:** {details.get('release_date', 'N/A')}")
                st.markdown(f"**Director:** {details.get('director', 'N/A')}")
                st.markdown(f"**Cast:** {details.get('cast', 'N/A')}")
                st.markdown(f"**Description:** {details.get('description', '')}")
                st.markdown(f"**Rating:** {details.get('rating', 'N/A')}")
                trailer_url = fetch_trailer(movie_id)
                if trailer_url:
                    st.markdown(f'<a href="{trailer_url}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)
                # Show reviews
                import pandas as pd
                try:
                    reviews_df = pd.read_csv("user_reviews.csv", header=0)
                    movie_reviews = reviews_df[reviews_df["movie_id"] == movie_id]
                    if not movie_reviews.empty:
                        avg_rating = movie_reviews["rating"].astype(float).mean()
                        st.markdown(f"**Average Rating:** {avg_rating:.1f} ⭐")
                        st.markdown("**Recent Reviews:**")
                        for _, row in movie_reviews.tail(5).iterrows():
                            st.markdown(f"- *{row['user']}*: {row['review']} ({row['rating']}⭐)")
                except Exception:
                    pass
                if st.button("Back to Watchlist", key="back_to_watchlist"):
                    st.session_state.selected_movie_details = None
        else:
            st.info("Your watchlist is empty.")
    else:
        st.warning("Please sign in to view your watchlist.")

elif st.session_state.page == "history":
    st.markdown("<h2>Your Activity History</h2>", unsafe_allow_html=True)
    if st.session_state.current_user:
        if os.path.exists("user_activity.csv"):
            try:
                activity_df = pd.read_csv("user_activity.csv")
                user_activity = activity_df[activity_df['user_id'] == st.session_state.current_user]
                user_activity = user_activity.sort_values(by="timestamp", ascending=False)
                if user_activity.empty:
                    st.info("No activity history found.")
                else:
                    st.markdown("<div class='history-container'>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    for idx, row in user_activity.iterrows():
                        with cols[idx % 3]:
                            action = row['action']
                            title = row['title']
                            movie_id = row['movie_id']
                            rating = row['rating'] if pd.notna(row['rating']) else None
                            timestamp = row['timestamp']
                            poster = fetch_poster(movie_id) if movie_id else "https://via.placeholder.com/200x300?text=No+Poster"
                            description = fetch_movie_details(movie_id)['description']
                            if action == "watched":
                                action_text = f"Watched on {timestamp}"
                            elif action == "rated":
                                action_text = f"Rated {rating}/5 on {timestamp}"
                            elif action == "added_to_watchlist":
                                action_text = f"Added to watchlist on {timestamp}"
                            else:
                                action_text = f"Unknown action on {timestamp}"
                            st.markdown(f"""
                                <div class="movie-card">
                                    <img src="{poster}" style="width: 100%; border-radius: 10px;">
                                    <h3>{title}</h3>
                                    <p>{action_text}</p>
                                    <p>{description[:100]}...</p>
                                </div>
                            """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Error reading activity history: {e}")
        else:
            st.info("No activity history yet.")
    else:
        st.warning("Please sign in to view your activity history.")
elif st.session_state.page == "signin":
    
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if not st.session_state.show_signup:
        st.subheader("Sign In")
        signin_email = st.text_input("Email", key="signin_email")
        signin_password = st.text_input("Password", type="password", key="signin_password")
        login_failed = False
        if st.button("Sign In", key="signin_btn"):
            users = load_users_from_csv()
            user = users.get(signin_email)
            if user and bcrypt.checkpw(signin_password.encode(), user["password"].encode()):
                st.session_state.current_user = user["user_id"]
                st.session_state.current_username = signin_email
                st.session_state.page = "home"
                st.success("Signed in successfully!")
            else:
                st.error("Invalid email or password.")
                login_failed = True
        st.markdown("<div style='text-align:center; margin-top:18px;'>", unsafe_allow_html=True)
        if st.button("Not registered? Click here to Sign Up", key="show_signup_btn"):
            st.session_state.show_signup = True
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.title("Sign Up")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up", key="signup_btn"):
            users = load_users_from_csv()
            if signup_email in users:
                st.error("Email already registered. Please sign in.")
            else:
                new_user_id = max([u["user_id"] for u in users.values()], default=0) + 1
                save_user_to_csv(signup_email, signup_password, new_user_id)
                st.success("Account created! Please sign in.")
                st.session_state.show_signup = False
        if st.button("Back to Sign In", key="back_to_signin"):
            st.session_state.show_signup = False
    st.stop()



    