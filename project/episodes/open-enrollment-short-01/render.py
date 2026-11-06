"""15-second review prototype, using approved v3 methods and references."""
from pathlib import Path
import sys,json,math,subprocess as sp,functools,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_propagation,binary_erosion,gaussian_filter,distance_transform_edt
B=Path(__file__).resolve().parent;ROOT=B.parents[2];BUILD=B/'build';OUT=B/'deliverables';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'project/prototypes/coffee-minute-v3'));import render as v3
font=functools.lru_cache(maxsize=32)(v3.font)
W,H,FPS,FRAMES=1080,1920,24,360
INK,GREEN,CREAM,MUTED=v3.INK,v3.GREEN,v3.CREAM,v3.MUTED
A=json.loads((B/'assumptions.json').read_text());DIFF=A['comparison_a']-A['comparison_b'];assert DIFF==1980
DISCLAIMER=A['disclaimer'];assert DISCLAIMER=='Educational content only, not financial advice.'
SCENES=[dict(id='email-click',start=0,end=2.8),dict(id='three-questions',start=2.8,end=7.1),dict(id='comparison',start=7.1,end=10.3),dict(id='tuesday',start=10.3,end=15)]
QUESTIONS=['Worst-year cost?','What did I use?','Where does the difference go?']
OFFICE=Image.open(B/'assets/ren-seated-office.png').convert('RGB').crop((100,0,620,941))
def txt(d,xy,value,size=50,fill=INK):d.multiline_text(xy,value,font=font(size),fill=fill,spacing=8)
def wrapped(d,value,size,width):
 lines=[];row=''
 for word in value.split():
  s=(row+' '+word).strip()
  if row and d.textlength(s,font=font(size))>width:lines.append(row);row=word
  else:row=s
 lines.append(row);return '\n'.join(lines)
def center(d,y,value,size=50,fill=INK):
 assert d.textlength(value,font=font(size))<=900,(value,size)
 txt(d,((1000-d.textlength(value,font=font(size)))/2,y),value,size,fill)
def panel(im,xy):
 layer=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(layer);d.rounded_rectangle(xy,24,fill=(255,255,255,185),outline=(23,42,58,255),width=3);return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
def ease(x):
 x=np.clip(x,0,1);return 1-(1-x)**3
def pointer(d,x,y):
 d.polygon([(x,y),(x+9,y+47),(x+22,y+35),(x+39,y+35)],fill=INK,outline='#FFFFFF',width=3)
def cleaned_actor(frame):
 # Refine only the exterior edge; preserve enclosed opaque white clothing.
 old=v3.actor_rgba(frame);a=np.asarray(frame).astype(np.float32);dist=np.sqrt(np.mean(((255-a)/255)**2,axis=2));seed=np.zeros(dist.shape,bool);seed[0,:]=seed[-1,:]=True;seed[:,0]=seed[:,-1]=True
 exterior=binary_propagation(seed&(dist<.24),mask=dist<.24);core=binary_erosion(~exterior,iterations=1);alpha=gaussian_filter(core.astype(np.float32),.55)
 edge=(alpha>0)&~core;idx=distance_transform_edt(~core,return_distances=False,return_indices=True);a[edge]=a[idx[0][edge],idx[1][edge]]
 return Image.fromarray(np.dstack([a,alpha*255]).astype('uint8'),'RGBA')
