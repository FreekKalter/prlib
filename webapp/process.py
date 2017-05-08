import subprocess
import re

# TODO: HANDLE FILENAMES WITH SPACES!!!!!!!!!!!!!!!!
input_file = 'movie.mp4'
cp = subprocess.run(['ffmpeg', '-i', input_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

m = re.search('Duration: (?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})\.(?P<milliseconds>\d{2})', cp.stderr)
total_seconds = int(m.group('hours')) * 3600
total_seconds = total_seconds + int(m.group('minutes')) * 60
total_seconds = total_seconds + int(m.group('seconds'))
# subtract first and last frames
total_seconds = total_seconds - 60

interval = int(total_seconds/4)
start_counter = interval

intervals = [30, interval, interval*2, interval*3, total_seconds+30]

create_palette = 'ffmpeg -y -ss {start} -t 2 -i {input} -vf \
fps=7,scale=320:-1:flags=lanczos,palettegen palette-{index}.png'

create_gif = 'ffmpeg -y -ss {start} -t 2 -i {input} -i palette-{index}.png -filter_complex \
fps=7,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse \
output-{index}.gif'

outputs = []
for i in range(5):
    outputs.append('output-{}.gif'.format(i))
    # create pallet
    c = create_palette.format(start=intervals[i], input=input_file, index=i)
    print(c.split(' '))
    subprocess.call(c.split(' '))

    # create gif
    c = create_gif.format(start=intervals[i], input=input_file, index=i)
    print(c.split(' '))
    subprocess.call(c.split(' '))

subprocess.call(['convert'] + outputs + ['result.gif'])
