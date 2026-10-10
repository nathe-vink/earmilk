#!/usr/bin/env python3
"""Stage a critic v2 round: the image under a neutral name, its part mask, its shot card, and the message for the
critic subagent (critic/PROMPT.md, the text between the rules), so a round is the same every time.

    python3 critic/round.py stage IMAGE.png --shot-id shot-02a --tag e1 [--stage DIR]
        -> DIR/render-<tag>.png (+ .mask.png/.mask.json), DIR/card-<tag>.md, DIR/message-<tag>.txt

    python3 critic/round.py save REPLY.json --shot-id shot-02a --version e1 --round 1
        -> critic/rounds/YYYY-MM-DD/shot-02a-e1-r1.json (validated: JSON, the keys PROMPT.md asks for)

    python3 critic/round.py check NEW.png critic/rounds/.../shot-02a-e1-r1.json
        -> the previous round's accept tests on the new render (critic/measure.py check)

The stage directory defaults to the session scratchpad's critic-stage/ when CLAUDE_SCRATCH is set, else
/tmp/critic-stage. The message names only the staged files and the measuring tool, never the product or the repo.
"""
import argparse, datetime, json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prompt_text():
    t = (ROOT / 'critic' / 'PROMPT.md').read_text()
    a = t.index('\n---\n') + 5; b = t.index('\n---\n', a)
    return t[a:b].strip()


def stage(a):
    d = Path(a.stage or os.environ.get('CLAUDE_SCRATCH', '/tmp') + '/critic-stage'); d.mkdir(parents=True, exist_ok=True)
    src = Path(a.image)
    img = d / f'render-{a.tag}.png'
    shutil.copy(src, img)
    for suf in ('.mask.png', '.mask.json', '.mirror.png', '.mirror.json'):
        m = src.with_suffix(suf)
        if m.exists():
            shutil.copy(m, img.with_suffix(suf))
    shotfile = src.with_suffix('.shot.json')
    card = d / f'card-{a.tag}.md'
    subprocess.run([sys.executable, str(ROOT / 'critic' / 'card.py'), a.shot_id, '--shot', str(shotfile), '--image', str(img),
                    '--report', str(src.with_suffix('.report.json')), '--out', str(card)], check=True)
    tool = d / 'measure.py'
    shutil.copy(ROOT / 'critic' / 'measure.py', tool)
    text = prompt_text().replace('TOOL', str(tool)).replace('IMAGE', str(img)).replace('SCRATCH', str(d / f'work-{a.tag}'))
    msg = (f'Image: {img}\nShot card (read only in stage 2): {card}\nMeasuring tool: {tool} (run it with python3)\n'
           f'Scratch directory for your crops and grids: {d / f"work-{a.tag}"}\n\n{text}\n')
    (d / f'message-{a.tag}.txt').write_text(msg)
    print(d / f'message-{a.tag}.txt')


REQUIRED = ('stage1', 'blocking_9', 'changes', 'out_of_scope', 'score_if_fixed')


def save(a):
    raw = Path(a.reply).read_text().strip()
    if raw.startswith('```'):
        raw = raw.strip('`').split('\n', 1)[1].rsplit('```', 1)[0]
    data = json.loads(raw[raw.index('{'):raw.rindex('}') + 1])
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise SystemExit(f'reply lacks {missing}')
    day = datetime.date.today().isoformat()
    out = ROOT / 'critic' / 'rounds' / day / f'{a.shot_id}-{a.version}-r{a.round}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1) + '\n')
    s = data['stage1']
    print(out, '| score', s.get('score'), '| if fixed', data.get('score_if_fixed'), '|', len(data['changes']), 'changes')
    for c in data['changes']:
        ch = c.get('change', {})
        print(f"  {c.get('id')} [{c.get('kind')}] {ch.get('setting')}: {ch.get('from')} -> {ch.get('to')}   {c.get('problem', '')[:110]}")
    for w in mirror_warnings(data, a.shot_id, a.version):
        print('  MIRROR', w)


