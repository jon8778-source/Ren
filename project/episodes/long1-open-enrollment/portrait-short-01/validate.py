"""Verify the portrait export, exact excerpt PCM and complete decoded frames."""
from pathlib import Path
import json,subprocess as sp,hashlib
import numpy as np,soundfile as sf
D=Path(__file__).resolve().parent;M=json.loads((D/'edit-manifest.json').read_text());V=D/'deliverables/Ren_Health_Plan_Portrait_1min.mp4'
def probe(path):return json.loads(sp.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))
p=probe(V);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],v['nb_read_frames'])==(1080,1920,'24/1','h264','1413')
assert a['codec_name']=='aac' and a['sample_rate']=='48000'
counts={}
for c in M['clips']:
 x=probe(D/'build'/(c['id']+'.mp4'));count=int(x['streams'][0]['nb_read_frames']);assert count==c['frames'];counts[c['id']]=count
assert hashlib.sha256(Path(M['source']).read_bytes()).hexdigest()==M['source_sha256']
original=np.memmap(D/'build/source-audio.f32',dtype='float32',mode='r');expected=np.concatenate([original[c['source_start_sample']:c['source_end_sample']] for c in M['clips']]);master,sr=sf.read(D/'build/narration.wav',dtype='float32');assert sr==48000 and np.array_equal(master,expected)
encoded=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(V),'-map','0:a:0','-f','f32le','-']),dtype='float32');n=min(len(master),len(encoded));corr=float(np.corrcoef(master[:n],encoded[:n])[0,1]);assert corr>.995
# Full-resolution fatal decoding, then inspect every frame's downsampled luminance.
sp.run(['ffmpeg','-v','error','-xerror','-i',str(V),'-f','null','-'],check=True)
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(V),'-an','-vf','scale=108:192,format=gray','-f','rawvideo','-']);frames=np.frombuffer(raw,dtype='uint8').reshape(-1,192,108);assert len(frames)==1413
assert np.all(frames.std(axis=(1,2))>10) and np.all(frames.mean(axis=(1,2))>10)
captions=json.loads((D/'captions.json').read_text());assert all(c['end']>c['start']>=0 and c['end']<=M['duration_seconds'] for c in captions)
assert all(captions[i]['end']<=captions[i+1]['start']+.001 for i in range(len(captions)-1))
joined=''.join(w['display'] for c in M['clips'] for w in c['words']);assert ''.join(c['text'].replace(' ','') for c in captions)==joined.replace(' ','')
report={'runtime_seconds':float(p['format']['duration']),'video_frames':len(frames),'resolution':[1080,1920],'fps':24,'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'clip_frames':counts,'source_sha256_unchanged':M['source_sha256'],'output_sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'source_pcm_selection_exact':True,'master_audio_duration_seconds':len(master)/sr,'encoded_audio_correlation':corr,'encoded_audio_peak_dbfs':float(20*np.log10(max(abs(encoded)))),'full_fatal_decode_passed':True,'all_frames_nonblank':True,'caption_count':len(captions),'hf_generation_calls':0,'new_gpu_allowance_used':0,'speed_change':False,'audio_listened':False,'physical_android_test':False}
(D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
