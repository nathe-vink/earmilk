"""Build a product's whole fabrication package from its product file.

    .venv-fab/bin/python studio/fabkit/build.py spinoffs/<name>/product.py [--out DIR] [--skip drawings,render]

Writes, under the product's out/ (or DIR):
  step/<name>.step, step/<part>.step   the assembly and every part, in place, for any CAD program or shop
  stl/<part>.stl                       every printed part (and the rest, for viewing)
  dxf/...                              cut files for every sheet part, the nested sheets, nest.svg (flats.py)
  cutlist.csv                          what each sheet part needs
  bom.csv, bom.md                      the parts list and its budget, for the set (bom.py)
  checks.json                          clashes, stock, thin walls, missing library entries (checks.py)
  drawings/<name>-sheets.pdf           the drawing set (drawings.py)
  render/<name>.glb + studio/products/<name>.json   the render model and its engine file (render.py)
  build.json                           what was built, the totals, and whether the checks passed

The build stops before writing drawings if a check finds two parts clashing, unless --force.
"""
import argparse, importlib.util, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))

from model import Printed, Bought  # noqa: E402
import flats, bom, checks, drawings, render  # noqa: E402


def load_product(path):
    path = os.path.abspath(path)
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location('product_' + os.path.basename(os.path.dirname(path)), path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.PRODUCT


def load_library(product_dir):
    """The kit's component library, with the product's own (components.json beside its product file) on top."""
    lib = json.load(open(os.path.join(HERE, 'library', 'components.json')))
    own = os.path.join(product_dir, 'components.json')
    if os.path.exists(own):
        lib.update(json.load(open(own)))
    return {k: v for k, v in lib.items() if not k.startswith('_')}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('product'); ap.add_argument('--out'); ap.add_argument('--skip', default='')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    skip = set(filter(None, a.skip.split(',')))
    t0 = time.time()
    P = load_product(a.product)
    pdir = os.path.dirname(os.path.abspath(a.product))
    out = a.out or os.path.join(pdir, 'out')
    os.makedirs(out, exist_ok=True)
    parts = P.parts(P.params)
    names = [p.name for p in parts]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        raise SystemExit(f'part names must be unique: {sorted(dup)}')
    lib = load_library(pdir)
    geo = [p for p in parts if p.solid is not None]      # bought sets with nothing to draw are only on the parts list
    print(f'{P.title}: {len(parts)} parts ({len(geo)} with solids)', flush=True)

    from build123d import Compound, export_step, export_stl
    for d in ('step', 'stl'):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    if 'step' not in skip:
        kids = []
        for p in geo:
            p.solid.label = p.name; kids.append(p.solid)
            export_step(p.solid, os.path.join(out, 'step', f'{p.name}.step'))
            if isinstance(p.make, Printed) or 'stl' not in skip:
                export_stl(p.solid, os.path.join(out, 'stl', f'{p.name}.stl'), tolerance=0.02, angular_tolerance=0.1)
        asm = Compound(children=kids); asm.label = P.name
        export_step(asm, os.path.join(out, 'step', f'{P.name}.step'))
        print(f'  step and stl {time.time() - t0:.0f}s', flush=True)

    recs, nests = flats.write(P, geo, out)
    print(f'  cut files: {len(recs)} sheet parts on ' + ', '.join(f'{n} x {k}' for k, n in nests.items()), flush=True)
    rep = checks.run(P, parts, lib)
    json.dump(rep, open(os.path.join(out, 'checks.json'), 'w'), indent=1, default=str)
    print(f"  checks: {'ok' if rep['ok'] else 'FAILED'}; {len(rep['clashes'])} clash(es), "
          f"{len(rep['prints'])} print warning(s), {len(rep['sheets'])} stock warning(s)", flush=True)
    for c in rep['clashes'][:12]:
        print(f"    clash {c['a']} x {c['b']}: {c.get('volume_mm3')} mm3 {c.get('error', '')}")
    rows, tot = bom.write(P, parts, recs, lib, out)
    opt_tot = bom.option_totals(rows)
    print(f"  parts list: {len(rows)} lines, budget ${sum(tot.values()):,.0f} for {P.count}"
          + ''.join(f"; option {o} ${v['usd']:,}" + (f" + {v['unpriced']} unpriced" if v['unpriced'] else '') for o, v in opt_tot.items()),
          flush=True)
    if not rep['ok'] and not a.force:
        raise SystemExit('checks failed: fix the clashes (or list intended overlaps in PRODUCT.touching), or --force')
    pdf = None
    if 'drawings' not in skip:
        pdf, n = drawings.write(P, geo, recs, rows, out)
        print(f'  drawings: {n} sheets, {os.path.relpath(pdf, ROOT)}', flush=True)
    glb = pf = None
    if 'render' not in skip:
        glb, pf = render.write(P, geo, out)
        print(f'  render model: {os.path.relpath(glb, ROOT)}; engine file {os.path.relpath(pf, ROOT)}', flush=True)
    summary = dict(product=P.name, title=P.title, parts=len(parts), seconds=round(time.time() - t0),
                   sheets=nests, budget_usd={k: round(v) for k, v in tot.items()}, options_usd=opt_tot, checks_ok=rep['ok'],
                   drawings=pdf and os.path.relpath(pdf, ROOT), render=glb and os.path.relpath(glb, ROOT))
    json.dump(summary, open(os.path.join(out, 'build.json'), 'w'), indent=1)
    print(f'done in {summary["seconds"]}s')


if __name__ == '__main__':
    main()
