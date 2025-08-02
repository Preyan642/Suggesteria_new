import pickle
import streamlit as st
import requests
import time

# Load model files
try:
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading model files: {e}")
    st.stop()

# Fetch poster using TMDb Search API (by title)
def fetch_poster(movie_title):
    api_key = "2e14804309c8641fbd7197e4fd53c2ef"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"

    try:
        time.sleep(0.5)  # avoid TMDb rate limiting
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except Exception as e:
        print(f"Error fetching poster for '{movie_title}': {e}")

    return "https://via.placeholder.com/500x750?text=No+Image"

# Recommendation logic
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Selected movie not found in dataset.")
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances:
        movie_title = movies.iloc[i[0]].title
        recommended_movie_names.append(movie_title)
        recommended_movie_posters.append(fetch_poster(movie_title))

    return recommended_movie_names, recommended_movie_posters

# Streamlit UI setup
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.header("🎬 Movie Recommender System")

# Dropdown UI
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie", movie_list)

# Show recommendations
if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(5)
        for i in range(len(names)):
            with cols[i]:
                st.image(posters[i], caption=names[i], use_container_width=True)
    else:
        st.warning("No recommendations found.")

