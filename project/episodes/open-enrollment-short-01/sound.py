"""Original sample-free procedural lo-fi bed and restrained UI effects."""
from pathlib import Path
import json,subprocess as sp
import numpy as np,soundfile as sf
B=Path(__file__).resolve().parent;SR=48000;N=15*SR;RNG=np.random.default_rng(912026)
def add(track,a,t):
 i=round(t*SR);n=min(len(a),len(track)-i)
 if n>0:track[i:i+n]+=a[:n]
def pluck(midi,d=1.4):
 t=np.arange(round(d*SR))/SR;f=440*2**((midi-69)/12)
 return (np.sin(2*np.pi*f*t)+.18*np.sin(2*np.pi*2*f*t))*np.exp(-t*3.2)*np.minimum(t/.008,1)
def build():
 sp.run(['ffmpeg','-v','error','-y','-i',str(B/'audio/narration-original.wav'),'-af','highpass=f=70,loudnorm=I=-16:TP=-2:LRA=8','-ar',str(SR),str(B/'build/narration-normalized.wav')],check=True)
 voice,sr=sf.read(B/'build/narration-normalized.wav');assert sr==SR
 speech=np.zeros(N);add(speech,voice,.25)
 music=np.zeros(N);beat=60/90
 chords=[[48,55,59,64],[45,52,55,60],[50,57,60,65],[43,50,53,59]]
 for j,t0 in enumerate(np.arange(0,15,beat/2)):
  chord=chords[int(t0/(beat*4))%4];note=chord[j%4]+(12 if j%4 else 0)
  add(music,.04*pluck(note),t0+(.045 if j%2 else 0))
 for j,t0 in enumerate(np.arange(0,15,beat)):
  t=np.arange(round(.15*SR))/SR
  kick=np.sin(2*np.pi*(55*t+6*(1-np.exp(-t*25))))*np.exp(-t*40)
  add(music,.024*kick,t0)
  if j%2:
   hat=RNG.normal(0,.006,round(.045*SR))*np.exp(-np.arange(round(.045*SR))/SR*95);add(music,hat,t0)
 music*=np.minimum(np.arange(N)/SR/.25,1)*np.minimum((N-np.arange(N))/SR/.8,1)
 effects=np.zeros(N);click=RNG.normal(0,.006,round(.023*SR))*np.exp(-np.arange(round(.023*SR))/SR*180);add(effects,click,.65)
 for at in [2.8,3.03,3.26]:
  t=np.arange(round(.1*SR))/SR;add(effects,.008*np.sin(2*np.pi*(1000*t-1200*t*t))*np.exp(-t*45),at)
 mix=speech+music+effects;assert np.max(np.abs(mix))<1
 for name,a in [('music-original',music),('ui-effects',effects),('narration-timed',speech),('mix-pre',mix)]:sf.write(B/'audio'/f'{name}.wav',a,SR,subtype='PCM_24')
 sp.run(['ffmpeg','-v','error','-y','-i',str(B/'audio/mix-pre.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=8','-ar',str(SR),str(B/'audio/prototype-mix.wav')],check=True)
 (B/'audio/music-rights.json').write_text(json.dumps({'composition':'Original procedural 90 BPM lo-fi plucks and soft percussion','author':'Created for this Ren prototype in sound.py','external_samples':False,'external_melodies':False,'licensed_music_dependency':None,'rng_seed':912026,'voice_lead_seconds':.25,'voice_duration':len(voice)/SR,'voice_end':.25+len(voice)/SR,'music_mixed_under_narration':True,'effects_times':{'click':.65,'card_pop':[2.8,3.03,3.26]}},indent=2)+'\n')
 print('15-second original sound mix saved')
if __name__=='__main__':build()
