"""Export encoded review evidence without TTS or changes to the video."""
import json
import subprocess as sp
from pathlib import Path
from PIL import Image,ImageDraw

BASE=Path(__file__).resolve().parent
VIDEO=BASE/'deliverables/Ren_When_Can_You_Ease_Off_Saving_v3.mp4'
SHOTS=json.loads((BASE/'shots.json').read_text())['shots']
OUT=BASE/'review'; OUT.mkdir(exist_ok=True)

def extract(indices,prefix):
    indices=sorted(set(indices))
    # Bounded expression groups avoid FFmpeg's expression recursion limit.
    terms=[f'eq(n,{i})' for i in indices]
    expr='+'.join('('+ '+'.join(terms[i:i+24])+')' for i in range(0,len(terms),24))
    expr=expr.replace(',',r'\,')
    sp.run(['ffmpeg','-v','error','-xerror','-y','-i',str(VIDEO),'-vf',f'select={expr},scale=320:180',
            '-fps_mode','vfr',str(OUT/f'{prefix}-%03d.jpg')],check=True)
    files=sorted(OUT.glob(f'{prefix}-*.jpg')); assert len(files)==len(indices)
    return files

def contact(files,prefix):
    for page in range((len(files)+23)//24):
        batch=files[page*24:(page+1)*24]
        sheet=Image.new('RGB',(1280,180*((len(batch)+3)//4)),'#FAF6EE')
        for i,path in enumerate(batch):
            im=Image.open(path).copy();ImageDraw.Draw(im).text((5,5),str(page*24+i+1),fill='black',stroke_width=2,stroke_fill='white')
            sheet.paste(im,((i%4)*320,(i//4)*180))
        sheet.save(OUT/f'{prefix}-{page+1}.jpg')

def main():
    mids=extract([s['start_frame']+s['frames']//2 for s in SHOTS],'encoded-frame')
    contact(mids,'encoded-contact')
    sheet=Image.new('RGB',(1280,180*((len(mids)+3)//4)),'#FAF6EE')
    for i,path in enumerate(mids):
        im=Image.open(path).copy();ImageDraw.Draw(im).text((5,5),SHOTS[i]['id'],fill='black',stroke_width=2,stroke_fill='white')
        sheet.paste(im,((i%4)*320,(i//4)*180))
    sheet.save(BASE/'deliverables/shot-contact-sheet.jpg')
    boundaries=list(range(1,len(SHOTS),max(1,len(SHOTS)//12)))
    frames=[]
    for i in boundaries:
        n=SHOTS[i]['start_frame'];frames.extend([n-7,n-2,n-1,n,n+1,n+6])
    contact(extract(frames,'motion-frame'),'motion-contact')
    (BASE/'review-evidence.json').write_text(json.dumps({'encoded_shot_midpoints':len(mids),
       'transition_boundaries_sampled':len(boundaries),'frames_per_boundary':6,
       'transition_offsets_frames':[-7,-2,-1,0,1,6],
       'note':'Frame samples, not a claim of full-motion playback or listening'},indent=2)+'\n')
    print('Encoded contact sheet and motion samples ready')

if __name__=='__main__':main()
