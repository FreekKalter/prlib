from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .declarative import Base, Movie, File, create
from . import app

import os
import re
import random
import subprocess
from pathlib import Path
from datetime import datetime


movie_regex = re.compile('.*\.(mp4|avi|mpeg|mpg|wmv|mkv|m4v|flv|divx)$')
if not Path(app.config['DB_FILE']).is_file():
    create()
engine = create_engine('sqlite:///' + app.config['DB_FILE'])

Base.metadata.bind = engine
Session = sessionmaker(bind=engine, expire_on_commit=False)

s = Session()
RANDOM_LIST = s.query(Movie).all()
s.close()
LAST_RANDOM = random.choice(RANDOM_LIST).id


def pick_random():
    global RANDOM_LIST
    global LAST_RANDOM
    RANDOM_LIST.sort(key=lambda movie: movie.last_played or datetime.fromtimestamp(0), reverse=True)
    print('length of ranomd list', len(RANDOM_LIST))
    # for movie in RANDOM_LIST:
    #         print('{0: <80}'.format(movie.name), (movie.last_played or datetime.fromtimestamp(0)))
    total_change = sum(range(len(RANDOM_LIST)))
    choice = random.randint(0, total_change)
    print('choice', choice, 'total_change', total_change)
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
            print(movie.id)
            return movie


def update_random_list(rows):
    global RANDOM_LIST
    # TODO: get lots of id in a bunch, but only if it proofs to be to slow
    RANDOM_LIST = []
    for row in rows:
        RANDOM_LIST.append(get_movie(row['id']))


def all_movies():
    session = Session()
    movies = session.query(Movie).all()
    session.close()
    return movies


def create_db():
    create()


def add_to_db():
    session = Session()
    source_path = '/data/bad'
    dirs = [d for d in os.listdir(source_path) if not d.startswith('.')]
    dirs = [(os.path.join(source_path, d), d) for d in dirs]

    for d, name in dirs:
        movie_files = []
        for root, dirs, files in os.walk(d):
            for f in files:
                if movie_regex.match(f):
                    fn = os.path.join(root, f)
                    movie_files.append((fn, os.stat(fn).st_size))
        if not movie_files:
            continue
        print(name, '\t', len(movie_files))
        print('\t', movie_files)
        new_movie = Movie(name=name,
                          location=d,
                          added=datetime.now(),
                          size=sum([mf[1] for mf in movie_files]))
        session.add(new_movie)
        session.commit()

        for f in movie_files:
            new_file = File(location=f[0], movie=new_movie, size=f[1])
            session.add(new_file)
            session.commit()
    session.close()


def delete_movie(id):
    for i, movie in enumerate(RANDOM_LIST):
        if movie.id == id:
            del[RANDOM_LIST[i]]
            break
    session = Session()
    movie = session.query(Movie).filter(Movie.id == id).one()
    subprocess.call(['trash-put', movie.location])
    session.delete(movie)
    session.commit()
    session.close()


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
