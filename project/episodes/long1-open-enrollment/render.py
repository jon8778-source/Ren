"""Landscape pilot extending approved v3 native matte, office and typography."""
from pathlib import Path
import sys,json,math,subprocess as sp,functools,re,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from scipy.ndimage import binary_propagation,binary_erosion,gaussian_filter,distance_transform_edt
B=Path(__file__).resolve().parent;ROOT=B.parents[2];BUILD=B/'build';OUT=B/'deliverables'
sys.path.insert(0,str(ROOT/'project/prototypes/coffee-minute-v3'));import render as v3
from calculations import calculate
A,C=calculate();font=functools.lru_cache(maxsize=64)(v3.font)
INK,GREEN,CREAM,MUTED=v3.INK,v3.GREEN,v3.CREAM,v3.MUTED
W,H,FPS=1280,720,24
T=json.loads((B/'audio-timing.json').read_text());WORDS=T['words'];TOKENS=[w['word'] for w in WORDS]
OFFICE=ImageOps.fit(v3.ART['office.png'],(W,H),method=Image.Resampling.LANCZOS)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def txt(d,pos,s,size=38,fill=INK):d.multiline_text(pos,s,font=font(size),fill=fill,spacing=5)
def center(d,y,s,size=38,fill=INK):txt(d,((W-d.textlength(s,font=font(size)))/2,y),s,size,fill)
def wrap(d,s,size,width):
 lines=[];row=''
 for word in s.split():
  q=(row+' '+word).strip()
  if row and d.textlength(q,font=font(size))>width:lines.append(row);row=word
  else:row=q
 lines.append(row);return '\n'.join(lines)
def locate(text):
 q=re.findall(r"[a-z]+(?:'[a-z]+)?",text.lower().replace('’',"'"));i=next((i for i in range(len(TOKENS)) if TOKENS[i:i+len(q)]==q),None);assert i is not None,text
 return WORDS[i]['start']
P=[(0,locate('four years running'),'ren','email'),(locate('four years running'),locate('this year i spent'),'ren','click'),(locate('this year i spent'),locate('my normal year comparison'),'graphic','clocks'),(locate('my normal year comparison'),locate('and i nearly'),'ren','potential'),(locate('and i nearly'),locate('at twenty five'),'ren','potential'),(locate('at twenty five'),locate('by twenty eight'),'graphic','lease'),(locate('by twenty eight'),locate('christmas'),'graphic','used'),(locate('christmas'),locate('that january'),'graphic','bank'),(locate('that january'),locate("i'm still driving"),'graphic','audit'),(locate("i'm still driving"),locate('but i missed'),'ren','samecar'),(locate('but i missed'),T['segments'][1]['end'],'graphic','paystub'),(T['segments'][1]['end'],locate('mine was going'),'ren','increase'),(locate('mine was going'),T['duration'],'ren','premium')]
SHOTS=[];cursor=0;ren=0
for start,end,kind,motif in P:
 end_frame=round(end*FPS) if end<T['duration'] else T['frames'];length=end_frame-cursor;cap=132 if kind=='ren' else 84;parts=math.ceil(length/cap);base=cursor
 for j in range(parts):
  n=round(length*(j+1)/parts)-round(length*j/parts);clip=['thinking','nod_yes'][ren%2] if kind=='ren' else None
  if clip:ren+=1
  SHOTS.append({'id':f'shot_{len(SHOTS)+1:03}','kind':kind,'motif':motif,'clip':clip,'part':j,'start_frame':cursor,'frames':n,'end_frame':cursor+n,'motif_start':base/FPS,'motif_end':end_frame/FPS});cursor+=n
assert cursor==T['frames']

def ease(x):x=float(np.clip(x,0,1));return 1-(1-x)**3
def matte(im):
 a=np.asarray(im).astype(np.float32);dist=np.sqrt(np.mean(((255-a)/255)**2,axis=2));seed=np.zeros(dist.shape,bool);seed[0,:]=seed[-1,:]=True;seed[:,0]=seed[:,-1]=True
 ext=binary_propagation(seed&(dist<.24),mask=dist<.24);core=binary_erosion(~ext,iterations=1);alpha=gaussian_filter(core.astype(np.float32),.55);edge=(alpha>0)&~core;idx=distance_transform_edt(~core,return_distances=False,return_indices=True);a[edge]=a[idx[0][edge],idx[1][edge]]
 return Image.fromarray(np.dstack([a,np.round(alpha*255)]).astype('uint8'),'RGBA')
