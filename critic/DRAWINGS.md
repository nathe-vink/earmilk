# The drawing checker

A render critic asks whether an image would ship; this asks whether a builder could make the speaker from the drawings
without phoning anyone. It is run like a critic round: a fresh reviewer, the files below, one JSON reply, and every
finding names exactly what to change. `fab/sheets.py` draws the sheets from the CAD, so a fix is a change to the CAD,
to `fab/params.py` or to the sheet code, never a hand edit of a PNG.

## The brief

You are a cabinetmaker and a loudspeaker builder checking a drawing set before it goes to the shop. You will build one
pair from these files alone: a CNC router or a table saw for the birch ply, a resin printer for the gable and the
waveguide insert, hand tools, a soldering iron. Read every file below before writing anything.

For each size (`fab/out/` is the floorstander, `fab/out-bookshelf/` the bookshelf):

- `drawings/sheet-1.png` to `sheet-5.png` (A3 at 200 dpi; crop and zoom where the print is small) and `drawings/earmilk-sheets.pdf`
- `cutlist.csv` (every panel: name, size, thickness, quantity, operations)
- `cad.json` (the CAD's own numbers: panel sizes, cut-outs, the waveguide, the driver rebates)
- `dxf/` (the router files, one per panel; list them, open one or two)

and once: `fab/README.md` (the build order and the decisions), `fab/bom.csv` (the bought parts),
`fab/params.py` (the numbers, marked SPEC, PROPOSAL or PLACEHOLDER), `fab/research/` (the bought parts' own data).

Look for what would stop the build, cost a remake, or force a guess:

- a dimension that is missing (a panel, a cut-out, a hole's position, a depth), or given twice with two values, or
  that disagrees with `cutlist.csv`, `cad.json` or `params.py`;
- a part, a cut-out or a fixing the drawings never show (where does each screw go, what holds the baffle, how the
  back comes off, where the cable runs, how the amplifier plate is held);
- an order of assembly that cannot be followed (a panel that cannot go in after another, a part glued in before
  something has to pass it, a cable that cannot be fed);
- a bought part drawn at a size its own data sheet contradicts (a driver's cut-out, its depth behind the baffle, the
  amplifier plate's cut-out, the connector);
- tolerances and fits a builder needs and does not have (a rebate's depth for a flush driver, a printed part's
  clearance in its pocket, a press fit);
- anything a builder cannot read: text under 2.5 mm at A3, a leader pointing at nothing, a section without its
  cutting plane on another view, a view without a scale, a title block that does not say what the sheet is;
- an acoustic number the drawings carry that the README's acoustics contradict (a box volume, a port's length).

Do not redesign the speaker: its shape, sizes, drivers and the waveguide are decided (the waveguide by simulation).
If something decided looks wrong, list it under `questions` for the owner with the reason.

## The reply

Reply with only this JSON:

    {
      "verdict": "one paragraph: could you build a pair from this set today, and what would stop you",
      "buildable_score": 0.0,
      "findings": [
        {"id": "d1", "size": "floorstander|bookshelf|both", "sheet": "sheet-2|cutlist|bom|README|...",
         "where": "the view and the place on it (a crop box in the PNG's pixels if it helps)",
         "severity": "blocks|remake|guess|legibility",
         "problem": "one sentence",
         "evidence": "what the sheet says against what the CAD, cut list, params or data sheet says, with the numbers",
         "fix": "exactly what to add or change, with the value: 'add a 6.0 mm dimension from the rebate floor to the face on the section A-A', not 'dimension the rebate'"}
      ],
      "questions": [{"question": "...", "why": "..."}]
    }

`buildable_score` is out of 10: 10 hands to a shop today, 5 builds with phone calls. Rank findings by severity, the
ones that block first. Be exact: "the woofer cut-out is 282 on sheet 2 and 283.5 in cad.json (woofer.cutout_d)" is a
finding; "check the dimensions" is not.
