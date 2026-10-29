"""Episode-specific structural/audio/equation checks adapted from v3 validation."""
import argparse
import importlib.util
import json
import subprocess as sp
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('episode_renderer',BASE/'render.py')
episode=importlib.util.module_from_spec(spec); spec.loader.exec_module(episode)

def probe(path):
    return json.loads(sp.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))

def pcm(path):
    return np.frombuffer(sp.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--preview',action='store_true'); ap.add_argument('--plan',action='store_true'); args=ap.parse_args()
    shots_path=BASE/('planned-shots.json' if args.plan else 'preview-shots.json' if args.preview else 'shots.json')
    m=json.loads(shots_path.read_text()); shots=m['shots']; v=episode.v3
    assert sum(s['frames'] for s in shots)==m['frames']
    assert all(a['end_frame']==b['start_frame'] for a,b in zip(shots,shots[1:]))
    for a,b in zip(shots,shots[1:]):
        if a['kind']==b['kind']=='graphic':
            assert episode.picture(a,a['frames']-1).tobytes()!=episode.picture(b,0).tobytes(), (a['id'],b['id'],'identical graphic cut')
    for i,s in enumerate(shots):
        assert 0<s['frames']<=(132 if s['kind']=='ren' else 60 if s['kind']=='story' else 84)
        assert not s['mirrored']
        if s['kind']=='ren':
            source=episode.ROOT/'assets/ren_library'/f"ren_{s['clip']}.mp4"
            p=probe(source)
            assert (p['streams'][0]['width'],p['streams'][0]['height'])==(1280,720)
            assert s['source_start_s']+s['frames']/24<=float(p['format']['duration'])
            if i and shots[i-1]['kind']=='ren': assert shots[i-1]['clip']!=s['clip']
    art={}
    for a in json.loads((Path(v.__file__).parent/'artwork/manifest.json').read_text()):
        actual=episode.digest(Path(v.__file__).parent/'assets'/a['file']); assert actual==a['sha256']; art[a['file']]=actual
    # Pixel-stability test is episode-specific: fixed approximate-compound
    # expressions and all labels, while only the separate timeline animates.
    equation_frames=0
    for s in shots:
        if s['kind']=='graphic' and s['motif'] in ('scenario_a','scenario_b','comparison'):
            box=(50,240,1230,610); baseline=episode.picture(s,0).crop(box).tobytes()
            for f in range(s['frames']):
                assert episode.picture(s,f).crop(box).tobytes()==baseline
                equation_frames+=1
    report=dict(mode='provisional planning only' if args.plan else 'opening preview' if args.preview else 'full episode',
                shots=len(shots),shot_limits='pass',frames=m['frames'],artwork_sha256=art,
                equation_frames_checked=equation_frames,fixed_correct_equations='pass',
                no_reference_similarity_target=True,source_dimensions=[1280,720],
                listening='not performed; pronunciation, words and identity unconfirmed')
    if not args.plan:
        out=BASE/'build'/('preview' if args.preview else 'full')
        for s in shots:
            path=out/(s['id']+'.mp4'); v.check_video(path,s['frames'])
            assert len(probe(path)['streams'])==1, 'Source audio leaked into shot'
        final=BASE/'deliverables'/('Ren_Retirement_Opening_v3.mp4' if args.preview else 'Ren_When_Can_You_Ease_Off_Saving_v3.mp4')
        p=probe(final); video=next(s for s in p['streams'] if s['codec_type']=='video'); audio=next(s for s in p['streams'] if s['codec_type']=='audio')
        assert (video['width'],video['height'],video['r_frame_rate'],video['codec_name'],audio['codec_name'])==(1280,720,'24/1','h264','aac')
        assert int(video['nb_read_frames'])==m['frames']
        assert float(p['format']['duration'])<480
        assert abs(float(video['duration'])-float(audio['duration']))<1/24
        decoded=sp.run(['ffmpeg','-v','error','-xerror','-i',str(final),'-f','null','-'],capture_output=True,text=True,check=True); assert not decoded.stderr
        track=BASE/'build'/('preview-narration.wav' if args.preview else 'narration.wav')
        x,y=pcm(track),pcm(final); n=min(len(x),len(y)); assert abs(len(x)-len(y))<2048
        correlation=float(np.corrcoef(x[:n],y[:n])[0,1]); assert correlation>.99
        report.update(duration_s=float(p['format']['duration']),video_frames=int(video['nb_read_frames']),
                      audio_source_correlation=correlation,full_decode='pass',every_encoded_shot_count='pass',
                      final_sha256=episode.digest(final),narration_sha256=episode.digest(track))
    episode.save(BASE/('planning-validation.json' if args.plan else 'preview-validation.json' if args.preview else 'validation.json'),report)
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
