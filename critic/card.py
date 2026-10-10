#!/usr/bin/env python3
"""The shot card the critic reads in stage 2: what the frame is for, what is fixed and why, every setting it may
change with its current value, unit and range, and the parts it can measure by name.

    python3 critic/card.py shot-02a --shot renders/2026-10-08/02a-e1.shot.json [--image renders/.../02a-e1.png] --out card.md

The fixed part comes from critic/cards/earmilk.yaml; the settings from the engine's resolved shot file (written beside
every render as NAME.shot.json), described by studio/engine/knobs.py; the parts from the render's mask (--masks).
"""
import argparse, json, re, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'studio' / 'engine'))
import knobs as K  # noqa: E402
import shot as S  # noqa: E402

LOCKED = ('product', 'products', 'size', 'render.samples', 'render.adaptive', 'render.denoise')
# inside the product, where it stands and how far an exploded part is drawn out are the shot's choices, not the product's
OPEN = re.compile(r'(product|products\.\d+)\.(instances\.\d+\.(position|rotate_z)|explode\.\d+\.offset_m|zone_parts)')


def fmt(v):
    if isinstance(v, float):
        return f'{v:g}'
    if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
        return '[' + ', '.join(f'{x:g}' if isinstance(x, float) else str(x) for x in v) + ']'
    return json.dumps(v) if not isinstance(v, str) else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shot_id'); ap.add_argument('--shot', required=True); ap.add_argument('--image')
    ap.add_argument('--card', default=str(ROOT / 'critic' / 'cards' / 'earmilk.yaml')); ap.add_argument('--out')
    ap.add_argument('--report', help="the render's report (its engine notes), when --image is a staged copy")
    ap.add_argument('--reshoot', action='store_true', help='a reshoot round: the first looks the blind score has held at')
    a = ap.parse_args()
    card = yaml.safe_load(Path(a.card).read_text())
    sc = card['shots'][a.shot_id]
    sh = json.loads(Path(a.shot).read_text())
    L = [f'# Shot card: {sc["title"]}', '']
    # the product's description: the shot's own, else the one for its product file, else the card's
    pdef_ = (sh.get('product') or (sh.get('products') or [{}])[0]).get('def', '')
    ptext = sc.get('product') or card.get('products', {}).get(pdef_, card['product'])
    L += ['## The product', '', ' '.join(ptext.split()), '']
    L += ['## What this frame is for', '', ' '.join(sc['purpose'].split()) if isinstance(sc['purpose'], str) else sc['purpose'], '',
          'It must show: ' + '; '.join(sc['must_show']) + '.', '']
    if a.reshoot:
        L += _reshoot(a.shot_id)
    L += ['## Fixed: never prescribe a change to these', '']
    for f in card['fixed'] + sc.get('fixed', []):
        L.append('- ' + ' '.join(f.split()))
    L += ['- The product and its flavour, and which of its parts are hidden, cut away or exploded and along which axis '
          '(everything under `product` but its placement and explode distances, below), the frame size and the sampling '
          'settings.', '']
    # an engine fact a critic measuring values cannot see: where the view transform starts to compress (01's round 6
    # found it by measuring; rounds holding whites at 230 to 245 had asked for gradients the curve flattens)
    L += ['## How the engine maps values', '',
          'The view transform is PBR Neutral: it is linear up to about 0.76 (about 226 in sRGB) and compresses everything '
          'above, so a white held at 230 to 245 prints as one flat value and no gradient or reflection on it can show. A '
          'white lacquer that should model and show its reflections sits at 200 to 220, with only its highlights above '
          '226: ask for the exposure or the light that puts it there before asking for more reflection on it.', '']
    L += _photo_light(sh)
    L += ['## Settings you may change', '',
          'Where the product stands and how it is turned (`product.instances.N.position`, `product.instances.N.rotate_z`) are '
          'yours where the frame\'s purpose allows: keep it standing on its floor or furniture, a pair a mirrored pair, and '
          'every must-show in view. So is how far an exploded part is drawn out (`product.explode.N.offset_m`), along its '
          'own axis. So is `product.zone_parts`: true splits the painted plinth band off each panel as its own part '
          '(`back-panel.plinth`, `side-right.plinth`, ...), so a lamp with `"receivers": ["*.plinth"]` lights the band '
          'alone; `part:back-panel` still measures the panel with its band. Name a setting by its path. Units and ranges are the engine\'s. Lengths are metres; the product stands at the '
          'origin with its front toward -y, z up; the camera\'s position and target are world points. Relative values are '
          'allowed in "to": "+0.5", "-20", "x0.8", "+15%". To add a light, set `lights.NEWNAME` to a whole spec, e.g. '
          '`{"type": "area", "size_m": [0.6, 0.6], "orbit": {"azimuth_deg": 30, "elevation_deg": 20, "distance_m": 2}, '
          '"irradiance": 1.0, "color": 5600}` (an orbit is round the product\'s centre; `"position": [x, y, z]` places a '
          'lamp anywhere else); to remove one, set `lights.NAME.off` to true. A graduated light for a gloss surface to '
          'mirror as a smooth ramp is a panel: `{"type": "panel", "size_m": [1.2, 0.25], "position": [x, y, z], "target": '
          '[x, y, z], "strength": 1.0, "color": "#FFFFFF", "ramp": {"axis": "y", "at_m": [0.2, 0.45], "values": [0, 1]}, '
          '"diffuse": false}` (strength the peak radiance; the ramp along a world axis; diffuse false: seen only in '
          'reflections). A flag that shades part of the set or the product from the lamps, as a photographer\'s black '
          'flag does, is `{"type": "flag", "size_m": [1.2, 0.5], "position": [x, y, z], "target": [x, y, z]}` (its face '
          'looks at its target; the camera and gloss never see it; `"color": "#F0F0F0"` makes it a bounce card; '
          '`"density": 0.4` makes it a net that lets 60 % through; `"lights": ["key"]` makes it shade the key alone). A lamp\'s '
          'shadow on the set can be lightened without touching the product: `lights.NAME.shadow_on_set` 0.5 halves its '
          'density on the floor and walls (a lamp without receivers). A glint (a highlight exactly '
          'where a surface would mirror a small lamp into the camera) is `glints.N`: `{"at": [x, y, z], "normal": [nx, ny, nz], '
          '"size_m": 0.05, "power_w": 2, "receivers": ["part name"]}`; it lights nothing (it only reflects), so it shows on a '
          'gloss or satin surface and spreads to nothing on a rough one (a rubber surround, a paper cone): light those. '
          'In a room, dress the set by adding a prop at '
          '`set.props.N` (N one past the last), e.g. `{"kind": "rug", "position": [x, y], "rotate_z": 0, "size": [2.0, 1.4], '
          '"color": "#C9C1B4"}`; position is its centre on the floor (a frame\'s on its wall). The kinds and their keys: '
          'rug (size [w, d], color); table (size [w, d, h], color); books (colors [hex, ...], z: the height they lie on); '
          'sideboard (size [w, d, h], color, turntable true/false, wood "birch" or "veneer": a sliced veneer under satin lacquer, its grain along the piece with book-matched cathedrals per door; with veneer, grain (latewood contrast, 0.2), figure_m (ring spacing, 0.022), leaf_m (a leaf\'s width, 0.4), arch_m (0.06), streak (0.8), roughness, coat); vase (height, z, color, branches); lamp (height, '
          'shade); sofa (size [w, d, h], color); curtain (size [w, h], folds, depth, color, translucent); frame (size '
          '[w, h], z, frame, art, artwork). To take one out, set `set.props.N.off` to true. A photographed environment '
          'lights the set and shows in every gloss surface: `sky.kind` "hdri" with `sky.file` (studio_small_03_1k, a small '
          'photo studio with softboxes; lebombo_1k, a sunlit apartment; st_fagans_interior_1k, a museum interior with '
          'windows; empty_warehouse_01_1k, a warehouse with skylights), `sky.strength`, and `sky.rotation_deg` to turn its '
          'brightest part where it should face; keep `sky.visible` false (at 1k it blurs as a background).', '',
          '| setting | now | unit | range | meaning |', '|---|---|---|---|---|']
    seen = set()
    for path, val in S.flatten(sh):
        if (any(path == l or path.startswith(l + '.') for l in LOCKED) and not OPEN.fullmatch(path)) or path.startswith('title'):
            continue
        d = K.describe(path) or ('', None, '')
        unit, rng, meaning = d
        rtxt = '' if rng is None else (f'{rng[0]:g} to {rng[1]:g}' if isinstance(rng, tuple) and len(rng) == 2 and all(isinstance(x, (int, float)) for x in rng) else ', '.join(map(str, rng)))
        flag = '' if K.in_range(val, rng) else ' (outside range)'
        L.append(f'| `{path}` | {fmt(val)}{flag} | {unit} | {rtxt} | {meaning} |')
        seen.add(path)
    # knobs the shot does not set yet but may (the common ones)
    extra = [k for k in ('camera.fstop', 'camera.shift_x', 'camera.shift_y', 'camera.polariser.strength', 'camera.polariser.angle_deg',
                         'render.exposure', 'render.white_balance_k', 'render.white_balance_tint', 'render.look',
                         'retouch.enabled', 'retouch.match', 'retouch.lightness', 'retouch.neutral', 'retouch.adapt')
             if k not in seen]
    for k in extra:
        unit, rng, meaning = K.describe(k)
        rtxt = '' if rng is None else (f'{rng[0]:g} to {rng[1]:g}' if isinstance(rng, tuple) and all(isinstance(x, (int, float)) for x in rng) else ', '.join(map(str, rng)))
        dflt = {'render.white_balance_tint': '10 (the default)', 'retouch.enabled': 'false (the default)',
                'retouch.match': '1 (the default)', 'retouch.lightness': '0.5 (the default)', 'retouch.neutral': '1 (the default)',
                'retouch.adapt': '1 (the default)'}.get(k, '(default)')
        L.append(f'| `{k}` | {dflt} | {unit} | {rtxt} | {meaning} |')
    L.append('')
    L.append('The set\'s materials take their preset\'s keys (`materials.oak.plank_contrast`, `materials.plaster.bump`, ...): '
             + '; '.join(f'**{n}**: ' + ', '.join(f'{k} {fmt(v)}' for k, v in p.items()) for n, p in _presets().items()) + '. '
             'The product\'s own materials (its paint and clear coat, metals, rubber, cones, birch) are its finish and fixed, '
             'like its geometry: a reflection they show is changed by what they reflect.')
    L.append('')
    if a.image:
        mp = Path(a.image).with_suffix('.mask.json')
        if mp.exists():
            sys.path.insert(0, str(ROOT / 'critic'))
            import measure as Me
            im, arr = Me.load(a.image); Me.load_mask(a.image)
            parts = Me.parts(arr)
            L += ['## Parts in this frame', '', 'Measure a part by name with `part:NAME` (or `part:woofer-*`) wherever a region is asked for, in the '
                  'tool and in accept tests: it follows the part if the camera moves.', '', '| part | pixels | box | luminance median | rgb median |', '|---|---|---|---|---|']
            for n, v in sorted(parts.items(), key=lambda kv: -kv[1]['pixels']):
                L.append(f'| {n} | {v["pixels"]} | {v["box"]} | {v["lum_median"]} | {v["rgb_median"]} |')
            L.append('')
        # the last rounds on this shot: what each changed, and whether the last round's tests pass on this image, so a
        # round does not undo the one before without knowing it (05's round 7 darkened the sweep round 6 had lightened)
        L += _history(a.shot_id, arr, Me)
        # what the engine could not do in this render, in its own words: the critic's prescriptions meet the physics here
        rp = Path(a.report) if a.report else Path(a.image).with_suffix('.report.json')
        if rp.exists():
            rep = json.loads(rp.read_text())
            notes = [f'- glint `{g["glint"]}` was skipped: {g["skipped"]}.' for g in rep.get('glints', []) if g.get('skipped')]
            notes += [f'- glint `{g["glint"]}`: {g["moved_in"]}.' for g in rep.get('glints', []) if g.get('moved_in')]
            notes += [f'- glint `{g["glint"]}` was moved {g["moved_mm"]} mm onto the {g["on"]}; the surface\'s own normal '
                      f'there is {g["normal_off_deg"]} degrees from the one given, so its lamp was placed from the surface\'s.'
                      for g in rep.get('glints', []) if not g.get('skipped') and g.get('normal_off_deg', 0) > 10]
            notes += [f'- change `{p_["id"]}` was not applied: {p_["why"]}.' for p_ in rep.get('pending', []) if p_.get('why') != 'not selected']
            # only the tuning of the round that made this frame: the shot's tune file keeps every round's, and an
            # older round's c4 is not this one's
            last_ = _last_round(a.shot_id)
            for tr in rep.get('tuning', []):
                if last_ is None or Path(tr.get('reply') or '').name != last_.name:
                    continue
                tried = ', '.join(f'{v:g} gave {r}' for v, r in tr['proofs'])
                verdict = ('it was set to %g' % tr['set'] if tr.get('set') is not None else 'nothing was set') + \
                          ('' if tr['moves_the_test'] else '; the test did not move with this setting, so it is not the lever for it')
                # a test that barely moves across the whole range tried, and still fails, is set by something else
                rs = [r for _, r in tr['proofs'] if isinstance(r, (int, float))]
                vs = [v for v, _ in tr['proofs'] if isinstance(v, (int, float))]
                tv = tr['test'].get('value')
                if rs and vs and tr['moves_the_test'] and not tr.get('passes') and isinstance(tv, (list, int, float)):
                    lo_, hi_ = (tv if isinstance(tv, list) else (tv, tv))
                    need = min(abs(r - lo_) if r < lo_ else abs(r - hi_) if r > hi_ else 0 for r in rs)
                    # wide enough to judge: a strength over a 2x range, or any setting (an angle, a position) over at
                    # least the step the critic asked for
                    if min(vs) > 0 and max(vs) / min(vs) >= 2:
                        wide = f'across a {max(vs) / min(vs):.0f}x range'
                    elif tr.get('asked') and max(vs) - min(vs) >= abs(tr['asked'][1] - tr['asked'][0]) > 0:
                        wide = (f'across {min(vs):g} to {max(vs):g}, wider than the {tr["asked"][0]:g} to '
                                f'{tr["asked"][1]:g} asked')
                    else:
                        wide = ''
                    if need > 0 and (max(rs) - min(rs)) < 0.25 * need and wide:
                        verdict += (f'; {wide}, it moved the reading only {max(rs) - min(rs):.2f}, still {need:.1f} '
                                    f'from the test, so something else sets it')
                notes.append(f'- the engine tuned `{tr["setting"]}` for {tr["change"]} ({tr["test"].get("metric")} {tr["test"].get("op")} '
                             f'{tr["test"].get("value")}) by proof renders: {tried}; {verdict}.')
            rt = rep.get('retouch')
            if rt and rt.get('paints'):
                L += ['## The retouch', '',
                      'The frame you judged is retouched (`retouch.*`): each paint matched to its swatch per copy, read off '
                      'its lit face (the pixels between the 40th and 90th percentile of its lightness that carry at least its '
                      'median chroma), every pixel by how much it is the paint, so highlights and edges move less. A '
                      'colour\'s remaining error in dE2000 is mostly the lightness `retouch.lightness` leaves; a white\'s is '
                      'its cast against a neutral of its own lightness. Before and after, on that lit face:', '',
                      '| paint | copy | swatch | before | after | how |', '|---|---|---|---|---|---|']
                for p_ in rt['paints']:
                    how = (f'cast {p_["cast_before"]} to {p_["cast_after"]} (a*, b*)' if p_['mode'] == 'neutral' else
                           f'gain {p_["lightness_gain"]}, chroma x{p_["chroma_scale"]}, hue {p_["hue_turn_deg"]:+g} deg')
                    L.append(f'| {p_["paint"]} | {p_["copy"]} | {p_["swatch"]} | {p_["de_before"]} | {p_["de_after"]} | {how} |')
                L.append('')
            mir = (rep.get('mirrors') or {}).get('parts') or {}
            if mir:
                tot = sum(v['pixels'] for v in mir.values())
                L += ['## What the product\'s surfaces mirror', '',
                      'A glossy part shows what lies along its mirror direction. The engine followed the camera\'s ray '
                      f'through one pixel in {(rep.get("mirrors") or {}).get("step", 2) ** 2} to the part, reflected it about the '
                      'surface\'s shading normal, and followed it as the render does: past what gloss does not see (flags), '
                      'past a panel\'s or a one-sided card\'s back, and through a panel linked to its receivers, which is '
                      'see-through (they see its light added to what lies behind it), to the first surface, unlinked panel '
                      'or the sky; an area lamp it crosses adds its light too. So "lamp fill + panel glint5 over world '
                      '(sky)" reads: the fill and the glint5 panel, brightest first, both seen over the sky. A highlight, a '
                      'sheen or a dark band is whatever those pixels mirror: change that (its strength, ramp, position, size '
                      'or colour, or a lamp\'s `specular` share), not a lamp they do not see; an unlinked panel placed in '
                      'front of a lamp hides it from them. For any region, the measuring tool\'s `mirrors` command gives '
                      'the breakdown (`mirrors X0 Y0 X1 Y1`, or `mirrors part:NAME`): where each share sits, each emitter\'s '
                      'radiance there (a clear coat shows about 0.05 of it head-on, up to 0.3 to 0.5 near grazing) and the '
                      'world point where the nearest one is met, which is where a panel and its ramp have to be. Before any '
                      'proof is rendered, the engine applies your changes to a copy of this shot and checks that each '
                      'reflection-only panel you prescribe is what its test\'s region mirrors.', '',
                      '| part | pixels | what its pixels mirror (share) |', '|---|---|---|']
                for n, v in list(mir.items())[:14]:
                    if v['pixels'] < 0.004 * tot:
                        continue
                    seen = ', '.join(f'{w} {sh * 100:.0f} %' for w, sh in v['seen'] if sh >= 0.03)
                    L.append(f'| {n} | {v["pixels"]} | {seen} |')
                L.append('')
            if notes:
                L += ['## What the engine did and could not do in this render', '',
                      'A glint is placed from the surface the camera sees at its point: where that surface mirrors a part of '
                      'the set or the product into the camera, its lamp moves in front of that part (to 60 % of the gap, '
                      'scaled to look the same); where the gap is under 5 cm no lamp can be there, and the glint is skipped.', ''] + notes + ['']
    text = '\n'.join(L) + '\n'
    if a.out:
        Path(a.out).write_text(text)
    else:
        print(text)