def actors(clip):
 folder=BUILD/f'actor-{clip}';folder.mkdir(exist_ok=True)
 if len(list(folder.glob('*.png')))<132:
  source=ROOT/'assets/ren_library'/f'ren_{clip}.mp4';probe=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert (v['width'],v['height'])==(1280,720) and float(probe['format']['duration'])>=6.75
  dec=sp.Popen(['ffmpeg','-v','error','-xerror','-ss','1.25','-i',str(source),'-an','-frames:v','132','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=sp.PIPE)
  for n in range(132):
   raw=dec.stdout.read(1280*720*3);assert len(raw)==1280*720*3;im=matte(Image.frombytes('RGB',(1280,720),raw)).resize((1152,648),Image.Resampling.LANCZOS);im.save(folder/f'{n:03}.png')
  dec.stdout.close();assert dec.wait()==0
 return folder
@functools.lru_cache(maxsize=220)
def actor(clip,n):return Image.open(BUILD/f'actor-{clip}'/f'{n:03}.png').convert('RGBA')
def textbox(im,pos,s,size=40):
 d=ImageDraw.Draw(im);value=wrap(d,s,size,475);bb=d.multiline_textbbox(pos,value,font=font(size),spacing=5);box=(bb[0]-22,bb[1]-18,bb[2]+22,bb[3]+18);assert box[0]>=650 and box[2]<=1245 and box[3]<=505,box
 layer=Image.new('RGBA',(W,H));draw=ImageDraw.Draw(layer);draw.rounded_rectangle(box,16,fill=(255,255,255,170),outline=(0,0,0,255),width=2);im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');txt(ImageDraw.Draw(im),pos,value,size);return im


def change(d,pos,a,b,size=60):
 x,y=pos;first=f'${a}';second=f'${b}';w=d.textlength(first,font=font(size));arrow=round(size*.95);gap=round(size*.3);cy=y+size*.6;left=x+w+gap;right=left+arrow
 txt(d,(x,y),first,size);d.line((left,cy,right-10,cy),fill=INK,width=max(3,round(size*.045)));d.polygon([(right,cy),(right-15,cy-10),(right-15,cy+10)],fill=INK);txt(d,(right+gap,y),second,size)
 return right+gap+d.textlength(second,font=font(size))
def changebox(im,pos,a,b,size):
 d=ImageDraw.Draw(im);w1=d.textlength(f'${a}',font=font(size));w2=d.textlength(f'${b}',font=font(size));w=w1+w2+round(size*.95)+2*round(size*.3);bb=d.textbbox(pos,f'${a}',font=font(size));box=(pos[0]-22,bb[1]-18,pos[0]+w+22,bb[3]+18);assert box[0]>=650 and box[2]<=1245 and box[3]<=505
 layer=Image.new('RGBA',(W,H));ImageDraw.Draw(layer).rounded_rectangle(box,16,fill=(255,255,255,170),outline=(0,0,0,255),width=2);im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');change(ImageDraw.Draw(im),pos,a,b,size);return im

# Original image-generation sheet retained unmodified. Crops are composition regions.
PROP_SHEET=Image.open(B/'assets/illustrated-props-v2.png').convert('RGBA')
PROPS={name:PROP_SHEET.crop(box) for name,box in {
 'new_car':(18,65,760,450),'used_car':(785,70,1525,450),
 'phone':(245,515,525,1000),'keys':(875,535,1430,990)}.items()}
@functools.lru_cache(maxsize=32)
def prop_size(name,width):
 a=PROPS[name];return a.resize((width,round(a.height*width/a.width)),Image.Resampling.LANCZOS)
def prop(im,name,x,y,width):
 a=prop_size(name,width);im.paste(a,(round(x),round(y)),a)
def driveway(im):
 d=ImageDraw.Draw(im)
 # Restrained environmental depth: house frontage, planting and driveway.
 d.rounded_rectangle((95,165,1185,540),26,fill='#E5EADF')
 d.rectangle((130,205,525,455),fill='#D3DED0');d.rectangle((158,230,492,455),fill='#F0F1E9')
 for yy in [280,330,380]:d.line((158,yy,492,yy),fill='#CAD4C5',width=3)
 d.rectangle((1050,220,1125,485),fill='#C5D3C0')
 for xx,yy,rr in [(1050,415,48),(1110,430,55),(165,440,43)]:d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill='#9FB39D')
 d.polygon([(95,495),(1185,495),(1250,625),(30,625)],fill='#D5D7D0')
 d.line((30,625,1250,625),fill='#AEB7AA',width=3)

def clock(d,cx,cy,r,phase):
 d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=CREAM,outline=GREEN,width=6)
 for i in range(12):
  a=i*math.pi/6;d.line((cx+(r-14)*math.cos(a),cy+(r-14)*math.sin(a),cx+(r-5)*math.cos(a),cy+(r-5)*math.sin(a)),fill=GREEN,width=3)
 a=-math.pi/2+phase;d.line((cx,cy,cx+(r-25)*math.cos(a),cy+(r-25)*math.sin(a)),fill=INK,width=5);d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=INK)

