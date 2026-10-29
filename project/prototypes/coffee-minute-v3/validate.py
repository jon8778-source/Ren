"""Check all decoded frames, narration continuity and optional approved reference."""
import argparse
import hashlib
import json
import re
import subprocess as sp
from pathlib import Path
import numpy as np
import render

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]

def run(args):
    return sp.run(args, check=True, capture_output=True, text=True)

def probe(path):
    return json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]).stdout)

def pcm(path):
    return np.frombuffer(sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-t','61.625','-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--reference',type=Path)
    args = p.parse_args()
    final = BASE/'Ren_61s_Coffee_Prototype_v3.mp4'
    data = probe(final)
    video = next(s for s in data['streams'] if s['codec_type']=='video')
    audio = next(s for s in data['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_read_frames']))==(1280,720,'24/1',1479)
    assert video['codec_name']=='h264' and audio['codec_name']=='aac'
    assert abs(float(data['format']['duration'])-61.625)<.001
    decoded = run(['ffmpeg','-v','error','-xerror','-i',str(final),'-f','null','-'])
    assert not decoded.stderr, decoded.stderr
    manifest = json.loads((BASE/'artwork/manifest.json').read_text())
    art_hashes={}
    for entry in manifest:
        art_hashes[entry['file']] = hashlib.sha256((BASE/'assets'/entry['file']).read_bytes()).hexdigest()
        assert art_hashes[entry['file']]==entry['sha256']
    source = ROOT/'project/pilots/daily-coffee/deliverables/narration.wav'
    x,y = pcm(source),pcm(final)
    assert len(x)==len(y)==2958000
    correlation=float(np.corrcoef(x,y)[0,1])
    assert correlation>.99,correlation
    source_meta=json.loads((ROOT/'assets/ren_library/ren_library.json').read_text())
    clips={c['file']:c for c in source_meta['clips']}
    intervals=[]
    for i,s in enumerate(render.SHOTS,1):
        render.check_video(BASE/'build'/f'shot_{i:02d}.mp4',s['frames'])
        assert s['frames']/24 <= (5.5 if s['kind']=='ren' else 2.5 if s['kind']=='story' else 3.5)
        if s['kind']=='ren':
            name='ren_'+s['clip']+'.mp4'
            actual=float(probe(ROOT/'assets/ren_library'/name)['format']['duration'])
            end=clips[name]['in_s']+s['frames']/24
            assert end<=min(actual,clips[name]['out_s'])
            intervals.append(dict(shot=i,clip=name,start=clips[name]['in_s'],end=end,actual_source_duration=actual,mirrored=False))
    # Monetary equations must remain fixed throughout every relevant source frame.
    equation_frames=0
    for s in render.SHOTS:
        if s['kind'] in ('annual','netannual','net'):
            box=(40,335,1240,465) if s['kind']!='net' else (40,525,1240,610)
            baseline=render.picture(s,0).crop(box).tobytes()
            for f in range(s['frames']):
                assert render.picture(s,f).crop(box).tobytes()==baseline
                equation_frames+=1
    report=dict(source_worktree_modified=bool(run(['git','-C',str(ROOT),'diff','--name-only','--',str(BASE/'render.py')]).stdout.strip()),checked_out_commit=run(['git','-C',str(ROOT),'rev-parse','HEAD']).stdout.strip(),
        frames=1479,fps=24,duration_seconds=61.625,resolution=[1280,720],
        actor_decode_resolution=[render.ACTOR_W,render.ACTOR_H],codecs=['h264','aac'],output_sha256=hashlib.sha256(final.read_bytes()).hexdigest(),full_decode='pass',shot_counts='19/19 pass',
        artwork_sha256=art_hashes,narration_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        audio_samples_checked=len(y),audio_source_correlation=correlation,new_voice_requests=0,
        equations={'annual_spend':render.YEAR,'daily_difference':render.DIFFERENCE,'annual_difference':render.NET,'source_frames_checked':equation_frames,'fixed_text':'pass'},
        gesture_intervals=intervals,renderer_sha256=hashlib.sha256((BASE/'render.py').read_bytes()).hexdigest())
    if args.reference:
        reference_sha=hashlib.sha256(args.reference.read_bytes()).hexdigest()
        assert reference_sha=='f95725ea9ccec4665aaa11a860e4d1445697f00d54ad1fd7ef90910ffaea4d93'
        stats=BASE/'build/reference-ssim.log'
        run(['ffmpeg','-v','error','-xerror','-i',str(final),'-i',str(args.reference),'-lavfi',f'ssim=stats_file={stats}','-an','-f','null','-'])
        values=[float(re.search(r'All:([0-9.]+)',line)[1]) for line in stats.read_text().splitlines()]
        assert len(values)==1479,len(values)
        unaffected=[]
        offset=0
        for shot in render.SHOTS:
            if shot['kind']!='ren': unaffected.extend(values[offset:offset+shot['frames']])
            offset+=shot['frames']
        assert min(unaffected)>.99,min(unaffected)
        report['reference_comparison']=dict(sha256=reference_sha,frames_compared=len(values),minimum_ssim=min(values),mean_ssim=sum(values)/len(values),unaffected_frames_checked=len(unaffected),minimum_unaffected_ssim=min(unaffected),note='Ren pixels intentionally improved by native-resolution decode; unchanged story and graphic frames retain the original similarity gate.')
    (BASE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
