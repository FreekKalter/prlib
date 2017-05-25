from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
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
    RANDOM_LIST.sort(key=lambda movie: movie.days, reverse=True)
    total_change = sum([m.days for m in RANDOM_LIST])
    if total_change == 0:
        return random.choice(RANDOM_LIST)
    choice = random.randint(0, total_change)
    counter = 0
    for m in RANDOM_LIST:
        counter = counter + m.days
        if counter >= choice:
            LAST_RANDOM = m.id
            m.last_played = datetime.now()
            m.days = 0
            session = Session()
            session.add(m)
            session.commit()
            session.close()
            return m


def update_random_list(rows):
    global RANDOM_LIST
    RANDOM_LIST = []
    for row in rows:
        m = get_movie(row['id'])
        if m.last_played:
            m.days = (datetime.now() - m.last_played).days
        else:
            m.days = 365
        if m.days > 365:
            m.days = 365
        RANDOM_LIST.append(m)


def all_movies():
    session = Session()
    movies = session.query(Movie).options(joinedload(Movie.files)).all()
    session.close()
    return movies


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
