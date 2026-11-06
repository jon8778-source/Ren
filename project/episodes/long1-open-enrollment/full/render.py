"""Timed full-film assembly; refuses missing audio/source gates, reuses approved opening."""
from pathlib import Path
import sys,json,math,subprocess as sp,hashlib
from PIL import ImageDraw,Image
import visuals as V
F=Path(__file__).resolve().parent;B=F.parent;p=V.p
OUT=F/'deliverables/Ren_Long_01_Auto_Renewed_My_Health_Plan.mp4';FPS=24
SPECS={
 's004':[(None,'annual')],'s005':[(None,'own_options')],'s006':[(None,'group')],
 's007':[(None,'neighbor'),('He asks questions','questions'),('We opened the plan summaries','illustrative'),('Plan A','ppo_premium')],
 's008':[(None,'ppo_bad'),('Plan B','hdhp_premium'),('Its in-network out-of-pocket maximum','hdhp_bad'),('My employer would also','employer')],
 's009':[(None,'bad_compare'),("But I'd need enough cash",'cashflow'),('and neither figure','limits')],
 's010':[(None,'used_care'),('That makes the PPO','ppo_normal'),('On the high-deductible plan','hdhp_cash')],
 's011':[(None,'hdhp_net'),('Difference','normal_compare'),("It isn't an instant",'not_rebate'),('It depends on','check_services'),('But now I had','illustrative')],
 's012':[(None,'priya'),('The premium gap','redirect')],
 's013':[(None,'contributions'),('If I used','withdrawal'),('If I paid','outside_cash')],
 's014':[(None,'hsa_rules')],'s015':[(None,'money_job')],
 's016':[(None,'warning'),("If you're expecting",'needs'),('Check both networks','network'),('Remember that high','early_bills'),('If you shop','marketplace')],
 's017':[(None,'deadline')],'s018':[(None,'employer_deadline')],
 's019':[(None,'choice'),('Not because cheaper','cheaper'),('I learned to ask','recap'),('Forty minutes once','forty'),("Next time there's",'next')],
 's020':[(None,'close')]}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tokens(s):
 import re
 return re.findall(r"[a-z]+(?:'[a-z]+)?",s.lower().replace('’',"'"))
def manifest(available=False):
 T=json.loads((F/('available-timing.json' if available else 'audio-timing.json')).read_text());M=json.loads((F/'manifest.json').read_text())
 if not available:assert all(s['status']=='complete' for s in M['segments'])
 checks=json.loads((F/'source-checks.json').read_text());assert all(checks[s['source_gate']]['status']=='verified' for s in M['segments'] if s.get('source_gate') and s['status']=='complete')
 pilot=json.loads((B/'shot-manifest.json').read_text());shots=[{**s,'approved_opening':True,'source_file':str(B/'build'/(s['id']+'.mp4'))} for s in pilot['shots']];cursor=shots[-1]['end_frame'];ren_count=sum(s['kind']=='ren' for s in shots)
 for segment in T['segments'][3:]:
  words=[w for w in T['words'] if w['segment']==segment['id']];alltokens=[w['word'] for w in words]
  def locate(phrase):
   target=tokens(phrase)
   for i in range(len(words)):
    if alltokens[i:i+len(target)]==target:return words[i]['start']
   raise ValueError('Missing timing anchor '+segment['id']+' '+phrase)
  beats=SPECS[segment['id']]
  for j,(anchor,motif) in enumerate(beats):
   a=segment['start'] if anchor is None else locate(anchor);z=locate(beats[j+1][0]) if j+1<len(beats) else segment['end'];end=round(z*FPS) if z<T.get('duration',T.get('duration_of_saved_subset')) else T['frames'];length=end-cursor
   if length<=0:raise ValueError('Nonpositive beat '+segment['id']+' '+motif)
   kind=V.MOTIFS[motif][0];cap=132 if kind=='ren' else 84;parts=math.ceil(length/cap);base=cursor
   for k in range(parts):
    n=round(length*(k+1)/parts)-round(length*k/parts);clip=['thinking','nod_yes'][ren_count%2] if kind=='ren' else None
    if clip:ren_count+=1
    shots.append({'id':f'shot_{len(shots)+1:03}','kind':kind,'motif':motif,'segment':segment['id'],'part':k,'start_frame':cursor,'end_frame':cursor+n,'frames':n,'clip':clip,'motif_start':base/FPS,'motif_end':end/FPS,'approved_opening':False});cursor+=n
 assert cursor==T['frames']
 r={'title':M['title'],'resolution':[1280,720],'fps':24,'frames':T['frames'],'duration':T['frames']/24,'narration_duration':T.get('duration',T.get('duration_of_saved_subset')),'not_full_episode':available,'shots':shots,'source_manifest':'manifest.json','assumptions':'../assumptions.json','pilot_reused':18,'no_source_audio':True,'no_music':True,'framing':'Ren left steady full-body, fitted right panels; no zoom/mirror'};(F/('available-shot-manifest.json' if available else 'shot-manifest.json')).write_text(json.dumps(r,indent=2)+'\n');return T,shots

