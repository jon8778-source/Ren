"""Approved targeted assembly: copy every video packet; encode sample-accurate AAC join."""
from pathlib import Path
import json,hashlib,subprocess as sp
import numpy as np,soundfile as sf
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd):sp.run(cmd,check=True)
def main():
 gate=json.loads((H/'review-gate.json').read_text());assert gate['approved'] is True,'Explicit opening-preview approval required'
 preview=H/'deliverables'/gate['preview_file'];assert sha(preview)==gate['preview_sha256'];s=json.loads((H/'source.json').read_text());source=Path(s['actual_path']);assert sha(source)==s['sha256'];T=json.loads((H/'timing.json').read_text())
 tail=H/'build/final-original-tail-video.mp4';remaining=s['original_frame_count']-s['cut_frame'];run(['ffmpeg','-v','error','-xerror','-y','-ss',str(s['cut_seconds']),'-i',str(source),'-map','0:v:0','-frames:v',str(remaining),'-an','-c:v','copy',str(tail)])
 files=[H/'build'/(x['id']+'.mp4') for x in T['shots']]+[tail];concat=H/'build/final-video-concat.txt';concat.write_text('\n'.join("file '%s'"%p for p in files)+'\n')
 decoded=H/'build/original-source-audio.f32'
 if not decoded.exists():run(['ffmpeg','-v','error','-xerror','-y','-i',str(source),'-map','0:a:0','-f','f32le',str(decoded)])
 original=np.fromfile(decoded,np.float32);voicefile=next((H/'processed').glob('hook001-*.wav'));voice,sr=sf.read(voicefile,dtype='float32');assert sr==48000;body=original[s['cut_audio_sample_48k']:];audio=H/'build/final-joined-audio.wav';sf.write(audio,np.concatenate([voice,body]),48000,subtype='FLOAT')
 check,_=sf.read(audio,dtype='float32');assert np.array_equal(check[:len(voice)],voice) and np.array_equal(check[len(voice):],body)
 approved_wave,_=sf.read(H/'build/preview-audio.wav',dtype='float32');assert np.array_equal(check[:len(approved_wave)],approved_wave),'Approved join waveform changed'
 out=H/'deliverables/Ren_Health_Plan_Revised_Opening.mp4';run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-auto_convert','0','-i',str(concat),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)])
 assert sha(source)==s['sha256'];report={'file':out.name,'sha256':sha(out),'bytes':out.stat().st_size,'source_sha256':sha(source),'approved_preview_sha256':sha(preview),'hook_frames':T['hook_frames'],'source_cut_frame':s['cut_frame'],'source_cut_seconds':s['cut_seconds'],'retained_source_frames':remaining,'total_frames':T['hook_frames']+remaining,'new_voice_requests':0,'new_artwork':0,'video_encoding':'None during final assembly: approved hook and all existing remainder packets stream-copied','audio_encoding':'Entire joined track AAC-LC192k/48k/mono encoded once from approved hook PCM plus unchanged decoded original remainder. No gain/filter/speed/content edits to remainder. AAC output is not byte-identical to original.','audio_copy_trial':'Failed with fatal non-monotonic DTS at splice (882688 ->878256); no timestamp-error suppression used','hook_pcm_samples':len(voice),'source_audio_cut_sample':s['cut_audio_sample_48k'],'source_body_pcm_samples':len(body),'joined_pcm_samples':len(check),'approved_join_PCM_identical':True,'remainder_PCM_identical_before_AAC_encode':True,'audio_video_boundary_rounding_ms':(len(voice)/48000-T['hook_frames']/24)*1000,'original_file_unmodified':True,'source_ending_preserved':True};(H/'final-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
