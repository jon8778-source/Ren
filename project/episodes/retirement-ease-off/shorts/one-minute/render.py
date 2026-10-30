"""Reframe the existing revised MP4's closing passage; no TTS or new art."""
import hashlib
import json
import math
import subprocess as sp
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont

BASE=Path(__file__).resolve().parent
EPISODE=BASE.parents[1]
ROOT=EPISODE.parents[2]
VIDEO=EPISODE/'deliverables/Ren_When_Can_You_Ease_Off_Saving_v3.mp4'
MASTER=EPISODE/'build/narration.wav'
EXPECTED_VIDEO='3b0d3faa7ffa1784804fcab8951202f9eb520f01f8772b2bb5f72730a7a7236b'
EXPECTED_AUDIO='f1d5dc690d4c20775f257bf381369bb9f94535904f53d324b5bc78c626cfa534'
W,H,FPS=720,1280,24
INK,GREEN,CREAM='#172A3A','#3F665B','#FAF6EE'
FONT=ROOT/'project/remotion/public/fonts/fredoka-latin-600-normal.woff2'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n')
def font(size):return ImageFont.truetype(str(FONT),size)

def heading(image,value,disclaimer=False):
    d=ImageDraw.Draw(image)
    for size in (48,46,44,42,40,38):
        lines=[];row=''
        for word in value.upper().replace('\n',' ').split():
            candidate=(row+' '+word).strip()
            if row and d.textlength(candidate,font=font(size))>565:
                lines.append(row);row=word
            else:row=candidate
        lines.append(row);text='\n'.join(lines)
        bounds=d.multiline_textbbox((40,65),text,font=font(size),spacing=8)
        if bounds[2]<=615 and bounds[3]<=205:break
    else:raise ValueError(f'Headline does not fit: {value}')
    d.multiline_text((40,65),text,font=font(size),spacing=8,fill=INK)
    if disclaimer:d.text((40,215),'Educational only, not financial advice',font=font(21),fill=GREEN)

def paste_crop(out,frame,box,xy,width=None):
    crop=frame.crop(box)
    if width and width!=crop.width:
        crop=crop.resize((width,round(crop.height*width/crop.width)),Image.Resampling.LANCZOS)
    x,y=xy
    assert x>=0 and x+crop.width<=620 and y>=230 and y+crop.height<=1000,(box,xy,crop.size)
    out.paste(crop,xy)

