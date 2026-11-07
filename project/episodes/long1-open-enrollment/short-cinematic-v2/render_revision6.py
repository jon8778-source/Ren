"""Targeted Revision 6 adapter: approved art, unchanged narration, prototype only."""
from pathlib import Path
import importlib.util
import functools
import json
import os
import subprocess as sp
import sys
from PIL import Image, ImageDraw

D = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r5_components', D/'render_revision5.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
b, S = previous.b, previous.S
R = D/'revision-06'
BUILD = D/'build/revision6'
BUILD.mkdir(parents=True, exist_ok=True)
M = S.load(R/'production.json')
REC = S.LayoutRecorder()
W, H, FPS = 1080, 1920, 24
INK, GREEN, CREAM, SAGE = b.INK, b.GREEN, b.CREAM, b.SAGE
font, ease = b.font, b.ease


def txt(im, s, n, xy, value, size=60, fill=INK, role='text'):
    draw = ImageDraw.Draw(im)
    draw.multiline_text(xy, value, font=font(size), fill=fill, spacing=9)
    REC.record(s['id'], draw, xy, value, font(size),
               (s['start_frame']+n)/24, (s['start_frame']+n+1)/24,
               role, spacing=9)


@functools.lru_cache(maxsize=4)
def art(name, width):
    source = Image.open(D/'revision6-art-review'/name).convert('RGBA')
    # One resize from the native, owner-approved master. No sharpening/upscaling.
    assert width <= source.width
    return source.resize((width, round(source.height*width/source.width)),
                         Image.Resampling.LANCZOS)


def opening(s, n):
    t = n/24
    im = previous.wood().copy()
    # Brief motivated pull-back exposes the actual trackpad action. Button is
    # already the focal point on frame zero; no establishing shot precedes it.
    pull = ease(t/.48)
    width = round(1350-100*pull)
    x, y = round((1080-width)/2), round(240+30*pull)
    prop = b.laptop_image(width)
    im.paste(prop, (x,y), prop)
    k = width/b.LAPTOP.width
    screen = tuple(round(v) for v in (x+193*k,y+81*k,x+1253*k,y+678*k))
    draw = ImageDraw.Draw(im)
    draw.rectangle(screen, fill=CREAM)
    txt(im,s,n,(120,390),'HEALTH PLAN',52,GREEN)
    txt(im,s,n,(120,477),'Annual renewal',62)
    pressed = t >= .625
    draw = ImageDraw.Draw(im)
    draw.rounded_rectangle((112,635,895,770),18,
                           fill=SAGE if pressed else GREEN)
    txt(im,s,n,(145,666),'Renewal confirmed' if pressed else 'Keep current plan',
        60,INK if pressed else CREAM)
    # Existing cursor provides the screen/trackpad relationship; never mirror or
    # rotate the approved palm-down hand to fake a pointing pose.
    cx,cy = 823,740
    draw = ImageDraw.Draw(im)
    draw.polygon([(cx,cy),(cx+9,cy+50),(cx+22,cy+34),(cx+39,cy+35)],
                 fill=CREAM,outline=INK,width=3)
    if .625 <= t <= 1.04:
        radius=round(20+100*(t-.625))
        draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=GREEN,width=5)
    hand = art('ren-right-hand-trackpad-click.png',620)
    # Approved native index tip approximately (500,260); align it to the
    # physical laptop's trackpad centre, not to the vertical display.
    fingertip = (x+725*k, y+982*k)
    press = 5*max(0,1-abs(t-.625)/.13)
    hx = round(fingertip[0]-500*620/1568)
    hy = round(fingertip[1]-260*620/1568+press)
    # Continue the cuff out of the composition rather than exposing the
    # transparent asset's straight export boundary across an empty desk.
    scale=620/1568
    left=(round(hx+994*scale),round(hy+1002*scale))
    right=(round(hx+1567*scale),round(hy+1000*scale))
    draw=ImageDraw.Draw(im)
    draw.polygon([left,right,(1130,right[1]+125),(1130,right[1]+345)],
                 fill='#3A3F58',outline='#20293A',width=2)
    im.paste(hand,(hx,hy),hand)
    return im


