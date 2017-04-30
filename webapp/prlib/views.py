from flask import render_template, Markup, request
from . import app, prlib
from sqlalchemy.orm.exc import NoResultFound
import json
import os
from datetime import datetime


@app.route("/")
def root():
    movies = prlib.all_movies()
    serialize = []
    for m in movies:
        if not m.rating:
            m.rating = 0
        serialize.append(serialize_movie(m))
    movies_json = 'var movies = ' + json.dumps(serialize) + ';'
    return render_template('index.html', movies_json=Markup(movies_json))


def serialize_movie(m):
    movie = {'id': m.id,
             'name': m.name,
             'location': m.location,
             'size': m.size,
             'added': m.added.timestamp(),
             'rating': m.rating}
    return movie


@app.route("/config")
def config():
    return render_template('config.html')


@app.route("/clear_db")
def clear_db():
    os.unlink(app.config['DB_FILE'])
    return 'Removed db file.'


@app.route("/init_db")
def init_db():
    prlib.create_db()
    return 'Initialized new db file.'


@app.route("/scan_dir")
def scan_dir():
    prlib.add_to_db()
    return 'Added new files to db'


@app.route("/reinit_db")
def reinit_db():
    os.unlink(app.config['DB_FILE'])
    prlib.create_db()
    prlib.add_to_db()
    return 'Reinitialized a new db'


@app.route("/details/<id>")
def details(id):
    return render_template('details.html')


@app.route("/movie/<id>", methods=['GET'])
def movie_get(id=None):
    try:
        m = prlib.get_movie(id)
    except NoResultFound:
        return 'id does not exist', 404
    return json.dumps(serialize_movie(m))


@app.route("/movie/<id>", methods=["PUT"])
def movie_put(id):
    movie = json.loads(request.data)
    print(movie)
    movie['added'] = datetime.fromtimestamp(movie['added'])
    prlib.update_movie(id, movie)
    return 'success'
