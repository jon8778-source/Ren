"""Story-focused15s adapter: approved v3 compositor, native animation and original audio."""
from pathlib import Path
import importlib.util,json,os,subprocess as sp,sys,functools,hashlib
import numpy as np
from scipy.ndimage import label
from PIL import Image,ImageDraw,ImageFilter
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('health_short_v3_components',D/'render.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
S=b.standards;P=b.parent;W,H,FPS=1080,1920,24
INK,GREEN,CREAM,SAGE=b.INK,b.GREEN,b.CREAM,b.SAGE
BUILD=D/'build/revision4';BUILD.mkdir(parents=True,exist_ok=True)
M=json.loads((D/'production.json').read_text());REC=S.LayoutRecorder()
font=b.font;ease=b.ease

def txt(im,s,n,xy,value,size=60,fill=INK,role='text'):
    d=ImageDraw.Draw(im);d.multiline_text(xy,value,font=font(size),fill=fill,spacing=9)
    REC.record(s['id'],d,xy,value,font(size),(s['start_frame']+n)/24,(s['start_frame']+n+1)/24,role,spacing=9)

@functools.lru_cache(maxsize=1)
def wood():
    # Reuse the established wood environment, removing the generic green desktop mat.
    im=Image.new('RGB',(W,H),'#C59971');d=ImageDraw.Draw(im)
    for j,y in enumerate(range(-100,2100,310)):
        fill=['#CBA37D','#C49A70','#D1AB84'][j%3]
        d.polygon([(0,y),(1080,y+75),(1080,y+385),(0,y+310)],fill=fill)
        d.line((0,y+310,1080,y+385),fill='#AC7F56',width=3)
        for offset in [35,100,160,240]:d.line([(0,y+offset),(390,y+offset+18),(1080,y+offset+75)],fill='#C1976E',width=2)
    return im

def reaction_matte(image):
    # Raised arm/head encloses a background pocket. Add seeds only in that
    # anatomical negative space; keep the separate white T-shirt component.
    rgb=np.asarray(image).astype(np.float32);dist=np.sqrt(np.mean(((255-rgb)/255)**2,axis=2))
    seed=np.zeros(dist.shape,bool);seed[0,:]=seed[-1,:]=True;seed[:,0]=seed[:,-1]=True
    for x,y in [(565,155),(580,155),(595,175)]:seed[y,x]=True
    outside=P.binary_propagation(seed&(dist<.24),mask=dist<.24)
    core=P.binary_erosion(~outside,iterations=1);alpha=P.gaussian_filter(core.astype(np.float32),.55)
    edge=(alpha>0)&~core;idx=P.distance_transform_edt(~core,return_distances=False,return_indices=True)
    rgb[edge]=rgb[idx[0][edge],idx[1][edge]]
    assert np.mean(alpha[235:300,630:655])>.99,'White shirt damaged'
    return Image.fromarray(np.dstack([rgb,np.round(alpha*255)]).astype('uint8'),'RGBA')

def prepare():
    # One existing hand pose, no new character/hand drawing or automatic mirroring.
    source=b.ROOT/'assets/ren_library/ren_point_down_right.mp4'
    key=S.digest({'source':S.sha(source),'matte':S.sha(b.B/'render.py'),'frame':3,'crop':[704,240,860,480],'rotation':-90,'size':[480,312],'isolate_main_component':True})
    mark=BUILD/'hand.json';target=BUILD/'ren-hand.png'
    if not target.exists() or not mark.exists() or json.loads(mark.read_text())['key']!=key:
        raw=sp.check_output(['ffmpeg','-v','error','-xerror','-ss','3','-i',str(source),'-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'])
        a=P.matte(Image.frombytes('RGB',(1280,720),raw)).crop((704,240,860,480))
        pixels=np.asarray(a).copy();components,_=label(pixels[:,:,3]>10)
        counts=np.bincount(components.ravel());counts[0]=0
        pixels[components!=int(np.argmax(counts)),3]=0
        a=Image.fromarray(pixels)  # Remove the unrelated torso-edge sliver.
        a=a.rotate(-90,expand=True).resize((480,312),Image.Resampling.LANCZOS);a.save(target);mark.write_text(json.dumps({'key':key}))
    source=b.ROOT/'assets/ren_library/ren_confused.mp4';folder=BUILD/'reaction';folder.mkdir(exist_ok=True)
    key=S.digest({'source':S.sha(source),'matte':S.sha(b.B/'render.py'),'start':2.0,'frames':72,'negative_space_seed_revision':1,'crop':[465,0,825,720],'size':[936,1872]})
    mark=folder/'cache.json'
    if mark.exists() and json.loads(mark.read_text())['key']==key and all((folder/f'{i:03}.png').exists() for i in range(72)):return
    dec=sp.Popen(['ffmpeg','-v','error','-xerror','-ss','2.0','-i',str(source),'-an','-frames:v','72','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=sp.PIPE)
    for i in range(72):
        raw=dec.stdout.read(1280*720*3);assert len(raw)==1280*720*3
        a=reaction_matte(Image.frombytes('RGB',(1280,720),raw));a=a.crop((465,0,825,720)).resize((936,1872),Image.Resampling.LANCZOS);a.save(folder/f'{i:03}.png')
    dec.stdout.close();assert dec.wait()==0;mark.write_text(json.dumps({'key':key}))

@functools.lru_cache(maxsize=90)
def reaction(n):return Image.open(BUILD/'reaction'/f'{n:03}.png').convert('RGBA')

@functools.lru_cache(maxsize=1)
def hand():return Image.open(BUILD/'ren-hand.png').convert('RGBA')

def opening(s,n):
    t=n/24;im=wood().copy()
    prop=b.laptop_image(1250);im.paste(prop,(-85,270),prop)
    d=ImageDraw.Draw(im);d.rectangle((82,340,995,855),fill=CREAM)
    txt(im,s,n,(120,390),'HEALTH PLAN',52,GREEN)
    txt(im,s,n,(120,470),'Same plan. Again.',62)
    d=ImageDraw.Draw(im);d.rounded_rectangle((112,585,890,710),16,fill=GREEN)
    txt(im,s,n,(150,612),'Keep current plan',60,CREAM)
    # Actual Ren forearm enters from the right and presses the real trackpad.
    u=ease((t-.25)/.8);dy=7*max(0,1-abs(t-3.26)/.14)
    im.paste(hand(),(round(650+480*(1-u)),round(810+dy)),hand())
    u=ease((t-.6)/.65);cx=960-220*u;cy=825-165*u
    d=ImageDraw.Draw(im);d.polygon([(cx,cy),(cx+10,cy+59),(cx+27,cy+41),(cx+48,cy+43)],fill=CREAM,outline=INK,width=3)
    if t>=3.26:
        d.rounded_rectangle((112,585,890,710),16,fill='#B8CCB1');txt(im,s,n,(150,612),'Keep current plan',60,INK)
        r=round(24+80*(t-3.26));d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=GREEN,width=5)
    txt(im,s,n,(115,1320),'FOUR YEARS.',76)
    return im

def calendar(s,n):
    im=wood().copy();local=n/24;step=min(3,int(local/.42));phase=(local-step*.42)/.42 if step<3 else 1
    d=ImageDraw.Draw(im)
    for j in [3,2,1]:
        d.rounded_rectangle((110+j*9,365+j*12,895+j*9,1235+j*12),8,fill='#E8E4D8',outline='#84927E',width=2)
    b.shadow(im,(120,390,915,1270),8);d=ImageDraw.Draw(im);d.rounded_rectangle((110,365,895,1235),8,fill=CREAM,outline='#61735D',width=3)
    d.rectangle((110,365,895,535),fill=GREEN)
    txt(im,s,n,(155,410),'ANNUAL RENEWAL',60,CREAM)
    txt(im,s,n,(165,620),f'YEAR {step+1}',130)
    txt(im,s,n,(165,900),'SAME PLAN',78,GREEN)
    for x in [270,735]:d.ellipse((x,320,x+35,420),outline=INK,width=8)
    # A turning page reveals the next completed annual label; no arithmetic/count-up.
    if step<3 and phase<.32:
        lift=round(240*(1-phase/.32));d.polygon([(110,1130),(895,1130),(895-lift//3,1235-lift),(110+lift//3,1235-lift)],fill='#D2DCC9',outline='#72846B',width=3)
    return im

def ren_scene(s,n):
    im=b.room(1).copy();a=reaction(n);im.paste(a,(20,350),a)
    # Camera is over the documents: their near edge naturally frames the waist,
    # without placing a desk or user-facing laptop in Ren's presenter view.
    d=ImageDraw.Draw(im);d.polygon([(-40,1460),(620,1415),(850,1920),(-40,1920)],fill='#F1EEE2',outline='#8B9581',width=4)
    d.polygon([(540,1450),(1140,1380),(1140,1920),(830,1920)],fill='#E6EAD8',outline='#819173',width=4)
    txt(im,s,n,(100,240),'I finally compared.',68)
    return im

def price_sheet(s,n):
    im=wood().copy();t=(s['start_frame']+n)/24
    dy=round(45*(1-ease(n/10))) if s['id']=='price-a' else 0
    d=ImageDraw.Draw(im);b.shadow(im,(92,230+dy,950,1465+dy),5);d=ImageDraw.Draw(im)
    d.polygon([(80,205+dy),(890,205+dy),(935,250+dy),(935,1440+dy),(80,1440+dy)],fill=CREAM,outline='#68775F',width=3)
    d.polygon([(890,205+dy),(890,250+dy),(935,250+dy)],fill='#D6DFCE',outline='#68775F',width=2)
    txt(im,s,n,(140,260+dy),'ILLUSTRATIVE',48,GREEN)
    txt(im,s,n,(140,325+dy),'ANNUAL PREMIUMS',52,GREEN)
    txt(im,s,n,(140,430+dy),'PLAN A',60)
    txt(im,s,n,(140,495+dy),f"${P.C['ppo_annual_premium']:,}",158)
    txt(im,s,n,(140,685+dy),'per year',56,GREEN)
    d=ImageDraw.Draw(im);d.line((140,790+dy,875,790+dy),fill='#B7C6AD',width=3)
    reveal=s['id']=='price-comparison' and n>=10
    if not reveal:
        # This is the back of the physical lower fold, not a green infographic.
        p=ease(n/10) if s['id']=='price-comparison' else 0
        h=round(570*(1-p));inset=round(35*np.sin(np.pi*p))
        d.polygon([(100,815+dy),(915,815+dy),(915-inset,815+dy+h),(100+inset,815+dy+h)],fill='#E9E6DB',outline='#9B9D8B',width=3)
        if h>310:txt(im,s,n,(150,1010+dy),'PLAN B',70,GREEN)
    else:
        txt(im,s,n,(140,840),'PLAN B',60)
        txt(im,s,n,(140,905),f"${P.C['hdhp_annual_premium']:,}",158)
        txt(im,s,n,(140,1095),'per year',56,GREEN)
        txt(im,s,n,(140,1225),'Premiums only',58,GREEN)
        if t>=13.84:
            txt(im,s,n,(140,1320),'Care costs?',56)
            d=ImageDraw.Draw(im);u=ease((t-13.84)/.3);cx=round(940-190*u);cy=1305
            d.ellipse((cx-55,cy-55,cx+55,cy+55),outline=GREEN,width=7);d.line((cx+40,cy+40,cx+112,cy+112),fill=GREEN,width=13)
    return im

def picture(s,n):
    kind=s['id'];t=(s['start_frame']+n)/24
    if kind=='renewal-action':im=opening(s,n)
    elif kind=='four-renewals':im=calendar(s,n)
    elif kind=='ren-reaction':im=ren_scene(s,n)
    else:im=price_sheet(s,n)
    if t<2.5 or t>=13:
        # Exact mandatory wording, no permanent caption panel or footer banner.
        txt(im,s,n,(95,1470),'Educational content only,\nnot financial advice.',36,INK,'disclaimer')
    return im

def save_layout():
    output={}
    for sid,items in REC.scenes.items():
        grouped={}
        for i in items:
            key=(i['text'],i['font_px'],i['role'])
            if key not in grouped:grouped[key]=dict(i)
            else:
                x=grouped[key];x['bbox']=[min(x['bbox'][0],i['bbox'][0]),min(x['bbox'][1],i['bbox'][1]),max(x['bbox'][2],i['bbox'][2]),max(x['bbox'][3],i['bbox'][3])];x['start']=min(x['start'],i['start']);x['end']=max(x['end'],i['end'])
        output[sid]=list(grouped.values())
    (D/'layout.json').write_text(json.dumps({'scenes':output},indent=2)+'\n')

def main():
    stills='--stills' in sys.argv
    if not stills:assert os.environ.get('REN_SHORTS_STAGE')=='prototype' and os.environ.get('REN_SHORTS_MAX_FRAMES')=='360','Prototype only; full production not approved'
    prepare();files=[];cache=S.SceneCache(BUILD/'cache')
    deps={a['id']:S.sha(S.resolve(D/'production.json',a['path'])) for a in M['assets']}
    for s in M['scenes']:
        REC.begin_scene(s['id']);count=s['end_frame']-s['start_frame'];key=S.scene_cache_key(s,deps,S.sha(__file__));cached=cache.get(key,count)
        if stills:
            for n in [0,count//2,count-1]:picture(s,n).save(BUILD/f"{s['id']}-{n:03}.png")
            continue
        if cached and cached.with_suffix('.layout.json').exists():REC.scenes[s['id']]=json.loads(cached.with_suffix('.layout.json').read_text());files.append(cached);continue
        path=BUILD/(s['id']+'.mp4');enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
        for n in range(count):
            im=picture(s,n);enc.stdin.write(im.tobytes())
            if n in [0,count//2,count-1]:im.save(BUILD/f"{s['id']}-{n:03}.png")
        enc.stdin.close();assert enc.wait()==0;cached=cache.store(key,path,count);cached.with_suffix('.layout.json').write_text(json.dumps(REC.scenes[s['id']]));files.append(cached);print('Rendered',s['id'],flush=True)
    save_layout()
    if stills:return
    audio=S.resolve(D/'production.json',next(a['path'] for a in M['assets'] if a['id']=='previous-prototype-audio'))
    assert S.sha(audio)==next(a['sha256'] for a in M['assets'] if a['id']=='previous-prototype-audio')
    concat=BUILD/'concat.txt';concat.write_text('\n'.join("file '%s'"%p for p in files)+'\n')
    sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-movflags','+faststart',str(D/'deliverables/Ren_Health_Short_v2_15s_Prototype_Rev04.mp4')],check=True)

if __name__=='__main__':main()
