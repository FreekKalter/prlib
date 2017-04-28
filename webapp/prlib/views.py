from flask import render_template, Markup
from . import app, prlib
import json


@app.route("/")
def root():
    movies = prlib.all_movies()
    serialize = []
    for m in movies:
        if not m.rating:
            m.rating = 0
        movie = {'id': m.id,
                 'name': m.name,
                 'size': m.size,
                 'rating': m.rating}
        serialize.append(movie)
    movies_json = 'var movies = ' + json.dumps(serialize)
    return render_template('index.html', movies_json=Markup(movies_json))


@app.route("/all_movies")
def all_movies():
    movies = prlib.all_movies()
    serialize = []
    for m in movies:
        movie = {'name': m.name,
                 'size': m.size,
                 'rating': m.rating}
        serialize.append(movie)
    return json.dumps(serialize)