def calendar(s,n):
    im=previous.wood().copy()
    t=n/24
    step=min(3,int(t/.58))
    phase=(t-step*.58)/.58 if step<3 else 1
    draw=ImageDraw.Draw(im)
    for j in [3,2,1]:
        draw.rounded_rectangle((110+j*9,365+j*12,895+j*9,1235+j*12),8,
                               fill='#E8E4D8',outline='#84927E',width=2)
    b.shadow(im,(120,390,915,1270),8)
    draw=ImageDraw.Draw(im)
    draw.rounded_rectangle((110,365,895,1235),8,fill=CREAM,outline='#61735D',width=3)
    draw.rectangle((110,365,895,535),fill=GREEN)
    txt(im,s,n,(155,410),'ANNUAL RENEWAL',60,CREAM)
    txt(im,s,n,(165,620),f'YEAR {step+1}',130)
    txt(im,s,n,(165,880),'CONFIRMED',76,GREEN)
    for x in [270,735]:draw.ellipse((x,320,x+35,420),outline=INK,width=8)
    # Four physical annual pages, with confirmation ticks accumulating.
    for i in range(4):
        x=190+i*165
        draw.ellipse((x,1055,x+76,1131),outline=GREEN,width=4)
        if i<=step:draw.line((x+18,1093,x+32,1106,x+60,1077),fill=GREEN,width=7)
    if step<3 and phase<.3:
        lift=round(240*(1-phase/.3))
        draw.polygon([(110,1160),(895,1160),(895-lift//3,1235-lift),
                      (110+lift//3,1235-lift)],fill='#D2DCC9',outline='#72846B',width=3)
    return im


def reaction(s,n):
    # The close camera sees the office's upper wall, not floorboards behind
    # Ren's face. Same approved office pixels, portrait crop, no new background.
    im=b.OFFICE.crop((1120,0,1480,640)).resize((W,H),Image.Resampling.LANCZOS)
    a=art('ren-chest-up-reaction.png',900)
    # Near-native detail; torso continues beyond the bottom edge instead of
    # exposing the artwork's export boundary. No enlarged full-body animation.
    im.paste(a,(0,650),a)
    txt(im,s,n,(100,260),'I finally\ncompared.',88)
    # A genuine reaction cut/hold: closed lips and restrained concerned brow.
    # No mouth/face warping, fake breathing, decorative wobble or foreground paper.
    return im


def prices(s,n):
    im=previous.wood().copy()
    t=(s['start_frame']+n)/24
    dy=round(55*(1-ease(n/8))) if s['id']=='price-a' else 0
    b.shadow(im,(92,230+dy,950,1465+dy),5)
    draw=ImageDraw.Draw(im)
    draw.polygon([(80,205+dy),(890,205+dy),(935,250+dy),(935,1440+dy),
                  (80,1440+dy)],fill=CREAM,outline='#68775F',width=3)
    draw.polygon([(890,205+dy),(890,250+dy),(935,250+dy)],fill='#D6DFCE',
                 outline='#68775F',width=2)
    txt(im,s,n,(140,260+dy),'ILLUSTRATIVE',48,GREEN)
    txt(im,s,n,(140,325+dy),'ANNUAL PREMIUMS',52,GREEN)
    txt(im,s,n,(140,430+dy),'PLAN A',60)
    txt(im,s,n,(140,490+dy),f"${b.parent.C['ppo_annual_premium']:,}",178)
    txt(im,s,n,(140,685+dy),'per year',56,GREEN)
    draw=ImageDraw.Draw(im)
    underline=ease(n/16) if s['id']=='price-a' else 1
    draw.line((140,760+dy,140+round(650*underline),760+dy),fill='#76977A',width=7)
    reveal=s['id']=='price-comparison' and n>=10
    if not reveal:
        p=ease(n/10) if s['id']=='price-comparison' else 0
        height=round(570*(1-p))
        inset=round(35*__import__('math').sin(__import__('math').pi*p))
        draw.polygon([(100,815+dy),(915,815+dy),(915-inset,815+dy+height),
                      (100+inset,815+dy+height)],fill='#E9E6DB',outline='#9B9D8B',width=3)
        if height>310:txt(im,s,n,(150,1010+dy),'PLAN B',70,GREEN)
    else:
        txt(im,s,n,(140,820),'PLAN B',60,GREEN)
        txt(im,s,n,(140,880),f"${b.parent.C['hdhp_annual_premium']:,}",178,GREEN)
        txt(im,s,n,(140,1070),'per year',56,GREEN)
        draw=ImageDraw.Draw(im)
        u=ease((n-10)/12)
        draw.line((140,1155,140+round(650*u),1155),fill='#76977A',width=7)
        txt(im,s,n,(140,1210),'Premiums only',58,GREEN)
        if t>=13.84:
            txt(im,s,n,(140,1310),'Care costs?',56)
            # Magnifier arrives at the still-correct premium document. No
            # arithmetic count-up or invented guaranteed savings number.
            u=ease((t-13.84)/.3);cx=round(940-190*u);cy=1300
            draw=ImageDraw.Draw(im)
            draw.ellipse((cx-55,cy-55,cx+55,cy+55),outline=GREEN,width=7)
            draw.line((cx+40,cy+40,cx+112,cy+112),fill=GREEN,width=13)
    return im


def picture(s,n):
    kind=s['id']
    if kind=='renewal-action':im=opening(s,n)
    elif kind=='four-renewals':im=calendar(s,n)
    elif kind=='ren-reaction':im=reaction(s,n)
    else:im=prices(s,n)
    t=(s['start_frame']+n)/24
    if t<2.5 or t>=13:
        txt(im,s,n,(95,1470),'Educational content only,\nnot financial advice.',
            36,INK,'disclaimer')
    return im


def save_layout():
    grouped={}
    for sid,items in REC.scenes.items():
        merged={}
        for i in items:
            key=(i['text'],i['font_px'],i['role'])
            if key not in merged:merged[key]=dict(i)
            else:
                a=merged[key]
                a['bbox']=[min(a['bbox'][0],i['bbox'][0]),min(a['bbox'][1],i['bbox'][1]),
                           max(a['bbox'][2],i['bbox'][2]),max(a['bbox'][3],i['bbox'][3])]
                a['start']=min(a['start'],i['start']);a['end']=max(a['end'],i['end'])
        grouped[sid]=list(merged.values())
    (R/'layout.json').write_text(json.dumps({'scenes':grouped},indent=2)+'\n')


def main():
    stills='--stills' in sys.argv
    if not stills:
        assert os.environ.get('REN_SHORTS_STAGE')=='prototype'
        assert os.environ.get('REN_SHORTS_MAX_FRAMES')=='360','Only 15s authorized'
    files=[];cache=S.SceneCache(BUILD/'cache')
    deps={a['id']:S.sha(S.resolve(R/'production.json',a['path'])) for a in M['assets']}
    for s in M['scenes']:
        REC.begin_scene(s['id'])
        count=s['end_frame']-s['start_frame']
        key=S.scene_cache_key(s,deps,S.sha(__file__))
        cached=cache.get(key,count)
        if stills:
            for n in [0,count//2,count-1]:picture(s,n).save(BUILD/f"{s['id']}-{n:03}.png")
            continue
        if cached and cached.with_suffix('.layout.json').exists():
            REC.scenes[s['id']]=S.load(cached.with_suffix('.layout.json'));files.append(cached)
            print('Reused verified chunk',s['id'],flush=True);continue
        path=BUILD/(s['id']+'.mp4')
        enc=sp.Popen(['ffmpeg','-v','error','-xerror','-y','-f','rawvideo','-pix_fmt',
                      'rgb24','-s','1080x1920','-r','24','-i','-','-an','-c:v',
                      'libx264','-threads','2','-preset','medium','-crf','18',
                      '-pix_fmt','yuv420p',str(path)],stdin=sp.PIPE)
        for n in range(count):
            im=picture(s,n);enc.stdin.write(im.tobytes())
            if n in [0,count//2,count-1]:im.save(BUILD/f"{s['id']}-{n:03}.png")
        enc.stdin.close();assert enc.wait()==0
        cached=cache.store(key,path,count)
        cached.with_suffix('.layout.json').write_text(json.dumps(REC.scenes[s['id']]))
        files.append(cached);print('Rendered/validated',s['id'],count,'frames',flush=True)
    save_layout()
    if stills:return
    audio=next(a for a in M['assets'] if a['id']=='revision5-audio')
    source=S.resolve(R/'production.json',audio['path'])
    assert S.sha(source)==audio['sha256']
    concat=BUILD/'concat.txt'
    concat.write_text('\n'.join("file '%s'"%p for p in files)+'\n')
    out=S.resolve(R/'production.json',M['prototype'])
    sp.run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i',str(concat),
            '-i',str(source),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy',
            '-movflags','+faststart',str(out)],check=True)


if __name__=='__main__':main()
