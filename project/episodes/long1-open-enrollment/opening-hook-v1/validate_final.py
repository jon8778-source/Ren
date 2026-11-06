"""Verify exact video preservation and sample-accurate audio inputs after targeted assembly."""
from pathlib import Path
import json,hashlib,subprocess as sp,math
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;S=json.loads((H/'source.json').read_text());B=json.loads((H/'final-build.json').read_text());V=H/'deliverables'/B['file'];original=Path(S['actual_path']);P=H/'deliverables/Ren_Health_Plan_Opening_Preview.mp4';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def probe(path):return json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def packets(path,stream):return sorted(json.loads(sp.check_output(['ffprobe','-v','error','-select_streams',stream,'-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,data_hash','-of','json',str(path)]))['packets'],key=lambda p:float(p['pts_time']))
def framehash(path,dest,select=None,count=None):
 cmd=['ffmpeg','-v','error','-xerror','-err_detect','explode','-y','-i',str(path),'-map','0:v:0','-an']
 if select:cmd+=['-vf',select]
 if count:cmd+=['-frames:v',str(count)]
 cmd+=['-fps_mode','passthrough','-f','framemd5',str(dest)];sp.run(cmd,check=True)
 return [s.split(',')[-1].strip() for s in dest.read_text().splitlines() if s and not s.startswith('#')]
def corr(a,b):
 n=min(len(a),len(b));s0=s1=q0=q1=c=0.
 for i in range(0,n,96000):
  x=a[i:i+min(96000,n-i)].astype(np.float64);y=b[i:i+min(96000,n-i)].astype(np.float64);s0+=x.sum();s1+=y.sum();q0+=np.dot(x,x);q1+=np.dot(y,y);c+=np.dot(x,y)
 return float((c-s0*s1/n)/math.sqrt((q0-s0*s0/n)*(q1-s1*s1/n)))
assert sha(original)==S['sha256'] and sha(V)==B['sha256'];info=probe(V);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],v['pix_fmt'],a['codec_name'],a['sample_rate'],a['channels'])==(1280,720,'24/1','h264','yuv420p','aac','48000',1);assert int(v['nb_frames'])==B['total_frames']
old=packets(original,'v:0');new=packets(V,'v:0');preview=packets(P,'v:0');N=B['hook_frames'];assert len(new)==len(preview[:N])+len(old[S['cut_frame']:])==B['total_frames'];assert [p['data_hash'] for p in new[:N]]==[p['data_hash'] for p in preview[:N]];assert [p['data_hash'] for p in new[N:]]==[p['data_hash'] for p in old[S['cut_frame']:]];assert max(abs(float(p['pts_time'])-i/24) for i,p in enumerate(new))<1e-6
new_frames=framehash(V,H/'build/final-frames.md5');old_frames=framehash(original,H/'build/source-retained-frames.md5',f"select='gte(n,{S['cut_frame']})'",B['retained_source_frames']);hook_frames=framehash(P,H/'build/approved-hook-frames.md5',count=N);assert new_frames[:N]==hook_frames and new_frames[N:]==old_frames
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(V),'-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-']);f=np.frombuffer(raw,np.uint8).reshape(-1,90,160);assert len(f)==B['total_frames'] and (f.mean((1,2))>10).all() and (f.std((1,2))>5).all()
final_audio=H/'build/final-decoded-audio.f32';sp.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-y','-i',str(V),'-map','0:a:0','-f','f32le',str(final_audio)],check=True);encoded=np.fromfile(final_audio,np.float32);master,sr=sf.read(H/'build/final-joined-audio.wav',dtype='float32');source_pcm=np.fromfile(H/'build/original-source-audio.f32',np.float32);voice,_=sf.read(next((H/'processed').glob('hook001-*.wav')),dtype='float32');assert np.array_equal(master[len(voice):],source_pcm[S['cut_audio_sample_48k']:]);assert np.array_equal(master[:len(voice)],voice)
overall=corr(master,encoded);body_corr=corr(source_pcm[S['cut_audio_sample_48k']:],encoded[len(voice):]);assert overall>.99 and body_corr>.99
preview_audio=packets(P,'a:0');new_audio=packets(V,'a:0');approved_audio_match=all(x['data_hash']==y['data_hash'] for x,y in zip(preview_audio[:1000],new_audio[:1000]))
log=sp.run(['ffmpeg','-v','info','-i',str(V),'-af','loudnorm=I=-18:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;loud=json.loads(log[log.rindex('{'):log.rindex('}')+1]);assert float(loud['input_tp'])<-.7
# Only unchanged pictures are reused: fixed labels/math from the source and approved preview.
import sys
sys.path.insert(0,str(H.parent));from calculations import calculate
A,C=calculate();assert (C['ppo_annual_premium'],C['hdhp_annual_premium'])==(2520,840)
review=H/'build/final-review';review.mkdir(exist_ok=True);pick=[0,72,288,N-6,N-2,N-1,N,N+1,N+2,N+6,N+24,N+65,N+129,B['total_frames']-48,B['total_frames']-1];expr='+'.join(f'eq(n,{i})' for i in pick)
sp.run(['ffmpeg','-v','error','-y','-i',str(V),'-vf',f"select='{expr}',scale=640:360",'-fps_mode','passthrough',str(review/'frame-%02d.jpg')],check=True)
images=sorted(review.glob('frame-*.jpg'));sheet=Image.new('RGB',(1280,180*math.ceil(len(images)/4)),'#FAF6EE')
for j,path in enumerate(images):
 im=Image.open(path).resize((320,180));ImageDraw.Draw(im).text((3,3),f'frame{pick[j]} {pick[j]/24:.3f}s',fill='black',stroke_fill='white',stroke_width=2);sheet.paste(im,((j%4)*320,(j//4)*180))
sheet.save(review/'join-ending-contact.jpg')
report={'file':V.name,'sha256':sha(V),'bytes':V.stat().st_size,'duration_seconds':float(info['format']['duration']),'video_seconds':B['total_frames']/24,'resolution':[1280,720],'fps':24,'video_codec':v['codec_name'],'video_profile':v.get('profile'),'audio_codec':a['codec_name'],'audio_profile':a.get('profile'),'frames':B['total_frames'],'original_source_unmodified':sha(original)==S['sha256'],'source_replacement_range_seconds':[0,S['cut_seconds']],'new_hook_video_seconds':N/24,'retained_video_frames':B['retained_source_frames'],'retained_video_packets_exact':True,'retained_decoded_frames_exact':True,'approved_hook_packets_and_frames_exact':True,'every_frame_timestamp_continuous':True,'all_frame_black_blank_screen':len(f),'full_video_audio_fatal_decode':'pass','remainder_audio_PCM_identical_before_encode':True,'audio_reencoded':'Complete joined track once, AAC-LC192k48kmono. Original input audio content/level/timing preserved; compressed AAC output is not byte-identical.','copy_splice_failure':'AAC concat failed with non-monotonic DTS; standard sample-accurate AAC encoding used, no error suppression.','overall_audio_correlation':overall,'body_audio_correlation':body_corr,'first_1000_AAC_packets_match_approved_preview':approved_audio_match,'loudness_lufs':float(loud['input_i']),'true_peak_dbfs':float(loud['input_tp']),'boundary_AV_rounding_ms':B['audio_video_boundary_rounding_ms'],'financial_figures':'2520/year and840/year unchanged; shared calculations pass; rest pixel-identical','new_HF_requests':0,'new_scene_or_artwork_rendering':False,'visual_final_join_review':'pending sampled review','listening_and_physical_android_test':False,'original_ending_preserved':True,'github_upload':False,'publication':False};(H/'final-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
