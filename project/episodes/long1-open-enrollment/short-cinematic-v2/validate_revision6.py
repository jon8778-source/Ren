"""Encoded-output evidence, original/audio preservation and review frames."""
from pathlib import Path
import importlib.util
import json
import subprocess as sp
import hashlib
import shutil
import functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D=Path(__file__).resolve().parent;R=D/'revision-06'
OUT=D/'deliverables';REVIEW=OUT/'revision6-review';REVIEW.mkdir(exist_ok=True)
video=OUT/'Ren_Health_Short_v2_15s_Prototype_rev06.mp4'
base=OUT/'Ren_Health_Short_v2_15s_Prototype_Rev05.mp4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base)=='8a78f5ef7d36faafa9c9caa641ef307a152aca1d3f2db7a3049881b626eed7d7'

def packets(p):
    return json.loads(sp.check_output(['ffprobe','-v','error','-select_streams','a:0',
        '-show_packets','-show_data_hash','sha256','-show_entries',
        'packet=pts_time,duration_time,data_hash','-of','json',str(p)]))['packets']

def pcm(p):
    return sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-vn',
                            '-c:a','pcm_s16le','-f','s16le','-'])

p1,p2=packets(base),packets(video)
assert p1==p2,'AAC packet data or timing differs'
sound=pcm(video);assert sound==pcm(base),'Decoded PCM differs'
samples=np.frombuffer(sound,dtype=np.int16).astype(np.float64)/32768
peak=float(20*np.log10(max(np.max(np.abs(samples)),1e-12)))

@functools.lru_cache(maxsize=6)
def frame(n):
    raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(video),'-vf',
       f'select=eq(n\\,{n})','-vsync','0','-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'])
    assert len(raw)==1080*1920*3
    return Image.frombytes('RGB',(1080,1920),raw)

for n,name in [(15,'01-opening-click.png'),(168,'02-ren-closeup.png'),(346,'03-price-reveal.png')]:
    frame(n).save(REVIEW/name)

# All-frame sequential contact pages: every encoded frame is visible for
# visual inspection. A separate larger 4fps sequence supports phone-sized review.
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(video),'-vf','scale=135:240',
                     '-pix_fmt','rgb24','-f','rawvideo','-'])
frames=np.frombuffer(raw,dtype='uint8').reshape(360,240,135,3)
font=ImageFont.load_default(size=16)
for page in range(6):
    sheet=Image.new('RGB',(1350,6*264),'#FFFFFF');draw=ImageDraw.Draw(sheet)
    for j in range(60):
        n=page*60+j;x=(j%10)*135;y=(j//10)*264
        sheet.paste(Image.fromarray(frames[n]),(x,y+24))
        draw.text((x+3,y+2),f'{n} / {n/24:.3f}s',font=font,fill='black')
    sheet.save(REVIEW/f'all-frames-{page+1}.jpg',quality=94)
phone_raw=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(video),'-vf',
    'fps=4,scale=360:640','-pix_fmt','rgb24','-f','rawvideo','-'])
phone_frames=np.frombuffer(phone_raw,dtype='uint8').reshape(60,640,360,3)
for page in range(3):
    sheet=Image.new('RGB',(1440,5*668),'white');draw=ImageDraw.Draw(sheet)
    for j in range(20):
        n=(page*20+j)*6;x=(j%4)*360;y=(j//4)*668
        im=Image.fromarray(phone_frames[page*20+j])
        sheet.paste(im,(x,y+28));draw.text((x+5,y+4),f'{n/24:.2f}s',font=font,fill='black')
    sheet.save(REVIEW/f'phone-sequence-{page+1}.jpg',quality=94)
face=frame(168).crop((225,1020,700,1500))
face.save(REVIEW/'face-detail-native.png')
frame(15).crop((455,1090,1080,1585)).save(REVIEW/'hand-detail-native.png')
frame(168).crop((340,1650,575,1900)).save(REVIEW/'shirt-detail-native.png')

m=json.loads((R/'production.json').read_text())
layout=json.loads((R/'layout.json').read_text())['scenes']
def first(text):return min(i['start'] for items in layout.values() for i in items if i['text']==text)
assert first('$2,520')==9
assert first('$840')>first('$2,520')+2.5
assert first('Premiums only')==first('$840')
assert abs(first('Care costs?')-13.875)<1/24
report={'video_sha256':sha(video),'duration':15,'frames':360,
 'original_revision5_preserved':True,'aac_packets_and_timestamps_identical':True,
 'aac_packet_count':len(p1),'decoded_pcm_identical':True,
 'decoded_pcm_sha256':hashlib.sha256(sound).hexdigest(),'audio_peak_dbfs':peak,
 'new_voice_calls':0,'new_artwork_generation_calls_this_revision':0,
 'opening_click_time_seconds':.625,
 'annual_confirmation_times_seconds':[2,2+.58,2+1.16,2+1.74],
 'reaction_interval':[5,9],
 'reaction_native_source':[941,1672],'reaction_composite_width':900,
 'approximate_face_width_measurement':{'native_x_bounds':[258,680],
    'output_pixels':(680-258)*900/941,'percent_canvas':(680-258)*900/941/1080*100,
    'method':'Manual facial-oval horizontal bounds checked against encoded close-up; approximate, not automated face recognition'},
 'plan_a_first_visible':first('$2,520'),'plan_b_first_visible':first('$840'),
 'premiums_only_first_visible':first('Premiums only'),'care_cost_first_visible':first('Care costs?'),
 'review_evidence':'Three native screenshots, six all-frame sequential sheets, three 4fps phone-sized sequences and native face/hand/shirt crops.',
 'listening_review_performed':False,'physical_android_test_performed':False,
 'motion_playback_review_performed':False,
 'limitations':['Frame-sequence review and all-frame checks do not equal real-time playback/listening.',
 'Reaction uses the single approved static expression with a deliberate four-second hold; no new facial rig or lip sync.']}
(R/'preservation-and-timing.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copy2(OUT/'Ren_Health_Short_v2_15s_Prototype_rev06.qa.json',R/'technical-qa.json')
print(json.dumps(report,indent=2))
