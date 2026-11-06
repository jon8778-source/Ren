"""Encoded QA and Qwen provenance/pacing checks for revision two."""
from pathlib import Path
import json,hashlib,subprocess as sp,math
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;F=B/'deliverables/Ren_Short_01_Open_Enrollment_Prototype_v2_Qwen.mp4';T=json.loads((B/'timing.json').read_text());M=json.loads((B/'manifest.json').read_text());S=M['segments'][0];A=json.loads((B.parent/'assumptions.json').read_text());assert S['status']=='complete'
assert S['settings']['model']=='Qwen/Qwen3-TTS-12Hz-1.7B-Base' and S['settings']['use_xvector_only'] is True
assert len(S['attempts'])==1 and hashlib.sha256((B/S['file']).read_bytes()).hexdigest()==S['sha256']
info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(F)]));v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],a['codec_name'])==(1080,1920,'24/1','h264','aac');assert int(v['nb_frames'])==432 and abs(float(info['format']['duration'])-18)<.01
sp.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(F),'-f','null','-'],check=True)
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(F),'-vf','scale=90:160','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,160,90);assert len(frames)==432 and (frames.mean((1,2))>10).all() and (frames.std((1,2))>5).all()
master,sr=sf.read(B/'deliverables/mix.wav');assert sr==48000 and len(master)==864000 and np.isfinite(master).all() and np.max(np.abs(master))<1
coded=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-i',str(F),'-map','0:a:0','-ar','48000','-f','f32le','-']),np.float32);n=min(len(coded),len(master));corr=float(np.corrcoef(master[:n],coded[:n])[0,1]);assert corr>.99
normal,_=sf.read(B/'build/normalized.wav');voice,_=sf.read(B/'deliverables/narration-with-reading-pauses.wav');pieces=[]
for b in T['beats']:
 start=round(b['output_start']*sr);n=b['source_samples'][1]-b['source_samples'][0];pieces.append(voice[start:start+n])
assert np.max(np.abs(np.concatenate(pieces)-normal))<2/2**23,'Spoken samples changed; no retiming allowed'
measure=sp.run(['ffmpeg','-v','info','-i',str(F),'-af','loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;stats=json.loads(measure[measure.rindex('{'):measure.rindex('}')+1]);assert float(stats['input_tp'])<-.8
# Exact completed figures stay fixed while bars animate, and disclaimer holds.
for name,roi,start,seconds in [('figures','crop=900:150:80:450',9.55,4.4),('equation','crop=900:95:70:1560',9.55,4.4),('disclaimer','crop=920:105:60:1600',14.05,3.9)]:
 raw=sp.check_output(['ffmpeg','-v','error','-xerror','-ss',str(start),'-i',str(F),'-t',str(seconds),'-vf',roi+',scale=180:90,format=gray','-f','rawvideo','-']);f=np.frombuffer(raw,np.uint8).reshape(-1,90,180).astype(float);assert np.max(np.mean(np.abs(f-f[0]),axis=(1,2)))<2,(name,'encoded labels changed')
assert A['comparison_a']-A['comparison_b']==1980 and A['disclaimer']=='Educational content only, not financial advice.'
scenes=[]
for s in T['stages']:
 x={**s,'start_frame':round(s['start']*24),'end_frame':round(s['end']*24)};x['frames']=x['end_frame']-x['start_frame'];scenes.append(x)
assert sum(x['frames'] for x in scenes)==432 and min(x['end']-x['start'] for x in scenes)>=4
folder=B/'build/review';folder.mkdir(exist_ok=True)
sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(F),'-vf','fps=2,scale=270:480','-fps_mode','passthrough',str(folder/'frame-%03d.jpg')],check=True)
files=sorted(folder.glob('frame-*.jpg'))
for page in range(0,len(files),12):
 part=files[page:page+12];sheet=Image.new('RGB',(1080,480*math.ceil(len(part)/4)))
 for j,p in enumerate(part):
  im=Image.open(p).copy();ImageDraw.Draw(im).text((4,4),f'{(page+j)*.5+.25:.2f}s',fill='red');sheet.paste(im,((j%4)*270,(j//4)*480))
 sheet.save(folder/f'contact-{page//12+1}.jpg')
for j,t in enumerate([2.5,6.5,12,16.5]):sp.run(['ffmpeg','-v','error','-xerror','-y','-ss',str(t),'-i',str(F),'-frames:v','1',str(folder/f'native-{j}.png')],check=True)
r={'file':F.name,'bytes':F.stat().st_size,'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'prototype_only':True,'approval':'Stop for explicit owner approval; no final render/publication','duration':float(info['format']['duration']),'frames':432,'resolution':[1080,1920],'fps':24,'codecs':['h264','aac'],'full_fatal_decode':'pass','black_blank_screening_frames':432,'scenes':scenes,'audio_correlation':corr,'all_normalized_source_spoken_samples_preserved':True,'no_speech_speed_change':True,'editorial_reading_pauses':T['editorial_reading_pauses'],'voice_model':S['settings']['model'],'reference_sha256':S['settings']['reference_sha256'],'transcript_sha256':S['settings']['transcript_sha256'],'language':'English','use_xvector_only':True,'stock_voice_used':False,'generation_calls':1,'measured_quota_gpu_seconds':S['attempts'][0].get('observed_quota_decrease_gpu_seconds'),'request_elapsed_seconds':S['attempts'][0]['elapsed_seconds'],'last_quota':M['quota'],'paid_compute':False,'loudness_lufs':float(stats['input_i']),'true_peak_dbfs':float(stats['input_tp']),'financial_calculation':'2670 - 690 = 1980','illustrative_not_guaranteed':True,'fixed_encoded_financial_regions':'pass','disclaimer':A['disclaimer'],'disclaimer_duration':4,'visual_review':'pending','listening_or_physical_android_test':False,'youtube_or_github_video_upload':False}
(B/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='scenes'},indent=2))
