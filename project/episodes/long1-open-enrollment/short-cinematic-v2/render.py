"""Portrait environmental prototype; approved native Ren matte and cached scene chunks."""
from pathlib import Path
import functools
import importlib.util
import json
import math
import os
import subprocess as sp
import sys
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D=Path(__file__).resolve().parent; B=D.parent; ROOT=B.parents[2]
sys.path.insert(0,str(B))
sys.path.insert(0,str(ROOT/'project/pipeline'))
import shorts_standards as standards
spec=importlib.util.spec_from_file_location('approved_health_parent',B/'render.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
W,H,FPS=1080,1920,24
INK='#172A3A';GREEN='#3F665B';CREAM='#FAF6EE';SAGE='#B8CCB1'
BUILD=D/'build';OUT=D/'deliverables';BUILD.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
M=json.loads((D/'production.json').read_text())
OFFICE=Image.open(ROOT/'project/prototypes/coffee-minute-v3/assets/office.png').convert('RGB')
REC=standards.LayoutRecorder()
@functools.lru_cache(maxsize=50)
def font(size):return ImageFont.truetype(str(ROOT/'project/remotion/public/fonts/fredoka-latin-600-normal.woff2'),size)
def ease(x):return 1-(1-float(np.clip(x,0,1)))**3

def txt(im,scene,n,xy,value,size=48,fill=INK,role='text',stroke=0):
    draw=ImageDraw.Draw(im);draw.multiline_text(xy,value,font=font(size),fill=fill,spacing=8,stroke_width=stroke,stroke_fill=CREAM)
    # Instrument the exact final-output draw, not a guessed text rectangle.
    REC.record(scene['id'],draw,xy,value,font(size),(scene['start_frame']+n)/24,
               (scene['start_frame']+n+1)/24,role,spacing=8,stroke_width=stroke)

def shadow(im,box,radius=15):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);d.rounded_rectangle(tuple(round(v) for v in box),radius,fill=(20,30,24,55));im.paste(Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(12))).convert('RGB'))

@functools.lru_cache(maxsize=4)
def room(which):
    # Environmental original fills the complete output; no video window/frame.
    crop=(180,0,709,941) if which==0 else (350,0,879,941)
    return OFFICE.crop(crop).resize((W,H),Image.Resampling.LANCZOS)

@functools.lru_cache(maxsize=4)
def tabletop(which=0):
    # Reusable hand-drawn prop environment, code-built, not a slide background.
    im=Image.new('RGB',(W,H),'#CA9B6C');d=ImageDraw.Draw(im)
    colors=['#BB885A','#D7AD7F','#BA885A','#D3A273']
    for i,y in enumerate(range(-140,2100,250)):
        d.polygon([(0,y),(1080,y+115),(1080,y+365),(0,y+250)],fill=colors[i%4])
        d.line((0,y+250,1080,y+365),fill='#A97951',width=4)
        for j in [45,95,155,205]:
            d.line([(0,y+j),(290,y+j+20),(680,y+j+85),(1080,y+j+115)],fill='#C69568',width=2)
    # Sage desk mat and real environmental peripherals extend off canvas.
    d.rounded_rectangle((-120,205,1190,1490),70,fill='#768D7B',outline='#4B6859',width=5)
    d.line((30,240,1070,240),fill='#9DB09A',width=3)
    # Pencil on the table, not a stock icon.
    d.polygon([(995,380),(1020,386),(950,1250),(932,1285),(925,1245)],fill='#D3B485',outline=INK,width=3)
    d.polygon([(932,1285),(935,1255),(950,1250)],fill='#4A4A43')
    return im

@functools.lru_cache(maxsize=200)
def actor(clip,index):
    return Image.open(BUILD/f'actor-{clip}'/f'{index:03}.png').convert('RGBA')