def _reshoot(shot_id, n=5):
    """A reshoot round's brief: the blind score has held while each round passed its own measured tests (01 at 5.0 four
    rounds running, 02b at 6.0 six), and the first looks kept naming the same things (the product lit apart from the
    room's light, its white a flat card, small in the frame), which no refinement of the present light reaches. The
    card shows the critic those first looks and asks for the changes a photographer would reshoot with."""
    import glob
    rows = []
    for f in glob.glob(str(ROOT / 'critic' / 'rounds' / '*' / f'{shot_id}-*-r*.json')):
        m = re.search(r'-(e\d+)-r(\d+)\.json$', f)
        if not m:
            continue
        s1 = json.loads(Path(f).read_text()).get('stage1') or {}
        if s1.get('score') is not None:
            rows.append((int(m.group(2)), m.group(1), s1['score'], ' '.join(str(s1.get('impression', '')).split())))
    rows = sorted(rows)[-n:]
    if not rows:
        return []
    out = ['## This round: a reshoot', '',
           f'Each of the last {len(rows)} rounds passed its own measured tests, and the first look did not move '
           f'({", ".join(f"{s:g}" for _, _, s, _ in rows)}). What it kept saying:', '']
    out += [f'- round {r} ({e}, {s:g}): "{imp}"' for r, e, s, imp in rows]
    out += ['', 'Refining the present light will not move it. This round, rank first the changes that remove what those '
            'first looks name, the way a photographer would reshoot the frame: where the camera stands and its lens; where '
            'the product stands and how it is turned; where the key light comes from and what it falls on (the product '
            'first, so that its faces carry the light the room or the set shows); what the set shows and how much of the '
            'frame it takes. Lamps, cards, nets and glints that earlier rounds placed for the old light and that the new '
            'light makes wrong go in the same round (`lights.NAME.off` true, a glint\'s `power_w` 0), or move with it. A '
            'reshoot moves every region: test the product by `part:NAME`, and the set only by a region the move leaves '
            'alone. This round you may prescribe up to twelve changes. Keep to the settings below and to what is fixed.', '']
    return out


