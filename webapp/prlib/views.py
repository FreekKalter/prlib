from flask import render_template, request
from . import app, prlib, tasks
from sqlalchemy.orm.exc import NoResultFound
import json
import os
from datetime import datetime
import subprocess
from pathlib import Path


@app.route("/")
def root():
    return render_template('index.html')


def serialize_movie(m):
    movie = {'id': m.id,
             'name': m.name,
             'location': m.location,
             'size': m.size,
             'tags': m.tags,
             'added': m.added.timestamp(),
             'rating': m.rating,
             'nr_files': len(m.files),
             'files': [(Path(file.location).name, file.size) for file in m.files]}
    if not movie['rating']:
        movie['rating'] = 0
    if not movie['tags']:
        movie['tags'] = ''
    if m.last_played:
        movie['last_played'] = m.last_played.timestamp()
    else:
        movie['last_played'] = 0
    return movie


def serialize_file(f):
    new_file = {'id': f.id,
                'location': f.location,
                'size': f.size,
                'preview': f.preview,
                'thumbnail': f.thumbnail}
    return new_file


@app.route("/all_movies")
def all_movies():
    movies = prlib.all_movies()
    serialize = []
    for m in movies:
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
def scan_dir_view():
    tasks.scan_dir.delay('/data/bad')
    return 'Added new files to db'


@app.route("/repair")
def repair_view():
    tasks.repair.delay('/data/bad')
    return 'Repaired db'


@app.route("/reinit_db")
def reinit_db():
    os.unlink(app.config['DB_FILE'])
    prlib.create_db()
    tasks.scan_dir.delay('/data/bad')
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
    movie['added'] = datetime.fromtimestamp(movie['added'])
    movie['last_played'] = datetime.fromtimestamp(movie['last_played'])
    print(movie)
    prlib.update_movie(id, movie)
    return 'success'


@app.route("/movie/<id>", methods=["DELETE"])
def movie_delete(id):
    print(id)
    prlib.delete_movie(id)
    return json.dumps('status')


@app.route("/play/<id>")
def play(id):
    movie = prlib.get_movie(id)
    prlib.update_movie(id, {'last_played': datetime.now()})
    subprocess.Popen(['vlc', movie.location], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return 'ok'


@app.route("/visible_ids", methods=["POST"])
def visible_ids():
    rows = json.loads(request.data)
    prlib.update_random_list(rows)
    return 'ok!'


@app.route("/compress", methods=["POST"])
def compress():
    rows = json.loads(request.data)
    prlib.compress(rows)
    return 'got it'


@app.route("/tagmultiple", methods=["POST"])
def tagmultiple():
    data = json.loads(request.data)
    prlib.tag_multiple(data['rows'], data['tag'])
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
    movie = prlib.pick_random()
    return json.dumps(serialize_movie(movie))


@app.route("/get_files/<id>")
def get_files(id):
    files = prlib.get_files_by_movie(id)
    serialezed = [serialize_file(file) for file in files]
    return json.dumps(serialezed)


@app.route("/delete_last")
def delete_last():
    prlib.delete_movie(prlib.LAST_RANDOM)
    return 'ok'
