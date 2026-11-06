"""Prototype QA, including fatal decode, native samples and fixed arithmetic."""
from pathlib import Path
import json,subprocess as sp,hashlib,math,sys
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;ROOT=B.parents[2];F=B/'deliverables/Ren_Short_01_Open_Enrollment_Prototype.mp4';A=json.loads((B/'assumptions.json').read_text());M=json.loads((B/'shot-manifest.json').read_text());assert A['comparison_a']-A['comparison_b']==1980
info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(F)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],a['codec_name'])==(1080,1920,'24/1','h264','aac');assert int(v['nb_frames'])==360;assert abs(float(info['format']['duration'])-15)<.02
sp.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(F),'-f','null','-'],check=True)
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(F),'-vf','scale=90:160','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,160,90);assert len(frames)==360 and (frames.mean((1,2))>10).all() and (frames.std((1,2))>5).all()
master,sr=sf.read(B/'audio/prototype-mix.wav');assert sr==48000 and len(master)==720000 and np.isfinite(master).all() and np.max(np.abs(master))<1
encoded=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-i',str(F),'-map','0:a:0','-ar','48000','-f','f32le','-']),np.float32);n=min(len(encoded),len(master));corr=float(np.corrcoef(encoded[:n],master[:n])[0,1]);assert corr>.99
measure=sp.run(['ffmpeg','-v','info','-i',str(F),'-af','loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;stats=json.loads(measure[measure.rindex('{'):measure.rindex('}')+1]);assert float(stats['input_tp'])<-.8
# Financial/disclaimer pixels must stay fixed throughout their encoded scenes.
for name,crop,start,dur in [('comparison','crop=900:720:70:500',7.15,3.1),('disclaimer','crop=900:130:70:1510',10.35,4.6)]:
 raw=sp.check_output(['ffmpeg','-v','error','-xerror','-ss',str(start),'-i',str(F),'-t',str(dur),'-vf',crop+',scale=180:144,format=gray','-f','rawvideo','-']);x=np.frombuffer(raw,np.uint8).reshape(-1,144,180).astype(float)
 assert np.mean(np.abs(x-x[0]),axis=(1,2)).max()<2,(name,'unstable encoded static labels')
folder=B/'build/review';folder.mkdir(exist_ok=True)
sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(F),'-vf','fps=2,scale=270:480','-fps_mode','passthrough',str(folder/'frame-%03d.jpg')],check=True)
files=sorted(folder.glob('frame-*.jpg'))
for page in range(0,len(files),12):
 part=files[page:page+12];sheet=Image.new('RGB',(1080,480*math.ceil(len(part)/4)))
 for j,p in enumerate(part):
  im=Image.open(p).copy();ImageDraw.Draw(im).text((4,4),f'{(page+j)*.5+.25:.2f}s',fill='red');sheet.paste(im,((j%4)*270,(j//4)*480))
 sheet.save(folder/f'contact-{page//12+1}.jpg')
for j,t in enumerate([.8,3.7,8.6,11,14.5]):sp.run(['ffmpeg','-v','error','-xerror','-y','-ss',str(t),'-i',str(F),'-frames:v','1',str(folder/f'native-{j}.png')],check=True)
scenes=[]
for s in M['scenes']:
 d=dict(s);d['start_frame']=math.ceil(s['start']*24-1e-7);d['end_frame']=math.ceil(s['end']*24-1e-7);d['frames']=d['end_frame']-d['start_frame'];scenes.append(d)
assert sum(s['frames'] for s in scenes)==360
r={'file':F.name,'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'bytes':F.stat().st_size,'prototype_only':True,'approval':'Explicit owner approval still required; no final production render exists','duration':float(info['format']['duration']),'frames':360,'resolution':[1080,1920],'fps':24,'codecs':['h264','aac'],'fatal_full_decode':'pass','blank_black_screening_frames':360,'scene_frame_coverage':scenes,'audio_correlation':corr,'loudness_lufs':float(stats['input_i']),'true_peak_dbfs':float(stats['input_tp']),'financial_calculation':f"{A['comparison_a']} - {A['comparison_b']} = 1980",'figures_illustrative':True,'guaranteed_savings_claim':False,'disclaimer':A['disclaimer'],'disclaimer_visible_seconds':15-10.3,'financial_and_disclaimer_encoded_pixels':'stable','narration_original_duration':json.loads((B/'audio/voice-result.json').read_text())['duration'],'US_voice':'Kokoro-82M am_michael, en-us, native rate 1.0; intentional change from British Qwen','music':'Original procedural composition, no external samples','new_hf_generation_requests':0,'paid_compute':False,'visual_review':'pending encoded samples','listening_full_playback':False,'physical_android_test':False,'main_modified':False,'youtube_publication':False}
(B/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='scene_frame_coverage'},indent=2))
