from flask import Flask, jsonify, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tmdbv3api import TMDb

app = Flask(__name__)
tmdb = TMDb()
tmdb.api_key = 'ca8fe287b27c56d6d770a37e9a12511b'

import requests

api_key = "your_api_key"
base_url = "https://api.themoviedb.org/3/search/movie"

def get_movie_id(movie_title):
    api_key = "ca8fe287b27c56d6d770a37e9a12511b"
    base_url = "https://api.themoviedb.org/3/search/movie"
    search_url = f"{base_url}?api_key={api_key}&query={movie_title}"

    response = requests.get(search_url)
    data = response.json()
    results = data['results']

    if len(results) > 0:
        return results[0]['id']
    else:
        return None

def get_poster_url(movie_id):
    api_key = "ca8fe287b27c56d6d770a37e9a12511b"
    base_url = "https://api.themoviedb.org/3/movie/"
    poster_size = "w500"
    poster_url = f"{base_url}{movie_id}/images?api_key={api_key}&poster_size={poster_size}"

    response = requests.get(poster_url)
    data = response.json()
    # print(data)
    poster_path = data['posters'][0]['file_path']

    return f"https://image.tmdb.org/t/p/{poster_size}/{poster_path}"

def get_movies():
    base_url = "https://api.themoviedb.org/3/movie/popular"

    url = f"{base_url}?api_key={api_key}"
    response = requests.get(url)
    data = response.json()

    movies = data['results'][:10]

    return [{'id': movie['id'], 'title': movie['title'], 'overview': movie['overview'],'poster_path':get_poster_url(movie['id'])} for movie in movies]


def recommend_movies(movies, movie_id):
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform([movie['overview'] for movie in movies])
    similarity_matrix = cosine_similarity(tfidf_matrix)

    movie_index = None
    for index, movie in enumerate(movies):
        if movie['id'] == movie_id:
            movie_index = index
            break

    if movie_index is None:
        return []

    similar_movies = list(enumerate(similarity_matrix[movie_index]))
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)

    recommended_movies = []
    for movie in sorted_similar_movies[1:11]:
        recommended_movies.append(movies[movie[0]])

    return recommended_movies

def get_recommended_movies(movie_id):
    endpoint = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}&language=en-US&page=1"
    response = requests.get(endpoint)
    data = response.json()
    return data['results']

def recommend_movies_by_title(movie_title):
    query = movie_title.replace(" ", "+")
    response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}")
    data = response.json()
    results = data.get("results", [])

    if len(results) == 0:
        return None

    print('Title',len(results))
    movie = results[0]
    return get_recommended_movies(movie["id"])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        movie_title = request.form['movie_tile']
        movies = recommend_movies_by_title(movie_title)
    else:
        movies = get_movies()

    return render_template('index.html',movies = movies)

@app.route('/recommend/<movie_title>', methods=['GET'])
def recommend(movie_title):
    movies = get_movies()
    recommended_movies = recommend_movies_by_title(movie_title)
    # return jsonify(recommended_movies)
    return render_template('index.html',movies = movies)


if __name__ == '__main__':
    app.run(debug=True)
