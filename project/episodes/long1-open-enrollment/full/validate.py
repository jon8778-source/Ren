"""Full-film validation; separate from historical pilot results."""
from pathlib import Path
import json,subprocess as sp,hashlib,math,sys
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
F=Path(__file__).resolve().parent;sys.path.insert(0,str(F.parent));from calculations import calculate
V=F/'deliverables/Ren_Long_01_Auto_Renewed_My_Health_Plan.mp4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 calculate();M=json.loads((F/'manifest.json').read_text());S=json.loads((F/'shot-manifest.json').read_text());T=json.loads((F/'audio-timing.json').read_text());checks=json.loads((F/'source-checks.json').read_text());assert all(s['status']=='complete' for s in M['segments']);assert all(checks[s['source_gate']]['status']=='verified' for s in M['segments'] if s.get('source_gate'))
 approved=json.loads((F/'wording-approval.json').read_text());assert all(s['sha256']==approved['completed_audio_reused'][s['id']] for s in M['segments'] if s['id'] in approved['completed_audio_reused']);assert all(next(s for s in M['segments'] if s['id']==sid)['text']==text for sid,text in approved['approved_changes'].items())
 info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]));v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],a['codec_name'])==(1280,720,'24/1','h264','aac');assert int(v['nb_frames'])==S['frames'] and float(info['format']['duration'])<=480
 cursor=0
 for s in S['shots']:
  path=Path(s['source_file']) if s.get('approved_opening') else F/s['cache_file'];q=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]));assert len(q['streams'])==1 and int(q['streams'][0]['nb_frames'])==s['frames'];assert s['start_frame']==cursor and s['frames']<=(132 if s['kind']=='ren' else 84);cursor=s['end_frame']
 assert cursor==S['frames'];chunks=[]
 for s,t in zip(M['segments'],T['segments']):
  assert sha(F/s['file'])==s['sha256'] and s['settings']==M['settings'];assert len(s['attempts'])==1
  x,sr=sf.read(F/t['processed']);assert sr==48000;chunks.append(x)
 master,sr=sf.read(F/'deliverables/narration.wav');assert sr==48000 and np.array_equal(master,np.concatenate(chunks));assert sha(F.parent/'deliverables/narration.wav')=='9b77f07fafb36dde17357806d8a85ebdacf2041e91afce4c617d070110e61ac1';assert np.array_equal(master[:len(chunks[0])+len(chunks[1])+len(chunks[2])],np.concatenate(chunks[:3]))
 sp.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(V),'-f','null','-'],check=True)
 raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(V),'-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-']);allframes=np.frombuffer(raw,np.uint8).reshape(-1,90,160);assert len(allframes)==S['frames'] and (allframes.mean((1,2))>10).all() and (allframes.std((1,2))>5).all()
 enc=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-i',str(V),'-map','0:a:0','-ar','48000','-f','f32le','-']),np.float32);n=min(len(master),len(enc));corr=float(np.corrcoef(master[:n],enc[:n])[0,1]);assert corr>.99
 log=sp.run(['ffmpeg','-v','info','-i',str(V),'-af','loudnorm=I=-18:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;stats=json.loads(log[log.rindex('{'):log.rindex('}')+1]);assert float(stats['input_tp'])<-.7
 financial_rois={'annual':'crop=490:150:700:245','ppo_premium':'crop=1000:100:130:620','hdhp_premium':'crop=1000:100:130:620','ppo_bad':'crop=1000:100:130:620','hdhp_bad':'crop=1000:100:130:620','ppo_normal':'crop=1000:100:130:620','hdhp_cash':'crop=1000:100:130:620','hdhp_net':'crop=1000:100:130:620','bad_compare':'crop=1020:60:130:550','normal_compare':'crop=1020:60:130:550','contributions':'crop=500:130:390:420','withdrawal':'crop=400:145:190:320','outside_cash':'crop=400:145:190:320'};fixed=0
 for s in S['shots']:
  if s['motif'] not in financial_rois:continue
  path=Path(s['source_file']) if s.get('approved_opening') else F/s['cache_file'];roi=financial_rois[s['motif']];raw=sp.check_output(['ffmpeg','-v','error','-i',str(path),'-vf',roi+',scale=180:90,format=gray','-f','rawvideo','-']);x=np.frombuffer(raw,np.uint8).reshape(-1,90,180).astype(float);assert np.max(np.mean(np.abs(x-x[0]),axis=(1,2)))<2,(s['id'],'financial region changed');fixed+=len(x)
 R=F/'build/review';R.mkdir(exist_ok=True);mids=[s['start_frame']+s['frames']//2 for s in S['shots']];motion=sorted(set(max(0,min(S['frames']-1,s['start_frame']+o)) for s in S['shots'][1:] for o in [-2,-1,0,1,2]));chosen=sorted(set(mids+motion))
 def expr(vals):
  if len(vals)==1:return f'eq(n,{vals[0]})'
  k=len(vals)//2;return '('+expr(vals[:k])+')+('+expr(vals[k:])+')'
 sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(V),'-vf',f"select='{expr(chosen)}',scale=640:360",'-fps_mode','passthrough',str(R/'extract-%04d.jpg')],check=True)
 for i,p in zip(chosen,sorted(R.glob('extract-*.jpg'))):p.replace(R/f'frame-{i:06}.jpg')
 for kind,indices,perpage in [('midpoints',mids,12),('transitions',motion,30)]:
  for page in range(0,len(indices),perpage):
   part=indices[page:page+perpage];cols=4 if kind=='midpoints' else 5;im=Image.new('RGB',(cols*320,180*math.ceil(len(part)/cols)),'#FAF6EE')
   for j,i in enumerate(part):
    a=Image.open(R/f'frame-{i:06}.jpg').resize((320,180));ImageDraw.Draw(a).text((4,4),f'frame {i}',fill='black',stroke_fill='white',stroke_width=2);im.paste(a,((j%cols)*320,(j//cols)*180))
   im.save(R/f'{kind}-{page//perpage+1:02}.jpg')
 report={'file':V.name,'sha256':sha(V),'bytes':V.stat().st_size,'full_episode':True,'duration_seconds':float(info['format']['duration']),'narration_seconds':T['duration'],'resolution':[1280,720],'fps':24,'frames':S['frames'],'shots':len(S['shots']),'all_shot_frame_counts':'pass','shot_caps':'Ren<=5.5, graphics<=3.5','fatal_full_decode':'pass','all_frame_black_blank_screen':len(allframes),'narration_originals':len(M['segments']),'exact_sample_sequence':'pass','source_animation_audio':'discarded','music':False,'audio_correlation':corr,'loudness_lufs':float(stats['input_i']),'true_peak_dbfs':float(stats['input_tp']),'fixed_financial_frames':fixed,'calculations':'MATHS OK','source_checks':'source-checks.json','closed_mouth':'Approved narrator-led source clips; inspect evidence','visual_review':'pending actual encoded inspection','listening_and_physical_android_test':False,'publication':False,'github_video_upload':False};(F/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
