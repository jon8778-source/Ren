"""Prepare full Short using the explicitly approved immutable Revision 6 opening."""
from pathlib import Path
import json, hashlib, os, subprocess as sp
import numpy as np
import soundfile as sf
D=Path(__file__).resolve().parent;F=D/'full-production';ROOT=D.parents[3]
BUILD=D/'build/full-production';BUILD.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prototype=D/'deliverables/Ren_Health_Short_v2_15s_Prototype_rev06.mp4'
assert sha(prototype)=='d9954b4d2518a120efc8b314e686e7fa11e5d5209d3efea0130187e870b5abcb'
source=D.parent/'portrait-short-01/deliverables/Ren_Health_Plan_Portrait_1min.mp4'
assert sha(source)=='a3bc18e231f3c4d40f84d5338048ec1b1f788ee615ef797896b9ab834092c2a9'
old=json.loads((D/'revision-06/production.json').read_text())
edit=json.loads((D.parent/'portrait-short-01/edit-manifest.json').read_text())
frames=edit['frames']-4;duration=frames/24
def decode(p):return np.frombuffer(sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-vn','-ar','48000','-ac','1','-f','f32le','-']),dtype=np.float32)
first=decode(prototype)[:720000];tail=decode(source)[728000:edit['frames']*2000]
master=np.concatenate([first,tail]);assert len(master)==frames*2000
sf.write(BUILD/'narration.wav',master,48000,subtype='FLOAT')
mapping={'sample_rate':48000,'samples':len(master),'duration':duration,'first_15s':'Exact decoded approved prototype samples [0:720000]','tail':'Original Short samples [728000:2826000]; accounts for already-approved 8000-sample quiet-pause removal','original_source_sha256':sha(source),'approved_prototype_sha256':sha(prototype),'master_pcm_sha256':hashlib.sha256(master.tobytes()).hexdigest(),'master_wav_sha256':sha(BUILD/'narration.wav'),'new_voice_requests':0,'speech_speed_changed':False,'silence_padding':False,'audio_encoding':'Final master AAC encoded once for seamless join; approved voice samples unchanged before encoding.'}
(F/'audio-preservation.json').write_text(json.dumps(mapping,indent=2)+'\n')
words=[]
for c in edit['clips']:
 for w in c['words']:
  a=dict(w)
  for k in ('start','end'):
   if a[k]>=14.006666666666668:a[k]-=1/6
  words.append(a)
captions=[]
for c in json.loads((D.parent/'portrait-short-01/captions.json').read_text()):
 a=dict(c)
 for k in ('start','end'):
  if a[k]>=14.006666666666668:a[k]-=1/6
 captions.append(a)
(F/'word-timing.json').write_text(json.dumps(words,indent=2)+'\n')
script='\n\n'.join(c['text'] for c in edit['clips'])+'\n'
(F/'narration.txt').write_text(script)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(D/'deliverables/Ren_Health_Short_v2_Final.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(captions))+'\n')
m=dict(old)
m.update(title='Ren Health Insurance Short v2 — full production',frames=frames,
 asset_report='ASSET_REQUIREMENTS.md',layout_evidence='layout.json',
 prototype='../deliverables/Ren_Health_Short_v2_15s_Prototype_rev06.mp4',
 prototype_report='approved-opening.qa.json',full_production_blocked=False,
 final='../deliverables/Ren_Health_Short_v2_Final.mp4',captions=captions)
m['audio_cues']=[dict(start=max(0,c['start_frame']/24-(1/6 if c['start_frame']>360 else 0)),end=min(duration,c['end_frame']/24-1/6),text=c['text']) for c in edit['clips']]
assets=[]
for a in old['assets']:
 a=dict(a);a['path']=os.path.relpath((D/'revision-06'/a['path']).resolve(),F);assets.append(a)
def add(id,p,kind,evidence):
 assets.append(dict(id=id,path=os.path.relpath(p,F),kind=kind,sha256=sha(p),status='approved',approval_evidence=evidence))
auth='Current Jon full-production message authorizes matching empty environments and implementation, with no additional gate except new major character art; none is used.'
for id,p,kind in [('full-renderer',D/'render_full.py','renderer'),('full-preparer',D/'prepare_full.py','renderer'),('full-script',F/'narration.txt','script'),('full-master',BUILD/'narration.wav','audio'),('full-authorization',F/'authorization.json','configuration'),('audio-preservation',F/'audio-preservation.json','configuration'),('clinic',F/'assets/clinic.png','environment'),('pharmacy',F/'assets/pharmacy.png','environment'),('medical-props',D.parent/'full/assets/medical-props.png','prop'),('phone-clip',ROOT/'assets/ren_library/ren_hold_phone.mp4','character'),('clipboard-clip',ROOT/'assets/ren_library/ren_clipboard_tick.mp4','character')]:
 add(id,p,kind,auth if kind!='character' else 'Existing approved Ren v3 animation library; native sources and actual action intervals inspected. No new major character artwork.')
for a in assets:a['sha256']=sha((F/a['path']).resolve())
m['assets']=assets
m['scenes']=[dict(s) for s in old['scenes']]
later=[
 ('care-catch',360,438,'clinic-bill-counter','Medical bill slides onto consultation counter; premiums remain a separate line','Introduce real care costs after premium comparison','consultation-bill-arrival',['clinic']),
 ('chat-alex',438,510,'ren-holding-phone-office','Native Ren raises his phone; Alex’s message appears beside it','Show the first number-free opinion as a conversation','native-phone-raise',['office','phone-clip']),
 ('chat-danny',510,582,'phone-message-macro','Camera cuts into same phone; Danny’s conflicting message arrives','Contrast advice without inventing supporting characters','second-message-arrival',['office']),
 ('clinic-visit',582,648,'doctor-room-appointment','Appointment calendar and baby bottle join the consultation desk','Connect planned care with comparing coverage','appointment-page-open',['clinic','medical-props']),
 ('pharmacy-pickup',648,720,'pharmacy-prescription-counter','Prescription bottle arrives at collection/payment counter','Tie medication costs to a real collection moment','prescription-collection',['pharmacy','medical-props']),
 ('ppo-review',720,774,'ren-clinic-bill-reaction','Approved concerned Ren examines bill in clinic foreground','Show that the PPO could suit greater care needs','concerned-bill-reading',['clinic','ren-chest-up-reaction']),
 ('network-check',774,834,'phone-network-search-clinic','Network search and prescription coverage are checked on phone','Make plan verification a concrete action','network-and-drug-check',['clinic']),
 ('plan-limits',834,900,'medical-bill-plan-detail','Deductible field and verified in-network out-of-pocket limits are inspected','Distinguish annual premiums from covered-care cost exposure','bill-limit-inspection',['clinic']),
 ('hsa-timing',900,982,'pharmacy-bill-and-hsa','Bill arrives beside HSA jar before annual contributions accumulate','Show funding timing risk without inventing day-one balance','early-bill-hsa-arrival',['pharmacy','medical-props']),
 ('desk-review',982,1056,'ren-at-desk-paper-review','Ren returns to office desk; physical plan documents laid out','Return to the same personal decision','desk-review-settle',['office','ren-chest-up-reaction']),
 ('deliberate-choice',1056,1146,'laptop-review-trackpad','Approved hand reviews network, drugs and costs on the laptop','Demonstrate checking numbers rather than repeating opening click','deliberate-plan-review',['laptop','ren-right-hand-trackpad-click']),
 ('three-questions',1146,1258,'desktop-planning-worksheet','Three questions gain sequential pen marks on one recurring worksheet','Bad year, real year and purpose of difference stay connected','worksheet-three-marks',['office']),
 ('annual-review',1258,1338,'office-review-timer','Physical timer set for 40 minutes on desk, with annual-review label','Replace autopilot with a repeatable yearly habit','annual-review-timer',['office']),
 ('total-cost-ending',1338,frames,'completed-plan-office-desk','Reviewed plan settles; takeaway stays readable in office environment','Finish on total cost, not premiums','completed-review-hold',['office'])]
for sid,start,end,comp,action,purpose,anim,extra in later:
 s=dict(id=sid,start_frame=start,end_frame=end,composition=comp,action=action,motion_purpose=purpose,animations=[anim],kind='presenter' if sid in ['ppo-review','desk-review'] else 'action',environment_fullscreen=True,assets=['full-renderer','font']+extra)
 if sid=='three-questions':s['timing_justification']='4.667s connected worksheet hold with three sequential marks tied to spoken questions; allows reading without flashing separate cards.'
 m['scenes'].append(s)
(F/'production.json').write_text(json.dumps(m,indent=2)+'\n')
(F/'shot-manifest.json').write_text(json.dumps(m['scenes'],indent=2)+'\n')
layout=json.loads((D/'revision-06/layout.json').read_text())
(F/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print(f'Prepared {frames} frames / {duration:.6f}s; exact 360-frame opening locked.')