def prepare_actors():
    configs=[('nod_yes',.5,66),('thinking',1.25,84)]
    for clip,start,count in configs:
        source=ROOT/'assets/ren_library'/f'ren_{clip}.mp4';folder=BUILD/f'actor-{clip}';folder.mkdir(exist_ok=True)
        signature=standards.digest({'source':standards.sha(source),'matte':standards.sha(B/'render.py'),
                                   'start':start,'frames':count,'crop':[465,0,825,720],'size':[400,800]})
        mark=folder/'cache.json'
        if mark.exists() and json.loads(mark.read_text())['key']==signature and all((folder/f'{i:03}.png').exists() for i in range(count)):continue
        dec=sp.Popen(['ffmpeg','-v','error','-xerror','-ss',str(start),'-i',str(source),'-an','-frames:v',str(count),'-pix_fmt','rgb24','-f','rawvideo','-'],stdout=sp.PIPE)
        for i in range(count):
            raw=dec.stdout.read(1280*720*3);assert len(raw)==1280*720*3
            rgba=parent.matte(Image.frombytes('RGB',(1280,720),raw))
            rgba=rgba.crop((465,0,825,720)).resize((400,800),Image.Resampling.LANCZOS)
            rgba.save(folder/f'{i:03}.png')
        dec.stdout.close();assert dec.wait()==0
        mark.write_text(json.dumps({'key':signature}))

def desk_front(im):
    d=ImageDraw.Draw(im)
    d.polygon([(0,1180),(1080,1130),(1080,1430),(0,1510)],fill='#C69A70',outline='#76583F',width=5)
    for y in [1230,1300,1370]:d.line((0,y,1080,y-50),fill='#BA8A5D',width=3)
    d.polygon([(0,1510),(1080,1430),(1080,1480),(0,1555)],fill='#A87950',outline='#76583F',width=4)

def laptop(im,s,n,close=False):
    t=(s['start_frame']+n)/24
    draw=ImageDraw.Draw(im)
    if close:
        box=(90,395,955,1195);screen=(125,435,920,1105)
    else:
        box=(450,780,960,1190);screen=(478,808,930,1135)
    shadow(im,(box[0]+10,box[1]+20,box[2]+15,box[3]+30));draw=ImageDraw.Draw(im)
    draw.rounded_rectangle(box,24,fill='#3E4545',outline=INK,width=5)
    draw.rounded_rectangle(screen,14,fill=CREAM)
    if close:
        # Portrait computer view: visible keyboard belongs to the action.
        draw.polygon([(90,1190),(955,1190),(1070,1510),(0,1510)],fill='#BCC1BC',outline=INK,width=5)
        for row in range(3):
            for col in range(11):
                x=95+col*70-row*8;y=1225+row*54
                draw.rounded_rectangle((x,y,x+53,y+35),5,fill='#8C9692',outline='#707B76',width=2)
        draw.rounded_rectangle((400,1410,645,1480),12,outline='#6D7B73',width=3)
        txt(im,s,n,(165,475),'HEALTH PLAN',44,GREEN)
        txt(im,s,n,(165,560),'Annual renewal',61)
        txt(im,s,n,(165,650),'Same plan. Again.',48)
        draw=ImageDraw.Draw(im);draw.rounded_rectangle((160,770,880,885),18,fill=GREEN)
        txt(im,s,n,(190,795),'Keep current plan',53,CREAM)
        # Click is synced to “click”, not arbitrary decorative motion.
        u=ease((t-2.9)/.38);x=935-185*u;y=970-130*u
        draw=ImageDraw.Draw(im);draw.polygon([(x,y),(x+10,y+62),(x+28,y+43),(x+52,y+44)],fill=CREAM,outline=INK,width=3)
        if 3.26<=t<3.66:
            r=round(24+75*(t-3.26));draw.ellipse((x-r,y-r,x+r,y+r),outline=SAGE,width=5)
        if t>=3.66:
            step=min(4,1+int((t-3.66)/.35))
            txt(im,s,n,(165,950),f'RENEWED  {step}/4',49,GREEN)
            for j in range(4):
                x=190+j*170;y=1050;draw.ellipse((x,y,x+33,y+33),fill=GREEN if j<step else '#C7D1C0')
    else:
        txt(im,s,n,(500,835),'HEALTH PLAN',43,GREEN)
        txt(im,s,n,(500,910),'Same plan',55)
        if t>.5:
            # Notification arrives in-world on the laptop screen.
            txt(im,s,n,(500,1000),'Fourth year',44)