def portrait(frame,shot,index,total,absolute):
    out=Image.new('RGB',(W,H),CREAM)
    first=index<72;last=index>=total-72
    title='When can you ease off saving for retirement?' if first else shot['title']
    heading(out,title,first or last)
    if shot['kind']=='ren':
        # Existing native MP4 pixels: strip out the old landscape caption,
        # centre Ren without enlarging or mirroring him, and extend only the
        # empty wall edge pixels to fill the portrait background width.
        out.paste(frame.crop((840,0,850,720)).resize((100,720)),(0,280))
        out.paste(frame.crop((840,0,1280,720)),(100,280))
        out.paste(frame.crop((1270,0,1280,720)).resize((180,720)),(540,280))
    elif shot['motif']=='calendar':
        paste_crop(out,frame,(65,220,605,560),(35,270),540)
        paste_crop(out,frame,(690,220,1205,560),(35,630),540)
    elif shot['motif']=='balance':
        for i in range(4):
            x=65+(i%2)*610;y=215+(i//2)*205
            paste_crop(out,frame,(x,y,x+575,y+170),(35,270+i*180),570)
    elif shot['motif']=='worksheet':
        for i in range(3):
            x=65+i*390
            paste_crop(out,frame,(x,240,x+365,490),(100,230+i*258))
    elif shot['motif'] in ('booking','interruption'):
        source_progress=(absolute-shot['start_frame'])/max(1,shot['frames']-1)
        ease=1-(1-min(1,source_progress/.38))**3
        paper_x=90+round(70*(1-ease))
        # Follow just the existing confirmation; do not include a sliver of
        # the neighbouring investment card in this portrait crop.
        paste_crop(out,frame,(paper_x,210,paper_x+650,520),(35,270),570)
        if shot['motif']=='booking':paste_crop(out,frame,(815,280,1205,505),(35,580),540)
        else:
            # Keep only the arriving investment card. A fixed broad crop can
            # otherwise capture a fragment of the neighbouring moving paper.
            card_x=775+round(250*(1-ease))
            card=Image.new('RGB',(505,265),CREAM)
            card.paste(frame.crop((card_x,255,min(1280,card_x+420),520)),(card_x-775,0))
            card=card.resize((570,round(265*570/505)),Image.Resampling.LANCZOS)
            out.paste(card,(35,580))
    else:raise ValueError('Unreviewed landscape layout: '+shot['motif'])
    return out

def main():
    assert sha(VIDEO)==EXPECTED_VIDEO,'Expected the revised existing MP4; do not substitute an older render'
    assert sha(MASTER)==EXPECTED_AUDIO,'Existing narration master changed'
    m=json.loads((EPISODE/'shots.json').read_text())
    segments=m['audio_segments'][-3:];assert [s['id'] for s in segments]==['s012','s013','s014']
    start=segments[0]['start_s'];end=segments[-1]['end_s']
    first_frame=round(start*FPS);last_frame=m['frames'];total=last_frame-first_frame
    shots=[s for s in m['shots'] if s['end_frame']>first_frame and s['start_frame']<last_frame]
    build=BASE/'build';build.mkdir(exist_ok=True)
    deliver=BASE/'deliverables';deliver.mkdir(exist_ok=True)
    narration=build/'narration.wav'
    sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(MASTER),'-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS','-c:a','pcm_s24le',str(narration)],check=True)
    source,rate=sf.read(MASTER);audio,sr=sf.read(narration)
    assert rate==sr==48000
    assert np.array_equal(source[round(start*rate):round(end*rate)],audio),'Narration sample timing changed'
    decoder=sp.Popen(['ffmpeg','-v','error','-xerror','-i',str(VIDEO),'-an','-vf',f'trim=start_frame={first_frame}:end_frame={last_frame},setpts=N/(24*TB)','-fps_mode','passthrough','-frames:v',str(total),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=sp.PIPE)
    silent=build/'portrait.mp4'
    encoder=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(silent)],stdin=sp.PIPE)
    thumbs=[];sidx=0;records=[]
    for i in range(total):
        absolute=first_frame+i
        while absolute>=shots[sidx]['end_frame']:sidx+=1
        shot=shots[sidx]
        raw=decoder.stdout.read(1280*720*3);assert len(raw)==1280*720*3
        frame=Image.frombytes('RGB',(1280,720),raw)
        out=portrait(frame,shot,i,total,absolute);encoder.stdin.write(out.tobytes())
        a=max(first_frame,shot['start_frame']);b=min(last_frame,shot['end_frame'])
        if absolute==(a+b)//2:
            path=build/(shot['id']+'.png');out.save(path)
            thumb=out.resize((180,320));ImageDraw.Draw(thumb).text((5,5),shot['id'],fill='black',stroke_width=2,stroke_fill='white');thumbs.append(thumb)
            records.append(dict(source_shot=shot['id'],kind=shot['kind'],motif=shot['motif'],start_frame=a-first_frame,end_frame=b-first_frame,frames=b-a,source_start_frame=a,source_end_frame=b,source_midpoint_frame=absolute,source_midpoint_sha256=hashlib.sha256(raw).hexdigest(),close=shot['close']))
            print(f"Reframed {shot['id']}",flush=True)
    decoder.stdout.close();assert decoder.wait()==0
    encoder.stdin.close();assert encoder.wait()==0
    # Verify shot-to-frame mapping against an independent frame-index select.
    terms=[f"eq(n,{s['source_midpoint_frame']})" for s in records]
    expr=('+'.join(terms)).replace(',',r'\,')
    original=sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(VIDEO),'-an','-vf',f'select={expr}','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'])
    frame_bytes=1280*720*3;assert len(original)==frame_bytes*len(records)
    for j,s in enumerate(records):
        assert hashlib.sha256(original[j*frame_bytes:(j+1)*frame_bytes]).hexdigest()==s['source_midpoint_sha256'],f"Source frame drift: {s['source_shot']}"
    final=deliver/'Ren_Retirement_Ease_Off_Short_9x16.mp4'
    sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(silent),'-i',str(narration),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(final)],check=True)
    count=json.loads(sp.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(final)]))
    v=next(s for s in count['streams'] if s['codec_type']=='video');a=next(s for s in count['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],a['codec_name'],int(v['nb_read_frames']))==(720,1280,'24/1','h264','aac',total)
    assert 59<float(count['format']['duration'])<62
    assert abs(float(v['duration'])-float(a['duration']))<1/FPS
    decoded=sp.run(['ffmpeg','-v','error','-xerror','-i',str(final),'-f','null','-'],capture_output=True,text=True,check=True);assert not decoded.stderr
    y=np.frombuffer(sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(final),'-vn','-f','f32le','-']),dtype='<f4')
    n=min(len(y),len(audio));correlation=float(np.corrcoef(audio[:n],y[:n])[0,1]);assert correlation>.99
    assert sum(s['frames'] for s in records)==total
    for x,y in zip(records,records[1:]):
        assert x['end_frame']==y['start_frame']
        if x['kind']==y['kind']=='ren':assert x['close']==y['close']
    contact=Image.new('RGB',(180*6,320*math.ceil(len(thumbs)/6)),CREAM)
    for i,im in enumerate(thumbs):contact.paste(im,((i%6)*180,(i//6)*320))
    contact.save(deliver/'contact-sheet.jpg')
    save(BASE/'shots.json',dict(resolution=[W,H],fps=FPS,shots=records))
    save(BASE/'validation.json',dict(status='technical pass; visual and listening review limits documented',source_video_sha256=EXPECTED_VIDEO,source_audio_sha256=EXPECTED_AUDIO,source_segments=['s012','s013','s014'],source_audio_interval_s=[start,end],source_video_interval_frames=[first_frame,last_frame],source_midpoints_independently_verified=len(records),frames=total,duration_s=float(count['format']['duration']),audio_duration_s=len(audio)/sr,resolution=[W,H],fps=FPS,codecs=['h264','aac'],full_decode='pass',continuous_audio_correlation=correlation,audio_samples_identical_to_master_excerpt=True,character_pixels='native crop; no upscaling/mirroring',important_content_bounds=[35,65,620,1000],hf_generation_calls=0,music=False,final_sha256=sha(final)))
    parts=json.loads((EPISODE/'segments.json').read_text())[-3:]
    (BASE/'script.md').write_text('\n\n'.join(s['text'] for s in parts)+'\n')
    print(final,flush=True)

if __name__=='__main__':main()
