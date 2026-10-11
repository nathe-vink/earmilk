"""The front covers side by side: each bark bare, as photographed, then with each cover option, one speaker a frame
under the same light and camera, set in a grid with their names.

    python3 spinoffs/barkhorn/render_covers.py [--samples 96] [--all | --only birch-cloth ...] [--out ...]

Writes each frame's shot to studio/shots/barkhorn/covers/ (so any one can be re-rendered or tuned) and its image beside
the grid, in covers/. Only frames not yet rendered are rendered, unless named with --only or all are asked for with
--all (after a change to the product); the grid is set again every run.
"""
import argparse, copy, io, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'studio', 'shots', 'barkhorn')

# (option, label); the slotted grille is each bark's own: birch's lenticels, eucalyptus's strips
COVERS = {
    'birch': [(None, 'bare, as photographed'), ('cloth', 'cloth grille'), ('lenticel-grille', 'lenticel grille'),
              ('bark-face', 'bark face'), ('cork-face', 'cork face')],
    'eucalyptus': [(None, 'bare, as photographed'), ('cloth', 'cloth grille'), ('strip-grille', 'strip grille'),
                   ('bark-face', 'bark face'), ('cork-face', 'cork face')],
}


def shot_for(bark, option):
    base = json.load(open(os.path.join(SHOTS, f'{bark}.json')))
    s = copy.deepcopy(base)
    inst = {'position': [0, 0, 0], 'rotate_z': 0, 'flavour': bark}
    if option:
        inst['options'] = [option]
    s['product'] = {'def': 'studio/products/barkhorn.json', 'flavour': bark, 'instances': [inst]}
    # a little off the front, so the recess, the grille's relief and the bark's edges read; the speaker fills the frame
    s['camera'] = {'position': [-0.78, -2.6, 1.0], 'target': [0.0, 0.0, 0.64], 'lens_mm': 66, 'level': True}
    s['size'] = [760, 1000]
    s['title'] = f'barkhorn, {bark}, ' + (option or 'bare')
    return s


def font(size, bold=False):
    from fontTools.ttLib import TTFont
    from PIL import ImageFont
    tt = TTFont(os.path.join(ROOT, 'render', 'fonts', 'Archivo-Bold.woff' if bold else 'Archivo-Regular.woff'))
    tt.flavor = None
    buf = io.BytesIO(); tt.save(buf); buf.seek(0)
    return ImageFont.truetype(buf, size)


def grid(cells, out, cell_w=480):
    """cells: {bark: [(png, label), ...]} -> one image, a row a bark under its name, the cover's name under each
    frame; each frame `cell_w` wide."""
    from PIL import Image, ImageDraw
    rows = list(cells)
    w0, h0 = Image.open(cells[rows[0]][0][0]).size
    w, h = cell_w, round(cell_w * h0 / w0)
    pad, lab, head, rowhead = 20, 40, 64, 40
    ncol = max(len(v) for v in cells.values())
    W = pad + ncol * (w + pad)
    H = head + len(rows) * (rowhead + h + lab) + pad
    sheet = Image.new('RGB', (W, H), (246, 244, 239))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 20), 'barkhorn: front covers (options)', font=font(28, True), fill=(30, 28, 26))
    for r, bark in enumerate(rows):
        y = head + r * (rowhead + h + lab)
        d.text((pad, y + 4), bark, font=font(24, True), fill=(30, 28, 26))
        y += rowhead
        for c, (png, label) in enumerate(cells[bark]):
            x = pad + c * (w + pad)
            sheet.paste(Image.open(png).convert('RGB').resize((w, h), Image.LANCZOS), (x, y))
            d.text((x, y + h + 8), label, font=font(20), fill=(60, 56, 52))
    sheet.save(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--samples', type=int, default=96)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--out', default=os.path.join(ROOT, 'renders', '2026-10-10', 'barkhorn', 'covers.png'))
    ap.add_argument('--only', nargs='*', default=[], help='bark-option names to render again (e.g. birch-cloth)')
    ap.add_argument('--all', action='store_true', help='render every frame again')
    a = ap.parse_args()
    sd = os.path.join(SHOTS, 'covers'); os.makedirs(sd, exist_ok=True)
    od = os.path.join(os.path.dirname(a.out), 'covers'); os.makedirs(od, exist_ok=True)
    cells = {}
    for bark, covers in COVERS.items():
        cells[bark] = []
        for option, label in covers:
            name = f'{bark}-{option or "bare"}'
            path = os.path.join(sd, f'{name}.json')
            json.dump(shot_for(bark, option), open(path, 'w'), indent=1)
            png = os.path.join(od, f'{name}.png')
            if a.all or name in a.only or not os.path.exists(png):
                print('render', name, flush=True)
                subprocess.run([sys.executable, os.path.join(ROOT, 'studio', 'engine', 'render.py'), path, '--out', png,
                                '--samples', str(a.samples), '--scale', str(a.scale)], check=True, cwd=ROOT,
                               stdout=subprocess.DEVNULL)
            cells[bark].append((png, label))
    print(grid(cells, a.out))


if __name__ == '__main__':
    main()
