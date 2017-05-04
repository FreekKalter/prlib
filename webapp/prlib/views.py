from flask import render_template, request
from . import app, prlib
from sqlalchemy.orm.exc import NoResultFound
import json
import os
import random
from datetime import datetime


@app.route("/")
def root():
    return render_template('index.html')


def serialize_movie(m):
    movie = {'id': m.id,
             'name': m.name,
             'location': m.location,
             'size': m.size,
             'added': m.added.timestamp(),
             'rating': m.rating}
    return movie


@app.route("/all_movies")
def all_movies():
    movies = prlib.all_movies()
    serialize = []
    for m in movies:
        if not m.rating:
            m.rating = 0
        serialize.append(serialize_movie(m))
    movies_json = json.dumps(serialize)
    return movies_json


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
    print(id)
    return render_template('index.html')


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


@app.route("/movie/<id>", methods=["DELETE"])
def movie_delete(id):
    print(id)
    prlib.delete_movie(id)
    return json.dumps('status')


@app.route("/visible_ids", methods=["POST"])
def visible_ids():
    rows = json.loads(request.data)
    prlib.RANDOM_LIST = [row['id'] for row in rows]
    return 'got it'


@app.route("/random")
def random_route():
    return render_template('index.html')


@app.route("/current_random")
def current_random():
    if prlib.LAST_RANDOM == -1:
        return 'no random selected yet this session', 404
    movie = prlib.get_movie(prlib.LAST_RANDOM)
    dumps = json.dumps(serialize_movie(movie))
    print(dumps)
    return dumps


@app.route("/new_random")
def new_random():
    prlib.LAST_RANDOM = random.choice(prlib.RANDOM_LIST)
    movie = prlib.get_movie(prlib.LAST_RANDOM)
    return json.dumps(serialize_movie(movie))


@app.route("/delete_last")
def delete_last():
    prlib.delete_movie(prlib.LAST_RANDOM)
    return 'ok'
