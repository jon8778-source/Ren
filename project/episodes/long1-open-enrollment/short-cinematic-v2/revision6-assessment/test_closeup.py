"""Diagnostic still generation only; does not create or approve new artwork."""
from pathlib import Path
import importlib.util,subprocess as sp
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent.parent
O=D/'deliverables/revision6-assessment';O.mkdir(parents=True,exist_ok=True);spec=importlib.util.spec_from_file_location('approved_r5',D/'render_revision5.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
raw=sp.check_output(['ffmpeg','-v','error','-xerror','-ss','4.5','-i',str(r.b.ROOT/'assets/ren_library/ren_confused.mp4'),'-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'])
source=Image.frombytes('RGB',(1280,720),raw);rgba=r.reaction_matte(source)
for scale in [4.0,5.0]:
 image=r.b.room(1).copy();actor=rgba.crop((465,0,825,720)).resize((int(360*scale),int(720*scale)),Image.Resampling.LANCZOS)
 offset=(int(540-175*scale),140);image.paste(actor,offset,actor)
 d=ImageDraw.Draw(image);d.text((100,190),'CLOSE-UP ASSET TEST',font=r.font(44),fill=r.INK)
 image.save(O/f'closeup-{scale:.1f}x.png')
 small=image.copy();small.thumbnail((360,640));small.save('/tmp/r6-closeup-phone-'+str(scale)+'.jpg')
 image.crop((280,300,880,1000)).save('/tmp/r6-closeup-native-'+str(scale)+'.png')
source.crop((550,0,740,180)).resize((570,540)).save(O/'source-head-detail.png')
