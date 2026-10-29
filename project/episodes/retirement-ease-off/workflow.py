"""Episode adapter around the existing quota-safe Qwen pilot workflow."""
import argparse
import fcntl
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / 'project/cliplib'))
import pilot

pilot.BRANCH = 'codex/retirement-ease-off-v3'
pilot.script_segments = lambda folder: json.loads((folder / 'segments.json').read_text())


def init():
    if (BASE / 'manifest.json').exists():
        pilot.load(BASE)
        return
    settings = pilot.current_settings()
    approved = json.loads((ROOT / 'project/pilots/daily-coffee/manifest.json').read_text())
    assert settings == approved['settings'], 'Approved voice settings/reference changed'
    script = (BASE / 'script.md').read_text()
    assert ' '.join(script.split()) == ' '.join(s['text'] for s in pilot.script_segments(BASE))
    m = dict(schema=1, title='When Can You Ease Off Saving for Retirement?',
             created_at=pilot.now(), script_sha256=pilot.digest(BASE / 'script.md'),
             settings=settings, target_duration_s=[420, 450], maximum_duration_s=480,
             segments=[], quota_events=[], overall_status='prepared',
             free_reserve_gpu_seconds=pilot.FREE_RESERVE,
             hardware_policy='public ZeroGPU only; no paid fallback or overquota',
             voice_provenance='Approved v3 rules and identical daily-coffee settings/reference hashes')
    for s in pilot.script_segments(BASE):
        m['segments'].append(dict(**s, settings=settings, fingerprint=pilot.fingerprint(s['text'], settings),
                                  status='pending', attempts=[]))
    pilot.checkpoint(BASE, m)


def calculate():
    sys.path.insert(0, str(ROOT / 'project/pipeline'))
    from calc import check_claims
    a = json.loads((BASE / 'assumptions.json').read_text())
    assert a['years'] == a['retirement_age'] - a['current_age']
    assert a['new_contributions'] == 0
    results = [a['starting_balance'] * (1+r)**a['years'] for r in a['real_returns_after_fees']]
    assert [round(x) for x in results] == [1066335, 656242]
    data = {'bill': 0, 'characters': {'example': dict(a, scenario_a=results[0], scenario_b=results[1])}}
    problems = check_claims(BASE, data)
    assert not problems, problems
    pilot.save(BASE / 'calculations.json', dict(assumptions_sha256=pilot.digest(BASE/'assumptions.json'),
               outcomes=results, displayed_outcomes=[round(x) for x in results],
               spoken_rounding=['roughly one point zero seven million', 'roughly six hundred and fifty-six thousand'],
               status='MATHS OK'))
    print('MATHS OK')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['init','opening','resume','verify','status','calculate','recover-queue-rejection'])
    p.add_argument('--asr-model',type=Path)
    args = p.parse_args()
    with (BASE / '.workflow.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command == 'calculate':
            calculate(); return
        init()
        if args.command=='recover-queue-rejection':
            m=pilot.load(BASE)
            candidates=[s for s in m['segments'] if s['status']=='failed']
            if len(candidates)!=1: raise ValueError('Expected exactly one reviewed queue rejection')
            s=candidates[0]; a=s['attempts'][-1]
            if not (a.get('error_type')=='QueueError' and a.get('error')=='Queue is full! Please try again.'
                    and a.get('phase')=='queue_submission' and not a.get('event_id')
                    and a.get('observed_quota_decrease_gpu_seconds')==0 and len(s['attempts'])==1):
                raise ValueError('Not an uncharged pre-admission rejection; manual recovery required')
            s['status']='pending'
            s['recovery']={'at':pilot.now(),'reason':'Explicit operator recovery of queue-full rejection; no event admitted, no charge; original failure retained'}
            m['overall_status']='ready_after_explicit_queue_recovery'
            pilot.checkpoint(BASE,m,True)
            print('Queue rejection reviewed and re-armed. No generation submitted. Run resume separately.'); return
        if args.command in ('opening','resume'):
            m = pilot.load(BASE)
            if args.command == 'resume' and not m.get('opening_technical_review'):
                raise ValueError('Run and inspect opening before remaining narration')
            if args.command == 'opening' and m['segments'][0]['status'] == 'complete':
                print('Opening already exists; not regenerated'); return
            pilot.resume(BASE, True, max_segments=1 if args.command == 'opening' else None)
        elif args.command == 'verify':
            pilot.verify(BASE,args.asr_model)
        elif args.command == 'status':
            m = pilot.load(BASE)
            print(json.dumps({'status':m['overall_status'], 'quota':m.get('quota'),
                  'remaining':[s['id'] for s in m['segments'] if s['status']!='complete']},indent=2))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        raise SystemExit(pilot.safe_error(e)) from None
