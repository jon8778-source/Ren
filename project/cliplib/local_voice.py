"""Generate Ren narration using a locally hosted Qwen Base model; no training needed.
Install requirements-voice-local.txt separately. Downloads model weights on first use.
"""
import argparse
import json
from pathlib import Path

REF = Path(__file__).resolve().parents[2] / 'Audio'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('shots', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model', default='Qwen/Qwen3-TTS-12Hz-1.7B-Base')
    ap.add_argument('--device', default='cuda:0')
    args = ap.parse_args()
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel
    model = Qwen3TTSModel.from_pretrained(args.model, device_map=args.device,
        dtype=torch.bfloat16 if args.device.startswith('cuda') else torch.float32,
        attn_implementation='sdpa')
    # Compute once, reuse for all new lines. This is a voice prompt, not separately trained weights.
    prompt = model.create_voice_clone_prompt(ref_audio=str(REF / 'ren_reference.wav'),
        ref_text=(REF / 'ren_reference.txt').read_text().strip().strip('"“”').strip(),
        x_vector_only_mode=False)
    args.out.mkdir(parents=True, exist_ok=True)
    for i, shot in enumerate(json.loads(args.shots.read_text())['shots'], 1):
        text = shot.get('voice', '').strip()
        if not text:
            raise ValueError(f'shot {i}: voice text required for this narration workflow')
        audio, sr = model.generate_voice_clone(text=text, language='English', voice_clone_prompt=prompt)
        path = args.out / f'line_{i:02d}.wav'
        sf.write(path, audio[0], sr)
        print(path, flush=True)


if __name__ == '__main__':
    main()
