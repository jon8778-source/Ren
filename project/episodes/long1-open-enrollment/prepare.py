"""Assemble saved Qwen originals without tempo changes; derive timing locally."""
from pathlib import Path
import sys,json,math,re,subprocess as sp,hashlib
import numpy as np,soundfile as sf
from pocketsphinx import Decoder
B=Path(__file__).resolve().parent;ROOT=B.parents[2];sys.path.insert(0,str(ROOT/'project/cliplib'));import pilot
pilot.script_segments=lambda folder:json.loads((folder/'segments.json').read_text())
# qwen_voice's SDK import is only for existing pilot validation, never called here.
def main():
 m=pilot.load(B);assert all(s['status']=='complete' for s in m['segments'])
 chunks=[];times=[];words=[];cursor=0
 for s in m['segments']:
  path,check=pilot.process_segment(B,s);a,sr=sf.read(path);assert sr==48000 and np.isfinite(a).all();start=cursor/48000
  raw=sp.check_output(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar','16000','-f','s16le','-'])
  target=' '.join(re.findall(r"[a-z]+(?:'[a-z]+)?",s['text'].lower().replace('’',"'")));d=Decoder(samprate=16000,loglevel='ERROR')
  for w in set(target.split()):
   if not d.lookup_word(w):
    if w=='ren':d.add_word('ren','R EH N',False)
    else:raise ValueError('Alignment dictionary missing '+w)
  d.set_align_text(target);d.start_utt();d.process_raw(raw,False,True);d.end_utt()
  aligned=[{'word':re.sub(r'\(\d+\)$','',w.word),'start':start+w.start_frame/100,'end':min(start+len(a)/sr,start+(w.end_frame+1)/100),'segment':s['id']} for w in d.seg() if not w.word.startswith('<')]
  assert [x['word'] for x in aligned]==target.split();words.extend(aligned)
  times.append({'id':s['id'],'start':start,'end':start+len(a)/sr,'file':s['file'],'original_sha256':s['sha256'],'text':s['text'],'processed':str(path.relative_to(B)),'validation':check});chunks.append(a);cursor+=len(a)
 master=np.concatenate(chunks);duration=len(master)/48000;assert 55<duration<66
 sf.write(B/'deliverables/narration.wav',master,48000,subtype='PCM_24');frames=math.ceil(duration*24)
 (B/'audio-timing.json').write_text(json.dumps({'duration':duration,'frames':frames,'fps':24,'segments':times,'words':words,'alignment':'Local CPU forced alignment, not independent listening/transcription','no_speed_changes':True,'no_silence_padding':True,'narration_sha256':hashlib.sha256((B/'deliverables/narration.wav').read_bytes()).hexdigest()},indent=2)+'\n')
 (B/'pilot-narration.txt').write_text('\n\n'.join(s['text'] for s in m['segments'])+'\n');print({'duration':duration,'frames':frames,'words':len(words)})
if __name__=='__main__':main()
