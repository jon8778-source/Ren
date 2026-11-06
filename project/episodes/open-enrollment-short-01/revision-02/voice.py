"""One checkpointed free-only Qwen request; never retries uncertain/failing audio."""
from pathlib import Path
import sys,json,os
B=Path(__file__).resolve().parent;ROOT=B.parents[3]
sys.path.insert(0,str(ROOT/'project/cliplib'));import pilot

def main():
 if not (B/'manifest.json').exists():
  settings=pilot.current_settings()
  assert settings['reference_sha256']=='78de4bd45743554f15ce32d8db39deaf1c0b1a9a5cd69fabb6d637dff323ed1c'
  assert settings['transcript_sha256']=='46de9b48af8de666aa7275169f1f95fab8a398de3198c7d2fa51edbe22fb8451'
  parts=pilot.script_segments(B);assert len(parts)==1
  m={'schema':1,'title':'Ren Open Enrollment Short 01: pacing/identity revision','created_at':pilot.now(),'script_sha256':pilot.digest(B/'script.md'),'settings':settings,'target_duration_s':[15,18],'segments':[{**s,'settings':settings,'fingerprint':pilot.fingerprint(s['text'],settings),'status':'pending','attempts':[]} for s in parts],'quota_events':[],'hardware_policy':'Free ZeroGPU only. No paid fallback or blind retry.','free_reserve_gpu_seconds':pilot.FREE_RESERVE,'overall_status':'prepared','owner_request':'Replace stock voice with actual Ren Qwen reference; calmer reading and richer animation. Prototype only.'}
  pilot.save(B/'manifest.json',m)
 m=pilot.load(B)
 if all(s['status']=='complete' for s in m['segments']):
  print('Saved Qwen original valid; no generation/quota request needed');return
 if not os.environ.get('HF_TOKEN'):raise SystemExit('HF_TOKEN missing; stopped without request')
 pilot.resume(B,False)
if __name__=='__main__':
 try:main()
 except Exception as e:raise SystemExit(pilot.safe_error(e))
