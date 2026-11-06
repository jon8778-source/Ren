"""Measured phrase edits for reading time; no speech retiming or new generation."""
from pathlib import Path
import json,subprocess as sp,math,importlib.util
import numpy as np,soundfile as sf
B=Path(__file__).resolve().parent;P=B.parent;SR=48000;N=18*SR
M=json.loads((B/'manifest.json').read_text());S=M['segments'][0];assert S['status']=='complete'
ORIGINAL=B/S['file'];OUT=B/'deliverables';OUT.mkdir(exist_ok=True)
sp.run(['ffmpeg','-v','error','-y','-i',str(ORIGINAL),'-af','highpass=f=70,loudnorm=I=-17:TP=-2:LRA=8','-ar',str(SR),str(B/'build/normalized.wav')],check=True)
a,sr=sf.read(B/'build/normalized.wav');assert sr==SR and abs(len(a)/SR-S['validation']['duration_s'])<.001
cuts=[0,2.58,6.74,9.6,len(a)/SR];places=[.4,4.45,10.,14.5];stages=[('email',0,4),('questions',4,9.5),('comparison',9.5,14),('ending',14,18)]
for c in cuts[1:-1]:assert np.sqrt(np.mean(a[round((c-.02)*SR):round((c+.02)*SR)]**2))<.008,'Phrase boundary is not quiet; stop for review'
voice=np.zeros(N);beats=[];recovered=[]
for j,start in enumerate(places):
 x0,x1=round(cuts[j]*SR),round(cuts[j+1]*SR);piece=a[x0:x1];i=round(start*SR);assert i+len(piece)<=N;voice[i:i+len(piece)]=piece;recovered.append(voice[i:i+len(piece)])
 beats.append({'id':stages[j][0],'source_start':x0/SR,'source_end':x1/SR,'output_start':start,'output_end':start+len(piece)/SR,'source_samples':[x0,x1]})
assert np.array_equal(np.concatenate(recovered),a),'Original spoken samples must all be retained in sequence'
words=json.loads((B/'alignment.json').read_text())['words'];timed=[]
for w in words:
 mid=(w['start']+w['end'])/2;beat=next(b for b in beats if b['source_start']<=mid<b['source_end']+.005)
 timed.append({**w,'output_start':max(beat['output_start'],w['start']-beat['source_start']+beat['output_start']),'output_end':min(beat['output_end'],w['end']-beat['source_start']+beat['output_start'])})
spec=importlib.util.spec_from_file_location('original_music',P/'sound.py');music_source=importlib.util.module_from_spec(spec);spec.loader.exec_module(music_source)
music=np.zeros(N);rng=np.random.default_rng(902);beat=60/84;chords=[[48,55,59,64],[45,52,55,60],[50,57,60,65],[43,50,53,59]]
def add(x,z,t):
 i=round(t*SR);n=min(len(z),len(x)-i)
 if n>0:x[i:i+n]+=z[:n]
for k,t in enumerate(np.arange(0,18,beat/2)):
 chord=chords[int(t/(beat*4))%4];add(music,.026*music_source.pluck(chord[k%4]+(12 if k%4 else 0)),t+(.04 if k%2 else 0))
for k,t0 in enumerate(np.arange(0,18,beat)):
 t=np.arange(round(.15*SR))/SR;add(music,.018*np.sin(2*np.pi*(55*t+6*(1-np.exp(-t*25))))*np.exp(-t*40),t0)
 if k%2:add(music,rng.normal(0,.003,round(.035*SR))*np.exp(-np.arange(round(.035*SR))/SR*100),t0)
music*=np.minimum(np.arange(N)/SR/.4,1)*np.minimum((N-np.arange(N))/SR/1.,1)
sfx=np.zeros(N);add(sfx,rng.normal(0,.007,960)*np.exp(-np.arange(960)/SR*170),1.35)
for at in [4.,4.25,4.5]:
 t=np.arange(4800)/SR;add(sfx,.009*np.sin(2*np.pi*(900*t-850*t*t))*np.exp(-t*50),at)
mix=voice+music+sfx;assert np.isfinite(mix).all() and np.max(np.abs(mix))<1
sf.write(B/'build/mix-pre.wav',mix,SR,subtype='PCM_24');sf.write(OUT/'narration-with-reading-pauses.wav',voice,SR,subtype='PCM_24')
sp.run(['ffmpeg','-v','error','-y','-i',str(B/'build/mix-pre.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=8','-ar',str(SR),str(OUT/'mix.wav')],check=True)
plan={'prototype_revision':2,'duration':18,'fps':24,'frames':432,'voice':'Qwen/Qwen3-TTS-12Hz-1.7B-Base, approved Ren reference, English, use_xvector_only=True','original':S['file'],'original_sha256':S['sha256'],'native_voice_seconds':len(a)/SR,'speech_speed_change':False,'all_spoken_samples_preserved':True,'beats':beats,'stages':[{'id':i,'start':s,'end':e} for i,s,e in stages],'editorial_reading_pauses':[beats[j+1]['output_start']-beats[j]['output_end'] for j in range(3)],'pause_reason':'Latest owner feedback asks for slower reading between animation beats. Explicit editorial breathing room under active graphics, not silence used to hide a generation failure.','music_bpm':84,'music_original_procedural':True,'word_timing':timed,'approval':'Revised prototype; stop for owner approval'}
(B/'timing.json').write_text(json.dumps(plan,indent=2)+'\n');print({k:plan[k] for k in ['duration','native_voice_seconds','editorial_reading_pauses','all_spoken_samples_preserved']})
