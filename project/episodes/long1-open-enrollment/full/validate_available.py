"""Check cached independent clips; deliberately not a full-film completion report."""
from pathlib import Path
import json,hashlib,subprocess as sp,sys,math
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
F=Path(__file__).resolve().parent;sys.path.insert(0,str(F.parent));from calculations import calculate
calculate();M=json.loads((F/'manifest.json').read_text());T=json.loads((F/'available-timing.json').read_text());P=json.loads((F/'available-shot-manifest.json').read_text());assert P['not_full_episode'] is True
R=F/'build/available-review';R.mkdir(exist_ok=True);mids=[];frames_total=0;checks=[]
for s in P['shots']:
 path=Path(s['source_file']) if s.get('approved_opening') else F/s['cache_file'];probe=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]));assert len(probe['streams'])==1;v=probe['streams'][0];assert int(v['nb_frames'])==s['frames'] and (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'24/1');assert s['frames']<=(132 if s['kind']=='ren' else 84)
 raw=sp.check_output(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(path),'-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','-']);a=np.frombuffer(raw,np.uint8).reshape(-1,180,320,3);assert len(a)==s['frames'];assert (a.mean((1,2,3))>10).all() and (a.std((1,2,3))>5).all();mid=Image.fromarray(a[len(a)//2]);ImageDraw.Draw(mid).text((3,3),s['id']+' '+s['motif'],fill='black',stroke_fill='white',stroke_width=2);mids.append(mid);frames_total+=len(a);checks.append({'id':s['id'],'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames':len(a),'fatal_decode':'pass','video_only':True})
 if s['motif'] in ['neighbor','redirect','bad_compare','normal_compare','needs','priya','contributions','forty']:
  for label,n in [('start',0),('middle',len(a)//2),('end',len(a)-1)]:Image.fromarray(a[n]).save(R/(s['id']+'-'+label+'.jpg'))
for page in range(0,len(mids),12):
 part=mids[page:page+12];sheet=Image.new('RGB',(1280,180*math.ceil(len(part)/4)),'#FAF6EE')
 for j,im in enumerate(part):sheet.paste(im,((j%4)*320,(j//4)*180))
 sheet.save(R/f'midpoints-{page//12+1:02}.jpg')
assert sum(s['frames'] for s in P['shots'])==frames_total
originals=[]
for s in M['segments']:
 if s['status']!='complete':continue
 raw=F/s['file'];assert hashlib.sha256(raw.read_bytes()).hexdigest()==s['sha256'];a,sr=sf.read(raw);assert sr==24000 and np.isfinite(a).all();originals.append(s['id'])
flags=[s['id'] for s in M['segments'] if s.get('validation',{}).get('boundary_voice_review_flag')]
report={'full_movie_finished':False,'not_final_episode_validation':True,'originals_saved_and_hash_verified':originals,'remaining':[s['id'] for s in M['segments'] if s['status']!='complete'],'source_status':'Three external claims unverified; none submitted for generation','independent_clips':len(checks),'encoded_frames_screened':frames_total,'all_clip_caps_framecounts_fatal_decode_blackblank':'pass','source_clip_audio':'none: every cached clip video-only','calculation_check':'MATHS OK','processed_subset_seconds':T['duration_of_saved_subset'],'subset_timestamps_are_not_final_episode_times':True,'speech_retiming':False,'silence_padding':False,'local_alignment':'forced alignment only; not independent word verification','voice_boundary_listening_flags':flags,'listening_and_physical_android_test':False,'visual_review':'pending encoded midpoint inspection','clips':checks};(F/'available-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='clips'},indent=2))
