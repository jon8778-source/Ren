"""Ren Qwen revision: full-colour code animation, four sustained reading beats."""
from pathlib import Path
import sys,json,math,subprocess as sp,functools
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from scipy.ndimage import binary_propagation,binary_erosion,gaussian_filter,distance_transform_edt
B=Path(__file__).resolve().parent;P=B.parent;ROOT=B.parents[3];BUILD=B/'build';OUT=B/'deliverables';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'project/prototypes/coffee-minute-v3'));import render as v3
font=functools.lru_cache(maxsize=40)(v3.font);W,H,FPS,FRAMES=1080,1920,24,432
CREAM='#FAF6EE';SAGE='#A5BC9E';MINT='#D8E6CE';INK='#112B39';GREEN='#3F665B';PANEL='#244C50';FAINT='#8DABA5'
A=json.loads((P/'assumptions.json').read_text());DIFF=A['comparison_a']-A['comparison_b'];assert DIFF==1980
SOURCE_ART=Image.open(P/'assets/ren-seated-office.png').convert('RGB')
y=np.linspace(0,1,H)[:,None,None];top=np.array([17,43,57])[None,None,:];bottom=np.array([22,64,65])[None,None,:];GRAD=Image.fromarray(np.repeat((top*(1-y)+bottom*y).astype(np.uint8),W,axis=1),'RGB')
def txt(d,pos,s,size=50,fill=CREAM):d.multiline_text(pos,s,font=font(size),fill=fill,spacing=8)
def wrap(d,s,size,width):
 lines=[];row=''
 for word in s.split():
  t=(row+' '+word).strip()
  if row and d.textlength(t,font=font(size))>width:lines.append(row);row=word
  else:row=t
 lines.append(row);return '\n'.join(lines)
def ease(x):x=float(np.clip(x,0,1));return 1-(1-x)**3
def icon(d,kind,x,y,color=CREAM):
 if kind=='mail':
  d.rounded_rectangle((x,y,x+66,y+45),8,outline=color,width=4);d.line([(x+3,y+4),(x+33,y+25),(x+63,y+4)],fill=color,width=4)
 elif kind=='shield':
  d.line([(x+4,y),(x+36,y),(x+36,y+24),(x+20,y+40),(x+4,y+24),(x+4,y)],fill=color,width=3);d.line([(x+12,y+19),(x+19,y+26),(x+29,y+12)],fill=color,width=3)
 elif kind=='receipt':
  d.rounded_rectangle((x+3,y,x+36,y+42),4,outline=color,width=3)
  for j in range(3):d.line((x+11,y+10+j*10,x+29,y+10+j*10),fill=color,width=3)
 elif kind=='fork':
  d.line([(x+4,y+22),(x+20,y+22),(x+20,y+8),(x+38,y+8)],fill=color,width=3);d.line([(x+20,y+22),(x+20,y+38),(x+38,y+38)],fill=color,width=3)
  d.line([(x+30,y+1),(x+38,y+8),(x+30,y+15)],fill=color,width=3);d.line([(x+30,y+31),(x+38,y+38),(x+30,y+45)],fill=color,width=3)
def matte(im):
 a=np.asarray(im).astype(np.float32);dist=np.sqrt(np.mean(((255-a)/255)**2,axis=2));seed=np.zeros(dist.shape,bool);seed[0,:]=seed[-1,:]=True;seed[:,0]=seed[:,-1]=True
 ext=binary_propagation(seed&(dist<.24),mask=dist<.24);core=binary_erosion(~ext,iterations=1);alpha=gaussian_filter(core.astype(np.float32),.55);edge=(alpha>0)&~core;idx=distance_transform_edt(~core,return_distances=False,return_indices=True);a[edge]=a[idx[0][edge],idx[1][edge]]
 return Image.fromarray(np.dstack([a,np.round(alpha*255)]).astype('uint8'),'RGBA')
