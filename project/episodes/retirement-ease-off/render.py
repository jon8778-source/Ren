"""Retirement episode extension of the approved v3 renderer, not a legacy route.

Imports v3 artwork restoration, native matte, actor composition, Fredoka drawing,
frame-count checks and command runner. Episode changes are beats/graphics/timing
and resumable output. Never changes the approved prototype's files or SHOTS.
"""
import argparse
import hashlib
import json
import math
import subprocess as sp
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT/'project/prototypes/coffee-minute-v3'))
import render as v3
# Loading this file as a module is unsupported; run it as a script.
sys.path.insert(0, str(ROOT/'project/cliplib'))
import pilot
from design import BEATS

W,H,FPS = v3.W,v3.H,v3.FPS
INK,GREEN,CREAM,MUTED = v3.INK,v3.GREEN,v3.CREAM,v3.MUTED
A=json.loads((BASE/'assumptions.json').read_text())
C=json.loads((BASE/'calculations.json').read_text())
ACTOR_CACHE={}

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data): pilot.save(path,data)
def txt(d,x,y,t,size=36,fill=INK): v3.text(d,(x,y),t,size,fill)
def line(d,xy,fill=GREEN,width=5): d.line(xy,fill=fill,width=width)

def card(d,box,title,body='',accent=GREEN,size=34):
    d.rounded_rectangle(box,22,fill='#E5EBE1',outline=accent,width=3)
    x,y,_,_=box
    width=box[2]-x-48
    def wrap(value,fs):
        lines=[]
        for original in value.split('\n'):
            row=''
            for word in original.split():
                candidate=(row+' '+word).strip()
                if row and d.textlength(candidate,font=v3.font(fs))>width:
                    lines.append(row); row=word
                else: row=candidate
            lines.append(row)
        return '\n'.join(lines)
    title=wrap(title,size)
    while title.count('\n')>1 and size>26:
        size-=1; title=wrap(title.replace('\n',' '),size)
    txt(d,x+24,y+22,title,size,accent)
    bottom=y+22+(size+8)*(title.count('\n')+1)
    if body:
        body=wrap(body,28)
        assert bottom+15+(28+8)*(body.count('\n')+1)<=box[3]-8, (title,body,box)
        txt(d,x+24,bottom+15,body,28)

def arrow(d,x,y,x2,y2):
    line(d,(x,y,x2,y2)); d.polygon([(x2,y2),(x2-14,y2-10),(x2-14,y2+10)],fill=GREEN)

def worksheet(d,active=0):
    labels=['Price your\nretirement','Test\nsetbacks','Choose what\nit makes possible']
    for i,label in enumerate(labels):
        x=65+i*390
        card(d,(x,240,x+365,490),str(i+1),label, GREEN if i==active else MUTED,52)
        if i==active: line(d,(x+24,455,x+330,455),width=8)

