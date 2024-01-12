import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
from flask import Flask, request, render_template, session, jsonify
import uuid
import tmdbsimple
from pickle import load
from logging.config import dictConfig

tmdbsimple.API_KEY = '2495cdbe2f3565acb5e4fe1228bc3543'

ratings = pd.read_csv('../data/ratings.csv')

movies = pd.read_csv('../data/movies.csv')

links = pd.read_csv('../data/links.csv')

movie_titles = dict(zip(movies['movieId'], movies['title']))

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "webSiteVisiters.log",
                "formatter": "default",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    }
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'axcipherkeyclassic'

X = load(open('X_matrix.pkl', 'rb'))
movie_mapper = load(open('movie_mapper.pkl', 'rb'))
movie_inv_mapper = load(open('movie_inv_mapper.pkl', 'rb'))
user_mapper = load(open('user_mapper.pkl', 'rb'))
user_inv_mapper = load(open('user_inv_mapper.pkl', 'rb'))
movie_genres = load(open('movie_genres.pkl', 'rb'))

movie_idx = dict(zip(movies['title'], list(movies.index)))

def find_similar_movies(movie_id, X, movie_mapper, movie_inv_mapper, k, metric='cosine'):
    """
    Finds k-nearest neighbours for a given movie id.

    Args:
        movie_id: id of the movie of interest
        X: user-item utility matrix
        k: number of similar movies to retrieve
        metric: distance metric for kNN calculations

    Output: returns list of k similar movie ID's
    """
    X = X.T
    neighbour_ids = []

    movie_ind = movie_mapper[movie_id]
    movie_vec = X[movie_ind]
    if isinstance(movie_vec, np.ndarray):
        movie_vec = movie_vec.reshape(1, -1)
    # use k+1 since kNN output includes the movieId of interest
    kNN = NearestNeighbors(n_neighbors=k + 1, algorithm="brute", metric=metric)
    kNN.fit(X)
    neighbour = kNN.kneighbors(movie_vec, return_distance=False)
    for i in range(0, k):
        n = neighbour.item(i)
        neighbour_ids.append(movie_inv_mapper[n])
    neighbour_ids.pop(0)
    return neighbour_ids

@app.route("/")
def home():
    session["ctx"] = {"request_id": str(uuid.uuid4())}

    app.logger.info("A user visited the home page >>> %s", session["ctx"])
    return render_template("index.html")

@app.route('/recommend', methods=['GET'])
def main():
    movie_input = request.args.get('movie')
    num_recommendations = int(request.args.get('num'))
    # Replace this with your actual recommendation logic
    recommendations = []
    recommendations_poster = []
    movie = movies[movies['title'] == movie_finder(movie_input)]
    idx = movie['movieId'].values[0]
    result = links[links['movieId'] == idx]['tmdbId'].values
    #add the poster of the movie entered for reccommendation
    recommendations_poster.append(fetch_poster(int(result[0])))
    recommendations.append(movie_titles[idx])
    similar_movies = find_similar_movies(idx, X, movie_mapper, movie_inv_mapper, metric='cosine', k=num_recommendations+1)
    movie_title = movie_titles[idx]
    print(f"Because you watched {movie_title}:")
    for i in similar_movies:
        print(movie_titles[i])
        recommendations.append(movie_titles[i])
        result = links[links['movieId'] == i]['tmdbId'].values
        recommendations_poster.append(fetch_poster(int(result[0])))
        print(fetch_poster(int(result[0])))
    """print(len(recommendations_poster))
    print(len(recommendations))"""
    # Inside your Flask route
    return jsonify({'titles': recommendations, 'posters': recommendations_poster})

def get_movie_poster(tmdb_id):
    try:
        movie = tmdbsimple.Movies(tmdb_id)
        details = movie.info()
        poster_path = details['poster_path']

        # Construct the full URL for the poster image
        poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
        return poster_url
    except Exception as e:
        print(f"Error retrieving poster for TMDb ID {tmdb_id}: {e}")
        return None

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=2495cdbe2f3565acb5e4fe1228bc3543&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def movie_finder(title):
    all_titles = movies['title'].tolist()
    closest_match = process.extractOne(title, all_titles)
    return closest_match[0]


if __name__ == '__main__':
    app.run(debug=True, port=5000)