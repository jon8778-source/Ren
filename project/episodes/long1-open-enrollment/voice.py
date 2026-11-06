"""Pilot-only resumable approved Ren Qwen generation; no paid/stock fallback."""
from pathlib import Path
import sys,json,os
B=Path(__file__).resolve().parent;ROOT=B.parents[2];sys.path.insert(0,str(ROOT/'project/cliplib'));import pilot
pilot.script_segments=lambda folder:json.loads((folder/'segments.json').read_text())
def main():
 if not (B/'manifest.json').exists():
  settings=pilot.current_settings();assert settings['reference_sha256']=='78de4bd45743554f15ce32d8db39deaf1c0b1a9a5cd69fabb6d637dff323ed1c';assert settings['transcript_sha256']=='46de9b48af8de666aa7275169f1f95fab8a398de3198c7d2fa51edbe22fb8451'
  parts=pilot.script_segments(B);m={'schema':1,'title':'I Auto-Renewed My Health Plan for 4 Years. Then I Did the Math. — pilot','created_at':pilot.now(),'script_sha256':pilot.digest(B/'script.md'),'settings':settings,'target_duration_s':[55,65],'segments':[{**p,'settings':settings,'fingerprint':pilot.fingerprint(p['text'],settings),'status':'pending','attempts':[]} for p in parts],'quota_events':[],'hardware_policy':'Free ZeroGPU only; no paid fallback or retries','free_reserve_gpu_seconds':pilot.FREE_RESERVE,'overall_status':'prepared','space_revision':'6ae5dfa536c7109b33606b2332b8f0545d45f228','scope':'Opening review pilot only. Full narration blocked pending owner approval.'};pilot.save(B/'manifest.json',m)
 m=pilot.load(B)
 if all(s['status']=='complete' for s in m['segments']):print('Completed pilot originals verified; no generation or quota request');return
 if not os.environ.get('HF_TOKEN'):raise ValueError('HF_TOKEN missing; stopped without request')
 pilot.resume(B,False)
if __name__=='__main__':
 try:main()
 except Exception as e:raise SystemExit(pilot.safe_error(e))
