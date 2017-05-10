import subprocess
import re
import os
from hashlib import sha256
import sys
import codecs
from pathlib import Path

movie_regex = re.compile('.*\.(mp4|avi|mpeg|mpg|wmv|mkv|m4v|flv|divx)$')


def make_preview(d, size=320, duration=1, nrsamples=8):
    movie_files = []
    for root, dirs, files in os.walk(d):
        for f in files:
            if movie_regex.match(f):
                fn = os.path.join(root, f)
                movie_files.append(fn)
    for movie in movie_files:
        # gif_name = Path(d).joinpath('.' + Path(movie).stem + '-preview.gif')
        h = sha256()
        h.update(movie.encode())
        gif_name = Path('./prlib/static/images/previews/').joinpath(h.hexdigest()).with_suffix('.gif')
        png_name = gif_name.with_suffix('.png')

        if gif_name.is_file():
            print('skipped: ', gif_name)
            continue
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
            continue

        # subtract first and last frames
        total_seconds = total_seconds - 60

        interval = int(total_seconds / nrsamples)
        intervals = [30]
        for i in range(1, nrsamples - 1):
            intervals.append(interval * i)
        intervals.append(total_seconds + 30)

        create_palette = 'ffmpeg -y -ss {start} -t {duration} -i movie -vf \
fps=7,scale={size}:-1:flags=lanczos,palettegen palette-{index}.png'

        create_gif = 'ffmpeg -y -ss {start} -t {duration} -i movie -i palette-{index}.png -filter_complex \
fps=7,scale={size}:-1:flags=lanczos[x];[x][1:v]paletteuse output-{index}.gif'

        create_png = 'ffmpeg -y -i input -ss 30 -ss 30 -vf scale=320:-1 -vframes 1 {output}'

        outputs = []
        for i in range(len(intervals)):
            outputs.append('output-{}.gif'.format(i))
            # create png
            c = create_png.format(output=png_name).split(' ')
            c[3] = movie
            subprocess.call(c, stderr=subprocess.PIPE)

            # create pallet
            c = create_palette.format(start=intervals[i], index=i, size=size, duration=duration).split(' ')
            c[7] = movie
            subprocess.call(c, stderr=subprocess.PIPE)

            # create gif
            c = create_gif.format(start=intervals[i], index=i, size=size, duration=duration).split(' ')
            c[7] = movie
            subprocess.call(c, stderr=subprocess.PIPE)
        subprocess.call(['convert'] + outputs + [gif_name])
        sys.stdout.flush()

source_path = '/data/bad'
dirs = [d for d in os.listdir(source_path) if not d.startswith('.')]
dirs = [os.path.join(source_path, d) for d in dirs]

for dir in dirs:
    make_preview(dir, nrsamples=8, duration=1)
