"""Validate the short preview only; prove unchanged-source video/audio usage."""
from pathlib import Path
import json,subprocess as sp,hashlib,math
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;src=json.loads((H/'source.json').read_text());timing=json.loads((H/'timing.json').read_text());V=H/'deliverables/Ren_Health_Plan_Opening_Preview.mp4';source=Path(src['actual_path']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==src['sha256'];assert json.loads((H/'review-gate.json').read_text())['approved'] is False
info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio');N=timing['hook_frames'];total=N+timing['preview_source_tail_frames'];assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],a['codec_name'])==(1280,720,'24/1','h264','aac');assert int(v['nb_frames'])==total and 20<=float(info['format']['duration'])<=25
sp.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(V),'-f','null','-'],check=True)
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(V),'-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,180,320,3);assert len(frames)==total and (frames.mean((1,2,3))>10).all() and (frames.std((1,2,3))>5).all()
for s in timing['shots']:assert s['frames']<=132
# Exact compressed-packet preservation, not merely similar-looking frames.
def packets(path,window=None):
 cmd=['ffprobe','-v','error','-select_streams','v:0']
 if window:cmd+=['-read_intervals',window]
 cmd+=['-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,data_hash','-of','json',str(path)]
 return json.loads(sp.check_output(cmd))['packets']
old=[p for p in packets(source,'17%27') if src['cut_seconds']-1e-6<=float(p['pts_time'])<src['preview_source_end_seconds']-1e-6]
new=[p for p in packets(V) if float(p['pts_time'])>=N/24-1e-6];old.sort(key=lambda p:float(p['pts_time']));new.sort(key=lambda p:float(p['pts_time']));assert len(old)==len(new)==timing['preview_source_tail_frames'];assert [p['data_hash'] for p in old]==[p['data_hash'] for p in new],'Source video packets changed'
# Compare decoded image hashes independently, including immediately across the join.
def md5s(path,vf):
 data=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-vf',vf,'-an','-fps_mode','passthrough','-frames:v',str(timing['preview_source_tail_frames']),'-f','framemd5','-']).decode()
 return [row.split(',')[-1].strip() for row in data.splitlines() if row and not row.startswith('#')]
source_frames=md5s(source,f"select='between(n,{src['cut_frame']},{src['preview_source_end_frame']-1})'");preview_frames=md5s(V,f"select='gte(n,{N})'");assert source_frames==preview_frames
wave,sr=sf.read(H/'build/preview-audio.wav',dtype='float32');tail,_=sf.read(H/'build/original-preview-tail-audio.wav',dtype='float32');assert sr==48000 and np.array_equal(wave[-len(tail):],tail)
encoded=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-i',str(V),'-map','0:a:0','-ar','48000','-f','f32le','-']),np.float32);count=min(len(wave),len(encoded));corr=float(np.corrcoef(wave[:count],encoded[:count])[0,1]);assert corr>.99;join=len(wave)-len(tail);jump=float(abs(wave[join]-wave[join-1]));assert jump<.04
log=sp.run(['ffmpeg','-v','info','-i',str(V),'-af','loudnorm=I=-18:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;stats=json.loads(log[log.rindex('{'):log.rindex('}')+1]);assert float(stats['input_tp'])<-.7
# Fixed price glyphs end before y268/403; animated bars begin y269/404.
# Check prices independently of those purposeful bar animations.
price_frames=0
for s in timing['shots']:
 if s['motif'] not in ['prices','twist']:continue
 price_frames+=s['frames']
 for y in [207,342]:
  raw=sp.check_output(['ffmpeg','-v','error','-i',str(H/'build'/(s['id']+'.mp4')),'-vf',f'crop=470:61:720:{y},scale=180:60,format=gray','-f','rawvideo','-']);f=np.frombuffer(raw,np.uint8).reshape(-1,60,180).astype(float);assert np.max(np.mean(np.abs(f-f[0]),axis=(1,2)))<2
R=H/'build/review';R.mkdir(exist_ok=True);selected=sorted(set(list(range(0,total,24))+[max(0,min(total-1,N+i)) for i in [-6,-3,-2,-1,0,1,2,3,6,12,24,48]]+[s['start_frame']+s['frames']//2 for s in timing['shots']]))
for page in range(0,len(selected),16):
 part=selected[page:page+16];sheet=Image.new('RGB',(1280,180*math.ceil(len(part)/4)),'#FAF6EE')
 for j,i in enumerate(part):
  im=Image.fromarray(frames[i]);ImageDraw.Draw(im).text((3,3),f'{i/24:.3f}s / frame{i}',fill='black',stroke_fill='white',stroke_width=2);sheet.paste(im,((j%4)*320,(j//4)*180))
 sheet.save(R/f'contact-{page//16+1}.jpg')
for i,s in enumerate(timing['shots']):
 n=s['start_frame']+s['frames']//2;sp.run(['ffmpeg','-v','error','-y','-i',str(V),'-vf',f"select='eq(n,{n})'",'-frames:v','1',str(R/f'native-{i+1}.png')],check=True)
m=json.loads((H/'manifest.json').read_text());attempt=m['segments'][0]['attempts'][0]
report={'file':V.name,'sha256':sha(V),'bytes':V.stat().st_size,'preview_duration_seconds':float(info['format']['duration']),'preview_video_seconds':total/24,'preview_frames':total,'hook_audio_seconds':timing['hook_audio_seconds'],'hook_video_seconds':N/24,'resolution':[1280,720],'fps':24,'codecs':['H.264','AAC-LC'],'source_cut_seconds':src['cut_seconds'],'source_cut_frame':src['cut_frame'],'source_resume_words':src['original_resume_words'],'source_tail_frames':len(new),'source_tail_video_packets_sha256_match':True,'source_tail_decoded_frames_exact_match':True,'source_tail_PCM_samples_before_preview_encode_exact_match':True,'preview_audio_reencoded':'AAC encoding limited to this23.8-second preview; original file never altered. Final full-audio splice not assembled or certified yet.','preview_audio_correlation':corr,'join_sample_jump':jump,'loudness_lufs':float(stats['input_i']),'true_peak_dbfs':float(stats['input_tp']),'all_frame_black_blank_screen':total,'fatal_decode':'pass','price_label_fixed_frames':price_frames,'financial_labels':'$2,520/year and$840/year annual premiums, from existing shared calculations; no savings claim','generation_calls':len(m['segments'][0]['attempts']),'observed_gpu_seconds':attempt.get('observed_quota_decrease_gpu_seconds'),'request_elapsed_seconds':attempt.get('elapsed_seconds'),'original_source_sha256':sha(source),'original_source_unmodified':True,'artwork_generation':False,'full_video_assembled':False,'visual_inspection':'pending encoded review','listening_and_physical_android_playback':False,'approval_required':True}
(H/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
