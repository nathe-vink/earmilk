"""The parts list and its cost, for a set (a pair of speakers is `count` 2): every made part with its stock, size and
mass, every bought part with its maker, model, supplier and price from the component library. Prices are budgets:
the library's from retailer listings (dated), the made parts' from the stock rates in model.py. A shop's quote
replaces both.

    bom.write(product, parts, flats_records, library, out)  ->  bom.csv, bom.md; returns the rows and the totals

An option's parts (Part.option: a cover, a stand) are listed after the product's, each option with its own subtotal;
the totals returned are the product's alone.
"""
import csv, os

from model import SHEETS, PRINTS, SOLIDS, Sheet, Printed, Machined, Bought


def rows(product, parts, recs, library):
    out = []
    for p in parts:
        n = p.qty * product.count
        m = p.make
        vol_cm3 = p.solid.volume / 1000.0 if p.solid is not None else 0.0
        sig = None
        if p.solid is not None and not isinstance(m, Bought):     # made parts merge only when their solids are alike
            b = p.solid.bounding_box()
            sig = (round(vol_cm3, 1), tuple(sorted(round(v, 1) for v in (b.size.X, b.size.Y, b.size.Z))), len(p.solid.faces()))
        if isinstance(m, Sheet):
            st = SHEETS.get(m.material, {})
            r = recs.get(p.name, {})
            area = r.get('w', 0) * r.get('h', 0) / 1e6
            rate = st.get('usd_per_m2', 0)
            out.append(dict(item=p.name, kind='cut', qty=n, what=f"{m.thickness:g} mm {st.get('title', m.material)}",
                            size=f"{r.get('w', 0):.0f} x {r.get('h', 0):.0f}", mass_g=round(vol_cm3 * st.get('density', 0.7)),
                            usd_each=round(area * rate * 1.25, 2) if rate is not None else None, source='cut file dxf/' + p.name + '.dxf',
                            finish=p.finish, option=p.option, _sig=sig))
        elif isinstance(m, Printed):
            pm = PRINTS.get(m.material, {})
            out.append(dict(item=p.name, kind='print', qty=n, what=pm.get('title', m.material), size=f'{vol_cm3:.0f} cm3',
                            mass_g=round(vol_cm3 * pm.get('density', 1.1)), usd_each=round(vol_cm3 * pm.get('usd_per_cm3', 0.1) + 8, 2),
                            source='stl/' + p.name + '.stl', finish=p.finish, option=p.option, _sig=sig))
        elif isinstance(m, Machined):
            sm = SOLIDS.get(m.material, {})
            b = p.solid.bounding_box()
            stock = m.stock or (b.size.X + 10, b.size.Y + 10, b.size.Z + 10)
            cast = m.process in ('cast', 'mould')
            blank_cm3 = vol_cm3 * 1.1 if cast else stock[0] * stock[1] * stock[2] / 1000      # a casting pours its own volume
            out.append(dict(item=p.name, kind=m.process, qty=n, what=sm.get('title', m.material),
                            size=(f'{vol_cm3:.0f} cm3, ' if cast else '') + ' x '.join(f'{v:.0f}' for v in stock),
                            mass_g=round(vol_cm3 * sm.get('density', 1)),
                            usd_each=round(blank_cm3 * sm.get('usd_per_cm3', 0.02) + 5, 2),
                            _setup=m.setup_usd if m.setup_usd is not None else 40.0,
                            source='step/' + p.name + '.step', finish=p.finish, option=p.option, _sig=sig))
        elif isinstance(m, Bought):
            c = library.get(m.ref, {})
            maker = c.get('maker', '?')
            out.append(dict(item=p.name, kind='buy', qty=n, what=(f'{maker} ' if maker != 'any' else '') + c.get('model', m.ref),
                            size=c.get('size', ''), mass_g=c.get('mass_g', ''), usd_each=c.get('usd', None),
                            source=c.get('url', ''), finish=c.get('note', ''), supplier=c.get('supplier', ''),
                            price_date=c.get('price_date', ''), option=p.option))
    # identical parts merge into one line: bought ones by what they are, made ones when their solids match too
    merged = {}
    for r in out:
        k = (r['kind'], r['what'], r['size'], r.get('finish', ''), r['option'], r.pop('_sig', None))
        if k in merged:
            merged[k]['qty'] += r['qty']; merged[k]['item'] += ', ' + r['item']
        else:
            merged[k] = dict(r)
    # a machining setup is paid once a line (one batch), spread over its pieces
    for r in merged.values():
        su = r.pop('_setup', 0.0)
        if su and isinstance(r['usd_each'], (int, float)):
            r['usd_each'] = round(r['usd_each'] + su / r['qty'], 2)
    # the product's lines first, then each option's
    order = {o: i for i, o in enumerate(dict.fromkeys([''] + [p.option for p in parts]))}
    return sorted(merged.values(), key=lambda r: order[r['option']])


