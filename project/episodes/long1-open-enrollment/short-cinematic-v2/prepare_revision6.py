"""Isolated Revision 6 contract; retain root Revision 5 production files."""
from pathlib import Path
import hashlib
import json
import os

D=Path(__file__).resolve().parent
R=D/'revision-06';R.mkdir(exist_ok=True)
ROOT=D.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((D/'revision6-art-review/manifest.json').read_text())
approval={'by':'Jon','evidence':'User replied "Approve" to the two generated artwork assets and request for approval to use them in the 15-second Revision 6 prototype.','scope':'The two listed artwork files only; not approval of Revision 6 MP4 or full Short.','assets':[{k:a[k] for k in ('id','file','sha256')} for a in review['assets']]}
for a in approval['assets']:assert sha(D/'revision6-art-review'/a['file'])==a['sha256']
(R/'artwork-approval.json').write_text(json.dumps(approval,indent=2)+'\n')
m=json.loads((D/'production.json').read_text())
m.update(title='Health Insurance Short — Revision 6 targeted prototype',
         asset_report='ASSETS_AND_STORYBOARD.md',layout_evidence='layout.json',
         prototype='../deliverables/Ren_Health_Short_v2_15s_Prototype_rev06.mp4',
         prototype_report='../deliverables/Ren_Health_Short_v2_15s_Prototype_rev06.qa.json',
         full_production_blocked='STOP after Revision 6: explicit approval of the actual 15-second prototype is required; only 360 frames implemented.')
assets=[]
for a in m['assets']:
    if a['id'] in ['render-r5','prepare-r5','config','reaction','reuse-registry','previous-layout','previous-prototype-audio']:continue
    a=dict(a);a['path']=os.path.relpath((D/a['path']).resolve(),R);assets.append(a)
def add(id,path,kind,evidence):
    assets.append(dict(id=id,path=os.path.relpath(path,R),kind=kind,sha256=sha(path),
                       status='approved',approval_evidence=evidence))
for id,p,kind in [('render-r6',D/'render_revision6.py','renderer'),('prepare-r6',D/'prepare_revision6.py','renderer'),('r5-components',D/'render_revision5.py','renderer')]:
    add(id,p,kind,'Jon authorized the targeted Revision 6 implementation; imported existing v3 components, not a replacement pipeline.')
add('artwork-approval',R/'artwork-approval.json','configuration',approval['evidence'])
for a in approval['assets']:
    add(a['id'],D/'revision6-art-review'/a['file'],'character',approval['evidence'])
add('revision5-audio',D/'deliverables/Ren_Health_Short_v2_15s_Prototype_Rev05.mp4','audio','Jon requires existing approved Qwen narration, unchanged; copy original Revision 5 AAC packets.')
add('standards',ROOT/'project/pipeline/shorts_standards.py','renderer','Existing mandatory Shorts preflight, gate and QA layer, unchanged.')
scenes=[
 ('renewal-action',0,48,'renewal-button-and-trackpad-closeup','Palm-down right hand presses the trackpad at 0.625s; screen confirms renewal','Immediate focal button and visible hand action','right-trackpad-press','action',['laptop','ren-right-hand-trackpad-click']),
 ('four-renewals',48,120,'physical-calendar-annual-confirmations','Four annual pages reveal confirmed choices, then hold Year 4','Make four-year repetition visible without a paragraph','four-confirmed-page-turns','action',[]),
 ('ren-reaction',120,216,'genuine-chest-up-concerned-reaction','Cut to approved concerned expression, chest-up, clear foreground','A locked human reaction hold lets the comparison register','approved-concerned-reaction-hold','presenter',['office','ren-chest-up-reaction']),
 ('price-a',216,276,'folded-premium-document-closeup','Plan A document settles; large fixed premium underlined','Reveal $2,520 first and hold before Plan B','premium-a-place-and-mark','action',[]),
 ('price-comparison',276,360,'unfolded-premium-document-closeup','Physical fold opens to $840; care-cost magnifier arrives','Sequential premium contrast followed by incomplete-total-cost cue','premium-b-unfold-and-inspect','action',[])]
m['scenes']=[]
for sid,start,end,comp,action,purpose,anim,kind,extra in scenes:
    m['scenes'].append(dict(id=sid,start_frame=start,end_frame=end,composition=comp,
        action=action,motion_purpose=purpose,animations=[anim],kind=kind,
        environment_fullscreen=True,assets=['render-r6','r5-components','font']+extra))
for a in assets:a['sha256']=sha((R/a['path']).resolve())
m['assets']=assets
(R/'production.json').write_text(json.dumps(m,indent=2)+'\n')
print('Revision 6 contract saved independently; original Revision 5 files untouched.')
