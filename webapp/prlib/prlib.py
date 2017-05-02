from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .declarative import Base, Movie, File, create
from . import app

import os
import re
from datetime import datetime


movie_regex = re.compile('.*\.(mp4|avi|mpeg|mpg|wmv|mkv|m4v|flv|divx)$')
engine = create_engine('sqlite:///' + app.config['DB_FILE'])

Base.metadata.bind = engine
Session = sessionmaker(bind=engine)

IDS = [1 ,2, 3]


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
    # TODO: REMOVE THE 100 LIMIT!!!!!
    dirs = [(os.path.join(source_path, d), d) for d in os.listdir(source_path)]
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


def get_movie(id):
    session = Session()
    return session.query(Movie).filter(Movie.id == id).one()


def update_movie(id, movie_dict):
    session = Session()
    movie = session.query(Movie).filter(Movie.id == id).one()
    for key in movie_dict:
        setattr(movie, key, movie_dict[key])
    session.add(movie)
    session.commit()
