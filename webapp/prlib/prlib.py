from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.orm.exc import NoResultFound
from .declarative import Base, Movie, File, create
from . import app

import random
import re
import socket
import subprocess
from pathlib import Path
from datetime import datetime


engine = create_engine('sqlite:///' + app.config['DB_FILE'])
compressed_regex = re.compile('-compressed\.mp4$')

Base.metadata.bind = engine
Session = sessionmaker(bind=engine, expire_on_commit=False)


def pick_random():
    global RANDOM_LIST
    global LAST_RANDOM
    if len(RANDOM_LIST) < 1:
        RANDOM_LIST = all_movies()
    RANDOM_LIST.sort(key=lambda movie: movie.change, reverse=True)
    total_change = sum([m.change for m in RANDOM_LIST])
    if total_change == 0:
        choice = random.choice(RANDOM_LIST)
        LAST_RANDOM = choice.id
        return choice
    choice = random.randint(0, total_change)
    counter = 0
    for m in RANDOM_LIST:
        counter = counter + m.change
        if counter >= choice:
            LAST_RANDOM = m.id
            m.last_played = datetime.now()
            session = Session()
            session.add(m)
            session.commit()
            session.close()
            return m


def compress(rows):
    files = all_files()
    ids = [row['id'] for row in rows]
    files = [file for file in files if file.movie_id in ids and not compressed_regex.search(file.location)]
    session = Session()
    for mId in [file.movie_id for fil in files]:
        movie = get_movie(mId)
        movie.comment += '_COMPRESSING_'
        session.add(movie)
    session.commit()
    session.close()
    locations = [file.location for file in files]
    print(locations)
    s = socket.socket()
    s.connect(('localhost', 1234))
    s.sendall(bytes('\n'.join(locations), 'UTF-8'))
    s.shutdown(socket.SHUT_WR)
    data = b''
    while 1:
        r = s.recv(1024)
        if r == b'':
            break
        data += r
    print(data.decode())
    s.close()


def tag_multiple(rows, tag):
    session = Session()
    for row in rows:
        movie = get_movie(row['id'])
        if movie.tags == '':
            movie.tags = tag
        else:
            movie.tags += ',' + tag
        session.add(movie)
        print(movie)
    session.commit()
    session.close()


def update_random_list(rows):
    global RANDOM_LIST
    movies = all_movies()
    ids = [row['id'] for row in rows]
    RANDOM_LIST = [movie for movie in movies if movie.id in ids]


def all_movies():
    session = Session()
    movies = session.query(Movie).options(joinedload(Movie.files)).all()
    session.close()
    return movies


def all_files():
    session = Session()
    files = session.query(File).all()
    session.close()
    return files


def get_nr_files_by_movie(id):
    session = Session()
    return session.query(File).filter(File.movie_id == id).count()


def get_files_by_movie(id):
    session = Session()
    m = session.query(Movie).options(joinedload(Movie.files)).filter(Movie.id == id).one()
    return m.files


def create_db():
    create()


def delete_movies(ids):
    for id in ids:
        delete_movie(id)


def delete_file(id):
    session = Session()
    file = session.query(File).filter(File.id == id).one()
    session.delete(file)
    session.commit()
    session.close()
    thumbnail = 'prlib/static/images/previews/' + file.thumbnail
    preview = 'prlib/static/images/previews/' + file.preview
    subprocess.call(['trash-put', file.location])
    subprocess.call(['trash-put', thumbnail])
    subprocess.call(['trash-put', preview])


def delete_movie(id):
    for i, movie in enumerate(RANDOM_LIST):
        if movie.id == id:
            del[RANDOM_LIST[i]]
            break
    session = Session()
    movie = session.query(Movie).options(joinedload(Movie.files)).filter(Movie.id == id).one()
    for id in [f.id for f in movie.files]:
        delete_file(id)
    subprocess.call(['trash-put', movie.location])
    session.delete(movie)
    session.commit()
    session.close()


def location_in_db(location):
    session = Session()
    try:
        session.query(Movie).filter(Movie.location == location).one()
    except NoResultFound:
        session.close()
        return False
    session.close()
    return True


def get_movie(id):
    session = Session()
    resp = session.query(Movie).options(joinedload(Movie.files)).filter(Movie.id == id).one()
    session.close()
    return resp


def update_movie(id, movie_dict):
    session = Session()
    movie = session.query(Movie).filter(Movie.id == id).one()
    for key in movie_dict:
        if key == 'files':
            continue
        setattr(movie, key, movie_dict[key])
    session.add(movie)
    session.commit()
    session.close()


if not Path(app.config['DB_FILE']).is_file():
    create()

RANDOM_LIST = []
LAST_RANDOM = 1

# s = Session()
# RANDOM_LIST = s.query(Movie).all()
# s.close()
# if len(RANDOM_LIST) > 0:
#     LAST_RANDOM = random.choice(RANDOM_LIST).id
# else:
#     LAST_RANDOM = 3
