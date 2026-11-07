"""Extend the approved v3 portrait opening; copy first 360 frames, render remainder."""
from pathlib import Path
import importlib.util,functools,json,os,subprocess as sp,sys
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;F=D/'full-production';BUILD=D/'build/full-production'
BUILD.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('approved_rev6',D/'render_revision6.py')
r6=importlib.util.module_from_spec(spec);spec.loader.exec_module(r6)
b,S=r6.b,r6.S;P=b.parent
M=S.load(F/'production.json');REC=S.LayoutRecorder()
W,H,FPS=1080,1920,24
INK,GREEN,CREAM,SAGE=b.INK,b.GREEN,b.CREAM,b.SAGE
font,ease=b.font,b.ease

def txt(im,s,n,xy,value,size=60,fill=INK,role='text'):
 d=ImageDraw.Draw(im);d.multiline_text(xy,value,font=font(size),fill=fill,spacing=9)
 REC.record(s['id'],d,xy,value,font(size),(s['start_frame']+n)/24,
            (s['start_frame']+n+1)/24,role,spacing=9)

@functools.lru_cache(maxsize=6)
def environment(name):
 if name=='office':return b.OFFICE.crop((1120,0,1480,640)).resize((W,H),Image.Resampling.LANCZOS)
 im=Image.open(F/'assets'/f'{name}.png').convert('RGB')
 return im.resize((W,H),Image.Resampling.LANCZOS)

@functools.lru_cache(maxsize=15)
def prop(name,width):
 source=Image.open(D.parent/'full/assets/medical-props.png').convert('RGBA')
 boxes={'baby':(985,535,1290,1015),'pills':(240,535,555,1010),
        'jar':(180,0,620,500),'clipboard':(935,10,1345,495)}
 a=source.crop(boxes[name]);return a.resize((width,round(a.height*width/a.width)),Image.Resampling.LANCZOS)

def paper(im,box):
 x,y,w,h=box;b.shadow(im,(x+9,y+13,x+w+9,y+h+13),8)
 d=ImageDraw.Draw(im);d.polygon([(x,y),(x+w-45,y),(x+w,y+45),(x+w,y+h),(x,y+h)],fill=CREAM,outline='#7D8874',width=3)
 d.polygon([(x+w-45,y),(x+w-45,y+45),(x+w,y+45)],fill='#D8E1D0',outline='#7D8874',width=2)

def desk(im,y=1220):
 d=ImageDraw.Draw(im)
 d.polygon([(0,y),(1080,y-45),(1080,1920),(0,1920)],fill='#CDA37A',outline='#886442',width=4)
 for row in range(y+90,2000,170):
  d.line((0,row,1080,row-45),fill='#B98E65',width=3)
  d.line((0,row+65,1080,row+20),fill='#C29A72',width=2)

def check(im,xy,progress=1,size=50):
 if progress<=0:return
 x,y=xy;d=ImageDraw.Draw(im)
 d.line((x,y+size*.5,x+size*.35,y+size*.85,x+size,y),fill=GREEN,width=8)

def approved_hand(im,x,y,width=620):
 a=r6.art('ren-right-hand-trackpad-click.png',width)
 k=width/1568;d=ImageDraw.Draw(im)
 left=(round(x+994*k),round(y+1002*k));right=(round(x+1567*k),round(y+1002*k))
 d.polygon([left,right,(1130,right[1]+150),(1130,right[1]+400)],fill='#3A3F58',outline='#20293A',width=2)
 im.paste(a,(round(x),round(y)),a)

