"""Record the revised15-second story contract; no artwork or voice generation."""
from pathlib import Path
import json,hashlib,os
D=Path(__file__).resolve().parent;ROOT=D.parents[3]
if (D/'prototype-approval.json').exists():raise SystemExit('Approved inputs locked; preserve evidence and obtain a new prototype review for changes.')
m=json.loads((D/'revision-03/production.json').read_text())
m.update(title='Health Insurance Short — Revision4 story prototype',asset_report='REVISION4_PLAN.md',prototype='deliverables/Ren_Health_Short_v2_15s_Prototype_Rev04.mp4',prototype_report='deliverables/Ren_Health_Short_v2_15s_Prototype_Rev04.qa.json',full_production_blocked='Explicit revised prototype approval pending; only15s implemented')
config={'revision':4,'width':1080,'height':1920,'fps':24,'frames':360,'actor_decode':[1280,720],'actor_source_crop':[465,0,825,720],'actor_size':[936,1872],'actor_position':[20,350],'reaction_interval':[2.0,5.0],'reaction_foreground_paper_top':1415,'hand_source_time':3,'hand_crop':[704,240,860,480],'hand_rotation':-90,'hand_size':[480,312],'burned_in_transcript':False,'separate_srt':True,'voice_generation_requests':0}
(D/'revision4-config.json').write_text(json.dumps(config,indent=2)+'\n')
scenes=[('renewal-action',0,84,'renewal-button-hand-closeup','Ren hand approaches trackpad and presses at spoken click','Show the automatic decision as an actual action','approved-pointing-hand-trackpad',False),('four-renewals',84,132,'physical-calendar-page-closeup','Four annual renewal pages turn then hold Year4','Compress repeated annual choices without a paragraph','annual-page-turn',True),('ren-reaction',132,204,'waist-up-ren-over-documents','Ren expression/gesture changes as he compares','Human reaction replaces full-body presenter pose','approved-confused-2-5',True),('price-a',204,276,'folded-comparison-document','First annual premium opens on a single comparison sheet','Hold the correct price at phone-readable size','comparison-page-place',True),('price-comparison',276,360,'unfolded-comparison-document','Reveal other premium then inspect the care-cost line','Compare premiums without implying guaranteed total saving','comparison-fold-open-and-inspect',True)]
m['scenes']=[dict(id=sid,start_frame=start,end_frame=end,composition=comp,action=action,motion_purpose=purpose,animations=[anim],kind='presenter' if sid=='ren-reaction' else 'action',environment_fullscreen=env,assets=['office','laptop','render-r4','font']+(['reaction'] if sid=='ren-reaction' else ['point-hand'] if sid=='renewal-action' else [])) for sid,start,end,comp,action,purpose,anim,env in scenes]
# Preserve narration timing/text. Larger story labels replace tiny burnt-in captions.
assets=[]
for a in m['assets']:
 if a['id'] in ['render','prepare','config','previous-layout','previous-production','previous-scene-cache','nod','thinking']:continue
 assets.append(a)
def add(id,path,kind,evidence):
 p=ROOT/path;assets.append(dict(id=id,path=os.path.relpath(p,D),kind=kind,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='approved',approval_evidence=evidence))
for id,path,kind in [('render-r4','project/episodes/long1-open-enrollment/short-cinematic-v2/render_revision4.py','renderer'),('prepare-r4','project/episodes/long1-open-enrollment/short-cinematic-v2/prepare_revision4.py','renderer'),('render-components','project/episodes/long1-open-enrollment/short-cinematic-v2/render.py','renderer'),('config','project/episodes/long1-open-enrollment/short-cinematic-v2/revision4-config.json','configuration')]:add(id,path,kind,'This task authorizes targeted Revision4 implementation; prototype approval remains pending')
add('point-hand','assets/ren_library/ren_point_down_right.mp4','character','Existing Ren v3 library; actual3s hand/sleeve inspected, crop/rotation only, no new hand design')
add('reaction','assets/ren_library/ren_confused.mp4','character','Existing Ren v3 library; actual closed-mouth reaction inspected, same face/outfit/model')
# Refresh declared bytes without altering any original assets.
for a in assets:a['sha256']=hashlib.sha256((D/a['path']).resolve().read_bytes()).hexdigest()
m['assets']=assets
(D/'production.json').write_text(json.dumps(m,indent=2)+'\n')
# Full subtitle text is retained separately; the video uses large scene-specific labels.
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(D/'deliverables/Revision4_Narration.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(m['captions']))+'\n')
