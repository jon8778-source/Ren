import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'qwen_voice.py'
spec = importlib.util.spec_from_file_location('qwen_voice', MODULE)
voice = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voice)


class VoiceDurationTests(unittest.TestCase):
    def test_coffee_limit_includes_ten_seconds(self):
        with patch.object(voice.subprocess, 'check_output', return_value=b'10.0\n'):
            self.assertEqual(voice.validate_generated_duration(voice.COFFEE_TEST_TEXT, 'audio.wav'), 10)

    def test_coffee_rejects_more_than_ten_seconds(self):
        with patch.object(voice.subprocess, 'check_output', return_value=b'10.001\n'):
            with self.assertRaisesRegex(ValueError, 'generation failed'):
                voice.validate_generated_duration(voice.COFFEE_TEST_TEXT, 'audio.wav')

    def test_limit_is_specific_to_coffee_sentence(self):
        with patch.object(voice.subprocess, 'check_output', return_value=b'12\n'):
            self.assertEqual(voice.validate_generated_duration('A different narration.', 'audio.wav'), 12)

    def test_rejects_invalid_duration(self):
        for duration in (b'nan', b'inf', b'0', b'-1'):
            with self.subTest(duration=duration):
                with patch.object(voice.subprocess, 'check_output', return_value=duration):
                    with self.assertRaisesRegex(ValueError, 'invalid duration'):
                        voice.validate_generated_duration(voice.COFFEE_TEST_TEXT, 'audio.wav')

    def test_overlong_result_stops_without_accepted_file_or_second_call(self):
        self.check_overlong_result([])

    def test_xvector_only_retains_rejection_guard(self):
        self.check_overlong_result(['--xvector-only'])

    def check_overlong_result(self, extra_args):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shots = folder / 'shots.json'
            shots.write_text(json.dumps({'shots': [{'voice': voice.COFFEE_TEST_TEXT}, {'voice': 'Do not generate.'}]}))
            output = folder / 'voice'
            with patch.object(voice, 'Client') as client, \
                 patch.object(voice, 'handle_file', return_value='reference'), \
                 patch.object(voice.subprocess, 'check_output', return_value=b'163.597708'), \
                 patch.object(voice.shutil, 'copyfile') as copy, \
                 patch.object(sys, 'argv',
                              ['qwen_voice.py', str(shots), '--out', str(output), '--only', '1'] + extra_args):
                client.return_value.predict.return_value = ('returned.wav', 'Success')
                with self.assertRaisesRegex(SystemExit, 'Output rejected'):
                    voice.main()
                client.return_value.predict.assert_called_once()
                kwargs = client.return_value.predict.call_args.kwargs
                self.assertEqual(kwargs['target_text'], voice.COFFEE_TEST_TEXT)
                self.assertEqual(kwargs['model_size'], '1.7B')
                self.assertEqual(kwargs['api_name'], '/generate_voice_clone')
                self.assertEqual(kwargs['use_xvector_only'], bool(extra_args))
                copy.assert_called_once_with('returned.wav', output / 'rejected_line_01.wav')
                self.assertFalse((output / 'line_01.wav').exists())


if __name__ == '__main__':
    unittest.main()