def picture(s,n):
 absolute=(s['start_frame']+n)/FPS;p=(absolute-s['motif_start'])/(s['motif_end']-s['motif_start']);k=s['motif']
 im=OFFICE.copy() if s['kind']=='ren' else Image.new('RGB',(W,H),CREAM)
 if s['kind']=='ren':
  rgba=actor(s['clip'],n);im.paste(rgba,(-300,33),rgba)
  if k in ('email','click','increase'):
   subject='Open enrollment\ncloses Friday.' if k!='increase' else 'Your premium contribution\nwill increase.'
   im=textbox(im,(710,105),subject,36 if k=='increase' else 40)
   if k!='increase':
    d=ImageDraw.Draw(im);clicked=k=='click' and p>.18;d.rounded_rectangle((710,290,1195,360),18,fill=GREEN if clicked else INK);txt(d,(738,308),'Keep current plan',32,CREAM)
    if k=='click':
     x=1100+80*(1-ease(p/.25));y=340+45*(1-ease(p/.25));d.polygon([(x,y),(x+7,y+36),(x+17,y+25),(x+30,y+25)],fill=CREAM,outline=INK,width=2)
     im=textbox(im,(850,420),f"0:{A['auto_click_seconds']:02d}",49)
  elif k=='potential':
   im=textbox(im,(710,105),'Potential normal-year\nnet difference',34);im=textbox(im,(790,265),f"${C['potential_normal_year_net_gap']:,}",78);txt(ImageDraw.Draw(im),(710,430),'Illustrative example • not a cash rebate',24,GREEN)
  elif k=='samecar':
   im=textbox(im,(710,105),f"Same used car.\n{A['backstory']['used_car_years_later']} years later.",38);layer=Image.new('RGBA',(W,H));ImageDraw.Draw(layer).rounded_rectangle((710,285,1090,475),16,fill=(255,255,255,170),outline=(0,0,0,255),width=2);im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');prop(im,'used_car',730,295,340)
  elif k=='premium':
   im=textbox(im,(710,100),'Monthly premium',36);im=changebox(im,(700,240),A['previous_premium_monthly'],A['ppo']['premium_monthly'],60);txt(ImageDraw.Draw(im),(710,390),'Per month • illustrative plan',27,GREEN)
 else:
  d=ImageDraw.Draw(im)
  if k=='clocks':
   center(d,60,'Four seconds. Forty minutes.',48)
   clock(d,360,320,128,2*math.pi*ease(p)*A['auto_click_seconds']/60);clock(d,920,320,128,2*math.pi*ease(p)*A['review_minutes']/60)
   txt(d,(265,495),f"0:{A['auto_click_seconds']:02d}",66);txt(d,(800,495),f"{A['review_minutes']}:00",66,GREEN);d.line((560,320,695,320),fill=GREEN,width=6);d.polygon([(695,320),(672,305),(672,335)],fill=GREEN)
  elif k in ('lease','used'):
   center(d,55,f"Age {A['backstory']['leased_car_age']}: a shiny leased car" if k=='lease' else f"Age {A['backstory']['returned_car_age']}: return the keys. Buy used.",45)
   driveway(im);d=ImageDraw.Draw(im)
   offset=round(120*(1-ease(p/.35)));prop(im,'used_car' if k=='used' else 'new_car',330-offset,270,650)
   if k=='lease':
    d.rounded_rectangle((995,200,1160,410),16,fill='#FFFFFF',outline=GREEN,width=3);txt(d,(1012,228),'LEASE',29,GREEN)
    for j in range(4):d.line((1012,285+j*25,1140,285+j*25),fill='#C3CCC1',width=3)
   else:prop(im,'keys',120+round(40*ease(p/.5)),235,175)
  elif k=='bank':
   im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im);txt(d,(100,115),'After Christmas',48,CREAM)
   prop(im,'phone',765,65,330);d=ImageDraw.Draw(im)
   txt(d,(810,205),'Available balance',25,GREEN);txt(d,(820,285),f"${A['backstory']['bank_balance']}",100);txt(d,(100,265),'A very small\nfinancial cushion.',42,CREAM)
   d.line((810,420,1050,420),fill='#D3DAD0',width=3);txt(d,(810,445),'Illustrative account',22,MUTED)
  elif k=='audit':
   im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im);center(d,55,'The January payment audit',48,CREAM)
   d.rounded_rectangle((190,175,1090,595),26,fill=CREAM,outline=GREEN,width=4)
   for j in range(5):
    shade=GREEN if int(p*6)%5==j else '#CED8CB';d.line((240,230+j*42,1035,230+j*42),fill=shade,width=4)
   change(d,(290,445),A['backstory']['payments_before'],A['backstory']['payments_after'],86);center(d,635,'Monthly payments',32,CREAM)
  elif k=='paystub':
   center(d,55,'The payment I never saw',48)
   d.rounded_rectangle((220,150,1080,625),20,fill='#FFFFFF',outline=GREEN,width=3);txt(d,(270,185),'PAY STUB',36,GREEN);txt(d,(270,235),'Illustrative excerpt',21,MUTED)
   labels=['Federal withholding','Medical premium','Other deductions']
   for j,label in enumerate(labels):
    y=315+j*85
    if j==1:
     amount=round(260*ease(p/.3));d.rounded_rectangle((250,y-12,250+amount+480,y+58),14,fill='#DCE8D9',outline=GREEN,width=3)
    txt(d,(280,y),label,35);d.line((855,y+28,1015,y+28),fill=MUTED,width=3)
 # Exact disclaimer appears briefly at beginning and end, never a persistent footer.
 if absolute<4 or absolute>T['duration']-3:
  d=ImageDraw.Draw(im);value=A['disclaimer'];bb=d.textbbox((28,688),value,font=font(18));layer=Image.new('RGBA',(W,H));ImageDraw.Draw(layer).rounded_rectangle((bb[0]-7,bb[1]-5,bb[2]+7,bb[3]+5),6,fill=(250,246,238,215));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');txt(ImageDraw.Draw(im),(28,688),value,18)
 return im

