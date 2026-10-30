"""Silent owner-requested layout experiment, reusing approved v3 assets/matte."""
import hashlib
import json
import subprocess as sp
import sys
from pathlib import Path

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE.parent / 'coffee-minute-v3'))
import render as v3

BUILD = BASE / 'build'
OUT = BASE / 'deliverables'
W, H, FPS = 1280, 720, 24
SCALE, POSITION = .9, (-300, 45)
SHOTS = [('thinking', 'When can you\nease off?'),
         ('nod_yes', 'Make room for\nlife now, too.')]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def compose(raw, shot, f):
    im = v3.ART['office.png'].copy()
    actor = v3.actor_rgba(Image.frombytes('RGB', (W, H), raw))
    actor = actor.resize((1152, 648), Image.Resampling.LANCZOS)
    im.paste(actor, POSITION, actor)
    # All content is on the existing clear right-hand wall, above the floor
    # and entirely outside the desk/chair envelope. No background panel.
    d = ImageDraw.Draw(im)
    v3.text(d, (650, 70), SHOTS[shot][1], 48)
    if shot == 0:
        for i, label in enumerate(['Price your retirement', 'Test the setbacks', 'Choose what matters']):
            y = 235 + 73*i
            d.ellipse((655, y, 697, y+42), fill=v3.GREEN)
            v3.text(d, (669, y+4), str(i+1), 25, v3.CREAM)
            v3.text(d, (718, y+3), label, 30)
        # Purposeful progress through the worksheet; no moving numbers.
        y = 235 + 73*min(2, f//40)
        d.line((710, y+44, 1150, y+44), fill=v3.GREEN, width=3)
    else:
        # Small code-drawn booking confirmation. Arrival moves into a fixed
        # wall region in the first .5 seconds; then holds for reading.
        ease = 1-(1-min(1, f/12))**3
        x, y = 650+round(35*(1-ease)), 242
        d.rounded_rectangle((x,y,x+510,y+165), 15, fill=v3.CREAM, outline=v3.GREEN, width=3)
        v3.text(d, (x+25,y+19), 'TRIP CONFIRMED', 33, v3.GREEN)
        v3.text(d, (x+25,y+77), 'A plan for time together', 29)
        if f >= 12:
            d.line((x+425,y+41,x+440,y+55,x+474,y+24), fill=v3.GREEN, width=6)
    if f < 36 and shot == 0 or f >= 84 and shot == 1:
        v3.text(d, (650, 455), 'Educational only · Not financial advice', 20, v3.MUTED)
    # The actual visible silhouette must remain left of the content region.
    solid=actor.getchannel('A').point(lambda a: 255 if a>20 else 0)
    assert solid.getbbox()[2] + POSITION[0] < 620
    return im

def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    report=[]
    for idx, (clip,title) in enumerate(SHOTS):
        source=ROOT/'assets/ren_library'/f'ren_{clip}.mp4'
        info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
        video=next(s for s in info['streams'] if s['codec_type']=='video')
        assert (video['width'],video['height']) == (W,H)
        assert float(info['format']['duration']) >= 6.25
        decoder=sp.Popen(['ffmpeg','-v','error','-xerror','-ss','1.25','-i',str(source),'-an','-vf','fps=24','-frames:v','120','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=sp.PIPE)
        path=BUILD/f'shot_{idx+1:02d}.mp4'
        encoder=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
        for f in range(120):
            raw=decoder.stdout.read(W*H*3)
            assert len(raw)==W*H*3
            im=compose(raw,idx,f)
            encoder.stdin.write(im.tobytes())
            if f in (0,24,60,96,119): im.save(BUILD/f'source-{idx+1}-{f:03d}.png')
        decoder.stdout.close(); encoder.stdin.close()
        assert decoder.wait()==0 and encoder.wait()==0
        v3.check_video(path,120)
        report.append(dict(shot=idx+1,clip=clip,source_sha256=digest(source),source_duration=float(info['format']['duration']),source_interval=[1.25,6.25],start=idx*5,duration=5,frames=120,title=title))
        print(f'Rendered {idx+1}/2',flush=True)
    concat=BUILD/'concat.txt'
    concat.write_text("file 'shot_01.mp4'\nfile 'shot_02.mp4'\n")
    final=OUT/'Ren_Left_Layout_10s_Silent.mp4'
    sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-an','-movflags','+faststart',str(final)],check=True)
    v3.check_video(final,240)
    sp.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(final),'-f','null','-'],check=True)
    info=json.loads(sp.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(final)]))
    assert len(info['streams'])==1
    s=info['streams'][0]
    assert (s['codec_name'],s['width'],s['height'],s['r_frame_rate'],s['nb_read_frames'])==('h264',W,H,'24/1','240')
    assert float(info['format']['duration'])==10
    (BASE/'validation.json').write_text(json.dumps(dict(output=final.name,sha256=digest(final),duration=10,resolution=[W,H],fps=FPS,frames=240,audio_streams=0,new_voice_requests=0,full_decode='pass',shots=report,matte='approved v3, native 1280x720',actor_scale=SCALE,actor_position=POSITION,mirrored=False,framing='fixed throughout',content_region=[650,70,1210,480],visual_review='pending encoded-frame review'),indent=2)+'\n')
    print(final,flush=True)

if __name__=='__main__': main()
