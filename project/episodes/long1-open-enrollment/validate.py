"""Validate real encoded pilot, voice coverage and every shot's frame count."""
from pathlib import Path
import json,subprocess as sp,hashlib,math
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;F=B/'deliverables/Ren_Long_01_Open_Enrollment_60s_Pilot.mp4';T=json.loads((B/'audio-timing.json').read_text());M=json.loads((B/'manifest.json').read_text());P=json.loads((B/'shot-manifest.json').read_text());S=P['shots'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(F)]));v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],a['codec_name'])==(1280,720,'24/1','h264','aac');assert int(v['nb_frames'])==T['frames'];assert abs(float(info['format']['duration'])-T['frames']/24)<.01
cursor=0
for s in S:
 q=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(B/'build'/(s['id']+'.mp4'))]));assert len(q['streams'])==1 and int(q['streams'][0]['nb_frames'])==s['frames'];assert s['start_frame']==cursor;cursor+=s['frames'];assert s['end_frame']==cursor and s['frames']<=(132 if s['kind']=='ren' else 84)
assert cursor==T['frames']
assert M['settings']['model']=='Qwen/Qwen3-TTS-12Hz-1.7B-Base' and M['settings']['use_xvector_only'] is True
assert len(M['segments'])==3 and all(x['status']=='complete' for x in M['segments'])
chunks=[]
for s,t in zip(M['segments'],T['segments']):
 assert sha(B/s['file'])==s['sha256'];assert s['settings']==M['settings'];assert len(s['attempts'])==1
 x,sr=sf.read(B/t['processed']);assert sr==48000;chunks.append(x)
master,sr=sf.read(B/'deliverables/narration.wav');assert sr==48000 and np.isfinite(master).all() and np.max(np.abs(master))<1;assert np.array_equal(np.concatenate(chunks),master)
full=' '.join(x['text'] for x in json.loads((B/'episode-script.json').read_text()));pilot=' '.join(x['text'] for x in M['segments']);assert full.startswith(pilot),'Pilot must be a continuous prefix, not an abridged full-story edit'
assert len(T['words'])==sum(len(x['text'].replace('’',"'").replace('-',' ').split()) for x in M['segments'])
sp.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(F),'-f','null','-'],check=True)
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(F),'-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,90,160);assert len(frames)==T['frames'] and (frames.mean((1,2))>10).all() and (frames.std((1,2))>5).all()
encoded=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-i',str(F),'-map','0:a:0','-ar','48000','-f','f32le','-']),np.float32);n=min(len(master),len(encoded));corr=float(np.corrcoef(master[:n],encoded[:n])[0,1]);assert corr>.99
log=sp.run(['ffmpeg','-v','info','-i',str(F),'-af','loudnorm=I=-18:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;stats=json.loads(log[log.rindex('{'):log.rindex('}')+1]);assert float(stats['input_tp'])<-.7
# All fixed financial displays remain fixed in every applicable encoded frame.
count=0
for s in S:
 roi={'potential':'crop=420:145:760:245','audit':'crop=760:120:265:430','premium':'crop=540:125:675:225'}.get(s['motif'])
 if roi:
  raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(B/'build'/(s['id']+'.mp4')),'-vf',roi+',scale=180:90,format=gray','-f','rawvideo','-']);x=np.frombuffer(raw,np.uint8).reshape(-1,90,180).astype(float);assert np.max(np.mean(np.abs(x-x[0]),axis=(1,2)))<2.0,(s['id'],'financial label changed');count+=len(x)
R=B/'build/review';R.mkdir(exist_ok=True);mids=[s['start_frame']+s['frames']//2 for s in S];cuts=sorted(set(max(0,min(T['frames']-1,s['start_frame']+offset)) for s in S[1:] for offset in [-2,-1,0,1,2]));chosen=sorted(set(mids+cuts))
def expr(values):
 if len(values)==1:return f'eq(n,{values[0]})'
 mid=len(values)//2;return '('+expr(values[:mid])+')+('+expr(values[mid:])+')'
sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(F),'-vf',f"select='{expr(chosen)}',scale=640:360",'-fps_mode','passthrough',str(R/'extract-%03d.jpg')],check=True)
for f,p in zip(chosen,sorted(R.glob('extract-*.jpg'))):p.replace(R/f'frame-{f:05d}.jpg')
for kind,indices,perpage in [('midpoints',mids,20),('transitions',cuts,30)]:
 for page in range(0,len(indices),perpage):
  part=indices[page:page+perpage];im=Image.new('RGB',(1600,180*math.ceil(len(part)/5)),'#FAF6EE')
  for j,f in enumerate(part):
   a=Image.open(R/f'frame-{f:05d}.jpg').resize((320,180));ImageDraw.Draw(a).text((3,3),f'frame {f}',fill='black',stroke_fill='white',stroke_width=2);im.paste(a,((j%5)*320,(j//5)*180))
  im.save(R/f'{kind}-{page//perpage+1}.jpg')
for j,s in enumerate([S[0],next(s for s in S if s['motif']=='audit'),S[-1]]):
 f=s['start_frame']+s['frames']//2;sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(F),'-vf',f"select='eq(n,{f})'",'-frames:v','1',str(R/f'native-{j}.png')],check=True)
attempts=[a for s in M['segments'] for a in s['attempts']]
r={'file':F.name,'bytes':F.stat().st_size,'sha256':sha(F),'pilot_only':True,'duration_seconds':float(info['format']['duration']),'narration_seconds':T['duration'],'resolution':[1280,720],'fps':24,'frames':T['frames'],'shots':len(S),'all_encoded_shot_frame_counts':'pass','shot_caps':'Ren <=5.5s; animated graphics <=3.5s; no story stills','codecs':['h264','aac'],'full_fatal_decode':'pass','blank_black_screening_frames':len(frames),'original_wavs_verified':3,'all_processed_source_samples_in_sequence':True,'continuous_script_prefix':True,'forced_aligned_word_coverage':len(T['words']),'source_clip_audio':'discarded; each shot video-only; final maps narration only','music':False,'audio_correlation':corr,'loudness_lufs':float(stats['input_i']),'true_peak_dbfs':float(stats['input_tp']),'fixed_financial_encoded_frames':count,'calculation_check':'MATHS OK; shared assumptions/calculation-results.json','generation_calls':len(attempts),'allowance_gpu_seconds':sum(x.get('observed_quota_decrease_gpu_seconds') or 0 for x in attempts),'request_elapsed_seconds':sum(x['elapsed_seconds'] for x in attempts),'overquota_used':M['quota']['overquota_used'],'last_quota':M['quota'],'voice_settings':M['settings'],'native_actor_decode':[1280,720],'single_composition_resize':.9,'framing':'Ren left, steady full-body; fitted content right; no mirroring','visual_review':'pending encoded evidence','independent_primary_source_verification':'Not completed for later 2027 claims; none voiced in this pilot','listening_and_physical_android_playback':False,'approval':'Stop for explicit pilot approval. No full episode or Shorts generated.','main_modified':False,'github_video_upload':False}
(B/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['voice_settings','last_quota']},indent=2))