def mirror_warnings(data, shot_id, version):
    """Changes to a reflection-only panel whose test region does not mirror it: the engine's mirror map of the judged
    image (its mask pass) says what the region's product pixels see, so a sheen prescribed on a panel they do not see
    cannot move the test (03's round 8: the waveguide wall mirrors glint5, the fin the base flag). One line each."""
    import glob
    num = shot_id.split('-', 1)[1]
    imgs = sorted(glob.glob(str(ROOT / 'renders' / '*' / 'engine' / f'{num}-{version}.png')))
    shots = sorted(glob.glob(str(ROOT / 'studio' / 'shots' / '*' / f'{num}.json')))
    if not imgs or not shots or not Path(imgs[-1]).with_suffix('.mirror.png').exists():
        return []
    sys.path.insert(0, str(ROOT / 'critic'))
    import measure as Me
    _, arr = Me.load(imgs[-1]); Me.load_mask(imgs[-1]); Me.load_mirror(imgs[-1])
    lights = json.loads(Path(shots[-1]).read_text()).get('lights', {})
    out = []
    for c in data.get('changes', []):
        st = (c.get('change') or {}).get('setting') or ''
        reg = (c.get('accept') or {}).get('region')
        if not st.startswith('lights.') or reg is None:
            continue
        name = st.split('.')[1]
        spec = lights.get(name)
        if not isinstance(spec, dict) or spec.get('type') != 'panel' or spec.get('diffuse', True) is not False:
            continue
        try:
            m = Me.mirrors(arr, reg)
        except SystemExit:
            continue
        if not m['mirrors']:
            continue
        comp = lambda w: w.split(' over ')[0].split(' + ') + w.split(' over ')[1:] if ' over ' in w else [w]
        share = sum(x['share_pct'] for x in m['mirrors'] if f'panel {name}' in comp(x['what']))
        if share < 10:
            top = ', '.join(f"{x['what']} {x['share_pct']} %" for x in m['mirrors'][:3])
            out.append(f"{c.get('id')}: `{name}` is a reflection-only panel, and the test's region mirrors it on {share:.0f} % of "
                       f"its product pixels; they mirror {top}")
    return out


