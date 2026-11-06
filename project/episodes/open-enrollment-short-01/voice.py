"""Free local US male prototype voice. Original assets never overwritten."""
from pathlib import Path
import json,hashlib,os
import numpy as np,soundfile as sf
from kokoro_onnx import Kokoro
B=Path(__file__).resolve().parent
ROOT=B.parents[2]
MODEL=Path(os.environ.get('REN_KOKORO_MODEL',str(ROOT/'project/.tools/kokoro-q8.onnx')))
VOICE=Path(os.environ.get('REN_KOKORO_VOICE',str(ROOT/'project/.tools/voices/am_michael.bin')))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
text=(B/'script-adapted.txt').read_text().strip()
raw=B/'audio/narration-original.wav'
if raw.exists():
 old=json.loads((B/'audio/voice-result.json').read_text());assert old['settings']['script_sha256']==sha(B/'script-adapted.txt') and old['sha256']==sha(raw),'Stale original: do not overwrite saved narration'
 print('Reused saved original',old['duration']);raise SystemExit
spec={'engine':'Kokoro-82M ONNX q8, local CPU','voice':'am_michael','language':'en-us','speed':1.0,'model_sha256':sha(MODEL),'voice_sha256':sha(VOICE),'script':text,'script_sha256':sha(B/'script-adapted.txt'),'channel_voice_change':'US American male; deliberately differs from British Qwen Ren cloning per latest user request','paid_compute':False,'huggingface_generation_requests':0}
(B/'audio/voice-settings.json').write_text(json.dumps(spec,indent=2)+'\n')
vec=np.fromfile(VOICE,dtype=np.float32).reshape(-1,1,256);np.savez(B/'build/voice.npz',voice=vec)
tts=Kokoro(str(MODEL),str(B/'build/voice.npz'));a,sr=tts.create(text,voice='voice',speed=1.0,lang='en-us');assert np.isfinite(a).all() and np.max(np.abs(a))<1
sf.write(raw,a,sr,subtype='PCM_24');d=len(a)/sr
(B/'audio/voice-result.json').write_text(json.dumps({'settings':spec,'file':raw.name,'sha256':sha(raw),'sample_rate':sr,'duration':d,'listening_review':'not yet performed'},indent=2)+'\n');print({'duration':d,'sample_rate':sr,'words':len(text.split())})
