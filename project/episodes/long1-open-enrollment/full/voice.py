"""Resumable full narration; approved pilot originals reused, source gates retained."""
from pathlib import Path
import sys,json,os,fcntl,copy,hashlib
F=Path(__file__).resolve().parent;ROOT=F.parents[3]
sys.path.insert(0,str(ROOT/'project/cliplib'));import pilot
pilot.script_segments=lambda folder:json.loads((folder/'segments.json').read_text())
def report():
 m=pilot.load(F);pending=[s['id'] for s in m['segments'] if s['status']!='complete'];complete=[s for s in m['segments'] if s['status']=='complete'];attempts=[a for s in m['segments'][3:] for a in s['attempts']]
 finished=False
 if (F/'validation.json').exists():
  validated=json.loads((F/'validation.json').read_text());movie=F/'deliverables'/validated['file']
  finished=len(complete)==len(m['segments']) and movie.is_file() and hashlib.sha256(movie.read_bytes()).hexdigest()==validated['sha256']
 r={'complete_segments':len(complete),'total_segments':len(m['segments']),'remaining_segments':pending,'source_gated':[s['id'] for s in m['segments'] if s['status']=='source_review'],'original_seconds_saved':sum(s.get('validation',{}).get('duration_s',0) for s in complete),'new_generation_calls':len(attempts),'new_allowance_gpu_seconds':sum(a.get('observed_quota_decrease_gpu_seconds') or 0 for a in attempts),'new_request_elapsed_seconds':sum(a.get('elapsed_seconds',0) for a in attempts),'quota_snapshot':m.get('quota'),'resume_command':'bash project/episodes/long1-open-enrollment/full/resume.sh','full_video_finished':finished,'listening_review':'Pilot approved; new segments require review','source_check_file':'source-checks.json'}
 pilot.save(F/'checkpoint-report.json',r);print(json.dumps(r,indent=2))
def resume():
 m=pilot.load(F);checks=json.loads((F/'source-checks.json').read_text())
 for s in m['segments']:
  if s.get('source_gate'):
   verified=checks[s['source_gate']]['status']=='verified'
   if not verified and s['status']!='complete':s['status']='source_review'
   elif verified and s['status']=='source_review':s['status']='pending'
 pilot.checkpoint(F,m)
 held=copy.deepcopy([s for s in m['segments'] if s['status']=='source_review'])
 if not any(s['status']!='complete' for s in m['segments'] if s['status']!='source_review'):
  report();return
 original_load,original_checkpoint=pilot.load,pilot.checkpoint
 def selected_load(folder):
  loaded=original_load(folder);loaded['segments']=[s for s in loaded['segments'] if s['status']!='source_review'];return loaded
 def merged_checkpoint(folder,manifest,publish=False):
  merged=copy.deepcopy(manifest);byid={s['id']:s for s in merged['segments']};byid.update({s['id']:s for s in held});merged['segments']=[byid[s['id']] for s in pilot.script_segments(folder)]
  if held and merged['overall_status']=='narration_generated_review_pending':merged['overall_status']='source_checks_pending'
  original_checkpoint(folder,merged,False)
 pilot.load,pilot.checkpoint=selected_load,merged_checkpoint
 try:pilot.resume(F,False)
 finally:pilot.load,pilot.checkpoint=original_load,original_checkpoint
 report()
if __name__=='__main__':
 try:
  with (F/'.workflow.lock').open('w') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   if '--status' in sys.argv:report()
   else:resume()
 except Exception as e:raise SystemExit(pilot.safe_error(e))