def picture(s,f,actor=None):
    p=f/max(1,s['frames']-1); ease=1-(1-min(1,p/.38))**3
    k=s['motif']; para=s['paragraph']; variant=s.get('part',0)
    if s['kind']=='ren':
        im=v3.ART['office.png'].copy()
        # Reuse v3's native matte and single LANCZOS composition resize.
        # The episode's wide framing includes trainers; its closer framing uses
        # a gentler 1.25x scale rather than enlarging the actor 1.65x.
        scale=1.25 if s['close'] else .9
        key=(s['clip'],f)
        if key not in ACTOR_CACHE:
            ACTOR_CACHE[key]=v3.actor_rgba(actor)
        rgba=ACTOR_CACHE[key].resize((round(W*scale),round(H*scale)),Image.Resampling.LANCZOS)
        im.paste(rgba,(150 if s['close'] else 374,25 if s['close'] else 45),rgba)
        d=ImageDraw.Draw(im)
        # Wall annotation above the furniture, screen-left of presenting Ren.
        title=s['title']
        txt(d,70,55,title,35 if max(map(len,title.split('\n'))) < 25 else 30)
        if k=='booking': txt(d,80,225,'PLAN CHECKED • TRIP CONFIRMED',30,GREEN)
    else:
        im=Image.new('RGB',(W,H),CREAM); d=ImageDraw.Draw(im)
        title=s['title']; size=43
        while d.textlength(title,font=v3.font(size))>1150: size-=1
        assert size>=30, title
        txt(d,65,45,title,size)
        txt(d,65,113,s['subtitle'],28,MUTED)
        if k in ('booking','interruption'):
            x=90+round(70*(1-ease)); y=210
            card(d,(x,y,x+650,y+310),'TRIP CONFIRMED','Booking confirmation\nA plan for time together',size=40)
            line(d,(x+40,y+230,x+70,y+260,x+125,y+200),width=9)
            if k=='interruption':
                xx=775+round(250*(1-ease))
                card(d,(xx,255,xx+420,520),'INVEST INSTEAD?','What could this\nmoney become?',size=32)
                arrow(d,740,380,xx-12,380)
            elif para>50:
                card(d,(815,280,1205,505),'PLANNING','Goal\nSetbacks\nReview date',size=32)
        elif k=='cards':
            for i,(title,body) in enumerate([('Save less','Lower contributions\nKeep working'),('Stop new\ncontributions','Keep working\nInvestments remain'),('Retire','Stop working\nFund living costs')]):
                x=65+i*390; y=230+round(30*(1-min(1,max(0,p*4-i*.45))))
                card(d,(x,y,x+365,y+330),title,accent=GREEN,size=34)
                txt(d,x+24,y+160,body,29)
                if variant%3==i:
                    d.rounded_rectangle((x+10,y+10,x+355,y+320),16,outline=GREEN,width=8)
                    txt(d,x+24,y+265,'Different job. Different needs.',24,GREEN)
        elif k=='coast':
            before=para==13 and variant==0
            if para==12 and variant%2==0:
                card(d,(65,210,580,420),'EMPLOYMENT INCOME','Your paycheck')
                card(d,(700,210,1210,420),'LIVING EXPENSES','Current life stays funded')
                arrow(d,590,310,690,310)
            else:
                card(d,(65,210,580,375),'EMPLOYMENT INCOME','Pays current living expenses')
                card(d,(700,210,1210,375),'INVESTMENTS','Contributions entering' if before else 'New contributions stop')
                if before:
                    arrow(d,590,290,690,290)
                    xx=590+round(75*p); d.ellipse((xx,270,xx+18,288),fill=GREEN)
                    txt(d,690,398,'BEFORE EASING OFF',28,GREEN)
                else:
                    # No income-to-investment arrow after contributions stop.
                    txt(d,690,398,'STILL WORKING • LIVING COSTS COVERED',25,GREEN)
            line(d,(100,530,1170,530)); marker=100+round(1000*ease)
            d.ellipse((marker-10,520,marker+10,540),fill=GREEN)
            txt(d,90,560,'Today',30); txt(d,890,560,'Later retirement',30)
        elif k in ('setup','target','scenario_a','scenario_b','comparison'):
            scenario=k in ('scenario_a','scenario_b','comparison')
            txt(d,65,185,f"Age {A['current_age']} to {A['retirement_age']}    |    {A['years']} years    |    ${A['new_contributions']} new contributions",32)
            if k=='setup':
                txt(d,115,290,f"${A['starting_balance']:,}",98,GREEN)
                txt(d,120,420,'Starting retirement investments',36)
            elif k=='target':
                txt(d,115,290,f"${A['illustrative_target']:,}",98,GREEN)
                txt(d,120,420,'Illustrative target • Not a universal requirement',32)
            else:
                indices=[0,1] if k=='comparison' else [0 if k=='scenario_a' else 1]
                for row,idx in enumerate(indices):
                    rate=A['real_returns_after_fees'][idx]; total=C['displayed_outcomes'][idx]
                    y=(255 if variant%2 else 290) + row*170
                    expression=f"${A['starting_balance']:,} × {1+rate:.2f}^{A['years']}"
                    fs=45 if len(indices)==2 else 53
                    txt(d,75,y,expression,fs,GREEN)
                    # Fredoka lacks the approximately-equal glyph: draw the
                    # mathematical sign explicitly instead of showing tofu.
                    xx=95+d.textlength(expression,font=v3.font(fs))
                    for yy in (y+22,y+36):
                        points=[(xx+t,yy+4*math.sin(t/32*2*math.pi)) for t in range(33)]
                        d.line(points,fill=GREEN,width=3)
                    txt(d,xx+48,y,f'${total:,}',fs,GREEN)
                    txt(d,80,y+70,f"Scenario {'AB'[idx]}: {rate:.0%} annual real return after fees",31)
                if len(indices)==1:
                    idx=indices[0]
                    if variant%2:
                        txt(d,80,445,f"${C['displayed_outcomes'][idx]:,}",88,GREEN)
                        txt(d,85,550,'Hypothetical retirement balance',33)
                    else:
                        txt(d,80,455,f"Illustrative target: ${A['illustrative_target']:,}",41)
                        txt(d,85,530,'Not a universal retirement requirement',30,MUTED)
                # Only a separate timeline moves; equations never count up.
                line(d,(85,620,85+round(1080*ease),620),width=7)
            txt(d,65,660,"Hypothetical • Today’s purchasing power • Before withdrawal taxes",25,MUTED)
        elif k=='worksheet':
            active=0 if para<32 else 1 if para<38 else 2
            worksheet(d,active)
            txt(d,65,555,'A realistic plan, with room for setbacks',35,GREEN)
            if variant%2:
                txt(d,65,615,['A spending plan, not a guessed target.','Try a less favorable future.','Make the extra take-home purposeful.'][active],29,MUTED)
        elif k=='budget':
            labels=['Housing','Food','Taxes','Health insurance','Travel','Occasional repairs']
            for i,label in enumerate(labels):
                x=65+(i%3)*395; y=220+(i//3)*180
                offset=round(20*(1-min(1,max(0,p*6-i*.4))))
                card(d,(x,y+offset,x+365,y+135+offset),label,size=30)
        elif k in ('income','bridge','real'):
            labels={'income':[('RETIREMENT BUDGET','What life will cost'),('DEPENDABLE INCOME','Amount and start date'),('INVESTMENT GAP','What remains to fund')],
                    'bridge':[('WORK ENDS','Spending continues'),('BRIDGE YEARS','Account-access rules'),('BENEFITS BEGIN','Check your own timing')],
                    'real':[('TODAY’S DOLLARS','Purchasing power'),('REAL RETURNS','After inflation and fees'),('CONSISTENT PLAN','Same basis throughout')]}[k]
            for i,(label,body) in enumerate(labels):
                x=65+i*390; card(d,(x,250,x+365,490),label,body,size=26)
                if i<2: arrow(d,x+368,535,x+390,535)
        elif k in ('setbacks','reserve','purpose','decision','match','balance'):
            labels={
                'setbacks':[('LOWER RETURNS','Less growth'),('HIGHER SPENDING','More to fund'),('LONGER RETIREMENT','More time'),('CONTRIBUTION GAP','Pause new saving')],
                'reserve':[('EMERGENCY RESERVE','Money for shocks'),('EXPENSIVE DEBT','Under control?'),('BROKEN FURNACE','A plan before a bill'),('THIS YEAR','Financial stability')],
                'purpose':[('FAMILY TRIP','Time together'),('HELP AT HOME','Room to breathe'),('FEWER HOURS','Time back'),('SUBSCRIPTIONS?','A deliberate choice')],
                'decision':[('CURRENT SAVING','Same planning inputs'),('REDUCED SAVING','Same setback tests'),('WHAT CHANGES?','Date • Spending'),('MARGIN FOR ERROR','Enough room?')],
                'match':[('EMPLOYER MATCH','If offered'),('PLAN RULES','Check conditions'),('VESTING','Check ownership'),('MEASURED CHANGE','Review the choice')],
                'balance':[('FUTURE YOU','Security'),('PRESENT YOU','Room in the budget'),('RETIREMENT BALANCE','A tool for living'),('PLANNED SPENDING','A specific purpose')]}[k]
            for i,(title,body) in enumerate(labels):
                x=65+(i%2)*610; y=215+(i//2)*205
                card(d,(x,y,x+575,y+170),title,body,size=31)
            selected=(variant%4)
            x=65+(selected%2)*610; y=215+(selected//2)*205
            line(d,(x+24,y+147,x+24+round(515*ease),y+147),width=6)
        elif k=='tax':
            card(d,(65,250,435,480),f"${A['contribution_reduction']:,} LESS",'Pre-tax 401(k)\ncontribution',size=35)
            card(d,(485,250,790,480),'TAX STEP','Taxes take\na share',size=35)
            card(d,(840,250,1210,480),'TAKE-HOME','Check the actual\npayroll change',size=35)
            arrow(d,442,365,477,365); arrow(d,798,365,832,365)
            txt(d,80,555,'No tax rate or take-home amount assumed',33,MUTED)
        elif k=='calendar':
            card(d,(65,220,605,560),'CHOSEN CONTRIBUTION','Set the amount\nGive extra take-home a purpose\nReview after major changes',size=32)
            card(d,(690,220,1205,560),'ANNUAL REVIEW','Same date next year\nCheck the whole plan',size=38)
            for i in range(7):
                x=730+i*59; d.rounded_rectangle((x,430,x+40,470),6,fill=GREEN if i==4 else '#B8CBBB')
            if p>.25: d.ellipse((958,416,1019,482),outline=INK,width=5)
        else: raise ValueError(k)
    if s.get('disclaimer'):
        txt(d,35,682,'Educational only, not financial advice',20)
    return im

def audio_and_shots(preview=False, plan=False):
    m=json.loads((BASE/'manifest.json').read_text()); done=[]
    assert m['settings']==pilot.current_settings(), 'Voice settings/reference changed'
    parts=json.loads((BASE/'segments.json').read_text())
    assert ' '.join((BASE/'script.md').read_text().split())==' '.join(s['text'] for s in parts)
    for old,new in zip(m['segments'],parts):
        assert old['id']==new['id'] and old['fingerprint']==pilot.fingerprint(new['text'],m['settings']), 'Stale audio text'
    for s in m['segments']:
        if s['status']!='complete' and not plan: break
        if s['status']=='complete': assert digest(BASE/s['file'])==s['sha256']
        done.append(s)
    if not preview and not plan and len(done)!=len(m['segments']): raise ValueError('Narration incomplete; no full render')
    if preview and sum(s['validation']['processed_duration_s'] for s in done)<45:
        raise ValueError('Opening preview needs at least 45 seconds of completed narration')
    pcm=[]; audio_segments=[]; total=0
    for s in done:
        if s['status']=='complete':
            path,v=pilot.process_segment(BASE,s); a,rate=sf.read(path)
            assert rate==48000
            pcm.append(a); n=len(a); meta=dict(source_sha256=s['sha256'],processed_sha256=digest(path),timing='measured')
        else:
            # Planning only. No synthetic/silent narration file is created.
            n=round(pilot.word_count(s['text'])/2.8*48000); meta=dict(timing='provisional at 168 wpm; missing audio')
        audio_segments.append(dict(id=s['id'],start_s=total/48000,end_s=(total+n)/48000,**meta))
        total+=n
        if preview and total/48000>=50: break
    audio=np.concatenate(pcm)
    # Preview may end mid-paragraph; this is an extract, never labelled full.
    if preview: audio=audio[:min(len(audio),55*48000)]
    dur=total/48000 if plan else len(audio)/48000
    if dur>480: raise ValueError(f'Natural narration {dur:.2f}s exceeds 8 minutes; propose a script trim')
    out=BASE/'build'; out.mkdir(exist_ok=True)
    track=out/('preview-narration.wav' if preview else 'narration.wav')
    if not plan: sf.write(track,audio,48000,subtype='PCM_24')
    paragraphs=(BASE/'script.md').read_text().strip().split('\n\n'); assert len(paragraphs)==len(BEATS)
    shots=[]; cursor=0; para_idx=0; ren_count=0; last_pose=None
    for s,seg in zip(done,audio_segments):
        segment_paras=[]; consumed=''
        while para_idx<len(paragraphs):
            para=paragraphs[para_idx]; segment_paras.append((para_idx,para)); consumed+=' '+para; para_idx+=1
            if ' '.join(consumed.split())==s['text']: break
        assert ' '.join(consumed.split())==s['text']
        words=sum(pilot.word_count(p) for _,p in segment_paras); cumulative=0
        start_frame=round(seg['start_s']*24); end_frame=round(min(dur,seg['end_s'])*24)
        if end_frame<=start_frame: break
        for idx,para in segment_paras:
            begin=start_frame+round((seg['end_s']-seg['start_s'])*24*cumulative/words)
            cumulative+=pilot.word_count(para)
            end=min(end_frame,start_frame+round((seg['end_s']-seg['start_s'])*24*cumulative/words))
            if idx==segment_paras[-1][0]: end=end_frame
            if end<=begin: continue
            motif,title,subtitle=BEATS[idx]
            isren=motif=='ren'
            max_frames=132 if isren else 84
            count=math.ceil((end-begin)/max_frames)
            for part in range(count):
                a=begin+round((end-begin)*part/count); b=begin+round((end-begin)*(part+1)/count)
                # Return to Ren within longer graphical explanations.
                ren=isren or (count>=3 and part==1 and idx not in (18,20,21,22,43))
                clip=['present_palm_left','nod_yes','shake_no','thinking'][ren_count%4]
                if ren:
                    ren_count+=1; assert clip!=last_pose; last_pose=clip
                # On Ren inserts use a concise caption in the same semantic scene.
                ren_title=title.replace('. ','\n')
                if ren and not isren:
                    import textwrap
                    ren_title='\n'.join(textwrap.wrap(title.upper(),22))
                shots.append(dict(id=f'shot_{len(shots)+1:03d}',segment=s['id'],paragraph=idx,
                                  kind='ren' if ren else 'graphic',motif=motif,title=ren_title if ren else title,
                                  subtitle=subtitle,frames=b-a,start_frame=a,end_frame=b,
                                  start_s=a/24,end_s=b/24,part=part,clip=clip if ren else None,
                                  close=bool(ren_count%2),mirrored=False,source_start_s=1.25,
                                  asset='approved office + Ren library' if ren else 'code-drawn episode props',
                                  disclaimer=(a<72 or (not preview and b>round(dur*24)-72))))
    assert shots[0]['start_frame']==0
    assert all(x['end_frame']==y['start_frame'] for x,y in zip(shots,shots[1:]))
    assert sum(s['frames'] for s in shots)==round(dur*24)
    save(BASE/('planned-shots.json' if plan else 'preview-shots.json' if preview else 'shots.json'),dict(fps=24,duration_s=dur,frames=round(dur*24),timing='PROVISIONAL missing segments; not production timing' if plan else 'Paragraph timing estimated by word weights within real generated segments; listening alignment review pending',audio_segments=audio_segments,shots=shots))
    return track,shots,dur

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--preview',action='store_true'); ap.add_argument('--stills',action='store_true'); ap.add_argument('--plan-stills',action='store_true'); args=ap.parse_args()
    if args.plan_stills: args.stills=True
    track,shots,dur=audio_and_shots(args.preview,args.plan_stills)
    out=BASE/'build'/('planned' if args.plan_stills else 'preview' if args.preview else 'full'); out.mkdir(parents=True,exist_ok=True)
    thumbs=[]
    for i,s in enumerate(shots):
        path=out/(s['id']+'.mp4'); png=out/(s['id']+'.png')
        fp=hashlib.sha256(json.dumps(s,sort_keys=True).encode()+(BASE/'render.py').read_bytes()+(BASE/'design.py').read_bytes()+(Path(v3.__file__)).read_bytes()+(BASE/'assumptions.json').read_bytes()+(BASE/'calculations.json').read_bytes()).hexdigest()
        state=out/(s['id']+'.hash')
        if not args.stills and path.exists() and state.exists() and state.read_text()==fp:
            v3.check_video(path,s['frames']); thumbs.append(Image.open(png).resize((320,180))); continue
        decoder=None; encoder=None
        if s['kind']=='ren':
            source=ROOT/'assets/ren_library'/f"ren_{s['clip']}.mp4"
            info=json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
            assert (info['streams'][0]['width'],info['streams'][0]['height'])==(1280,720)
            assert 1.25+s['frames']/24<=min(6.75,float(info['format']['duration']))
            decoder=sp.Popen(['ffmpeg','-v','error','-xerror','-ss','1.25','-i',str(source),'-an','-vf','fps=24','-frames:v',str(s['frames']),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=sp.PIPE)
        if not args.stills:
            encoder=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
        for f in range(s['frames']):
            actor=None
            if decoder:
                raw=decoder.stdout.read(W*H*3); assert len(raw)==W*H*3
                actor=Image.frombytes('RGB',(W,H),raw)
            if encoder or f in (0,s['frames']//2,s['frames']-1):
                im=picture(s,f,actor)
                if encoder: encoder.stdin.write(im.tobytes())
                if f==s['frames']//2:
                    im.save(png); thumb=im.resize((320,180)); ImageDraw.Draw(thumb).text((5,5),s['id'],fill=INK,stroke_width=2,stroke_fill=CREAM); thumbs.append(thumb)
                if f in (0,s['frames']-1): im.save(out/(s['id']+f'-edge{f}.jpg'))
        if decoder: decoder.stdout.close(); assert decoder.wait()==0
        if encoder:
            encoder.stdin.close(); assert encoder.wait()==0
            v3.check_video(path,s['frames']); state.write_text(fp)
        print(f"{'Inspected frames' if args.stills else 'Rendered'} {i+1}/{len(shots)}",flush=True)
    deliver=BASE/'deliverables'; deliver.mkdir(exist_ok=True)
    for page in range(math.ceil(len(thumbs)/24)):
        batch=thumbs[page*24:(page+1)*24]; contact=Image.new('RGB',(1280,180*math.ceil(len(batch)/4)),CREAM)
        for i,t in enumerate(batch): contact.paste(t,((i%4)*320,(i//4)*180))
        contact.save(deliver/f"{'planned' if args.plan_stills else 'preview' if args.preview else 'full'}-contact-{page+1:02d}.jpg")
    if args.stills: return
    concat=out/'concat.txt'; concat.write_text('\n'.join(f"file '{s['id']}.mp4'" for s in shots))
    final=deliver/('Ren_Retirement_Opening_v3.mp4' if args.preview else 'Ren_When_Can_You_Ease_Off_Saving_v3.mp4')
    v3.cmd(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(track),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(final)])
    v3.check_video(final,sum(s['frames'] for s in shots))
    decoded=sp.run(['ffmpeg','-v','error','-xerror','-i',str(final),'-f','null','-'],capture_output=True,text=True,check=True); assert not decoded.stderr,decoded.stderr
    save(BASE/('preview-validation.json' if args.preview else 'validation.json'),dict(status='technical render pass; visual/audio/source review pending',duration_s=dur,frames=sum(s['frames'] for s in shots),resolution=[W,H],fps=FPS,codecs=['h264','aac'],full_decode='pass',every_shot_frame_count='pass',sha256=digest(final),actor_decode_resolution=[1280,720],no_music=True,no_source_audio=True,approved_artwork_preserved=True))
    print(final,flush=True)

if __name__=='__main__': main()
