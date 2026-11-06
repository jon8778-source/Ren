"""Portrait edit of completed MP4: existing voice/native presenter, readable v3 graphics."""
from pathlib import Path
import json,hashlib,subprocess as sp,math,functools,sys
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;B=D.parent;R=B.parents[2];M=json.loads((D/'edit-manifest.json').read_text());SOURCE=Path(M['source']);W,H,FPS=1080,1920,24
INK,GREEN,CREAM='#172A3A','#3F665B','#FAF6EE';SAGE='#B8CCB1'
sys.path.insert(0,str(B));from calculations import calculate
A,C=calculate()
@functools.lru_cache(maxsize=24)
def font(size):return ImageFont.truetype(str(R/'project/remotion/public/fonts/fredoka-latin-600-normal.woff2'),size)
def wrap(draw,text,size,width):
 lines=[]
 for para in text.split('\n'):
  line=''
  for word in para.split():
   trial=(line+' '+word).strip()
   if line and draw.textlength(trial,font=font(size))>width:lines.append(line);line=word
   else:line=trial
  lines.append(line)
 return '\n'.join(lines)

def text(draw,xy,value,size=44,fill=INK,width=None):
 value=wrap(draw,value,size,width) if width else value;draw.multiline_text(xy,value,font=font(size),fill=fill,spacing=10);return value
MED=Image.open(B/'full/assets/medical-props.png').convert('RGBA');PROPS={key:MED.crop(box) for key,box in {'baby':(985,535,1290,1015),'clipboard':(935,10,1345,495),'pills':(240,535,555,1010)}.items()}
@functools.lru_cache(maxsize=12)
def icon(key,width):
 a=PROPS[key];return a.resize((width,round(a.height*width/a.width)),Image.Resampling.LANCZOS)
ALLWORDS=[w for p in M['clips'] for w in p['words']]
CAPTIONS=[]
for part in M['clips']:
 units=[]
 for word in part['words']:
  if units and not units[-1][-1]['display'][-1:].isspace():units[-1].append(word)
  else:units.append([word])
 rows=[];row=[]
 for unit in units:
  if row and (len(''.join(w['display'] for w in row+unit).strip())>58 or unit[-1]['end']-row[0]['start']>3.0):rows.append(row);row=[]
  row.extend(unit)
 if row:rows.append(row)
 if len(rows)>1 and rows[-1][-1]['end']-rows[-1][0]['start']<.8:rows[-2].extend(rows.pop())
 for row in rows:CAPTIONS.append({'start':row[0]['start'],'end':row[-1]['end'],'text':''.join(w['display'] for w in row).strip()})
def card(draw,box,fill=CREAM,outline='#000000',width=3):draw.rounded_rectangle(box,24,fill=fill,outline=outline,width=width)
def presenter(im,raw):
 image=Image.frombytes('RGB',(610,680),raw);mask=Image.new('L',image.size,0);ImageDraw.Draw(mask).rounded_rectangle((0,0,609,679),22,fill=255);im.paste(image,(35,475),mask)
 ImageDraw.Draw(im).rounded_rectangle((33,473,647,1157),23,outline=SAGE,width=3)
def price_card(draw,y,label,value):
 card(draw,(685,y,935,y+185));text(draw,(705,y+20),label,29,GREEN);text(draw,(705,y+68),f'${value:,}',54);text(draw,(705,y+132),'/year',29,GREEN)
