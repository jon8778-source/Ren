"""Gate and detector regressions. No voice requests or video renders."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import shorts_standards as s


class StandardsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)
        self.path = self.d/'production.json'
        (self.d/'assets.md').write_text('Actual approved inventory fixture')
        assets = []
        for kind in ('script','audio','renderer','configuration','character','environment'):
            p = self.d/(kind+'.fixture');p.write_text(kind)
            assets.append(dict(id=kind, path=p.name, kind=kind, sha256=s.sha(p),
                               status='approved', approval_evidence='Test fixture only'))
        scenes = [dict(id=f's{i}', start_frame=i*72, end_frame=(i+1)*72,
                       composition=f'composition-{i}', kind='action', action='click/reveal',
                       motion_purpose='show choice', assets=['environment','character'],
                       animations=[f'animation-{i}'], environment_fullscreen=True)
                  for i in range(5)]
        self.m = dict(schema_version=1,width=1080,height=1920,fps=24,frames=360,
                      full_bleed=True,permanent_border=False,asset_report='assets.md',
                      assets=assets, scenes=scenes, audio_cues=[dict(start=0,end=15)],
                      layout_evidence='layout.json',prototype='prototype.mp4',
                      prototype_report='prototype.qa.json')
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.m))

    def errors(self):
        self.save();return s.preflight(self.path)['errors']

    def test_valid_asset_preflight(self):
        self.assertEqual([],self.errors())

    def test_missing_and_changed_assets(self):
        (self.d/'audio.fixture').unlink()
        (self.d/'character.fixture').write_text('substitution')
        self.assertTrue(any('Missing asset' in e for e in self.errors()))
        self.assertTrue(any('Changed/unhashed' in e for e in self.errors()))

    def test_unapproved_asset(self):
        self.m['assets'][4]['status']='temporary'
        self.assertTrue(any('Unapproved' in e for e in self.errors()))

    def test_fullscreen_and_composition_gate(self):
        self.m['permanent_border']=True
        for c in self.m['scenes']:
            c['composition']='same';c['environment_fullscreen']=False
        errors=self.errors()
        self.assertTrue(any('full-bleed' in e for e in errors))
        self.assertTrue(any('three distinct' in e for e in errors))
        self.assertTrue(any('full-screen' in e for e in errors))

    def test_gap_duplicate_ids_and_repeated_animation(self):
        self.m['scenes'][1]['start_frame']=73
        self.m['scenes'][1]['id']='s0'
        self.m['scenes'][1]['animations']=['animation-0']
        errors=self.errors()
        self.assertTrue(any('gap/overlap' in e for e in errors))
        self.assertTrue(any('unique' in e for e in errors))
        self.assertTrue(any('Repeated animation' in e for e in errors))

    def test_approved_repeat_is_not_rejected(self):
        self.m['scenes'][1]['animations']=['animation-0']
        self.m['scenes'][1]['repeat_justification']='same action recalled for consequence'
        self.assertEqual([],self.errors())

    def test_cues_outside_timeline_rejected(self):
        self.m['audio_cues'][0]['end']=16
        self.assertTrue(any('Narration cues' in e for e in self.errors()))

    def layout(self):
        x={'scenes': {c['id']:[] for c in self.m['scenes']}}
        x['scenes']['s4']=[dict(text=s.DISCLAIMER,bbox=[72,1400,850,1500],
                             font_px=30,role='disclaimer',start=13,end=15)]
        return x

    def test_layout_and_disclaimer(self):
        self.assertEqual([],s.check_layout(self.m,self.layout(),15))
        x=self.layout();x['scenes']['s4'][0]['bbox'][2]=1000
        self.assertTrue(any('safe area' in e for e in s.check_layout(self.m,x,15)))
        x=self.layout();x['scenes']['s4'][0]['text']='Educational only'
        self.assertTrue(any('disclaimer' in e for e in s.check_layout(self.m,x,15)))

    def test_missing_layout_and_small_text(self):
        x=self.layout();del x['scenes']['s0'];x['scenes']['s4'][0]['font_px']=20
        errors=s.check_layout(self.m,x,15)
        self.assertTrue(any('Missing measured' in e for e in errors))
        self.assertTrue(any('too small' in e for e in errors))

    def approval_fixture(self):
        preview=self.d/'prototype.mp4';preview.write_bytes(b'fixture media, not an encoded video')
        report=self.d/'prototype.qa.json'
        report.write_text(json.dumps(dict(errors=[],stage='prototype',status='technical-pass-review-required',
            fingerprint=s.fingerprint(self.path),video_sha256=s.sha(preview))))
        approval=self.d/'prototype-approval.json'
        approval.write_text(json.dumps(dict(by='Jon',evidence='Fixture explicit approval',approved_at='fixture',review_notes='Fixture reviewed, not real media approval',
            fingerprint=s.fingerprint(self.path),prototype_sha256=s.sha(preview),report_sha256=s.sha(report))))
        return preview,report,approval

    def test_matching_approval_and_stale_input(self):
        p,r,a=self.approval_fixture();s.approved(self.path,p,r,a)
        (self.d/'character.fixture').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Stale'):s.approved(self.path,p,r,a)

    def test_stale_preview_or_report(self):
        p,r,a=self.approval_fixture();p.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Stale'):s.approved(self.path,p,r,a)
        p,r,a=self.approval_fixture();r.write_text(r.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'Stale'):s.approved(self.path,p,r,a)

    def test_full_render_never_runs_without_approval(self):
        with patch.object(s.subprocess,'run') as run:
            with self.assertRaises(OSError):
                s.main(['run','--manifest',str(self.path),'--stage','full',
                        '--output',str(self.d/'final.mp4'),'--','renderer'])
            run.assert_not_called()

    def test_layout_recorder_uses_measured_font_box(self):
        from PIL import Image,ImageDraw,ImageFont
        draw=ImageDraw.Draw(Image.new('RGB',(1080,1920)))
        font=ImageFont.truetype(str(Path(__file__).resolve().parents[2]/'remotion/public/fonts/fredoka-latin-600-normal.woff2'),42)
        recorder=s.LayoutRecorder();recorder.begin_scene('empty')
        box=recorder.record('s0',draw,(80,200),'Actual text',font,0,2)
        self.assertEqual(box,draw.multiline_textbbox((80,200),'Actual text',font=font))
        target=self.d/'layout.json';recorder.save(target)
        self.assertEqual([],s.load(target)['scenes']['empty'])

    def test_missing_review_notes_block_approval(self):
        p,r,a=self.approval_fixture();data=s.load(a);del data['review_notes'];a.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'approval evidence'):s.approved(self.path,p,r,a)

    def test_cache_invalidates_only_changed_inputs(self):
        scene=self.m['scenes'][0]
        self.assertEqual(s.scene_cache_key(scene,{'art':'a'},'r'),s.scene_cache_key(scene,{'art':'a'},'r'))
        self.assertNotEqual(s.scene_cache_key(scene,{'art':'a'},'r'),s.scene_cache_key(scene,{'art':'b'},'r'))

    def test_scene_cache_checks_frames_and_corruption(self):
        cache=s.SceneCache(self.d/'cache');key=s.scene_cache_key({'id':'s0'},{'art':'a'},'r')
        video=self.d/'chunk.mp4';video.write_bytes(b'encoded fixture')
        streams=[dict(codec_type='video',width=1080,height=1920,r_frame_rate='24/1',
            codec_name='h264',pix_fmt='yuv420p',nb_read_frames='72')]
        with patch.object(s.subprocess,'check_output',return_value=json.dumps(dict(streams=streams))),patch.object(s.subprocess,'run'):
            cached=cache.store(key,video,72)
        self.assertEqual(cached,cache.get(key,72));self.assertIsNone(cache.get(key,73))
        cached.write_bytes(b'corrupt');self.assertIsNone(cache.get(key,72))
        with self.assertRaises(ValueError):cache.get('../escape',72)

    def test_border_freeze_and_black_detection(self):
        rng=np.random.default_rng(5)
        x=rng.integers(30,240,(48,192,108,3),dtype='uint8')
        self.assertEqual([],s.pixel_checks(x)[0]);self.assertEqual([],s.pixel_checks(x)[1])
        x[:,:4]=0;x[:,-4:]=0
        self.assertTrue(any('black bars' in e for e in s.pixel_checks(x)[0]))
        x[:]=[23,42,58]
        self.assertTrue(any('uniform edge' in e for e in s.pixel_checks(x)[1]))
        self.assertTrue(any('duplicate' in e for e in s.pixel_checks(x)[1]))
        x[:]=0;self.assertTrue(any('Black/blank' in e for e in s.pixel_checks(x)[0]))

    def test_audio_video_frame_validation(self):
        streams=[dict(codec_type='video',width=1080,height=1920,r_frame_rate='24/1',
             codec_name='h264',pix_fmt='yuv420p',nb_read_frames='24',start_time='0',duration='1'),
             dict(codec_type='audio',codec_name='aac',start_time='0',duration='1')]
        probe=dict(streams=streams,format=dict(duration='1'))
        timeline=dict(frames=[dict(best_effort_timestamp_time=str(i/24)) for i in range(24)])
        raw=np.random.default_rng(1).integers(30,240,(24,192,108,3),dtype='uint8').tobytes()
        with patch.object(s.subprocess,'check_output',side_effect=[json.dumps(probe),json.dumps(timeline),raw]),patch.object(s.subprocess,'run'):
            self.assertEqual([],s.media_qa('fixture.mp4',1)['errors'])
        streams[1]['start_time']='.3';timeline['frames'][2]['best_effort_timestamp_time']='.4'
        with patch.object(s.subprocess,'check_output',side_effect=[json.dumps(probe),json.dumps(timeline),raw]),patch.object(s.subprocess,'run'):
            errors=s.media_qa('fixture.mp4',1)['errors']
            self.assertTrue(any('A/V' in e for e in errors))
            self.assertTrue(any('timestamps' in e for e in errors))


if __name__=='__main__':unittest.main()