def main():
 for clip in ['thinking','nod_yes']:actors(clip)
 (B/'shot-manifest.json').write_text(json.dumps({'title':'I Auto-Renewed My Health Plan for 4 Years. Then I Did the Math.','pilot_only':True,'resolution':[W,H],'fps':FPS,'frames':T['frames'],'narration_duration':T['duration'],'shots':SHOTS,'native_actor_decode':[1280,720],'actor_composition_scale':.9,'actor_position':[-300,33],'framing':'Steady full-body Ren left; content right; no mirroring or zoom changes','no_music':True},indent=2)+'\n')
 if '--stills' in sys.argv:
  for s in SHOTS:picture(s,s['frames']//2).save(BUILD/(s['id']+'.jpg'))
  return
 files=[]
 signature=sha(Path(__file__))+sha(B/'assets/illustrated-props-v2.png')
 for s in SHOTS:
  path=BUILD/(s['id']+'.mp4');mark=path.with_suffix('.json');key=hashlib.sha256((signature+json.dumps(s,sort_keys=True)).encode()).hexdigest()
  if not(path.exists() and mark.exists() and json.loads(mark.read_text()).get('key')==key):
   enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','slow','-crf','17','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
   for n in range(s['frames']):
    im=picture(s,n);enc.stdin.write(im.tobytes())
    if n==s['frames']//2:im.save(BUILD/(s['id']+'.jpg'))
   enc.stdin.close();assert enc.wait()==0;v3.check_video(path,s['frames']);mark.write_text(json.dumps({'key':key,'sha256':sha(path),'frames':s['frames']}))
  v3.check_video(path,s['frames']);files.append(path);print('Rendered/reused',s['id'],flush=True)
 concat=BUILD/'concat.txt';concat.write_text('\n'.join("file '%s'"%p.name for p in files)+'\n');final=OUT/'Ren_Long_01_Open_Enrollment_Pilot_v2.mp4'
 sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(OUT/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(final)],check=True);v3.check_video(final,T['frames']);print(final,flush=True)
if __name__=='__main__':main()