def picture(part,n,raw):
 outframe=part['start_frame']+n;t=outframe/24;src=(part['source_start_frame']+n)/24;name=part['id'];im=Image.new('RGB',(W,H),INK);draw=ImageDraw.Draw(im)
 # Restrained sage accent, not a progress bar or permanent channel heading.
 draw.rounded_rectangle((90,125,160,135),4,fill=SAGE)
 if name=='hook':title='Four years.\nOne click.' if src<5.95 else 'Cheaper premiums.\nBetter plan?'
 elif name=='group_chat':title='“Best” or\n“cheapest” ?'
 elif name=='checklist':title='When the PPO\ncould be better' if src<273 else 'Check the plan,\nnot just the price' if src<278.25 else 'Can you cover\nan early bill?'
 elif name=='decision':title='Your plans.\nYour numbers.'
 elif name=='three_questions':title='Three questions.\nOne deliberate choice.'
 else:title='Watch the\nfull comparison'
 text(draw,(90,180),title,62,CREAM,width=850)
 if name in ['hook','decision','close'] or (name=='checklist' and src>=278.25):
  presenter(im,raw);draw=ImageDraw.Draw(im)
  if name=='hook':
   if src<5.95:
    card(draw,(685,520,935,710));text(draw,(710,545),'Renew',40);text(draw,(710,610),'Same plan',31,GREEN)
    for j in range(A['auto_renew_years']):
     y=755+j*90;card(draw,(685,y,935,y+70));text(draw,(705,y+18),f'YEAR {j+1}',28,GREEN)
     if src>j*.85+.3:draw.line((865,y+35,878,y+47,910,y+18),fill=GREEN,width=5)
   else:
    price_card(draw,510,'PLAN A',C['ppo_annual_premium']);price_card(draw,735,'PLAN B',C['hdhp_annual_premium']);card(draw,(685,970,935,1140));text(draw,(705,995),'Premiums only',28,GREEN,width=210);text(draw,(705,1040),'Check total care costs',28,width=210)
  elif name=='checklist':
   card(draw,(685,535,935,825));text(draw,(705,560),'HSA',50);text(draw,(705,640),'Health savings account',30,GREEN,width=205);card(draw,(685,865,935,1125));text(draw,(705,895),'Bills can arrive before funds build up.',32,width=205)
  elif name=='decision':
   for y,value in [(560,'Check your numbers'),(870,'Choose deliberately')]:card(draw,(685,y,935,y+235));text(draw,(705,y+35),value,36,width=205)
  else:card(draw,(685,600,935,920));text(draw,(710,650),'Full video',40,width=200);text(draw,(710,790),'Compare your plans',30,GREEN,width=200)
 elif name=='group_chat':
  for j,(who,msg) in enumerate([('Alex','“Pick the best.”'),('Danny','“Pick the cheapest.”')]):
   y=530+j*300;active=(j==0 and src<75.53) or (j==1 and src>=75.53);card(draw,(90,y,930,y+225),outline=SAGE if active else '#000000',width=5 if active else 3);text(draw,(130,y+25),who,34,GREEN);text(draw,(130,y+95),msg,56,width=740)
 elif name=='checklist':
  if src<273:items=[('baby','Baby or planned surgery'),('clipboard','Regular specialist care'),('pills','Expensive medication')]
  else:items=[(None,'Doctors in-network'),(None,'Prescription coverage'),(None,'Deductible + out-of-pocket limit')]
  for j,(prop,label) in enumerate(items):
   y=490+j*215;card(draw,(90,y,930,y+185));
   if prop:
    a=icon(prop,80);im.paste(a,(125,y+20),a);draw=ImageDraw.Draw(im)
   else:draw.line((125,y+80,141,y+96,177,y+55),fill=GREEN,width=6)
   text(draw,(245,y+40),label,44,width=635)
  text(draw,(100,1175),'Compare your own plan details',30,SAGE,width=800)
 else:
  for j,label in enumerate(['Worst-year cost?','What did you use?','Where does the difference go?']):
   y=490+j*170;card(draw,(90,y,930,y+140));text(draw,(120,y+38),str(j+1),44,GREEN);text(draw,(195,y+28),label,42,width=675)
  if src>=314.33:
   card(draw,(90,1040,930,1200),fill='#DDE8D6');text(draw,(130,1065),'40 minutes',58);text(draw,(130,1140),'Once a year',31,GREEN)
 # Stable multi-word captions, not flashing single-word text.
 cue=next((c for c in CAPTIONS if c['start']<=t<c['end']),None)
 if cue:
  value=wrap(draw,cue['text'],42,820);assert len(value.splitlines())<=2,value;text(draw,(90,1270),value,42,CREAM)
 if t<2.5 or t>=M['duration_seconds']-3.5:
  value='Educational content only,\nnot financial advice.';text(draw,(90,1475),value,30,SAGE)
 return im

def main():
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==M['source_sha256']
 decoded=D/'build/source-audio.f32';metadata=D/'build/source-audio.json'
 if not decoded.exists() or not metadata.exists() or json.loads(metadata.read_text())['source_sha256']!=M['source_sha256']:
  sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(SOURCE),'-map','0:a:0','-f','f32le',str(decoded)],check=True);metadata.write_text(json.dumps({'source_sha256':M['source_sha256']}))
 original=np.memmap(decoded,dtype='float32',mode='r');chunks=[original[p['source_start_sample']:min(p['source_end_sample'],len(original))] for p in M['clips']];master=np.concatenate(chunks);sf.write(D/'build/narration.wav',master,48000,subtype='FLOAT')
 def stamp(t):
  m=round(t*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'
 (D/'deliverables/Ren_Health_Plan_Portrait_Short.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(CAPTIONS))+'\n')
 (D/'captions.json').write_text(json.dumps(CAPTIONS,indent=2)+'\n')
 files=[]
 for part in M['clips']:
  path=D/'build'/(part['id']+'.mp4');base=part['source_start_frame']//24;offset=part['source_start_frame']%24
  dec=sp.Popen(['ffmpeg','-v','error','-xerror','-ss',str(base),'-i',str(SOURCE),'-map','0:v:0','-vf',f"trim=start_frame={offset}:end_frame={offset+part['frames']},setpts=PTS-STARTPTS,crop=610:680:0:0",'-frames:v',str(part['frames']),'-an','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=sp.PIPE)
  if '--stills' not in sys.argv:enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
  for n in range(part['frames']):
   raw=dec.stdout.read(610*680*3);assert len(raw)==610*680*3
   if '--stills' in sys.argv:
    if n in [part['frames']//2]:picture(part,n,raw).save(D/'build'/(part['id']+'.png'))
   else:
    im=picture(part,n,raw);enc.stdin.write(im.tobytes())
    if n==part['frames']//2:im.save(D/'build'/(part['id']+'.png'))
  dec.stdout.close();assert dec.wait()==0
  if '--stills' not in sys.argv:enc.stdin.close();assert enc.wait()==0;files.append(path)
  print('Prepared',part['id'],flush=True)
 if '--stills' in sys.argv:return
 concat=D/'build/concat.txt';concat.write_text('\n'.join("file '%s'"%f for f in files)+'\n');out=D/'deliverables/Ren_Health_Plan_Portrait_1min.mp4';sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(D/'build/narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)],check=True);assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==M['source_sha256'];print(out)
if __name__=='__main__':main()
