"""One-minute visual revision; continuous existing audio, no TTS requests."""
import hashlib
from unpack_artwork import unpack
import json
import subprocess as sp
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import binary_propagation

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
W, H, FPS = 1280, 720, 24
ACTOR_W, ACTOR_H = 1280, 720
INK, GREEN, CREAM, MUTED = '#172A3A', '#3F665B', '#FAF6EE', '#63736D'
DAILY, HOME, DAYS = 4, 1, 365
YEAR, DIFFERENCE, NET = DAILY * DAYS, DAILY - HOME, (DAILY - HOME) * DAYS
assert (YEAR, DIFFERENCE, NET) == (1460, 3, 1095)

def font(size):
    return ImageFont.truetype(str(ROOT/'project/remotion/public/fonts/fredoka-latin-600-normal.woff2'), size)

def shot(kind, n, title='', **kw):
    return dict(kind=kind, frames=n, title=title, **kw)

SHOTS = [
    shot('ren',50,'KEEP THE\nCOFFEE?',clip='present_palm_left'),
    shot('ren',100,'COFFEE\nON TRIAL?',clip='nod_yes',close=True),
    shot('story',54,image='alex-cafe.png'),
    shot('purpose',72,'What should your money do?'),
    shot('ren',108,'LESS JOY\nIS NOT THE GOAL.',clip='shake_no'),
    shot('ren',65,'WHAT NEEDS\nTO CHANGE?',clip='thinking',close=True),
    shot('story',54,image='alex-cafe.png',detail=True),
    shot('ren',83,'START WITH\nTHE NUMBERS.',clip='present_palm_left'),
    shot('daily',78,'An illustrative daily habit'),
    shot('ren',102,'EVERY DAY.\n365 DAYS.',clip='nod_yes',close=True),
    shot('annual',78,'Across a full year'),
    shot('ren',108,'YOUR NUMBERS\nMAY DIFFER.',clip='present_palm_left'),
    shot('ren',50,'AN EXAMPLE.\nYOUR BUDGET\nMAY DIFFER.',clip='thinking',close=True),
    shot('ren',92,'SPENDING\nIS NOT THE SAME\nAS SAVING.',clip='shake_no'),
    shot('story',54,image='alex-home.png'),
    shot('ren',99,'COMPARE THE\nDIFFERENCE.',clip='present_palm_left',close=True),
    shot('net',78,'Compare the two choices'),
    shot('ren',101,'THREE DOLLARS\nLESS PER DAY.',clip='nod_yes'),
    shot('netannual',53,'The illustrative yearly difference'),
]
assert sum(s['frames'] for s in SHOTS) == 1479

unpack()
ART = {p.name: ImageOps.fit(Image.open(p).convert('RGB'), (W,H)) for p in (BASE/'assets').glob('*.png')}

def text(d, xy, value, size=42, fill=INK):
    d.multiline_text(xy,value,font=font(size),fill=fill,spacing=8)

def centered(d,y,value,size=42,fill=INK):
    text(d,((W-d.textlength(value,font=font(size)))/2,y),value,size,fill)

def cup(d,x,y,scale=1,fill=GREEN):
    def b(a): return tuple(round(v*scale+(x if i%2==0 else y)) for i,v in enumerate(a))
    d.arc(b((80,15,130,85)),270,90,fill=fill,width=max(3,round(8*scale)))
    d.rounded_rectangle(b((0,0,95,100)),radius=round(12*scale),fill=fill)
    d.ellipse(b((7,3,88,20)),fill=CREAM)
    d.line(b((-5,112,110,112)),fill=fill,width=max(3,round(6*scale)))

def actor_rgba(frame):
    a=np.asarray(frame).astype(np.float32)
    dist=np.sqrt(np.mean(((255-a)/255)**2,axis=2))
    seed=np.zeros(dist.shape,dtype=bool)
    seed[0,:]=seed[-1,:]=True
    seed[:,0]=seed[:,-1]=True
    exterior=binary_propagation(seed & (dist<.13),mask=dist<.13)
    alpha=np.ones(dist.shape,dtype=np.float32)
    alpha[exterior]=np.clip((dist[exterior]-.06)/.06,0,1)
    return Image.fromarray(np.dstack([a,alpha*255]).astype('uint8'),'RGBA')

