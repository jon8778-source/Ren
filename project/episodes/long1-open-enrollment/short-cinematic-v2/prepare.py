"""Build hashed prototype manifest; refuses to rewrite approved inputs."""
from pathlib import Path
import json,hashlib,os
D=Path(__file__).resolve().parent; B=D.parent; R=B.parents[2]
if (D/'prototype-approval.json').exists():
 raise SystemExit('Approved inputs are locked. Preserve approval evidence; a material change requires a new prototype review.')

config={'width':1080,'height':1920,'fps':24,'frames':360,'text_safe':[72,180,900,1560],'audio_ranges_samples':[[0,664320],[672320,728000]],'audio_sample_rate':48000,'approval_gate':'prototype only; no full rendering implemented'}
(D/'composition-config.json').write_text(json.dumps(config,indent=2)+'\n')
script="For four years, I renewed the same health plan. One click. Same plan. Done. Then I compared my options. One plan: two thousand five hundred and twenty dollars a year in premiums. Another: just eight hundred and forty. But here's the catch."
(D/'script-prototype.txt').write_text(script+'\n')
captions=[{'start':.08,'end':2.74,'text':'For four years, I renewed the same health plan.'},{'start':3.06,'end':5.45,'text':'One click. Same plan. Done.'},{'start':5.95,'end':7.36,'text':'Then I compared my options.'},{'start':7.79,'end':11.69,'text':'One plan: $2,520 a year in premiums.'},{'start':11.69,'end':13.77,'text':'Another: just $840.'},{'start':13.963333,'end':14.923333,'text':"But here's the catch."}]
scenes=[]
data=[('renewal-office',0,66,'office-ren-laptop','Ren acknowledges renewal notification; screen notification arrives','Establish familiar automatic choice',['nod_yes-.5-3.25'],True),('renewal-close',66,138,'laptop-closeup','Cursor click and four annual renewal confirmations','Make the four repeated decisions visible',['cursor-renewal-years'],False),('documents-arrive',138,204,'desk-overhead','Two insurance documents land on the physical desktop','Reveal the alternative plans',['papers-arrive'],True),('premium-close',204,276,'insurance-paper-detail','Marker draws beneath the completed annual premium','Hold the correct annual premium legibly',['premium-underline'],False),('reaction-office',276,360,'office-ren-paper-reaction','Ren raises hand to chin while the cost-detail tab is revealed','Introduce the catch and the need to compare total cost',['thinking-1.25-4.75'],True)]
for sid,start,end,comp,act,purpose,anims,environment in data:
 scenes.append(dict(id=sid,start_frame=start,end_frame=end,composition=comp,kind='presenter' if 'office' in sid else 'action',action=act,motion_purpose=purpose,animations=anims,environment_fullscreen=environment,assets=['office','thinking' if sid=='reaction-office' else 'nod','render','font']))
assets=[]
def asset(id,path,kind,evidence):
 path=R/path
 assets.append(dict(id=id,path=os.path.relpath(path,D),kind=kind,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),status='approved',approval_evidence=evidence))
asset('script',Path('project/episodes/long1-open-enrollment/short-cinematic-v2/script-prototype.txt'),'script','Existing approved opening narration, reused verbatim through catch; current request authorizes visual prototype')
asset('source-short',Path('project/episodes/long1-open-enrollment/portrait-short-01/deliverables/Ren_Health_Plan_Portrait_1min.mp4'),'audio','Exact existing Short specified by Jon, preserved; Qwen provenance in opening-hook-v1/manifest.json')
asset('office',Path('project/prototypes/coffee-minute-v3/assets/office.png'),'environment','Approved coffee v3 original; exact hash in artwork/manifest.json')
asset('nod',Path('assets/ren_library/ren_nod_yes.mp4'),'character','Approved Ren v3 animation library; actual source intervals inspected')
asset('thinking',Path('assets/ren_library/ren_thinking.mp4'),'character','Approved Ren v3 animation library; actual source intervals inspected')
for id,p in [('render','short-cinematic-v2/render.py'),('prepare','short-cinematic-v2/prepare.py'),('config','short-cinematic-v2/composition-config.json'),('voice-config','short-cinematic-v2/voice-configuration.json'),('native-matte','render.py'),('calculations','calculations.py'),('assumptions','assumptions.json'),('parent-timing','audio-timing.json'),('voice-provenance','opening-hook-v1/manifest.json')]:asset(id,Path('project/episodes/long1-open-enrollment')/p,'renderer' if id in ['render','native-matte','calculations'] else 'configuration','Existing approved dependencies or this task-authorized implementation; not a claim of prototype approval')
for id,p,kind in [('font','project/remotion/public/fonts/fredoka-latin-600-normal.woff2','configuration'),('v3-render','project/prototypes/coffee-minute-v3/render.py','renderer'),('v3-unpack','project/prototypes/coffee-minute-v3/unpack_artwork.py','renderer'),('qa-gate','project/pipeline/shorts_standards.py','renderer'),('voice-ref','Audio/ren_reference.wav','configuration'),('voice-text','Audio/ren_reference.txt','configuration')]:asset(id,Path(p),kind,'Existing approved production dependency; reference hashes verified')
m=dict(schema_version=1,title='Health Insurance Short v2 — 15-second prototype only',width=1080,height=1920,fps=24,frames=360,full_bleed=True,permanent_border=False,asset_report='ASSET_REQUIREMENTS.md',layout_evidence='layout.json',prototype='deliverables/Ren_Health_Short_v2_15s_Prototype.mp4',prototype_report='deliverables/Ren_Health_Short_v2_15s_Prototype.qa.json',assets=assets,scenes=scenes,audio_cues=captions,captions=captions,full_production_blocked='Await explicit approval; future medical artwork unresolved; renderer only implements first 15s')
(D/'production.json').write_text(json.dumps(m,indent=2)+'\n')