def precheck(a):
    """A reply's reflections, tried on geometry before any proof is rendered: its changes applied to a copy of the
    judged frame's shot, the mirror map run on that (no render, about 40 s), and for every change to a light or a glint,
    what its test's region mirrors then: whether the light it adds or moves is in the region's reflections at all, how
    bright it is there and where on it they land. A reflection-only light its region does not mirror cannot move its
    test, at any strength (03's round 8, 07's round 9)."""
    import glob, tempfile
    num = a.shot_id.split('-', 1)[1]
    imgs = sorted(glob.glob(str(ROOT / 'renders' / '*' / 'engine' / f'{num}-{a.version}.png')))
    if not imgs:
        raise SystemExit(f'no render {num}-{a.version}.png')
    img = Path(imgs[-1]); reply = json.loads(Path(a.reply).read_text())
    td = Path(tempfile.mkdtemp(prefix='precheck-', dir=os.environ.get('CLAUDE_SCRATCH')))
    shot = td / 'shot.json'; out = td / 'frame.png'
    shutil.copy(img, out)
    eng = ROOT / 'studio' / 'engine' / 'render.py'
    subprocess.run([sys.executable, str(eng), str(img.with_suffix('.shot.json')), '--apply', a.reply, '--save-shot', str(shot),
                    '--no-render'], check=True, capture_output=True)
    r = subprocess.run([sys.executable, str(eng), str(shot), '--out', str(out), '--scale', str(a.scale), '--masks-only',
                        '--set', 'retouch.enabled=false'], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    sys.path.insert(0, str(ROOT / 'critic'))
    import measure as Me
    _, arr = Me.load(out); Me.load_mask(out); Me.load_mirror(out)
    rep = json.loads(out.with_suffix('.report.json').read_text())
    for p_ in rep.get('pending', []):
        if 'match no part' in str(p_.get('why', '')):
            print(f"  {p_['id']}: {p_['why']}")
    for g in rep.get('glints', []):
        if 'match no part' in str(g.get('skipped', '')):
            print(f"  glints.{g['glint']}: {g['skipped']}")
    lights = json.loads(shot.read_text()).get('lights', {})
    for c in reply.get('changes', []):
        st = (c.get('change') or {}).get('setting') or ''
        reg = (c.get('accept') or {}).get('region')
        # reflection-only panels: what they do depends on being mirrored. A lamp also lights diffusely, and a glint is
        # placed from the surface itself (and too small for a map that samples one pixel in four)
        if reg is None:
            continue
        if st.startswith('glints.'):
            # a glint with a ramp is a reflector panel placed on its surface's mirror ray (lights.glint); a plain glint is
            # a small lamp, too small for a map that samples one pixel in four
            gl = json.loads(shot.read_text()).get('glints') or []
            key = st.split('.')[1]
            g = (gl.get(key) if isinstance(gl, dict) else (gl[int(key)] if key.isdigit() and int(key) < len(gl) else None))
            if not isinstance(g, dict) or not g.get('ramp'):
                continue
            idx = list(gl.keys()).index(key) if isinstance(gl, dict) else int(key)
            name = f'glint{idx}'
        elif st.startswith('lights.'):
            name = st.split('.')[1]
            spec = lights.get(name)
            if not isinstance(spec, dict) or spec.get('type') != 'panel' or spec.get('diffuse', True) not in (False, 0, 0.0):
                continue
        else:
            continue
        try:
            m = Me.mirrors(arr, reg)
        except SystemExit as e:
            print(f"  {c['id']} {st}: {e}"); continue
        comp = lambda w: (w.split(' over ')[0].split(' + ') + w.split(' over ')[1:]) if ' over ' in w else [w]
        mine = [x for x in m['mirrors'] if any(k.split(' ', 1)[-1] == name for k in comp(x['what']))]
        share = sum(x['share_pct'] for x in mine)
        top = '; '.join(f"{x['what']} {x['share_pct']} %" for x in m['mirrors'][:3])
        rad = ', '.join(f"{k} {v[1]}" for x in mine[:1] for k, v in (x.get('radiance') or {}).items())
        # what share can carry the test: a p95 rides on its brightest 5 % (a rim's line), a median needs half
        met = (c.get('accept') or {}).get('metric', '')
        need = 5 if met in ('lum_p95', 'clip_pct') else 25 if met in ('lum_range', 'lum_mean', 'falloff', 'edge') else 45
        verdict = 'enough' if share >= need else 'TOO LITTLE'
        if met == 'falloff' and share > 0:
            # a falloff test wants the first slice brighter than the last (a positive value) or the reverse: the ramp the
            # region mirrors has to run that way (04a's round 8: the letters' panel ran bottom-bright, -50 at full strength)
            ax = (c.get('accept') or {}).get('axis', 'y')
            prof = Me.mirror_profile(arr, reg, name, ax)
            known = [v for v in (prof or []) if v is not None]
            if known and max(known) - min(known) <= 0.02 * max(max(known), 1e-6):
                verdict += f"; its radiance along {ax} is FLAT across the region ({known[0]}): the reflections meet the panel beyond its ramp, so no strength makes a falloff"
            elif prof and prof[0] is not None and prof[-1] is not None and prof[0] != prof[-1]:
                tv = (c.get('accept') or {}).get('value')
                want = (tv[0] + tv[1]) / 2 if isinstance(tv, list) else tv
                runs = 1 if prof[0] > prof[-1] else -1
                ok = (want or 0) * runs > 0
                verdict += f"; its radiance along {ax}, first slice to last: {prof} ({'the right way' if ok else 'THE WRONG WAY for this test'})"
        print(f"  {c['id']} {st}: the region mirrors `{name}` on {share:.0f} % of its product pixels"
              + (f" (radiance there: {rad})" if rad else '') + f"; it mirrors {top} [{met} needs about {need} %: {verdict}]")
    print(f'  (the mirror map with the changes: {out.with_suffix(".mirror.png")})')


def check(a):
    r = subprocess.run([sys.executable, str(ROOT / 'critic' / 'measure.py'), a.image, 'check', a.reply], capture_output=True, text=True)
    print(r.stdout)
    sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('stage'); s.add_argument('image'); s.add_argument('--shot-id', required=True); s.add_argument('--tag', required=True); s.add_argument('--stage')
    v = sub.add_parser('save'); v.add_argument('reply'); v.add_argument('--shot-id', required=True); v.add_argument('--version', required=True); v.add_argument('--round', type=int, required=True)
    c = sub.add_parser('check'); c.add_argument('image'); c.add_argument('reply')
    pc = sub.add_parser('precheck'); pc.add_argument('reply'); pc.add_argument('--shot-id', required=True)
    pc.add_argument('--version', required=True); pc.add_argument('--scale', type=float, default=0.75)
    a = ap.parse_args()
    {'stage': stage, 'save': save, 'check': check, 'precheck': precheck}[a.cmd](a)


if __name__ == '__main__':
    main()
