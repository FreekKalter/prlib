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


class prlib:
    def __init__(self, session):
        self.session = session

    def __del__(self):
        self.session.close()

    @property
    def all_files(self):
        try:
            return self.files
        except AttributeError:
            self.files = self.session.query(File).all()
            return self.files

    @property
    def all_movies(self):
        try:
            return self.movies
        except AttributeError:
            self.movies = self.session.query(Movie).options(joinedload(Movie.files)).all()
            return self.movies

    def get_files_by_movie(self, id):
        m = self.session.query(Movie).options(joinedload(Movie.files)).filter(Movie.id == id).one()
        return m.files

    def get_movie(self, id):
        resp = self.session.query(Movie).options(joinedload(Movie.files)).filter(Movie.id == id).one()
        return resp

    def pick_random(self):
        global RANDOM_LIST
        global LAST_RANDOM
        if len(RANDOM_LIST) < 1:
            RANDOM_LIST = self.all_movies
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
                self.session.add(m)
                self.session.commit()
                return m

    def compress(self, rows):
        files = self.all_files
        ids = [row['id'] for row in rows]
        files = [file for file in files if file.movie_id in ids and not compressed_regex.search(file.location)]
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

    def tag_multiple(self, rows, tag):
        for row in rows:
            movie = self.get_movie(row['id'])
            if movie.tags == '':
                movie.tags = tag
            else:
                movie.tags += ',' + tag
            self.session.add(movie)
            print(movie)
        self.session.commit()

    def update_random_list(self, rows):
        global RANDOM_LIST
        movies = self.all_movies
        ids = [row['id'] for row in rows]
        RANDOM_LIST = [movie for movie in movies if movie.id in ids]

    def get_nr_files_by_movie(self, id):
        return self.ession.query(File).filter(File.movie_id == id).count()

    def create_db(self):
        create()

    def delete_movies(self, ids):
        for id in ids:
            self.delete_movie(id)

    def delete_file(self, id):
        try:
            self.files = self.all_files
            for i, f in enumerate(self.files):
                if f.id == id:
                    del self.files[i]
                    break
            file = self.session.query(File).filter(File.id == id).one()
        except NoResultFound:
            return
        self.session.delete(file)
        self.session.commit()
        thumbnail = 'prlib/static/images/previews/' + file.thumbnail
        preview = 'prlib/static/images/previews/' + file.preview
        subprocess.call(['trash-put', file.location])
        subprocess.call(['trash-put', thumbnail])
        subprocess.call(['trash-put', preview])

    def delete_movie(self, id):
        for i, movie in enumerate(RANDOM_LIST):
            if movie.id == id:
                del[RANDOM_LIST[i]]
                break
        movie = self.session.query(Movie).options(joinedload(Movie.files)).filter(Movie.id == id).one()
        for id in [f.id for f in movie.files]:
            self.delete_file(id)
        subprocess.call(['trash-put', movie.location])
        self.session.delete(movie)
        self.session.commit()

    def update_movie(self, id, movie_dict):
        movie = self.session.query(Movie).filter(Movie.id == id).one()
        for key in movie_dict:
            if key in ['files', 'size', 'compressed']:
                continue
            setattr(movie, key, movie_dict[key])
        self.session.add(movie)
        self.session.commit()


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
