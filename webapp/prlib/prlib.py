from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .declarative import Base, Movie, File

import os
import re
import json


movie_regex = re.compile('.*\.(mp4|avi|mpeg|mpg|wmv|mkv|m4v|flv|divx)$')
engine = create_engine('sqlite:///movie.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def write():
    new_movie = Movie(name='Anal', rating=100)
    session.add(new_movie)
    session.commit()

    new_file = File(location='/data/bad/anal/a.mp4', movie=new_movie)
    session.add(new_file)
    session.commit()


def all_movies():
    movies = session.query(Movie).all()
    return movies


def read():
    movies = session.query(Movie).all()
    for m in movies:
        files = session.query(File).filter(File.movie == m).all()
        if len(files) > 1:
            for f in files:
                print(f.location, f.size)


def add_to_db():
    source_path = '/data/bad'
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
        new_movie = Movie(name=name, size=sum([mf[1] for mf in movie_files]))
        session.add(new_movie)
        session.commit()

        for f in movie_files:
            new_file = File(location=f[0], movie=new_movie, size=f[1])
            session.add(new_file)
            session.commit()
