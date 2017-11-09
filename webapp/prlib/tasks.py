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
from sqlalchemy.orm import sessionmaker, joinedload
import sqlalchemy.orm.exc
from .declarative import Base, Movie, File

engine = create_engine('sqlite:///' + app.config['DB_FILE'])
movie_regex = re.compile('.*\.(mp4|avi|mpeg|mpg|wmv|mkv|m4v|flv|divx)$')
compress_regex = re.compile('_COMPRESSING_$')

Base.metadata.bind = engine
# TODO: after in-memory cache, no more need for expire_on_commit?
Session = sessionmaker(bind=engine, expire_on_commit=False)


def make_hash(f):
    h = sha256()
    h.update(f.encode())
    return h.hexdigest()


def get_movie_files(d):
    movie_files = []
    for root, dirs, files in os.walk(d):
        for f in files:
            if movie_regex.match(f):
                fn = os.path.join(root, f)
                movie_files.append((fn, os.stat(fn).st_size))
    return movie_files


def add_movie(d):
    session = Session()
    movie_files = get_movie_files(d)
    if not movie_files:
        session.close()
        return
    print('adding movie: {}'.format(Path(d).stem))
    print([item[0] for item in movie_files])
    new_movie = Movie(name=Path(d).stem,
                      location=d,
                      added=datetime.now(),
                      size=sum([mf[1] for mf in movie_files]))
    session.add(new_movie)
    add_files_to_movie(session, new_movie, movie_files)
    session.commit()
    session.close()


def add_files_to_movie(s, movie, movie_files):
    for f in movie_files:
        hash_digest = make_hash(f[0])
        make_thumbnail(f[0], hash_digest)
        make_preview.delay(f[0], hash_digest)
        new_file = File(location=f[0],
                        movie=movie,
                        size=f[1],
                        preview=hash_digest + '.gif',
                        thumbnail=hash_digest + '.png')
        s.add(new_file)
        s.commit()


@celery.task()
def scan_dir(source_path):
    session = Session()
    dirs = [d for d in os.listdir(source_path) if not d.startswith('.')]
    dirs = [(os.path.join(source_path, d), d) for d in dirs if not d.startswith('_UNPACK_')]

    # add new dir to db
    for d, name in dirs:
        if prlib.location_in_db(d):
            continue
        add_movie(d)

    # remove from db if no longer on filesystem
    movies = prlib.all_movies()
    for movie in movies:
        if not Path(movie.location).is_dir():
            print('no longer on fs: {}'.format(movie.location))
            prlib.delete_movie(movie.id)
    session.commit()
    session.close()


@celery.task()
def repair(source_path):
    print('------------------------------------------------------------------')
    print('----------scan files to add new movies')
    scan_dir(source_path)

    print('----------delete previews if to small to be not corrupted')
    p_dir = './prlib/static/images/previews/'
    for f in os.listdir(p_dir):
        f = Path(os.path.join(p_dir, f))
        if os.stat(f).st_size < 5:
            f.unlink()

    print('----------delete previews if file no longer in db')
    # delete previews if file no longer in db
    files = prlib.all_files()
    thumbnails = [f.thumbnail for f in files]  # png
    previews = [f.preview for f in files]  # gif
    for f in os.listdir(p_dir):
        if f.endswith('gif') and f not in previews:
            subprocess.call(['trash-put', os.path.join(p_dir, f)])
        if f.endswith('png') and f not in thumbnails:
            subprocess.call(['trash-put', os.path.join(p_dir, f)])

    print('----------check if file still exists on fs, if not rescan that dir')
    # when compressing via interface, add _COMPRESSING_ to the comments field of the movie
    # when we would have deleted it here, check if _COMPRESSING_ is in the comments
    # then delete old Files belong to movie and scan dir for new files
    # without touching Movie itself and thus keeping (tags, comments, rating)

    session = Session()
    for f in files:
        if not Path(f.location).exists():
            movie = prlib.get_movie(f.movie_id)
            for f in movie.files:
                session.delete(f)
                session.commit()
            add_files_to_movie(session, movie, get_movie_files(movie.location))
            if movie.comment:
                movie.comment = compress_regex.sub('', movie.comment)
                session.add(movie)
            # else:
            #     # delete movie from db
            #     try:
            #         movie = session.query(Movie).options(joinedload(Movie.files)).filter(Movie.id == f.movie_id).one()
            #     except sqlalchemy.orm.exc.NoResultFound:
            #         print('sql no results for: {}'.format(f.location))
            #         prlib.delete_file(f.id)
            #         continue
            #     location = movie.location
            #     print(location)
            #     session.delete(movie)
            #     add_movie(location)

    print('----------check if every file in db has a corresponding png/gif')
    # check if every file has a corresponding png and gif
    for f in files:
        h = make_hash(f.location)
        base = Path(p_dir).joinpath(h)
        png = base.with_suffix('.png')
        gif = base.with_suffix('.gif')
        if f.preview != 'no_preview' and not gif.exists():
            print('making missing gif: {}'.format(gif))
            if make_preview(f.location, h) == 'error':
                print('error creating: {}'.format(gif))
                f.preview = 'no_preview'
                session.add(f)

        if f.thumbnail != 'no_thumbnail' and not png.exists():
            print('making missing png: {}'.format(png))
            if make_thumbnail(f.location, h) == 'error':
                print('error creating: {}'.format(png))
                f.thumbnail = 'no_thumbnail'
                session.add(f)

    print('----------delete movies without files')
    for movie in prlib.all_movies():
        if len(movie.files) == 0:
            print(movie.location)
            prlib.delete_movie(movie.id)

    session.commit()
    session.close()
    print('------------------------------------------------------------------')


def get_duration(movie):
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
        return('error')
    return total_seconds


def make_thumbnail(movie, hash_digest, size=320):
    png_name = Path('./prlib/static/images/previews/').joinpath(hash_digest).with_suffix('.png')
    if png_name.is_file():
        print('skipped: ', png_name)
        return
    print(movie)
    print(png_name)
    duration = get_duration(movie)
    if duration < 50:
        create_png = 'ffmpeg -y -i "{input}" -ss 3 -ss 3 -vf scale=320:-1 -vframes 1 {output}'
    else:
        create_png = 'ffmpeg -y -i "{input}" -ss 50 -ss 50 -vf scale=320:-1 -vframes 1 {output}'
    # create png
    c = shlex.split(create_png.format(input=movie, output=png_name))
    try:
        subprocess.check_call(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return 'error'


# TODO: use a temp dir for intermediary files
@celery.task()
def make_preview(movie, hash_digest, size=320, duration=1, nrsamples=8):
    # gif_name = Path(d).joinpath('.' + Path(movie).stem + '-preview.gif')
    gif_name = Path('./prlib/static/images/previews/').joinpath(hash_digest).with_suffix('.gif')

    if gif_name.is_file():
        # print('skipped: ', gif_name)
        return
    print(gif_name)

    total_seconds = get_duration(movie)
    # subtract first and last frames
    total_seconds -= 60

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
    try:
        subprocess.check_call(['convert'] + outputs + [gif_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return 'error'
