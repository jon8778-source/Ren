"""Check the complete encoded Short, preserved opening and narration sample map."""
from pathlib import Path
import hashlib,json,subprocess as sp,sys
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont
F=Path(__file__).resolve().parent;D=F.parent;ROOT=D.parents[3]
sys.path.insert(0,str(ROOT/'project/pipeline'));import shorts_standards as S
OUT=D/'deliverables';BUILD=D/'build/full-production';REVIEW=OUT/'full-review'
REVIEW.mkdir(exist_ok=True)
m=S.load(F/'production.json');video=OUT/'Ren_Health_Short_v2_Final.mp4'
opening=OUT/'Ren_Health_Short_v2_15s_Prototype_rev06.mp4'
original=D.parent/'portrait-short-01/deliverables/Ren_Health_Plan_Portrait_1min.mp4'
assert S.sha(opening)==S.load(F/'authorization.json')['approved_prototype_sha256']
assert S.sha(original)==S.load(F/'audio-preservation.json')['original_source_sha256']

def md5frames(p):
 text=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-an','-frames:v','360','-f','framemd5','-'],text=True)
 return [s.split(',')[-1].strip() for s in text.splitlines() if s and not s.startswith('#')]
assert md5frames(opening)==md5frames(video),'Approved first360 decoded frames changed'

def pcm(p):
 return np.frombuffer(sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-vn','-ar','48000','-ac','1','-f','f32le','-']),dtype=np.float32)
master,sr=sf.read(BUILD/'narration.wav',dtype='float32')
assert sr==48000 and len(master)==m['frames']*2000
assert np.array_equal(master[:720000],pcm(opening)[:720000])
assert np.array_equal(master[720000:],pcm(original)[728000:2826000])
audio=pcm(video)[:len(master)]
assert len(audio)==len(master)
cor=float(np.corrcoef(master,audio)[0,1]);assert cor>.995
peak=float(20*np.log10(max(np.max(np.abs(audio)),1e-12)));assert peak<-.1
join={'sample':720000,'master_step':float(abs(master[720000]-master[719999])),
      'encoded_peak_40ms_dbfs':float(20*np.log10(max(np.max(np.abs(audio[719040:720960])),1e-12)))}

def still(t,p):
 sp.run(['ffmpeg','-v','error','-xerror','-y','-ss',str(t),'-i',str(video),'-frames:v','1',str(p)],check=True)

for t,name in [(14.9,'join-before'),(15,'join-after'),(19.6,'ren-phone'),(28.6,'pharmacy'),
               (31,'ren-bill'),(36,'plan-limits'),(42,'ren-desk'),(46,'deliberate-review'),(57,'takeaway')]:
 still(t,REVIEW/(name+'.png'))

# Complete timeline, every quarter second; not just selected shot midpoints.
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(video),'-vf','fps=4,scale=216:384',
                     '-pix_fmt','rgb24','-f','rawvideo','-'])
frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,384,216,3)
font=ImageFont.load_default(size=16)
for page in range((len(frames)+29)//30):
 sheet=Image.new('RGB',(6*216,5*410),'white');draw=ImageDraw.Draw(sheet)
 for j in range(30):
  i=page*30+j
  if i>=len(frames):break
  x=(j%6)*216;y=(j//6)*410
  sheet.paste(Image.fromarray(frames[i]),(x,y+26));draw.text((x+4,y+4),f'~{i/4:.2f}s',font=font,fill='black')
 sheet.save(REVIEW/f'whole-timeline-{page+1:02}.jpg',quality=94)

# Exact 24fps transition strip straddles the immutable opening join.
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(video),'-vf',
 'select=between(n\\,348\\,371),scale=216:384','-vsync','0','-pix_fmt','rgb24','-f','rawvideo','-'])
joinframes=np.frombuffer(raw,dtype=np.uint8).reshape(24,384,216,3)
sheet=Image.new('RGB',(6*216,4*410),'white');draw=ImageDraw.Draw(sheet)
for j,fr in enumerate(joinframes):
 x=(j%6)*216;y=(j//6)*410;sheet.paste(Image.fromarray(fr),(x,y+26));draw.text((x+4,y+4),f'{(348+j)/24:.3f}s',font=font,fill='black')
sheet.save(REVIEW/'join-motion-24fps.jpg',quality=95)

sheet=Image.new('RGB',(5*216,4*410),'white');draw=ImageDraw.Draw(sheet)
for j,s in enumerate(m['scenes']):
 t=(s['start_frame']+s['end_frame']-1)/48
 p=REVIEW/'contact-temp.png';still(t,p)
 x=(j%5)*216;y=(j//5)*410;sheet.paste(Image.open(p).resize((216,384)),(x,y+26))
 draw.text((x+3,y+4),s['id'],font=font,fill='black')
sheet.save(OUT/'Ren_Health_Short_v2_Contact_Sheet.jpg',quality=95)
(REVIEW/'contact-temp.png').unlink(missing_ok=True)

audio_ref=ROOT/'Audio/ren_reference.wav';transcript=ROOT/'Audio/ren_reference.txt'
v=S.load(D/'voice-configuration.json')
assert S.sha(audio_ref)==v['reference_sha256'] and S.sha(transcript)==v['transcript_sha256']
assumptions=S.load(D.parent/'assumptions.json')
assert assumptions['ppo']['premium_monthly']*12==2520
assert assumptions['hdhp']['premium_monthly']*12==840
assert assumptions['ppo']['in_network_oop_max']==4000
assert assumptions['hdhp']['in_network_oop_max']==6500
report={'video_sha256':S.sha(video),'duration_seconds':m['frames']/24,'frames':m['frames'],
 'approved_opening_first360_frames_pixel_identical':True,'opening_video_reencoded':False,
 'master_first15_seconds_pcm_identical':True,'master_remaining_pcm_identical_to_existing_short':True,
 'final_audio_encoded_once':'AAC 192k; voice samples unchanged before encoding',
 'full_audio_correlation_to_master':cor,'audio_peak_dbfs':peak,'join_audio':join,
 'source_originals_preserved':True,'financial_figures_checked':[2520,840,4000,6500],
 'unestablished_deductible_amount':'Not invented; field says Check your plan',
 'hsa_timing':'No day-one balance or fabricated contribution schedule shown',
 'qwen_model':v['model'],'qwen_space':v['space'],'qwen_endpoint':v['endpoint'],
 'language':v['language'],'use_xvector_only':v['use_xvector_only'],
 'reference_hashes_verified':True,'new_tts_calls':0,'speech_speed_changes':False,
 'new_environments':['clinic','pharmacy'],'new_major_character_artwork':False,
 'review_sheets':len(list(REVIEW.glob('whole-timeline-*.jpg'))),
 'audio_listening_performed':False,'physical_android_test':False}
(F/'preservation-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
