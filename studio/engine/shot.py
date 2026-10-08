"""Shot files: one JSON document per frame that says everything the render depends on, so a change is a path and a value.

A shot file can extend another (`"extends": "base.json"`, merged depth-first, the child winning), and every leaf is a
knob the critic can name by its dotted path: `camera.lens_mm`, `lights.key.power_w`, `materials.paint.coat_roughness`,
`camera.position.2` (an element of a list). `studio/engine/knobs.py` gives each path its unit and range.

    from studio.engine import shot
    s = shot.load('studio/shots/earmilk/02a.json')
    shot.set_path(s, 'lights.key.power_w', 450)
    applied = shot.apply_changes(s, json.load(open('critic/rounds/2026-10-08/02a-v27-r1.json')))

Values in a change's "to" may be absolute (a number, a list, a string) or relative to the current value: "+0.5",
"-20", "x0.8" (multiply) or "+15%". A change of kind "asset" is never applied by machine: it is returned as pending.
"""
import copy, json, re
from pathlib import Path


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load(path):
    """A shot file with its `extends` chain resolved. The result keeps `_path` (where it came from)."""
    path = Path(path)
    data = json.loads(path.read_text())
    if 'extends' in data:
        parent = load(path.parent / data.pop('extends'))
        parent.pop('_path', None)
        data = _merge(parent, data)
    data['_path'] = str(path)
    return data


def _split(path):
    return [int(p) if re.fullmatch(r'-?\d+', p) else p for p in path.split('.')]


def get_path(d, path, default=KeyError):
    cur = d
    for p in _split(path):
        try:
            cur = cur[p]
        except (KeyError, IndexError, TypeError):
            if default is KeyError:
                raise KeyError(path)
            return default
    return cur


def set_path(d, path, value):
    """Set a dotted path, making what is missing on the way: a dict for a name, a list for an index. An index one past
    a list's end appends (`glints.0` on a shot with no glints adds the first)."""
    parts = _split(path)
    cur = d
    for p, nxt in zip(parts[:-1], parts[1:]):
        if isinstance(cur, list):
            while len(cur) <= p:
                cur.append([] if isinstance(nxt, int) else {})
            if cur[p] is None:
                cur[p] = [] if isinstance(nxt, int) else {}
            cur = cur[p]
            continue
        if p not in cur or cur[p] is None:
            cur[p] = [] if isinstance(nxt, int) else {}
        cur = cur[p]
    last = parts[-1]
    if isinstance(cur, list):
        while len(cur) <= last:
            cur.append(None)
    cur[last] = value


def parse_value(text):
    """A command-line value: JSON if it parses (numbers, lists, true, "quoted"), else the bare string."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text


def resolve(current, to):
    """The new value for a change: absolute, or relative to `current` ("+0.5", "-20", "x0.8", "+15%")."""
    if isinstance(to, str) and isinstance(current, (int, float)) and not isinstance(current, bool):
        t = to.strip()
        m = re.fullmatch(r'([+-])\s*([\d.]+)\s*%', t)
        if m:
            f = float(m.group(2)) / 100 * (1 if m.group(1) == '+' else -1)
            return type(current)(current * (1 + f)) if isinstance(current, float) else current * (1 + f)
        m = re.fullmatch(r'[x*]\s*([\d.]+)', t)
        if m:
            return current * float(m.group(1))
        m = re.fullmatch(r'([+-])\s*([\d.]+)', t)
        if m:
            return current + float(m.group(2)) * (1 if m.group(1) == '+' else -1)
        try:
            return float(t)
        except ValueError:
            return to
    # an absolute value written as JSON text ("[2, 1]", "{\"at\": ...}", "0.12") becomes the value; "#897C6E" stays text
    return parse_value(to) if isinstance(to, str) else to


def apply_overrides(d, items):
    """`--set path=value` pairs."""
    for it in items or []:
        path, _, val = it.partition('=')
        set_path(d, path.strip(), parse_value(val.strip()))
    return d


def apply_changes(d, critic, only=None):
    """Apply a critic reply's `changes` (critic/PROMPT.md) to a shot. Returns (applied, pending): applied as
    [{id, setting, from, to}], pending (assets, unknown settings, changes not in `only`) as [{id, why}]."""
    applied, pending = [], []
    for ch in critic.get('changes', []):
        cid = ch.get('id')
        if only and cid not in only:
            pending.append({'id': cid, 'why': 'not selected'}); continue
        if ch.get('kind') == 'asset':
            pending.append({'id': cid, 'why': 'asset: ' + json.dumps(ch.get('change', {}))[:200]}); continue
        c = ch.get('change', {})
        setting = c.get('setting', '')
        try:
            cur = get_path(d, setting)
        except KeyError:
            cur = None
            if not setting or ' ' in setting:
                pending.append({'id': cid, 'why': f'no such setting: {setting!r}'}); continue
        new = resolve(cur, c.get('to'))
        set_path(d, setting, new)
        applied.append({'id': cid, 'setting': setting, 'from': cur, 'to': new})
    return applied, pending


def flatten(d, prefix=''):
    """Every leaf as (path, value); lists of numbers stay whole (a position is one knob)."""
    out = []
    if isinstance(d, dict):
        for k, v in d.items():
            if k.startswith('_') or k in ('extends', 'notes'):
                continue
            out += flatten(v, f'{prefix}{k}.' if prefix or k else k)
    elif isinstance(d, list) and d and all(isinstance(v, dict) for v in d):
        for i, v in enumerate(d):
            out += flatten(v, f'{prefix}{i}.')
    else:
        out.append((prefix.rstrip('.'), d))
    return out


def save(d, path):
    d = {k: v for k, v in d.items() if not k.startswith('_')}
    Path(path).write_text(json.dumps(d, indent=1) + '\n')