def paper(im,s,n,x,y,width,label,amount,detail=False,scale=1):
    height=round(width*1.22);draw=ImageDraw.Draw(im)
    shadow(im,(x+8,y+12,x+width+8,y+height+12),5)
    draw=ImageDraw.Draw(im);draw.polygon([(x,y),(x+width-55,y),(x+width,y+55),(x+width,y+height),(x,y+height)],fill=CREAM,outline='#626D60',width=3)
    draw.polygon([(x+width-55,y),(x+width-55,y+55),(x+width,y+55)],fill='#DDE5D6',outline='#626D60',width=2)
    size=round(42*scale);txt(im,s,n,(x+28,y+35),label,size,GREEN)
    txt(im,s,n,(x+28,y+115),'PREMIUM',42,GREEN)
    txt(im,s,n,(x+28,y+178),f'${amount:,}',round(65*scale))
    txt(im,s,n,(x+28,y+(310 if scale>1 else 270)),'per year',42)
    draw=ImageDraw.Draw(im)
    for j in range(3):draw.line((x+28,y+370+j*37,x+width-38,y+370+j*37),fill='#C3CBBD',width=3)
    if detail:txt(im,s,n,(x+28,y+480),'Total cost?',42,GREEN)

def picture(s,n):
    sid=s['id'];t=(s['start_frame']+n)/24
    if sid=='renewal-office':
        im=room(0).copy();a=actor('nod_yes',n);im.paste(a,(65,600),a);desk_front(im);laptop(im,s,n)
    elif sid=='renewal-close':
        im=tabletop().copy();laptop(im,s,n,True)
    elif sid=='documents-arrive':
        im=tabletop().copy()
        # Papers settle into the same desk geography used in the next close-up.
        u=ease(n/18);v=ease((n-9)/18)
        paper(im,s,n,90,445+round(65*(1-u)),385,'PLAN A',parent.C['ppo_annual_premium'])
        paper(im,s,n,505,575+round(75*(1-v)),385,'PLAN B',parent.C['hdhp_annual_premium'])
    elif sid=='premium-close':
        im=tabletop().copy();paper(im,s,n,125,380,705,'PLAN A',parent.C['ppo_annual_premium'],scale=1.55)
        draw=ImageDraw.Draw(im);u=ease(n/20)
        # Highlight the fixed correct premium rather than count up a false total.
        draw.line((155,685,155+round(470*u),685),fill='#719878',width=8)
        txt(im,s,n,(155,1100),'Illustrative premiums',42,GREEN)
    else:
        im=room(1).copy();a=actor('thinking',n);im.paste(a,(35,520),a);desk_front(im)
        # Both documents on a desk, Ren left; no floating frame or presenter panel.
        paper(im,s,n,455,735,415,'PLAN B',parent.C['hdhp_annual_premium'],detail=False)
        if t>=13.84:
            draw=ImageDraw.Draw(im);draw.polygon([(445,1245),(865,1210),(865,1310),(445,1345)],fill='#DBE5D2',outline=GREEN,width=3)
            txt(im,s,n,(475,1248),'Total cost?',48,GREEN)
    # Captions are on a fitted translucent strip only when speech is present.
    cue=next((c for c in M['captions'] if c['start']<=t<c['end']),None)
    if cue:
        draw=ImageDraw.Draw(im);value=parent.wrap(draw,cue['text'],42,790)
        bb=draw.multiline_textbbox((90,1365),value,font=font(42),spacing=8)
        layer=Image.new('RGBA',(W,H));ImageDraw.Draw(layer).rounded_rectangle((bb[0]-14,bb[1]-10,bb[2]+14,bb[3]+12),12,fill=(250,246,238,230))
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');txt(im,s,n,(90,1365),value,42,INK,'caption')
    if t<2.5 or t>=13:
        # Brief educational text, never a permanent footer/banner.
        value='Educational content only,\nnot financial advice.'
        draw=ImageDraw.Draw(im);bb=draw.multiline_textbbox((90,1490),value,font=font(30),spacing=8)
        layer=Image.new('RGBA',(W,H));ImageDraw.Draw(layer).rounded_rectangle((bb[0]-8,bb[1]-5,bb[2]+8,bb[3]+6),8,fill=(250,246,238,235));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
        txt(im,s,n,(90,1490),value,30,INK,'disclaimer')
    return im