def _last_round(shot_id):
    """The newest critic reply saved for the shot (the round that made the frame now being judged), or None."""
    import glob
    files = []
    for f in glob.glob(str(ROOT / 'critic' / 'rounds' / '*' / f'{shot_id}-*-r*.json')):
        m = re.search(r'-r(\d+)\.json$', f)
        if m:
            files.append((int(m.group(1)), Path(f).stat().st_mtime, f))
    return Path(max(files)[2]) if files else None


def _photo_light(sh):
    """What makes the frame read as a photograph of lacquer rather than a render, in this frame's own lamps: fifteen
    rounds of blind scores held at 5 to 6 while each round lifted one more part with a lamp linked to it alone, and the
    blind impressions kept naming the result ('self-glow', 'pasted', 'flat card', 'paint, not lacquer')."""
    def share(v, dflt=True):
        v = dflt if v is None else v
        return (1.0 if v else 0.0) if isinstance(v, bool) else float(v)
    lights = {n: l for n, l in (sh.get('lights') or {}).items() if isinstance(l, dict) and not l.get('off')}
    linked = sorted(n for n, l in lights.items() if l.get('receivers') and l.get('type') != 'flag'
                    and share(l.get('diffuse')) > 0)
    cards = sorted(n for n, l in lights.items() if l.get('type') == 'panel' and share(l.get('diffuse')) == 0)
    pol = (sh.get('camera') or {}).get('polariser') or {}
    ev = float((sh.get('render') or {}).get('exposure', 0.0))
    sky = sh.get('sky') or {}
    L = ['## How light reads as a photograph', '']
    L.append(f'This frame has {len(lights)} lamps. A lamp with `receivers` that lights (a diffuse share above 0) brightens '
             'those parts and nothing round them: the part lifts while the floor, the wall and its own shadow do not, and '
             'blind critics of these frames have read it as self-glow and as a pasted cut-out. '
             + (f'Lamps here that light one part alone: {", ".join(f"`{n}`" for n in linked)}. ' if linked else 'None here lights one part alone. ')
             + 'To lift a face, move, resize or re-aim a light the whole set sees, or add a bounce card the set would have; '
             'turning a linked lamp off (`lights.NAME.off`) is in scope, and is often the change that removes the glow. '
             'Keep `receivers` for reflection-only cards (diffuse 0) and glints: a gloss surface shows those as reflections '
             'and nothing else, as it would a card a photographer holds out of frame; and for a lamp that lights the set alone, '
             'named by its pieces (`"receivers": ["sweep"]`, `"floor*"`, `"wall-back"`): a background light, or a lamp over '
             'floating parts that lays their shadows on the floor without lighting them.')
    L.append('')
    L.append('A clear coat mirrors about 4 to 5 % of what it sees head-on (more toward grazing), so a reflection shows on '
             'a white only when what it mirrors is many times brighter than the white itself: on a white at scene-linear '
             f'0.6 (about 200), a soft gradient across the face takes a card of strength about 4 to 8 at exposure 0 (it adds '
             f'about 0.045 times the strength times 2^exposure; this frame\'s exposure is {ev:+g}, so x{2 ** ev:.2f}). '
             'A dark or coloured face needs far less: the same card washes out a chocolate or a green; in a frame of several '
             'copies, `"receivers": ["front-baffle#0", "front-baffle#2"]` gives a card to those copies\' fronts alone (copies '
             'count from 0 in `product.instances` order). The mirror map '
             '(below) says what each face sees and its radiance; ramp the card along the axis its reflection runs on the face.'
             + (f' Reflection cards here: {", ".join(f"`{n}`" for n in cards)}.' if cards else ''))
    L.append('')
    if pol.get('strength', 0) > 0:
        L.append(f'The lens carries a polariser at strength {pol["strength"]:g} (angle {pol.get("angle_deg", 90):g} deg). It removes '
                 'the reflections that tell lacquer from paint on every face it covers: set `camera.polariser.strength` to 0 '
                 'unless one specific glare needs it, and expect the faces it covers to read as matte paint while it stays.')
        L.append('')
    if (sh.get('set') or {}).get('kind') == 'sweep' and sky.get('kind') == 'gradient' and float(sky.get('strength', 1.0)) > 0:
        L.append(f'The world is a gradient dome at strength {float(sky.get("strength", 1.0)):g}: light from every direction at '
                 'once, which fills every shadow and flattens every face toward one value. A studio is dark round its lamps.')
        L.append('')
    return L


