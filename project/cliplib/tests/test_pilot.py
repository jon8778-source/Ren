import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pilot
import pilot_render


class PilotTests(unittest.TestCase):
    def fixture(self, folder, status='pending'):
        text = pilot.COFFEE_TEST_TEXT
        (folder / 'script.md').write_text(f'## s001 — Question\n{text}\n')
        settings = pilot.current_settings()
        segment = {'id': 's001', 'title': 'Question', 'text': text, 'settings': settings,
                   'fingerprint': pilot.fingerprint(text, settings), 'status': status, 'attempts': []}
        m = {'segments': [segment], 'settings': settings, 'quota_events': [], 'overall_status': 'prepared'}
        pilot.save(folder / 'manifest.json', m)
        return m

    def tone(self, path, seconds=2.4):
        t = np.arange(round(24000 * seconds)) / 24000
        sf.write(path, .1 * np.sin(2 * np.pi * 140 * t), 24000, subtype='PCM_16')

    def test_fingerprint_changes_with_text_or_settings(self):
        a = pilot.fingerprint('hello', {'voice': 'one'})
        self.assertNotEqual(a, pilot.fingerprint('hello!', {'voice': 'one'}))
        self.assertNotEqual(a, pilot.fingerprint('hello', {'voice': 'two'}))

    def test_rejects_silence_and_runaway(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'test.wav'
            sf.write(p, np.zeros(24000 * 3), 24000)
            with self.assertRaisesRegex(ValueError, 'ilent'):
                pilot.inspect_audio(p, pilot.COFFEE_TEST_TEXT)
            self.tone(p, 11)
            with self.assertRaisesRegex(ValueError, 'Duration'):
                pilot.inspect_audio(p, pilot.COFFEE_TEST_TEXT)

    def test_modified_text_and_bytes_become_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            m = self.fixture(folder, 'complete')
            self.tone(folder / 'raw.wav')
            m['segments'][0].update(file='raw.wav', sha256=pilot.digest(folder / 'raw.wav'))
            pilot.save(folder / 'manifest.json', m)
            self.assertEqual(pilot.load(folder)['segments'][0]['status'], 'complete')
            (folder / 'raw.wav').write_bytes(b'corrupted')
            self.assertEqual(pilot.load(folder)['segments'][0]['status'], 'stale')
            (folder / 'script.md').write_text('## s001 — Question\nA changed sentence.\n')
            self.assertEqual(pilot.load(folder)['segments'][0]['status'], 'stale')

    def test_quota_stop_has_no_generation_call(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {'HF_TOKEN': 'test'}), \
             patch('huggingface_hub.HfApi') as api, patch('gradio_client.Client') as client:
            folder = Path(tmp)
            self.fixture(folder)
            api.return_value.get_space_runtime.return_value = SimpleNamespace(hardware='zero-a10g', stage='RUNNING')
            api.return_value.get_zero_gpu_quota.return_value = SimpleNamespace(
                remaining=80, base=300, overquota_used=0, resets_at=None)
            pilot.resume(folder, False)
            client.assert_not_called()
            self.assertEqual(json.loads((folder / 'manifest.json').read_text())['overall_status'], 'quota_checkpoint')

    def test_interrupted_request_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {'HF_TOKEN': 'test'}), \
             patch('gradio_client.Client') as client:
            folder = Path(tmp)
            self.fixture(folder, 'inflight')
            with self.assertRaisesRegex(ValueError, 'recovery'):
                pilot.resume(folder, False)
            client.assert_not_called()

    def test_valid_original_saved_and_reused_without_regeneration(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {'HF_TOKEN': 'test'}), \
             patch('huggingface_hub.HfApi') as api, patch('gradio_client.Client') as client, \
             patch('gradio_client.handle_file', return_value='reference'):
            folder = Path(tmp)
            self.fixture(folder)
            raw = folder / 'returned.wav'
            self.tone(raw)
            api.return_value.get_space_runtime.return_value = SimpleNamespace(hardware='zero-a10g', stage='RUNNING')
            api.return_value.get_zero_gpu_quota.return_value = SimpleNamespace(
                remaining=250, base=300, overquota_used=0, resets_at=None)
            client.return_value.predict.return_value = (str(raw), 'Success')
            pilot.resume(folder, False)
            m = pilot.load(folder)
            s = m['segments'][0]
            self.assertEqual(s['status'], 'complete')
            self.assertEqual((folder / s['file']).read_bytes(), raw.read_bytes())
            pilot.resume(folder, False)
            client.return_value.predict.assert_called_once()
            self.assertTrue(client.return_value.predict.call_args.kwargs['use_xvector_only'])

    def test_incomplete_pilot_cannot_be_assembled(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.fixture(folder)
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                pilot_render.assemble(folder)

    def test_visual_cuts_preserve_duration_and_shot_limits(self):
        for frames in (59, 120, 500, 801):
            plan = pilot_render.cuts(frames)
            self.assertEqual(sum(n for _, n in plan), frames)
            for kind, n in plan:
                self.assertGreater(n, 0)
                self.assertLessEqual(n, {'ren': 108, 'graphic': 78, 'story': 54}[kind])

    def test_transcription_comparison_detects_changed_words(self):
        self.assertEqual(pilot.word_error_rate('Keep the coffee.', 'Keep the coffee'), 0)
        self.assertGreater(pilot.word_error_rate('Keep the coffee.', 'Cut the coffee'), .1)


if __name__ == '__main__':
    unittest.main()
