"""Prepare full natural-rate narration only when every source/audio gate passes."""
from pathlib import Path
import sys,json,re,math,subprocess as sp,hashlib
import numpy as np,soundfile as sf
from pocketsphinx import Decoder
F=Path(__file__).resolve().parent;ROOT=F.parents[3];sys.path.insert(0,str(ROOT/'project/cliplib'));import pilot
pilot.script_segments=lambda folder:json.loads((folder/'segments.json').read_text())
def main():
 m=pilot.load(F);remaining=[s['id'] for s in m['segments'] if s['status']!='complete']
 available='--available' in sys.argv
 if remaining and not available:raise ValueError('Full narration incomplete; no silent gaps/partial film: '+', '.join(remaining))
 checks=json.loads((F/'source-checks.json').read_text());assert all(checks[s['source_gate']]['status']=='verified' for s in m['segments'] if s.get('source_gate') and s['status']=='complete')
 chunks=[];times=[];words=[];cursor=0
 for s in m['segments']:
  if s['status']!='complete':continue
  path,check=pilot.process_segment(F,s);a,sr=sf.read(path);assert sr==48000 and np.isfinite(a).all();start=cursor/sr
  raw=sp.check_output(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar','16000','-f','s16le','-'])
  target=' '.join(re.findall(r"[a-z]+(?:'[a-z]+)?",s['text'].lower().replace('’',"'")));d=Decoder(samprate=16000,loglevel='ERROR')
  lexicon={"example's":'IH G Z AE M P AH L Z','priya':'P R IY AH','ren':'R EH N','ppo':'P IY P IY OW','hsa':'EY CH EH S EY','copays':'K OW P EY Z','healthcare':'HH EH L TH K EH R','hdhp':'EY CH D IY EY CH P IY','healthcare.gov':'HH EH L TH K EH R D AA T G AA V'}
  for w in set(target.split()):
   if not d.lookup_word(w):
    if w not in lexicon:raise ValueError('Alignment lexicon needs review: '+w)
    d.add_word(w,lexicon[w],False)
  # 250ms decoder-only context flushes final phonemes; it never enters exported audio.
  d.set_align_text(target);d.start_utt();d.process_raw(raw+bytes(8000),False,True);d.end_utt()
  aligned=[{'word':re.sub(r'\(\d+\)$','',w.word),'start':start+w.start_frame/100,'end':min(start+len(a)/sr,start+(w.end_frame+1)/100),'segment':s['id']} for w in d.seg() if not w.word.startswith('<')];assert [w['word'] for w in aligned]==target.split()
  assert all(w['start']<start+len(a)/sr and w['end']>w['start'] for w in aligned),s['id']+' word outside original waveform'
  original_tokens=list(re.finditer(r"[a-z]+(?:['’][a-z]+)?",s['text'],re.I));assert len(original_tokens)==len(aligned)
  boundaries=[]
  for token in original_tokens:
   offset=token.start()
   while offset>0 and s['text'][offset-1] in ['“','‘','\"']:offset-=1
   boundaries.append(offset)
  for i,w in enumerate(aligned):
   end=boundaries[i+1] if i+1<len(boundaries) else len(s['text']);w['display']=s['text'][boundaries[i]:end]
  words.extend(aligned)
  times.append({'id':s['id'],'scene':s['scene'],'start':start,'end':start+len(a)/sr,'file':s['file'],'original_sha256':s['sha256'],'processed':str(path.relative_to(F)),'text':s['text'],'validation':check});chunks.append(a);cursor+=len(a)
 total=cursor/48000
 if available:
  pilot.save(F/'available-timing.json',{'duration_of_saved_subset':total,'frames':math.ceil(total*24),'segments':times,'words':words,'remaining':remaining,'not_episode_timing':True,'note':'Subset coordinates are only for validating independent segment renders. No partial narration/video assembled.'})
  print(json.dumps({'validated_segments':len(times),'saved_subset_seconds':total,'remaining':remaining,'full_track_created':False}));return
 if total>480:raise ValueError(f'Natural narration {total:.2f}s exceeds eight minutes; propose script trim, do not accelerate')
 sf.write(F/'deliverables/narration.wav',np.concatenate(chunks),48000,subtype='PCM_24')
 pilot.save(F/'audio-timing.json',{'duration':total,'frames':math.ceil(total*24),'fps':24,'segments':times,'words':words,'alignment':'Local forced alignment, not independent transcription/listening','no_speed_changes':True,'no_silence_padding':True})
 (F/'narration.txt').write_text('\n\n'.join(s['text'] for s in m['segments'])+'\n')
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 units=[]
 for w in words:
  if units and w['segment']==units[-1][-1]['segment'] and not units[-1][-1]['display'][-1:].isspace():units[-1].append(w)
  else:units.append([w])
 captions=[];line=[]
 for unit in units:
  if line and (unit[0]['segment']!=line[-1]['segment'] or len(''.join(x['display'] for x in line+unit).strip())>44 or unit[-1]['end']-line[0]['start']>3.5):
   captions.append(line);line=[]
  line.extend(unit)
 if line:captions.append(line)
 assert ' '.join(''.join(x['display'] for x in c).strip() for c in captions)==' '.join(s['text'] for s in m['segments'])
 (F/'deliverables/captions.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c[0]['start'])} --> {stamp(c[-1]['end'])}\n"+''.join(x['display'] for x in c).strip() for i,c in enumerate(captions))+'\n')
 print(json.dumps({'narration_seconds':total,'frames':math.ceil(total*24),'segments':len(times),'captions':'forced-aligned, review punctuation/accuracy'}))
if __name__=='__main__':
 try:main()
 except Exception as e:raise SystemExit(pilot.safe_error(e))
