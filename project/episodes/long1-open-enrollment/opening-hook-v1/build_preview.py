"""Render only the hook; stream-copy a short source-video tail; never assemble full movie."""
from pathlib import Path
import sys,json,math,re,subprocess as sp,hashlib,importlib.util
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
from pocketsphinx import Decoder
H=Path(__file__).resolve().parent;B=H.parent;R=H.parents[3]
sys.path.insert(0,str(B));sys.path.insert(0,str(R/'project/cliplib'));import pilot
pilot.script_segments=lambda folder:json.loads((folder/'segments.json').read_text())
spec=importlib.util.spec_from_file_location('approved_hook_v3',B/'render.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
FPS=24;W,HGT=1280,720
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(cmd,**kwargs):return sp.run(cmd,check=True,**kwargs)
def main():
 src=json.loads((H/'source.json').read_text());source=Path(src['actual_path']);assert sha(source)==src['sha256'];m=pilot.load(H);assert len(m['segments'])==1 and m['segments'][0]['status']=='complete';s=m['segments'][0]
 processed,checks=pilot.process_segment(H,s);voice,rate=sf.read(processed,dtype='float32');assert rate==48000
 duration=len(voice)/rate;assert 15<=duration<=20,'Opening duration outside15–20 seconds; stop without speed changes or automatic retry'
 N=round(duration*FPS);assert abs(N/FPS-duration)<1/FPS
 raw=sp.check_output(['ffmpeg','-v','error','-i',str(processed),'-ac','1','-ar','16000','-f','s16le','-']);d=Decoder(samprate=16000,loglevel='ERROR');target=' '.join(re.findall(r"[a-z]+(?:'[a-z]+)?",s['text'].lower()));d.set_align_text(target);d.start_utt();d.process_raw(raw+bytes(8000),False,True);d.end_utt();words=[{'word':re.sub(r'\(\d+\)$','',w.word),'start':w.start_frame/100,'end':min(duration,(w.end_frame+1)/100)} for w in d.seg() if not w.word.startswith('<')];assert [w['word'] for w in words]==target.split();assert all(w['start']<duration and w['end']>w['start'] for w in words)
 tokens=[w['word'] for w in words]
 def at(phrase):
  q=re.findall(r"[a-z]+(?:'[a-z]+)?",phrase.lower())
  return next(words[i]['start'] for i in range(len(words)) if tokens[i:i+len(q)]==q)
 discover=at('Then I compared');twist=at("But here's the catch");click=at('One click');prices=at('One plan');beats=[(0,discover,'auto'),(discover,twist,'prices'),(twist,N/FPS,'twist')];shots=[];cursor=0
 for a,z,kind in beats:
  end=round(z*FPS);length=end-cursor;pieces=math.ceil(length/132);base=cursor
  for j in range(pieces):
   frames=round(length*(j+1)/pieces)-round(length*j/pieces);shots.append({'id':f'hook_{len(shots)+1:02}','motif':kind,'start_frame':cursor,'frames':frames,'end_frame':cursor+frames,'clip':['thinking','nod_yes'][len(shots)%2],'phase_start':base/FPS,'phase_end':end/FPS});cursor+=frames
 assert cursor==N
 pilot.save(H/'timing.json',{'hook_audio_seconds':duration,'hook_video_seconds':N/FPS,'hook_frames':N,'words':words,'shots':shots,'source_cut_seconds':src['cut_seconds'],'preview_source_tail_frames':src['preview_source_end_frame']-src['cut_frame'],'forced_alignment':'Local analysis only; not independent transcription. Decoder context does not enter exported audio.'})
 p.actors('thinking');p.actors('nod_yes')
 def picture(shot,n):
  t=(shot['start_frame']+n)/FPS;im=p.OFFICE.copy();actor=p.actor(shot['clip'],n);im.paste(actor,(-300,33),actor)
  if shot['motif']=='auto':
   im=p.textbox(im,(710,100),'Health plan renewal',36);draw=ImageDraw.Draw(im);clicked=t>=click
   draw.rounded_rectangle((710,245,1215,320),16,fill=p.GREEN if clicked else p.INK,outline=p.INK,width=2);p.txt(draw,(735,265),'Keep Current Plan',32,p.CREAM)
   # Four distinct renewals; no fictitious dates, running monetary totals or long static slide.
   for year in range(p.A['auto_renew_years']):
    x=710+year*130;y=390;completed=t>min(click,year*.85+.3);layer=Image.new('RGBA',(W,HGT));ld=ImageDraw.Draw(layer);ld.rounded_rectangle((x,y,x+112,y+88),12,fill=(255,255,255,185),outline=(0,0,0,255),width=2);im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');draw=ImageDraw.Draw(im);p.txt(draw,(x+15,y+13),f'YEAR {year+1}',21,p.GREEN)
    if completed:draw.line((x+35,y+57,x+49,y+69,x+77,y+43),fill=p.GREEN,width=5)
   if click-.35<t<click+.9:
    q=p.ease((t-click+.35)/.35);x=1175-60*q;y=350-60*q;draw.polygon([(x,y),(x+6,y+29),(x+15,y+20),(x+26,y+20)],fill=p.CREAM,outline=p.INK,width=2)
  else:
   im=p.textbox(im,(710,90),'Annual premiums only',34)
   for j,(label,value) in enumerate([('PLAN A',p.C['ppo_annual_premium']),('PLAN B',p.C['hdhp_annual_premium'])]):
    y=165+j*135;layer=Image.new('RGBA',(W,HGT));ld=ImageDraw.Draw(layer);ld.rounded_rectangle((710,y,1215,y+115),16,fill=(255,255,255,185),outline=(0,0,0,255),width=2);im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');draw=ImageDraw.Draw(im);p.txt(draw,(732,y+10),label,23,p.GREEN);p.txt(draw,(732,y+43),f'${value:,}/year',48)
    width=round(435*value/p.C['ppo_annual_premium']*p.ease((t-discover)/1.0));draw.rounded_rectangle((732,y+104,732+max(2,width),y+109),2,fill=p.INK if j==0 else p.GREEN)
   if shot['motif']=='twist':im=p.textbox(im,(710,450),'Deductible + out-of-pocket costs?',24)
   else:p.txt(ImageDraw.Draw(im),(710,455),'Illustrative plans • not total care costs',23,p.GREEN)
  if t<3:
   draw=ImageDraw.Draw(im);value=p.A['disclaimer'];bb=draw.textbbox((28,688),value,font=p.font(18));layer=Image.new('RGBA',(W,HGT));ImageDraw.Draw(layer).rounded_rectangle((bb[0]-7,bb[1]-5,bb[2]+7,bb[3]+5),6,fill=(250,246,238,225));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');p.txt(ImageDraw.Draw(im),(28,688),value,18)
  return im
 files=[]
 for shot in shots:
  file=H/'build'/(shot['id']+'.mp4');enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','slow','-crf','17','-pix_fmt','yuv420p',str(file)],stdin=sp.PIPE)
  for n in range(shot['frames']):
   im=picture(shot,n);enc.stdin.write(im.tobytes())
   if n==shot['frames']//2:im.save(H/'build'/(shot['id']+'.png'))
  enc.stdin.close();assert enc.wait()==0;p.v3.check_video(file,shot['frames']);files.append(file)
 tail=H/'build/original-preview-tail-video.mp4';tail_frames=src['preview_source_end_frame']-src['cut_frame']
 run(['ffmpeg','-v','error','-xerror','-y','-ss',str(src['cut_seconds']),'-i',str(source),'-map','0:v:0','-frames:v',str(tail_frames),'-an','-c:v','copy','-movflags','+faststart',str(tail)]);p.v3.check_video(tail,tail_frames)
 tail_audio=H/'build/original-preview-tail-audio.wav';start=src['cut_audio_sample_48k'];end=src['preview_source_end_frame']*2000
 run(['ffmpeg','-v','error','-xerror','-y','-i',str(source),'-map','0:a:0','-af',f'atrim=start_sample={start}:end_sample={end},asetpts=PTS-STARTPTS','-c:a','pcm_f32le',str(tail_audio)])
 old,rate2=sf.read(tail_audio,dtype='float32');assert rate2==48000 and len(old)==end-start
 preview_audio=H/'build/preview-audio.wav';sf.write(preview_audio,np.concatenate([voice,old]),48000,subtype='FLOAT');merged,_=sf.read(preview_audio,dtype='float32');assert np.array_equal(merged[len(voice):],old)
 # Both sections remain encoded H.264; concat only remuxes their compressed video packets.
 concat=H/'build/preview-concat.txt';concat.write_text('\n'.join("file '%s'"%x for x in files+[tail])+'\n');out=H/'deliverables/Ren_Health_Plan_Opening_Preview.mp4'
 run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-auto_convert','0','-i',str(concat),'-i',str(preview_audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)])
 p.v3.check_video(out,N+tail_frames);assert sha(source)==src['sha256'];pilot.save(H/'preview-build.json',{'file':out.name,'sha256':sha(out),'hook_frames':N,'original_tail_frames':tail_frames,'preview_frames':N+tail_frames,'source_cut_seconds':src['cut_seconds'],'source_audio_samples_used':[start,end],'source_tail_audio_before_preview_encode':'Exact decoded source samples; no gain, tempo, trimming within selection or substitution','preview_audio_encoding':'Only this short review preview AAC encoded; original source untouched. Final splice/audio preservation will be verified after approval.','preview_video_encoding':'New hook rendered only. Original tail video stream-copied; no unchanged source scene regenerated.','full_video_assembled':False,'gate':'Await explicit owner approval of this preview','original_source_sha256':sha(source)});print(json.dumps({'preview':str(out),'hook_seconds':duration,'preview_video_seconds':(N+tail_frames)/24,'full_video_assembled':False}))
if __name__=='__main__':main()
