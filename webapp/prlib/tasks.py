from . import app, celery, prlib
import os
import shlex
import codecs
import re
import subprocess
from pathlib import Path
from hashlib import sha256
from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from .declarative import Base, Movie, File

engine = create_engine('sqlite:///' + app.config['DB_FILE'])
movie_regex = re.compile('.*\.(mp4|avi|mpeg|mpg|wmv|mkv|m4v|flv|divx)$')

Base.metadata.bind = engine
# TODO: after in-memory cache, no more need for expire_on_commit?
Session = sessionmaker(bind=engine, expire_on_commit=False)


def make_hash(f):
    h = sha256()
    h.update(f.encode())
    return h.hexdigest()


@celery.task()
def scan_dir(source_path):
    session = Session()
    dirs = [d for d in os.listdir(source_path) if not d.startswith('.')]
    dirs = [(os.path.join(source_path, d), d) for d in dirs]

    # add new dir to db
    for d, name in dirs:
        if prlib.location_in_db(d):
            continue
        movie_files = []
        for root, dirs, files in os.walk(d):
            for f in files:
                if movie_regex.match(f):
                    fn = os.path.join(root, f)
                    movie_files.append((fn, os.stat(fn).st_size))
        if not movie_files:
            continue
        new_movie = Movie(name=name,
                          location=d,
                          added=datetime.now(),
                          size=sum([mf[1] for mf in movie_files]))
        session.add(new_movie)

        for f in movie_files:
            hash_digest = make_hash(f[0])
            make_thumbnail(f[0], hash_digest)
            make_preview.delay(f[0], hash_digest)
            new_file = File(location=f[0],
                            movie=new_movie,
                            size=f[1],
                            preview=hash_digest + '.gif',
                            thumbnail=hash_digest + '.png')
            session.add(new_file)

    # remove from db if no longer on filesystem
    movies = prlib.all_movies()
    for movie in movies:
        if not Path(movie.location).is_dir():
            session.delete(movie)

    session.commit()
    session.close()


def get_movie_files(d):
    movie_files = []
    for root, dirs, files in os.walk(d):
        for f in files:
            if movie_regex.match(f):
                fn = os.path.join(root, f)
                movie_files.append(fn)
    return movie_files


def make_thumbnail(movie, hash_digest, size=320):
    png_name = Path('./prlib/static/images/previews/').joinpath(hash_digest).with_suffix('.png')
    if png_name.is_file():
        # print('skipped: ', png_name)
        return
    print(png_name)
    create_png = 'ffmpeg -y -i "{input}" -ss 30 -ss 30 -vf scale=320:-1 -vframes 1 {output}'
    # create png
    c = shlex.split(create_png.format(input=movie, output=png_name))
    subprocess.call(c, stderr=subprocess.PIPE)


# TODO: use a temp dir for intermediary files
@celery.task()
def make_preview(movie, hash_digest, size=320, duration=1, nrsamples=8):
    # gif_name = Path(d).joinpath('.' + Path(movie).stem + '-preview.gif')
    gif_name = Path('./prlib/static/images/previews/').joinpath(hash_digest).with_suffix('.gif')

    if gif_name.is_file():
        # print('skipped: ', gif_name)
        return
    print(gif_name)
    cp = subprocess.run(['ffmpeg', '-i', movie], stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    output = codecs.decode(cp.stderr, errors='ignore')

    m = re.search('Duration: (?P<hours>\d{2}):(?P<minutes>\d{2}):\
(?P<seconds>\d{2})\.(?P<milliseconds>\d{2})', output)
    try:
        total_seconds = int(m.group('hours')) * 3600
        total_seconds = total_seconds + int(m.group('minutes')) * 60
        total_seconds = total_seconds + int(m.group('seconds'))
    except AttributeError:
        print('Error, can\'t find out duration:', movie)
        return

    # subtract first and last frames
    total_seconds = total_seconds - 60

    interval = int(total_seconds / nrsamples)
    intervals = [30]
    for i in range(1, nrsamples - 1):
        intervals.append(interval * i)
    intervals.append(total_seconds + 30)

    create_palette = 'ffmpeg -y -ss {start} -t {duration} -i "{input}" -vf \
fps=7,scale={size}:-1:flags=lanczos,palettegen palette-{index}.png'

    create_gif = 'ffmpeg -y -ss {start} -t {duration} -i "{input}" -i palette-{index}.png -filter_complex \
fps=7,scale={size}:-1:flags=lanczos[x];[x][1:v]paletteuse -threads 1 output-{index}.gif'

    outputs = []
    for i in range(len(intervals)):
        outputs.append('output-{}.gif'.format(i))
        # create pallet
        c = create_palette.format(input=movie, start=intervals[i], index=i, size=size, duration=duration)
        subprocess.call(shlex.split(c), stderr=subprocess.PIPE)

        # create gif
        c = create_gif.format(input=movie, start=intervals[i], index=i, size=size, duration=duration)
        subprocess.call(shlex.split(c), stderr=subprocess.PIPE)
    subprocess.call(['convert'] + outputs + [gif_name])
