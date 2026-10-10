"""The duel: a new frame against the shot's best, judged blind side by side, so the loop keeps only what is better.

A round's tests check that its prescriptions landed, not that the picture improved, and a single critic's blind score
is too coarse to tell (it sat at 5 to 6 through sixteen rounds whose tests mostly passed, and four reshoots scored as
low as or lower than the frames they replaced). A blind judge who sees both frames is more sensitive: five of five
preferred the finished frame by about a point where single scores barely moved (critic/ab/2026-10-10-finish.md). So
after each render the new frame meets the shot's best (critic/best.json): the judge, a fresh agent with the A/B prompt
(critic/ab/PROMPT-DUEL.txt, the A/B's own with the two frames free to differ in light, set and camera), sees them in a random order and says which it would ship. The winner is the shot's best;
the deck shows the best frames, and the next round starts from the best frame's settings.

    python3 critic/duel.py stage NEW --shot-id shot-04a --stage DIR       pair NEW with the shot's best, write the prompt
    python3 critic/duel.py save REPLY --shot-id shot-04a --stage DIR      record the verdict; a win makes NEW the best
    python3 critic/duel.py best                                          print critic/best.json

A frame is named by its image path; `best.json` holds per shot `{"frame": path, "since": date, "record": [...]}`.
"""
import argparse, datetime, json, random, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEST = ROOT / 'critic' / 'best.json'
PROMPT = ROOT / 'critic' / 'ab' / 'PROMPT-DUEL.txt'


def _load():
    return json.loads(BEST.read_text()) if BEST.exists() else {}


def _rel(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def stage(a):
    best = _load()
    cur = best.get(a.shot_id)
    if not cur:
        raise SystemExit(f'{a.shot_id} has no best frame in {BEST}; set one with: duel.py set {a.shot_id} IMG')
    new, old = ROOT / a.new if not Path(a.new).is_absolute() else Path(a.new), ROOT / cur['frame']
    if new.resolve() == old.resolve():
        raise SystemExit(f'{a.new} is already the best frame of {a.shot_id}')
    d = Path(a.stage); d.mkdir(parents=True, exist_ok=True)
    tag = f"{a.shot_id.replace('shot-', '')}-{new.stem}"
    new_is_a = random.Random(a.seed if a.seed is not None else hash((str(new), str(old))) & 0xffff).random() < 0.5
    pa, pb = (new, old) if new_is_a else (old, new)
    A, B = d / f'duel-{tag}-A.png', d / f'duel-{tag}-B.png'
    shutil.copy(pa, A); shutil.copy(pb, B)
    work = d / f'work-duel-{tag}'; work.mkdir(exist_ok=True)
    order = {'shot_id': a.shot_id, 'new': _rel(new), 'old': cur['frame'], 'new_is': 'A' if new_is_a else 'B'}
    (d / f'duel-{tag}.order.json').write_text(json.dumps(order, indent=1) + '\n')
    msg = PROMPT.read_text().replace('AB_A', str(A)).replace('AB_B', str(B)).replace(
        'TOOL', str(d / 'measure.py')).replace('SCRATCH', str(work))
    (d / f'message-duel-{tag}.txt').write_text(msg)
    print(d / f'message-duel-{tag}.txt')


def save(a):
    d = Path(a.stage)
    reply = json.loads(Path(a.reply).read_text())
    tag = f"{a.shot_id.replace('shot-', '')}-{Path(a.new).stem}" if a.new else None
    orders = sorted(d.glob(f'duel-{tag}.order.json' if tag else f"duel-{a.shot_id.replace('shot-', '')}-*.order.json"),
                    key=lambda p: p.stat().st_mtime)
    if not orders:
        raise SystemExit('no staged duel for this shot')
    order = json.loads(orders[-1].read_text())
    ni = order['new_is']; oi = 'B' if ni == 'A' else 'A'
    won = reply.get('prefer') == ni
    rec = {'date': datetime.date.today().isoformat(), 'new': order['new'], 'old': order['old'],
           'new_score': reply.get(ni), 'old_score': reply.get(oi), 'prefer': 'new' if won else (
               'old' if reply.get('prefer') == oi else 'none'), 'differences': reply.get('differences', [])}
    out = ROOT / 'critic' / 'duels' / rec['date']
    out.mkdir(parents=True, exist_ok=True)
    name = f"{a.shot_id}-{Path(order['new']).stem}-vs-{Path(order['old']).stem}.json"
    (out / name).write_text(json.dumps(rec, indent=1) + '\n')
    best = _load()
    entry = best.setdefault(a.shot_id, {'frame': order['old'], 'since': rec['date'], 'record': []})
    entry['record'].append({k: rec[k] for k in ('date', 'new', 'old', 'new_score', 'old_score', 'prefer')})
    if won:
        entry['frame'] = order['new']; entry['since'] = rec['date']
    BEST.write_text(json.dumps(best, indent=1) + '\n')
    print(f"{a.shot_id}: {Path(order['new']).name} {rec['new_score']} against {Path(order['old']).name} "
          f"{rec['old_score']}: {'NEW is the best' if won else 'the best stays'} ({_rel(out / name)})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('stage'); s.add_argument('new'); s.add_argument('--shot-id', required=True)
    s.add_argument('--stage', required=True); s.add_argument('--seed', type=int)
    v = sub.add_parser('save'); v.add_argument('reply'); v.add_argument('--shot-id', required=True)
    v.add_argument('--stage', required=True); v.add_argument('--new')
    t = sub.add_parser('set'); t.add_argument('shot_id'); t.add_argument('img')
    sub.add_parser('best')
    a = ap.parse_args()
    if a.cmd == 'stage':
        stage(a)
    elif a.cmd == 'save':
        save(a)
    elif a.cmd == 'set':
        best = _load()
        best[a.shot_id] = dict(best.get(a.shot_id, {'record': []}), frame=_rel(a.img),
                               since=datetime.date.today().isoformat())
        BEST.write_text(json.dumps(best, indent=1) + '\n')
        print(a.shot_id, '->', best[a.shot_id]['frame'])
    else:
        print(BEST.read_text() if BEST.exists() else '{}')


if __name__ == '__main__':
    main()