def collapse_layout():
    output={}
    for sid,items in REC.scenes.items():
        grouped={}
        for item in items:
            key=(item['text'],item['font_px'],item['role'])
            if key not in grouped:grouped[key]=dict(item)
            else:
                a=grouped[key];a['bbox']=[min(a['bbox'][0],item['bbox'][0]),min(a['bbox'][1],item['bbox'][1]),max(a['bbox'][2],item['bbox'][2]),max(a['bbox'][3],item['bbox'][3])];a['start']=min(a['start'],item['start']);a['end']=max(a['end'],item['end'])
        output[sid]=list(grouped.values())
    (D/'layout.json').write_text(json.dumps({'scenes':output},indent=2)+'\n')

def main():
    if '--stills' not in sys.argv:
        assert os.environ.get('REN_SHORTS_STAGE')=='prototype' and os.environ.get('REN_SHORTS_MAX_FRAMES')=='360','Only the gated 15-second prototype is implemented/authorized'
    prepare_actors();cache=standards.SceneCache(BUILD/'scene-cache');files=[]
    deps={a['id']:standards.sha(standards.resolve(D/'production.json',a['path'])) for a in M['assets']}
    for scene in M['scenes']:
        REC.begin_scene(scene['id']);count=scene['end_frame']-scene['start_frame']
        key=standards.scene_cache_key(scene,deps,standards.sha(Path(__file__)));cached=cache.get(key,count)
        if '--stills' in sys.argv:
            for n in range(count):
                if n in [0,count//2,count-1]:picture(scene,n).save(BUILD/(scene['id']+f'-{n:03}.png'))
            continue
        if cached:
            layout_cache=cached.with_suffix('.layout.json')
            if layout_cache.exists():REC.scenes[scene['id']]=json.loads(layout_cache.read_text());files.append(cached);print('Reused',scene['id'],flush=True);continue
        path=BUILD/(scene['id']+'.mp4')
        enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
        for n in range(count):
            im=picture(scene,n);enc.stdin.write(im.tobytes())
            if n in [0,count//2,count-1]:im.save(BUILD/(scene['id']+f'-{n:03}.png'))
        enc.stdin.close();assert enc.wait()==0
        cached=cache.store(key,path,count);cached.with_suffix('.layout.json').write_text(json.dumps(REC.scenes[scene['id']]))
        files.append(cached);print('Rendered',scene['id'],flush=True)
    collapse_layout()
    if '--stills' in sys.argv:return
    source=standards.resolve(D/'production.json',next(a['path'] for a in M['assets'] if a['id']=='source-short'))
    assert standards.sha(source)==json.loads((D/'voice-configuration.json').read_text())['source_sha256']
    raw=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(source),'-map','0:a:0','-f','f32le','-']),dtype='float32')
    pcm=np.concatenate([raw[:664320],raw[672320:728000]]) # 13.84 + (15.1666667-14.0066667) = 15.0s
    assert len(pcm)==720000
    sf.write(BUILD/'prototype-narration.wav',pcm,48000,subtype='FLOAT')
    concat=BUILD/'concat.txt';concat.write_text('\n'.join("file '%s'"%p for p in files)+'\n')
    sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(BUILD/'prototype-narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(OUT/'Ren_Health_Short_v2_15s_Prototype.mp4')],check=True)
    assert standards.sha(source)==json.loads((D/'voice-configuration.json').read_text())['source_sha256']

if __name__=='__main__':main()