def prepare_actors():
 # Decode native sources FIRST. The phone action is a medium composition, not
 # a close-up made from the tiny source face; clipboard shot excludes the face.
 for name,start,count,crop,size in [('hold_phone',.75,72,(470,0,830,405),(720,810))]:
  folder=BUILD/name;folder.mkdir(exist_ok=True)
  source=b.ROOT/'assets/ren_library'/f'ren_{name}.mp4'
  key=S.digest({'source':S.sha(source),'matte':S.sha(b.B/'render.py'),
                'start':start,'frames':count,'crop':crop,'size':size,'native_decode':[1280,720]})
  mark=folder/'cache.json'
  if mark.exists() and S.load(mark).get('key')==key and all((folder/f'{n:03}.png').exists() for n in range(count)):continue
  dec=sp.Popen(['ffmpeg','-v','error','-xerror','-ss',str(start),'-i',str(source),
               '-frames:v',str(count),'-an','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=sp.PIPE)
  for n in range(count):
   raw=dec.stdout.read(1280*720*3);assert len(raw)==1280*720*3
   a=P.matte(Image.frombytes('RGB',(1280,720),raw)).crop(crop).resize(size,Image.Resampling.LANCZOS)
   a.save(folder/f'{n:03}.png')
  dec.stdout.close();assert dec.wait()==0;mark.write_text(json.dumps({'key':key}))

@functools.lru_cache(maxsize=170)
def actor(name,n):return Image.open(BUILD/name/f'{n:03}.png').convert('RGBA')

def phone_body(im,x=90,y=285,w=820,h=1190):
 b.shadow(im,(x+10,y+15,x+w+10,y+h+15),55)
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,x+w,y+h),58,fill='#263548',outline='#111E2C',width=5)
 d.rounded_rectangle((x+20,y+25,x+w-20,y+h-25),42,fill=CREAM)
 d.rounded_rectangle((x+w//2-75,y+16,x+w//2+75,y+46),14,fill='#263548')

def catch(s,n):
 im=environment('clinic').copy();y=470+round(340*(1-ease(n/16)))
 paper(im,(115,y,780,780))
 txt(im,s,n,(155,y+65),'MEDICAL BILL',64,GREEN)
 txt(im,s,n,(155,y+210),'Premiums',80)
 txt(im,s,n,(155,y+325),'+ care costs',80)
 d=ImageDraw.Draw(im);u=ease((n-20)/18)
 d.line((155,y+455,155+round(640*u),y+455),fill=GREEN,width=7)
 txt(im,s,n,(155,y+535),'Compare the total.',64)
 return im

def chat_alex(s,n):
 im=environment('office').copy();a=actor('hold_phone',n);im.paste(a,(-25,520),a)
 desk(im,1300)
 # Real native phone-raising gesture, with message read beside it; no new pose.
 phone_body(im,520,400,385,760)
 txt(im,s,n,(560,490),'GROUP CHAT',43,GREEN)
 if n>=8:
  txt(im,s,n,(560,615),'Alex',54,GREEN)
  txt(im,s,n,(560,705),'“Pick the\nbest.”',58)
 txt(im,s,n,(100,235),'I asked around.',70)
 return im

def chat_danny(s,n):
 im=r6.previous.wood().copy();phone_body(im)
 txt(im,s,n,(145,385),'GROUP CHAT',56,GREEN)
 txt(im,s,n,(145,540),'Alex',52,GREEN)
 txt(im,s,n,(145,625),'“Pick the best.”',64)
 dy=round(75*(1-ease(n/12)))
 txt(im,s,n,(145,850+dy),'Danny',52,GREEN)
 txt(im,s,n,(145,945+dy),'“Pick the\ncheapest.”',70)
 return im

def clinic_visit(s,n):
 im=environment('clinic').copy()
 p=prop('baby',210);im.paste(p,(110,1110),p)
 y=910+round(200*(1-ease(n/12)));paper(im,(365,y,535,520))
 txt(im,s,n,(405,y+65),'PLANNED CARE',48,GREEN)
 txt(im,s,n,(405,y+175),'Baby /\nsurgery',66)
 # A date is selected without inventing a medical amount or named patient.
 d=ImageDraw.Draw(im)
 for j in range(5):d.ellipse((410+j*78,y+380,447+j*78,y+417),outline=GREEN,width=3)
 if n>22:check(im,(568,y+375),size=43)
 return im

def pharmacy(s,n):
 im=environment('pharmacy').copy();u=ease(n/15)
 p=prop('pills',265);im.paste(p,(round(-300+440*u),1005),p)
 y=955+round(80*(1-u));paper(im,(475,y,420,490))
 txt(im,s,n,(515,y+55),'PRESCRIPTION',42,GREEN)
 txt(im,s,n,(515,y+160),'Drug\ncoverage?',64)
 return im

def ppo(s,n):
 im=environment('clinic').copy();a=r6.art('ren-chest-up-reaction.png',800)
 im.paste(a,(-130,120),a)
 desk(im,1430)
 paper(im,(500,895,400,555))
 txt(im,s,n,(540,965),'PPO',84,GREEN)
 txt(im,s,n,(540,1100),'Could suit\nhigher\ncare needs',50)
 return im

def network(s,n):
 im=environment('clinic').copy();phone_body(im,90,300,815,1180)
 txt(im,s,n,(145,415),'CHECK YOUR PLAN',58,GREEN)
 txt(im,s,n,(145,625),'Doctors\nin-network?',76)
 if n>=12:check(im,(765,655),size=58)
 txt(im,s,n,(145,960),'Drug\ncoverage?',76)
 if n>=30:check(im,(765,995),size=58)
 return im

def limits(s,n):
 im=environment('clinic').copy();paper(im,(90,280,825,1140))
 txt(im,s,n,(140,355),'PLAN DETAILS',64,GREEN)
 txt(im,s,n,(140,530),'Deductible:',60)
 txt(im,s,n,(140,620),'Check your plan',60,GREEN)
 txt(im,s,n,(140,800),'Covered in-network\nout-of-pocket limits',48)
 txt(im,s,n,(140,1010),f"Plan A  ${b.parent.A['ppo']['in_network_oop_max']:,}",68)
 txt(im,s,n,(140,1150),f"Plan B  ${b.parent.A['hdhp']['in_network_oop_max']:,}",68,GREEN)
 u=ease(n/25);d=ImageDraw.Draw(im);d.line((140,1315,140+round(665*u),1315),fill=GREEN,width=6)
 return im

def hsa(s,n):
 im=environment('pharmacy').copy();p=prop('jar',335);im.paste(p,(100,1050),p)
 txt(im,s,n,(190,1225),'HSA',58,GREEN)
 y=815+round(180*(1-ease(n/14)));paper(im,(460,y,430,610))
 txt(im,s,n,(500,y+65),'EARLY BILL',52,GREEN)
 txt(im,s,n,(500,y+185),'Funds may\nstill be\nbuilding.',56)
 # No fabricated day-one HSA balance or assumed contribution schedule.
 return im

def desk_review(s,n):
 im=environment('office').copy();a=r6.art('ren-chest-up-reaction.png',820)
 im.paste(a,(-30,90),a);desk(im,1130)
 y=1130+round(70*(1-ease(n/14)));paper(im,(500,y,390,560))
 txt(im,s,n,(540,y+50),'MY PLAN',52,GREEN)
 txt(im,s,n,(540,y+145),'Review\nfirst.',64)
 return im

def choice(s,n):
 im=r6.previous.wood().copy()
 txt(im,s,n,(100,250),'Check. Compare.\nThen choose.',78)
 a=b.laptop_image(1250);im.paste(a,(-85,520),a)
 d=ImageDraw.Draw(im);d.rectangle((82,590,995,1105),fill=CREAM)
 txt(im,s,n,(125,630),'MY PLAN REVIEW',52,GREEN)
 for j,label in enumerate(['Network','Drug coverage','Total costs']):
  yy=740+j*100;txt(im,s,n,(145,yy),label,58)
  if n>=j*18+4:check(im,(800,yy+10),size=50)
 # Same approved right hand, distinct review action rather than replaying the
 # opening renewal click. A cursor follows the sequential review checks.
 approved_hand(im,365,1255,width=620)
 if n>=55:txt(im,s,n,(125,1490),'Choose deliberately.',48,GREEN)
 return im

def worksheet(s,n):
 im=r6.previous.wood().copy();paper(im,(90,260,825,1185))
 txt(im,s,n,(145,335),'MY PLAN REVIEW',60,GREEN)
 rows=[(550,'Bad year?',.8),(805,'Real year?',2.1),(1060,'Difference\nfor what?',3.6)]
 for y,label,t in rows:
  txt(im,s,n,(205,y),label,70)
  if n/24>=t:check(im,(120,y+22),size=52)
 # Approved right hand follows the three marks, rather than floating cards.
 point=0 if n/24<2.1 else 1 if n/24<3.6 else 2
 u=ease((n/24-[0,2.1,3.6][point])/.22)
 yy=[610,865,1120][point]
 approved_hand(im,510,yy-110+round(4*u),width=500)
 return im

def annual(s,n):
 im=environment('office').copy();desk(im,800)
 txt(im,s,n,(110,300),'A yearly review.',80)
 # An actual mechanical review timer rests on the desk, with a single fixed
 # 40-minute setting. No decorative continuously spinning clock.
 import math
 d=ImageDraw.Draw(im)
 d.ellipse((170,760,860,1450),fill='#D8E1D0',outline=INK,width=8)
 d.ellipse((200,790,830,1420),fill=CREAM,outline=GREEN,width=4)
 for j in range(12):
  a=j*math.pi/6
  d.line((515+270*math.sin(a),1105-270*math.cos(a),515+294*math.sin(a),1105-294*math.cos(a)),fill=GREEN,width=5)
 d.line((515,1105,330,1212),fill=INK,width=11)
 d.ellipse((502,1092,528,1118),fill=INK)
 txt(im,s,n,(305,925),'40 MIN',90)
 txt(im,s,n,(285,1310),'Once a year.',48,GREEN)
 if n>=20:check(im,(740,610),size=90)
 return im

def ending(s,n):
 im=environment('office').copy();desk(im,1190)
 txt(im,s,n,(145,355),'Compare\ntotal cost.',88)
 txt(im,s,n,(145,665),'Not just\npremiums.',88,GREEN)
 d=ImageDraw.Draw(im);u=ease(n/12)
 d.line((145,955,145+round(620*u),955),fill=GREEN,width=7)
 # The reviewed insurance folder settles on the desk beneath the takeaway.
 y=1200+round(60*(1-ease(n/12)))
 d=ImageDraw.Draw(im);d.polygon([(90,y),(380,y),(420,y+50),(900,y+50),
   (900,y+230),(90,y+230)],fill=SAGE,outline=GREEN,width=4)
 txt(im,s,n,(145,y+95),'PLAN REVIEWED',56,GREEN)
 check(im,(715,y+100),size=60)
 txt(im,s,n,(95,1470),'Educational content only,\nnot financial advice.',36,INK,'disclaimer')
 return im

FUNCTIONS=dict(zip(['care-catch','chat-alex','chat-danny','clinic-visit','pharmacy-pickup',
 'ppo-review','network-check','plan-limits','hsa-timing','desk-review','deliberate-choice',
 'three-questions','annual-review','total-cost-ending'],
 [catch,chat_alex,chat_danny,clinic_visit,pharmacy,ppo,network,limits,hsa,desk_review,choice,worksheet,annual,ending]))

def save_layout():
 result=S.load(D/'revision-06/layout.json')['scenes']
 for sid,items in REC.scenes.items():
  merged={}
  for i in items:
   key=(i['text'],i['font_px'],i['role'])
   if key not in merged:merged[key]=dict(i)
   else:
    a=merged[key];a['bbox']=[min(a['bbox'][0],i['bbox'][0]),min(a['bbox'][1],i['bbox'][1]),max(a['bbox'][2],i['bbox'][2]),max(a['bbox'][3],i['bbox'][3])]
    a['start']=min(a['start'],i['start']);a['end']=max(a['end'],i['end'])
  result[sid]=list(merged.values())
 (F/'layout.json').write_text(json.dumps({'scenes':result},indent=2)+'\n')

def main():
 stills='--stills' in sys.argv
 if not stills:
  assert os.environ.get('REN_SHORTS_STAGE')=='full'
  assert int(os.environ['REN_SHORTS_MAX_FRAMES'])==M['frames']
 prepare_actors();cache=S.SceneCache(BUILD/'cache');files=[]
 source=S.resolve(F/'production.json',M['prototype'])
 assert S.sha(source)==S.load(F/'authorization.json')['approved_prototype_sha256']
 opening=BUILD/'approved-opening-video.mp4'
 if not opening.exists():
  sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(source),'-map','0:v:0','-an','-c:v','copy',str(opening)],check=True)
 P.v3.check_video(opening,360);files.append(opening)
 dependencies={a['id']:S.sha(S.resolve(F/'production.json',a['path'])) for a in M['assets']}
 for s in M['scenes'][5:]:
  count=s['end_frame']-s['start_frame'];REC.begin_scene(s['id'])
  key=S.scene_cache_key(s,dependencies,S.sha(__file__));cached=cache.get(key,count)
  if stills:
   for n in [0,count//2,count-1]:FUNCTIONS[s['id']](s,n).save(BUILD/f"{s['id']}-{n:03}.png")
   continue
  if cached and cached.with_suffix('.layout.json').exists():
   REC.scenes[s['id']]=S.load(cached.with_suffix('.layout.json'));files.append(cached)
   print('Reused',s['id'],flush=True);continue
  path=BUILD/(s['id']+'.mp4')
  enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
  for n in range(count):
   im=FUNCTIONS[s['id']](s,n);enc.stdin.write(im.tobytes())
   if n in [0,count//2,count-1]:im.save(BUILD/f"{s['id']}-{n:03}.png")
  enc.stdin.close();assert enc.wait()==0
  cached=cache.store(key,path,count);cached.with_suffix('.layout.json').write_text(json.dumps(REC.scenes[s['id']]))
  files.append(cached);print('Rendered/validated',s['id'],count,'frames',flush=True)
 save_layout()
 if stills:return
 concat=BUILD/'concat.txt';concat.write_text('\n'.join("file '%s'"%p for p in files)+'\n')
 master=BUILD/'narration.wav'
 assert S.sha(master)==S.load(F/'audio-preservation.json')['master_wav_sha256']
 out=S.resolve(F/'production.json',M['final'])
 sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)],check=True)
 print(out,flush=True)

if __name__=='__main__':main()
