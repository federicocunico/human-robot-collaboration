from glob import glob
import os


FRAMES_FOLDER = "output"
FRAME_RATE = 8
cmd = "ffmpeg -framerate {framerate} -i {input}/%d.jpg {output}.mp4"


folders = glob(FRAMES_FOLDER+"/*")
for f in folders:
    if not os.path.isdir(f):
        continue
    
    n = f.split(os.sep)[-1]
    output = os.path.join(FRAMES_FOLDER, n)
    curr_cmd = cmd.format(input=f, framerate=FRAME_RATE, output=output)
    print(curr_cmd)
    os.system(curr_cmd)