def actor_cache():
 folder=BUILD/'actor';folder.mkdir(exist_ok=True)
 n=math.ceil((15-10.3)*24)
 if len(list(folder.glob('*.png')))!=n:
  src=ROOT/'assets/ren_library/ren_nod_yes.mp4';dec=sp.Popen(['ffmpeg','-v','error','-xerror','-ss','1.25','-i',str(src),'-an','-frames:v',str(n),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=sp.PIPE)
  for j in range(n):
   raw=dec.stdout.read(1280*720*3);assert len(raw)==1280*720*3;im=cleaned_actor(Image.frombytes('RGB',(1280,720),raw));im.crop((460,10,820,450)).resize((432,528),Image.Resampling.LANCZOS).save(folder/f'{j:03d}.png')
  dec.stdout.close();assert dec.wait()==0
 return folder
@functools.lru_cache(maxsize=120)
def actor(n):return Image.open(BUILD/'actor'/f'{min(112,n):03d}.png').convert('RGBA')
def graphic(t):
 im=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(im)
 if t<7.1:
  # Native sharp episode art; no body wobble, mirroring or extra zoom cuts.
  im.paste(OFFICE,(25,400));d=ImageDraw.Draw(im)
  if t<2.8:
   txt(d,(80,140),'Four seconds.\nKeep my plan.',78)
   im=panel(im,(550,545,960,990));d=ImageDraw.Draw(im)
   txt(d,(580,580),'INBOX',30,GREEN);txt(d,(580,650),'Open enrollment\ncloses Friday.',44)
   clicked=t>=.65;d.rounded_rectangle((580,825,930,935),18,fill=GREEN if clicked else INK)
   txt(d,(602,851),'Keep My Plan',43,CREAM)
   if .4<t<1.25:
    x=880+80*(1-ease((t-.4)/.25));pointer(d,x,900)
    if .65<=t<1.05:
     r=int(12+55*(t-.65)/.4);d.ellipse((880-r,900-r,880+r,900+r),outline=GREEN,width=3)
   if t>=.7:
    im=panel(im,(550,1060,960,1260));d=ImageDraw.Draw(im);cx,cy,r=625,1160,48
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=INK,width=5);d.line((cx,cy-r-10,cx,cy-r-23),fill=INK,width=5)
    theta=-math.pi/2+2*math.pi*min(1,(t-.7)/.55);d.line((cx,cy,cx+36*math.cos(theta),cy+36*math.sin(theta)),fill=GREEN,width=5)
    txt(d,(700,1113),'4 SEC',67,GREEN)
   value='I clicked “keep my plan”\nin four seconds.'
   txt(d,(85,1450),value,49)
   txt(d,(85,1660),'Fictional enrollment example',32,MUTED)
  else:
   txt(d,(80,140),'Three questions.\nA better review.',76)
   for j,label in enumerate(QUESTIONS):
    if t<2.8+j*.23:continue
    before=im.copy()
    u=ease((t-(2.8+j*.23))/.25);y=575+j*235+round(25*(1-u));xy=(540,y,960,y+205)
    # Cards persist; only focus follows the spoken question.
    im=panel(im,xy);d=ImageDraw.Draw(im)
    d.ellipse((560,y+20,610,y+70),fill=GREEN);txt(d,(575,y+24),str(j+1),30,CREAM)
    value=wrapped(d,label,47,310);txt(d,(620,y+30),value,47)
    bb=d.multiline_textbbox((620,y+30),value,font=font(47),spacing=8);assert bb[2]<=945 and bb[3]<=y+201
    if u<1:im=Image.blend(before,im,float(u));d=ImageDraw.Draw(im)
    if (j==0 and 3.3<=t<4.58) or (j==1 and 4.58<=t<5.96) or (j==2 and t>=5.96):d.rounded_rectangle(xy,24,outline=GREEN,width=5)
   txt(d,(85,1450),'Before choosing a plan.',49)
 else:
  if t<10.3:
   txt(d,(80,140),'Forty minutes.',80)
   txt(d,(85,305),'ILLUSTRATIVE COMPARISON',34,GREEN)
   for x,value in [(80,A['comparison_a']),(550,A['comparison_b'])]:
    d.rounded_rectangle((x,510,x+410,755),26,fill='#FFFFFF',outline=INK,width=3);txt(d,(x+28,575),f'${value:,}',90)
   center(d,815,'vs',46,MUTED)
   center(d,935,f"${A['comparison_a']:,} − ${A['comparison_b']:,}",66)
   center(d,1040,f'= ${DIFF:,}',112,GREEN)
   center(d,1245,'Illustrative difference',40,MUTED)
   txt(d,(85,1430),'Not plan quotations.\nNot guaranteed savings.',43)
   txt(d,(85,1600),'Lower cost alone does not mean\na better-fit plan.',34,MUTED)
  else:
   txt(d,(80,140),'Full story\nTuesday.',88)
   d.rounded_rectangle((65,490,500,1060),32,fill='#E4EADC',outline=GREEN,width=3)
   n=int((t-10.3)*24);rgba=actor(n);im.paste(rgba,(65,520),rgba);d=ImageDraw.Draw(im)
   txt(d,(535,560),'FULL STORY\nTUESDAY',58,GREEN)
   txt(d,(535,775),'NOVEMBER 10\n2026',38)
   txt(d,(535,930),'Open enrollment',32,MUTED)
   d.rounded_rectangle((80,1160,950,1440),28,fill='#FFFFFF',outline=GREEN,width=3)
   txt(d,(110,1185),'Illustrative difference',38,MUTED);txt(d,(110,1240),f'${DIFF:,}',92,GREEN)
   txt(d,(110,1360),f"${A['comparison_a']:,} − ${A['comparison_b']:,}",44)
   disclaimer=wrapped(d,DISCLAIMER,38,840);txt(d,(85,1545),disclaimer,38)
   bb=d.multiline_textbbox((85,1545),disclaimer,font=font(38),spacing=8);assert bb[2]<=950 and bb[3]<1740
 return im

def main():
 actor_cache()
 info={'title':'I Clicked "Keep My Plan" in 4 Seconds','prototype':True,'approval_status':'Awaiting explicit owner approval; no final render authorized','frames':FRAMES,'fps':FPS,'duration':15,'resolution':[W,H],'scenes':SCENES,'calculations':{'equation':'2670 - 690 = 1980','difference':DIFF},'disclaimer':DISCLAIMER,'disclaimer_start':10.3,'voice':'am_michael / Kokoro US English, speed=1.0','voice_file':'audio/narration-original.wav','new_qwen_requests':0}
 (B/'shot-manifest.json').write_text(json.dumps(info,indent=2)+'\n')
 if '--stills' in sys.argv:
  for i,t in enumerate([.5,1.8,3.4,5.1,6.7,8.5,9.8,10.8,13.6]):graphic(t).save(BUILD/f'still-{i}.png')
  return
 video=BUILD/'video.mp4';enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','slow','-crf','17','-pix_fmt','yuv420p',str(video)],stdin=sp.PIPE)
 for n in range(FRAMES):enc.stdin.write(graphic(n/FPS).tobytes())
 enc.stdin.close();assert enc.wait()==0;v3.check_video(video,FRAMES)
 final=OUT/'Ren_Short_01_Open_Enrollment_Prototype.mp4';sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(video),'-i',str(B/'audio/prototype-mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(final)],check=True);v3.check_video(final,FRAMES);print(final,flush=True)
if __name__=='__main__':main()
