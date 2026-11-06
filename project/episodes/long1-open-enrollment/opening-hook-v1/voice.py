"""One opening request only; existing resumable free-Qwen safeguards."""
from pathlib import Path
import sys,json,fcntl
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'project/cliplib'));import pilot
pilot.script_segments=lambda folder:json.loads((folder/'segments.json').read_text())
if __name__=='__main__':
 try:
  with (H/'.workflow.lock').open('w') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);m=pilot.load(H)
   if all(s['status']=='complete' for s in m['segments']):print('Saved opening verified; no generation request')
   else:pilot.resume(H,False)
 except Exception as e:raise SystemExit(pilot.safe_error(e))