def cache_actor(clip,n):
 target_size=(432,864) if clip=='nod_yes' else (480,960)
 folder=BUILD/f'actor-{clip}-{target_size[0]}';folder.mkdir(exist_ok=True)
 if len(list(folder.glob('*.png')))<n:
  p=ROOT/'assets/ren_library'/f'ren_{clip}.mp4';info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(x for x in info['streams'] if x['codec_type']=='video');assert (v['width'],v['height'])==(1280,720) and float(info['format']['duration'])>1.25+n/24
  dec=sp.Popen(['ffmpeg','-v','error','-xerror','-ss','1.25','-i',str(p),'-an','-frames:v',str(n),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=sp.PIPE)
  for i in range(n):
   raw=dec.stdout.read(1280*720*3);assert len(raw)==1280*720*3;actor=matte(Image.frombytes('RGB',(1280,720),raw)).crop((460,0,820,720)).resize(target_size,Image.Resampling.LANCZOS);actor.save(folder/f'{i:03}.png')
  dec.stdout.close();assert dec.wait()==0
 return folder
@functools.lru_cache(maxsize=240)
def actor(clip,n):return Image.open(BUILD/f"actor-{clip}-{432 if clip=='nod_yes' else 480}"/f'{n:03}.png').convert('RGBA')
def glow(im):
 d=ImageDraw.Draw(im);d.rounded_rectangle((40,480,520,1460),110,fill='#829E86');d.arc((75,515,485,925),185,340,fill=SAGE,width=3)
def base():
 im=GRAD.copy();d=ImageDraw.Draw(im);d.line((80,375,950,375),fill='#345B61',width=2);return im

def picture(t):
 im=base();d=ImageDraw.Draw(im)
 if t<4:
  txt(d,(80,130),'Four seconds.\nSame plan.',88)
  txt(d,(85,335),'OPEN ENROLLMENT',32,SAGE)
  # Native office/character pixels, gentle camera drift only; no generated new art.
  shift=round(t);room=SOURCE_ART.crop((100+shift,0,620+shift,941));mask=Image.new('L',room.size,0);ImageDraw.Draw(mask).rounded_rectangle((0,0,519,940),26,fill=255);im.paste(room,(15,455),mask);d=ImageDraw.Draw(im)
  z=ease((t-.10)/.4);dy=round(55*(1-z));card=im.copy();cd=ImageDraw.Draw(card)
  cd.rounded_rectangle((550,555+dy,980,1050+dy),28,fill=PANEL,outline=SAGE,width=3);icon(cd,'mail',580,590+dy)
  txt(cd,(580,680+dy),'Open enrollment\ncloses Friday.',44)
  clicked=t>=1.35;cd.rounded_rectangle((578,870+dy,952,990+dy),20,fill=MINT if clicked else GREEN)
  txt(cd,(595,899+dy),'Keep My Plan',43,INK if clicked else CREAM)
  im=Image.blend(im,card,z);d=ImageDraw.Draw(im)
  if .9<t<2.1:
   p=ease((t-.9)/.45);x=1005-120*p;y=1080-145*p
   d.polygon([(x,y),(x+10,y+48),(x+23,y+34),(x+42,y+35)],fill=CREAM,outline=INK,width=2)
   if 1.35<=t<1.9:
    r=round(15+(t-1.35)*80);d.ellipse((885-r,935-r,885+r,935+r),outline=MINT,width=3)
  if t>=1.45:
   d.rounded_rectangle((565,1115,970,1350),28,fill=PANEL,outline=SAGE,width=3);cx,cy=655,1230;d.ellipse((cx-62,cy-62,cx+62,cy+62),outline=MINT,width=5);d.line((cx,1155,cx,1138),fill=MINT,width=5)
   theta=-math.pi/2+2*math.pi*ease((t-1.45)/.8);d.line((cx,cy,cx+46*math.cos(theta),cy+46*math.sin(theta)),fill=SAGE,width=5);txt(d,(745,1174),'4',88);txt(d,(755,1270),'SEC',31,SAGE)
  txt(d,(80,1525),'A decision worth another look.',42,MINT)
  txt(d,(80,1710),'Fictional enrollment example',30,FAINT)
 elif t<9.5:
  txt(d,(80,130),'Three questions.\nBefore you click.',78)
  glow(im);n=int((t-4)*24);a=actor('thinking',min(n,131));im.paste(a,(45,475),a)
  for j,label in enumerate(['Worst-year cost?','What did I use?','Where does the difference go?']):
   at=4+j*.25
   if t<at:continue
   u=ease((t-at)/.4);before=im.copy();d=ImageDraw.Draw(im);dx=round(100*(1-u));x,y=540+dx,515+j*265
   active=(j==0 and t<5.89) or (j==1 and 5.89<=t<7.1) or (j==2 and t>=7.1)
   d.rounded_rectangle((x,y,x+430,y+225),26,fill=GREEN if active else PANEL,outline=MINT if active else '#5B7C79',width=3)
   icon(d,['shield','receipt','fork'][j],x+24,y+20,SAGE);value=wrap(d,label,43,330);txt(d,(x+74,y+70),value,43)
   bb=d.multiline_textbbox((x+74,y+70),value,font=font(43),spacing=8);assert bb[2]<=x+415 and bb[3]<=y+218
   if u<1:im=Image.blend(before,im,u)
  d=ImageDraw.Draw(im);txt(d,(80,1570),'Risk. Use. Purpose.',47,MINT)
 elif t<14:
  txt(d,(80,130),'Forty minutes.',88)
  txt(d,(85,295),'ILLUSTRATIVE PLAN COMPARISON',32,SAGE)
  # Labels stay completed and correct while proportional bars animate below.
  txt(d,(115,470),f"${A['comparison_a']:,}",103);txt(d,(625,470),f"${A['comparison_b']:,}",103)
  d.line((160,1250,925,1250),fill=FAINT,width=3)
  grow=ease((t-9.7)/1.15);h1=round(620*grow);h2=round(620*A['comparison_b']/A['comparison_a']*grow)
  if h1:d.rounded_rectangle((220,1245-h1,410,1245),16,fill=SAGE)
  if h2:d.rounded_rectangle((700,1245-h2,890,1245),16,fill='#5E8E86')
  if t>=10.75:
   yy=1245-round(620*A['comparison_b']/A['comparison_a']);d.line([(465,625),(490,625),(490,yy),(465,yy)],fill=MINT,width=4)
   txt(d,(505,815),'vs',42,MINT)
  d.rounded_rectangle((80,1330,965,1530),26,fill=GREEN,outline=SAGE,width=3);txt(d,(110,1370),f'${DIFF:,}',91);txt(d,(555,1390),'Illustrative\ndifference',35,MINT)
  txt(d,(85,1590),f"${A['comparison_a']:,} − ${A['comparison_b']:,} = ${DIFF:,}",49)
  txt(d,(85,1700),'Not a quote or guaranteed saving.\nLower cost alone does not mean better.',30,FAINT)
 else:
  txt(d,(80,130),'Full story\nTuesday.',96)
  glow(im);a=actor('nod_yes',min(int((t-14)*24),95));im.paste(a,(45,475),a);d=ImageDraw.Draw(im)
  # Calendar assembles once and holds; no constant bouncing/zooming.
  u=ease((t-14)/.45);y=560+round(35*(1-u));before=im.copy();d=ImageDraw.Draw(im)
  d.rounded_rectangle((555,y,970,y+430),28,fill=PANEL,outline=SAGE,width=3);d.rounded_rectangle((555,y,970,y+100),25,fill=GREEN)
  txt(d,(600,y+28),'NOVEMBER',40);txt(d,(655,y+130),'10',143);txt(d,(610,y+330),'TUESDAY',44,MINT)
  if u<1:im=Image.blend(before,im,u)
  d=ImageDraw.Draw(im);txt(d,(610,1080),'2026',40,SAGE)
  d.rounded_rectangle((80,1370,965,1575),26,fill=GREEN,outline=SAGE,width=3);txt(d,(110,1400),f'${DIFF:,}',88);txt(d,(555,1415),'Illustrative\ndifference',35,MINT)
  disclaimer=wrap(d,A['disclaimer'],37,850);txt(d,(85,1625),disclaimer,37)
  bb=d.multiline_textbbox((85,1625),disclaimer,font=font(37),spacing=8);assert bb[2]<970 and bb[3]<1680
 return im

def main():
 cache_actor('thinking',132);cache_actor('nod_yes',96)
 if '--stills' in sys.argv:
  for i,t in enumerate([.4,1.8,3.5,4.8,6.5,8.5,10,11.5,13.2,14.8,17]):picture(t).save(BUILD/f'layout-{i}.png')
  return
 video=BUILD/'video.mp4';enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','slow','-crf','17','-pix_fmt','yuv420p',str(video)],stdin=sp.PIPE)
 for n in range(FRAMES):enc.stdin.write(picture(n/FPS).tobytes())
 enc.stdin.close();assert enc.wait()==0;v3.check_video(video,FRAMES)
 final=OUT/'Ren_Short_01_Open_Enrollment_Prototype_v2_Qwen.mp4';sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(video),'-i',str(OUT/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(final)],check=True);v3.check_video(final,FRAMES);print(final,flush=True)
if __name__=='__main__':main()