def picture(s,frame,actor=None):
    p=frame/max(1,s['frames']-1)
    ease=1-(1-min(1,p/.35))**3
    k=s['kind']
    if k=='story':
        art=ART[s['image']]
        z=(1.13 if s.get('detail') else 1)+.035*p
        large=art.resize((round(W*z),round(H*z)),Image.Resampling.LANCZOS)
        cx=(large.width-W)//2
        cy=(large.height-H)//2
        return large.crop((cx,cy,cx+W,cy+H))
    if k=='ren':
        im=ART['office.png'].copy()
        # Matte the native-resolution source before one final composition resize.
        # Preserve enclosed white shirt/shoes; never downsample the actor first.
        close=s.get('close',False)
        factor=3.3 if close else 2.2
        rgba=actor_rgba(actor)
        rgba=rgba.resize((round(640*factor),round(360*factor)),Image.Resampling.LANCZOS)
        im.paste(rgba,(-5 if close else 326,10 if close else 55),rgba)
        d=ImageDraw.Draw(im)
        text(d,(550,100+round(10*(1-ease))),s['title'],34 if len(s['title'])>34 else 39)
        return im
    im=Image.new('RGB',(W,H),CREAM)
    d=ImageDraw.Draw(im)
    text(d,(65,45),s['title'],43)
    text(d,(65,105),'Example figures' if k!='purpose' else 'A plan for today and tomorrow',24,MUTED)
    if k=='purpose':
        labels=['Cover what matters','Protect tomorrow','Enjoy something today']
        for i,label in enumerate(labels):
            x=80+i*405
            yy=250+round((1-min(1,max(0,p*4-i*.6)))*60)
            d.ellipse((x,yy,x+68,yy+68),fill=GREEN)
            text(d,(x+23,yy+9),str(i+1),35,CREAM)
            words=label.split()
            text(d,(x,yy+105),' '.join(words[:2])+'\n'+' '.join(words[2:]),31)
    elif k=='daily':
        cup(d,160,250,1.8)
        text(d,(480,200),f'${DAILY}',115,GREEN)
        text(d,(490,345),'per day',40)
        for i in range(7):
            x=485+i*86
            d.rounded_rectangle((x,440,x+62,507),radius=9,fill=GREEN if p>(i/12) else '#DCE4DB')
            if p>(i/12): d.line((x+16,474,x+27,486,x+47,461),fill=CREAM,width=4)
    elif k in ('annual','netannual'):
        # Equations and monetary totals stay correct on EVERY frame.
        total=YEAR if k=='annual' else NET
        equation=f'${DAILY} × {DAYS} days = ${YEAR:,}' if k=='annual' else f'(${DAILY} − ${HOME}) × {DAYS} days = ${NET:,}'
        centered(d,190,f'${total:,}',122,GREEN)
        centered(d,350,equation,42)
        centered(d,430,'Total purchased coffee' if k=='annual' else 'Difference after replacement costs',30,MUTED)
        # Motion belongs to the calendar dots, never an incorrect equation.
        for i in range(36):
            x=108+(i%18)*60
            y=525+(i//18)*39
            d.ellipse((x,y,x+16,y+16),fill=GREEN if p>(i/48) else '#DCE4DB')
    elif k=='net':
        cup(d,130,250,1.25)
        cup(d,660,250,1.25,fill='#B67C55')
        text(d,(320,220),f'${DAILY}',90,GREEN)
        text(d,(850,220),f'${HOME}',90,'#B67C55')
        text(d,(135,420),'Bought coffee',32)
        text(d,(665,420),'Made at home',32)
        centered(d,535,f'${DAILY} − ${HOME} = ${DIFFERENCE} difference per day',42)
        # Animated connector joins the same two choices.
        d.line((480,335,480+round(110*ease),335),fill=MUTED,width=5)
    return im

def cmd(args): sp.run(args,check=True)

def check_video(path, expected):
    info=json.loads(sp.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames','-of','json',str(path)]))
    assert int(info['streams'][0]['nb_read_frames'])==expected, str(path)

def main(preview=False):
    out=BASE/'build'
    out.mkdir(exist_ok=True)
    library=json.loads((ROOT/'assets/ren_library/ren_library.json').read_text())
    clips={c['file']:c for c in library['clips']}
    report=[]
    thumbs=[]
    for i,s in enumerate(SHOTS,1):
        decoder=None
        if s['kind']=='ren':
            path=ROOT/'assets/ren_library'/('ren_'+s['clip']+'.mp4')
            meta=clips[path.name]
            dimensions=json.loads(sp.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(path)]))['streams'][0]
            assert (dimensions['width'],dimensions['height'])==(ACTOR_W,ACTOR_H), f'Unexpected actor source dimensions: {path}'
            assert meta['in_s']+s['frames']/FPS<=meta['out_s']
            decoder=sp.Popen(['ffmpeg','-v','error','-xerror','-ss',str(meta['in_s']),'-i',str(path),'-an','-vf','fps=24','-frames:v',str(s['frames']),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=sp.PIPE)
        encoder=None
        if not preview:
            encoder=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(out/f'shot_{i:02d}.mp4')],stdin=sp.PIPE)
        for f in range(s['frames']):
            actor=None
            if decoder:
                raw=decoder.stdout.read(ACTOR_W*ACTOR_H*3)
                assert len(raw)==ACTOR_W*ACTOR_H*3
                actor=Image.frombytes('RGB',(ACTOR_W,ACTOR_H),raw)
            if encoder or f==s['frames']//2:
                im=picture(s,f,actor)
                if i in (1,len(SHOTS)):
                    text(ImageDraw.Draw(im),(38,678),'Educational only • Not financial advice',20)
                if encoder: encoder.stdin.write(im.tobytes())
                if f==s['frames']//2:
                    im.save(out/f'frame_{i:02d}.jpg')
                    thumb=im.resize((320,180))
                    ImageDraw.Draw(thumb).text((5,5),str(i),fill='black',stroke_width=2,stroke_fill='white')
                    thumbs.append(thumb)
        if decoder:
            decoder.stdout.close()
            assert decoder.wait()==0
        if encoder:
            encoder.stdin.close()
            assert encoder.wait()==0
            check_video(out/f'shot_{i:02d}.mp4',s['frames'])
        report.append(dict(shot=i,**s))
        print(f'{"Checked" if preview else "Rendered"} {i}/{len(SHOTS)}',flush=True)
    contact=Image.new('RGB',(1280,180*((len(thumbs)+3)//4)),CREAM)
    for i,t in enumerate(thumbs): contact.paste(t,((i%4)*320,(i//4)*180))
    contact.save(out/'contact.jpg')
    if preview: return
    audio=ROOT/'project/pilots/daily-coffee/deliverables/narration.wav'
    narration=out/'narration.wav'
    cmd(['ffmpeg','-v','error','-xerror','-y','-i',str(audio),'-t','61.625','-c:a','pcm_s16le',str(narration)])
    concat=out/'concat.txt'
    concat.write_text('\n'.join("file 'shot_%02d.mp4'"%i for i in range(1,len(SHOTS)+1)))
    final=BASE/'Ren_61s_Coffee_Prototype_v3.mp4'
    cmd(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(narration),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','61.625','-movflags','+faststart',str(final)])
    check_video(final,1479)
    cmd(['ffmpeg','-v','error','-xerror','-i',str(final),'-f','null','-'])
    (BASE/'revision-report.json').write_text(json.dumps(dict(shots=report,duration=61.625,source_narration_sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),new_voice_requests=0,actor_decode_resolution=[ACTOR_W,ACTOR_H],maths=dict(annual=YEAR,daily_difference=DIFFERENCE,annual_difference=NET),lip_sync=False),indent=2))
    print(final,flush=True)

if __name__=='__main__':
    import sys
    main('--preview' in sys.argv)