def _history(shot_id, arr, Me, rounds=3):
    """The card's account of the shot's last rounds: the last round's changes with its tests measured on this image, and
    every setting the last `rounds` rounds changed, in order."""
    import glob
    files = []
    for f in glob.glob(str(ROOT / 'critic' / 'rounds' / '*' / f'{shot_id}-*-r*.json')):
        m = re.search(r'-r(\d+)\.json$', f)
        if m:
            files.append((int(m.group(1)), Path(f).stat().st_mtime, f))
    if not files:
        return []
    files.sort()
    last = json.loads(Path(files[-1][2]).read_text())
    ver = re.search(rf'{re.escape(shot_id)}-(e\d+)-r', files[-1][2])
    try:
        res = {r_['id']: r_ for r_ in Me.check(arr, last)['tests']}
    except SystemExit:
        res = {}
    def short(v):
        s = json.dumps(v) if not isinstance(v, str) else v
        return s if len(s) <= 90 else s[:87] + '...'
    out = ['## The last rounds on this shot', '',
           f'Round {files[-1][0]} judged {ver.group(1) if ver else "the frame before"} and made this frame from it. Its changes, '
           f'and its tests measured on this image:', '']
    for c in last.get('changes', []):
        ch = c.get('change', {}); r_ = res.get(c.get('id'))
        verdict = '' if r_ is None else (f' Its test {"passes" if r_["pass"] else "fails"} here: {r_["metric"]} {r_["measured"]} '
                                          f'(wanted {r_["op"]} {r_["value"]}).')
        why = ' '.join(str(c.get('problem', '')).split())
        why = why if len(why) <= 220 else why[:220].rsplit(' ', 1)[0].rstrip(',;:') + '...'
        out.append(f'- {c.get("id")} `{ch.get("setting")}`: {short(ch.get("from"))} to {short(ch.get("to"))}, for: '
                   f'{why.rstrip(".")}.{verdict}')
    seen = {}
    for n, _, f in files[-rounds:]:
        for c in json.loads(Path(f).read_text()).get('changes', []):
            s = c.get('change', {}).get('setting')
            if s and not str(s).startswith('asset'):
                seen.setdefault(s, []).append(f'round {n}: {short(c["change"].get("from"))} to {short(c["change"].get("to"))}')
    rep = {s: v for s, v in seen.items() if len(v) > 1}
    if rep:
        out += ['', 'Settings more than one of the last rounds changed: ' +
                '; '.join(f'`{s}` ({", ".join(v)})' for s, v in rep.items()) + '.']
    out += ['', 'A change that reverses one of these undoes what it was for: if you prescribe one, say in "expected" why the '
            'trade is worth it and what keeps the earlier problem from coming back.', '']
    return out


def _presets():
    import materials as M
    return {k: v for k, v in M.PRESET_DEFAULTS.items() if k in ('oak', 'plaster', 'sweep')}


if __name__ == '__main__':
    main()
