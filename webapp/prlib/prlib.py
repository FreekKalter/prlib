from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .declarative import Base, Movie, File, create
from . import app

import random
import subprocess
from pathlib import Path
from datetime import datetime


engine = create_engine('sqlite:///' + app.config['DB_FILE'])

Base.metadata.bind = engine
Session = sessionmaker(bind=engine, expire_on_commit=False)


def pick_random():
    global RANDOM_LIST
    global LAST_RANDOM
    RANDOM_LIST.sort(key=lambda movie: movie.last_played or datetime.fromtimestamp(0), reverse=True)
    total_change = sum(range(len(RANDOM_LIST)))
    choice = random.randint(0, total_change)
    counter = 0
    for i in range(len(RANDOM_LIST)):
        counter = counter + i
        if counter >= choice:
            LAST_RANDOM = RANDOM_LIST[i].id
            movie = RANDOM_LIST[i]
            movie.last_played = datetime.now()
            session = Session()
            session.add(movie)
            session.commit()
            session.close()
            return movie


def update_random_list(rows):
    global RANDOM_LIST
    RANDOM_LIST = []
    for row in rows:
        RANDOM_LIST.append(get_movie(row['id']))


def all_movies():
    session = Session()
    movies = session.query(Movie).all()
    session.close()
    return movies


def get_nr_files_by_movie(id):
    session = Session()
    return session.query(File).filter(File.movie_id == id).count()


def get_files_by_movie(id):
    session = Session()
    return session.query(File).filter(File.movie_id == id).all()


def create_db():
    create()


def delete_movies(ids):
    for id in ids:
        delete_movie(id)


def delete_files(ids):
    for id in ids:
        delete_file(id)


def delete_file(id):
    session = Session()
    file = session.query(File).filter(File.id == id).one()
    thumbnail = 'prlib/static/images/previews/' + file.thumbnail
    preview = 'prlib/static/images/previews/' + file.preview
    if not app.config['DEBUG']:
        subprocess.call(['trash-put', file.location])
        subprocess.call(['trash-put', thumbnail])
        subprocess.call(['trash-put', preview])
    session.delete(file)
    session.commit()
    session.close()


def delete_movie(id):
    for i, movie in enumerate(RANDOM_LIST):
        if movie.id == id:
            del[RANDOM_LIST[i]]
            break
    session = Session()
    movie = session.query(Movie).filter(Movie.id == id).one()
    files = get_files_by_movie(movie.id)
    delete_files([file.id for file in files])
    if not app.config['DEBUG']:
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
    resp = session.query(Movie).filter(Movie.id == id).one()
    session.close()
    return resp


def update_movie(id, movie_dict):
    session = Session()
    movie = session.query(Movie).filter(Movie.id == id).one()
    for key in movie_dict:
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