def main():
 available='--available' in sys.argv
 T,shots=manifest(available);files=[]
 (F/'build/clips').mkdir(exist_ok=True);p.actors('thinking');p.actors('nod_yes')
 signature=sha(Path(__file__))+sha(F/'visuals.py')+sha(B/'assets/illustrated-props-v2.png')+sha(B/'assumptions.json')+sha(F/'source-checks.json')
 for s in shots:
  if s['approved_opening']:
   path=Path(s['source_file']);p.v3.check_video(path,s['frames']);files.append(path);continue
  path=F/'build/clips'/(s['segment']+'-'+s['motif']+'-'+str(s['part'])+'.mp4');s['cache_file']=str(path.relative_to(F));mark=path.with_suffix('.json');content={k:v for k,v in s.items() if k not in ['id','start_frame','end_frame','motif_start','motif_end','cache_file']};content.update(local_motif_start=s['motif_start']-s['start_frame']/24,local_motif_end=s['motif_end']-s['start_frame']/24);key=hashlib.sha256((signature+json.dumps(content,sort_keys=True)).encode()).hexdigest()
  if not(path.exists() and mark.exists() and json.loads(mark.read_text()).get('key')==key):
   enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','slow','-crf','17','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
   for n in range(s['frames']):
    t=(s['start_frame']+n)/24;progress=(t-s['motif_start'])/(s['motif_end']-s['motif_start']);im=V.picture(s['motif'],n,s['frames'],s['clip'] or 'thinking',progress)
    if s['segment']=='s020' and t>T.get('duration',T.get('duration_of_saved_subset'))-4:
     d=ImageDraw.Draw(im);txt=p.A['disclaimer'];bb=d.textbbox((28,688),txt,font=p.font(18));layer=Image.new('RGBA',(1280,720));ImageDraw.Draw(layer).rounded_rectangle((bb[0]-7,bb[1]-5,bb[2]+7,bb[3]+5),6,fill=(250,246,238,225));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');p.txt(ImageDraw.Draw(im),(28,688),txt,18)
    enc.stdin.write(im.tobytes())
    if n==s['frames']//2:im.save(F/'build'/(s['id']+'.jpg'))
   enc.stdin.close();assert enc.wait()==0;p.v3.check_video(path,s['frames']);mark.write_text(json.dumps({'key':key,'sha256':sha(path),'frames':s['frames']}))
  p.v3.check_video(path,s['frames']);files.append(path);print('Rendered/reused',s['id'],s['motif'],flush=True)
 if available:
  (F/'available-shot-manifest.json').write_text(json.dumps({'not_full_episode':True,'shots':shots,'remaining':T['remaining'],'note':'Independent cached clips only. No partial movie assembled.'},indent=2)+'\n');print('Independent clips cached; source-gated passages still missing. No full/partial film assembled.');return
 (F/'shot-manifest.json').write_text(json.dumps({'shots':shots,'frames':T['frames'],'fps':24,'narration_duration':T['duration'],'full_episode':True},indent=2)+'\n')
 concat=F/'build/concat.txt';concat.write_text('\n'.join("file '%s'"%p for p in files)+'\n');sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(F/'deliverables/narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(OUT)],check=True);p.v3.check_video(OUT,T['frames']);print(OUT)
if __name__=='__main__':main()
