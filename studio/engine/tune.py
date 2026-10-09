#!/usr/bin/env python3
"""Find the value of one setting that passes a critic's accept test, by proof renders instead of a guess.

    python3 studio/engine/tune.py SHOT REPLY c3 lights.roof_ramp.strength 0.5 1.5 [--save] [--samples 16] [--max 4]
    python3 studio/engine/tune.py SHOT REPLY '{"region": {"part": "woofer-cone"}, "metric": "lum_p95", "op": "between",
        "value": [110, 160]}' glints.1.power_w,glints.2.power_w 8 24 --save      (a test of your own; knobs set alike)

A critic says what the next image must measure ("the slope falls at least 10 levels from under the fin to the eave")
and which setting moves it; how far to move it is a guess until something is rendered. This renders proofs at the
critic's scale (0.75, so its regions line up) with the setting at the two values given, reads the test exactly as
`critic/round.py check` will, and moves the setting along the secant between the last two proofs toward a reading a
margin inside the test (the middle of a "between"), up to --max proofs. It prints every proof's reading, and every
other test of the reply on that proof, and with --save writes the best value into the shot: the passing one nearest
the aim, else the nearest to passing.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / 'critic'))
import shot as S  # noqa: E402
import knobs as K  # noqa: E402
import measure as Me  # noqa: E402


def aim(t, margin):
    v, op = t['value'], t['op']
    if op == 'between':
        return (v[0] + v[1]) / 2
    if margin is None:
        margin = min(15.0, max(1.0, 0.2 * abs(v))) if v else 3.0
    return v + margin if op in ('>', '>=') else v - margin


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('shot'); ap.add_argument('reply'); ap.add_argument('change'); ap.add_argument('knob')
    ap.add_argument('v0', type=float); ap.add_argument('v1', type=float)
    ap.add_argument('--samples', type=int, default=16); ap.add_argument('--scale', type=float, default=0.75)
    ap.add_argument('--max', type=int, default=4); ap.add_argument('--margin', type=float)
    ap.add_argument('--save', action='store_true')
    a = ap.parse_args()
    reply = json.loads(Path(a.reply).read_text())
    tests = [dict(c['accept'], id=c['id']) for c in reply['changes'] if c.get('accept')]
    if a.change.lstrip().startswith('{'):
        t = dict(json.loads(a.change), id='tune'); tests.append(t); a.change = 'tune'
    else:
        t = next(x for x in tests if x['id'] == a.change)
    knobs = a.knob.split(',')
    goal = aim(t, a.margin)
    rng = (K.describe(knobs[0]) or (None, None, None))[1]
    parts = any(isinstance(x['region'], (str, dict)) for x in tests)
    td = Path(tempfile.mkdtemp(prefix='tune-'))
    proofs = []

    def proof(v):
        out = td / f'proof-{len(proofs)}.png'
        cmd = [sys.executable, str(HERE / 'render.py'), a.shot, '--out', str(out), '--samples', str(a.samples),
               '--scale', str(a.scale)] + sum((['--set', f'{k}={v:.6g}'] for k in knobs), []) + (['--masks'] if parts else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode or not out.exists():
            raise SystemExit(r.stderr[-2000:])
        MeMASK = Me.MASK; MeMASK.clear()
        _, arr = Me.load(out); Me.load_mask(out)
        res = Me.check(arr, tests)['tests']
        mine = next(x for x in res if x['id'] == a.change)
        proofs.append((v, mine['measured'], mine['pass'], res))
        others = ', '.join(f"{x['id']} {x['measured']}{'' if x['pass'] else ' FAIL'}" for x in res if x['id'] != a.change)
        print(f"  {a.knob} = {v:.4g}: {t['metric']} {mine['measured']} ({'pass' if mine['pass'] else 'FAIL'}; aim {goal:.4g})   others: {others}",
              flush=True)
        return mine['measured']

    print(f"{a.shot}: {a.change} wants {t['metric']} {t['op']} {t['value']}; tuning {a.knob}")
    f0, f1 = proof(a.v0), proof(a.v1)
    v0, v1 = a.v0, a.v1
    while len(proofs) < a.max:
        if Me.passes(f1, t['op'], t['value']) and abs(f1 - goal) <= max(1.0, 0.25 * abs(goal - t['value'] if t['op'] != 'between' else 1.0)):
            break
        if f1 == f0:
            print(f'  the test does not move with {a.knob} between {v0:g} and {v1:g}: not this setting\'s to fix'); break
        v2 = v1 + (goal - f1) * (v1 - v0) / (f1 - f0)
        # a strength (a power, an irradiance) never crosses zero, and where the reading saturates (a highlight in the
        # view's shoulder) the secant overshoots: then step by a factor of three toward the aim instead
        positive = (v0 > 0 and v1 > 0) or knobs[0].split('.')[-1] in ('power_w', 'irradiance', 'strength')
        if positive and (v2 <= 0 or v2 > 10 * max(v0, v1) or v2 < min(v0, v1) / 10):
            v2 = v1 * (3.0 if (goal - f1) * (f1 - f0) * (v1 - v0) > 0 else 1 / 3.0)
        # never more than two spans past the values given: a reading that barely moves sends the secant far off (02b's
        # sky, 1.5 and 2 moving the test 0.8, sent to 11.75, which broke five other tests); then the setting is not the
        # one that sets the test, and the card says so
        span = abs(a.v1 - a.v0) or abs(a.v0) or 1.0
        v2 = min(max(v2, min(a.v0, a.v1) - 2 * span), max(a.v0, a.v1) + 2 * span)
        if isinstance(rng, tuple) and len(rng) == 2 and all(isinstance(x, (int, float)) for x in rng):
            v2 = min(max(v2, rng[0]), rng[1])
        if abs(v2 - v1) < 1e-9:
            break
        v0, f0, v1 = v1, f1, v2
        f1 = proof(v2)
    # a value that breaks the reply's other tests (ones passing at the values given) is worse than one that only misses
    # its own: the fewest broken first, then passing nearest the aim, then nearest to passing
    first_ok = {x['id'] for p in proofs[:2] for x in p[3] if x['pass'] and x['id'] != a.change}
    def broken(p):
        return [x['id'] for x in p[3] if x['id'] in first_ok and not x['pass']]
    fewest = min(len(broken(p)) for p in proofs)
    for p in proofs:
        if len(broken(p)) > fewest:
            print(f"  {a.knob} = {p[0]:.4g} set aside: it breaks {', '.join(broken(p))}")
    cand = [p for p in proofs if len(broken(p)) == fewest]
    ok = [p for p in cand if p[2]]
    best = min(ok, key=lambda p: abs(p[1] - goal)) if ok else min(cand, key=lambda p: abs(p[1] - goal))
    print(f"best: {a.knob} = {best[0]:.4g} ({t['metric']} {best[1]}, {'passes' if best[2] else 'still fails'})")
    # what was tried, for the render's report and the next critic's card (the shot's .tune.json, one record a run)
    side = Path(a.shot).with_suffix('.tune.json')
    log = json.loads(side.read_text()) if side.exists() else []
    moved = len({p[1] for p in proofs}) > 1
    log.append({'change': a.change, 'setting': ','.join(knobs), 'test': {k: t[k] for k in ('metric', 'op', 'value') if k in t},
                'proofs': [[round(p[0], 4), p[1]] for p in proofs], 'set': round(best[0], 4) if a.save else None,
                'passes': bool(best[2]), 'moves_the_test': moved})
    side.write_text(json.dumps(log, indent=1) + '\n')
    if a.save:
        raw = json.loads(Path(a.shot).read_text())
        for k in knobs:
            S.set_path(raw, k, round(best[0], 4))
        Path(a.shot).write_text(json.dumps(raw, indent=1) + '\n')
        print('saved', a.shot)


if __name__ == '__main__':
    main()
