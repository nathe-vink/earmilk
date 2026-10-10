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
        share = sum(x['share_pct'] for x in m['mirrors'] if x['what'] == f'panel {name}')
        if share < 10:
            top = ', '.join(f"{x['what']} {x['share_pct']} %" for x in m['mirrors'][:3])
            out.append(f"{c.get('id')}: `{name}` is a reflection-only panel, and the test's region mirrors it on {share:.0f} % of "
                       f"its product pixels; they mirror {top}")
    return out


def check(a):
    r = subprocess.run([sys.executable, str(ROOT / 'critic' / 'measure.py'), a.image, 'check', a.reply], capture_output=True, text=True)
    print(r.stdout)
    sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('stage'); s.add_argument('image'); s.add_argument('--shot-id', required=True); s.add_argument('--tag', required=True); s.add_argument('--stage')
    v = sub.add_parser('save'); v.add_argument('reply'); v.add_argument('--shot-id', required=True); v.add_argument('--version', required=True); v.add_argument('--round', type=int, required=True)
    c = sub.add_parser('check'); c.add_argument('image'); c.add_argument('reply')
    a = ap.parse_args()
    {'stage': stage, 'save': save, 'check': check}[a.cmd](a)


if __name__ == '__main__':
    main()