def _totals(R):
    tot = {}
    for r in R:
        if isinstance(r['usd_each'], (int, float)):
            tot[r['kind']] = tot.get(r['kind'], 0) + r['usd_each'] * r['qty']
    return tot


def write(product, parts, recs, library, out):
    R = rows(product, parts, recs, library)
    base = [r for r in R if not r['option']]
    tot = _totals(base)
    unknown = [r['what'] for r in base if not isinstance(r['usd_each'], (int, float))]
    cols = ['item', 'kind', 'qty', 'what', 'size', 'mass_g', 'usd_each', 'finish', 'supplier', 'price_date', 'source', 'option']
    with open(os.path.join(out, 'bom.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in R]

    def table(rs):
        md = ['| item | make | qty | what | size | each, USD |', '|---|---|---|---|---|---|']
        for r in rs:
            each = f"{r['usd_each']:,.2f}" if isinstance(r['usd_each'], (int, float)) else '[PRICE]'
            md.append(f"| {r['item']} | {r['kind']} | {r['qty']} | {r['what']} | {r['size']} | {each} |")
        return md
    md = [f'# {product.title}: parts for {product.count} ({product.kind})', ''] + table(base)
    md += ['', '| | USD |', '|---|---|'] + [f'| {k} | {v:,.0f} |' for k, v in sorted(tot.items())] + [f'| total | {sum(tot.values()):,.0f} |', '']
    if unknown:
        md.append('No price yet for: ' + '; '.join(unknown) + '.')
    opts = list(dict.fromkeys(r['option'] for r in R if r['option']))
    if opts:
        md += ['', f'## Options (each for {product.count}, on top of the total above)', '']
        for o in opts:
            rs = [r for r in R if r['option'] == o]
            ot = sum(_totals(rs).values())
            missing = [r['what'] for r in rs if not isinstance(r['usd_each'], (int, float))]
            head = (f'about ${ot:,.0f}' + (' before the unpriced' if missing else '')) if ot else '[PRICE]'
            md += [f'### {o}: {head}', ''] + table(rs) + ['']
            if missing:
                md += ['No price yet for: ' + '; '.join(missing) + '.', '']
    md.append('Budget figures: bought parts from the component library (dated retailer listings), made parts from the '
              "kit's stock rates: 25 % offcut on sheet parts, a handling charge a print, and a setup a machined line spread "
              "over its pieces. A shop's quote replaces them.")
    open(os.path.join(out, 'bom.md'), 'w').write('\n'.join(md) + '\n')
    return R, tot


def option_totals(R):
    """{option: {'usd': the set's priced lines, 'unpriced': how many lines have no price yet}}."""
    out = {}
    for o in dict.fromkeys(r['option'] for r in R if r['option']):
        rs = [r for r in R if r['option'] == o]
        out[o] = dict(usd=round(sum(_totals(rs).values())), unpriced=sum(not isinstance(r['usd_each'], (int, float)) for r in rs))
    return out
