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

- `drawings/sheet-1.png` to `sheet-6.png` (A3 at 200 dpi; crop and zoom where the print is small) and `drawings/earmilk-sheets.pdf`
- `cutlist.csv` (every panel: name, size, thickness, quantity, operations)
- `cad.json` (the CAD's own numbers: panel sizes, cut-outs, the waveguide, the driver rebates)
- `dxf/` (the router files, one per panel; list them, open one or two)
- `stl/` and `step/` (the printed parts and the solids; list them)

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

## Rounds

Each round's reply is in `critic/drawings/`. The fixes go into the CAD, `fab/params.py`, `fab/flats.py`,
`fab/sheets.py`, `fab/bom.csv` and `fab/README.md`, and the drawings are regenerated from them.

| date | round | buildable | findings | what changed |
|---|---|---|---|---|
| 2026-10-09 | 1 | 3.5 | 2 block, 3 remake, 19 guess, 6 legibility; 6 owner questions | d1 the tweeter went in from behind past a bore smaller than its flange: one ø73.4 bore from the boss's back to the throat, the flange seated on the throat's ring (the bookshelf's boss 68.4, flattened on the top panel, 1.5 of insert under the bore); d2 the front dowels moved behind the insert's pocket (9.7 and 6.7 clear); d3 the lid's gland drawn from its front edge, 43, with FRONT EDGE on the DXF; d4 the rebates 1.0 deeper for a flange gasket; d5 the upper magnets level with the throat, 12.6 and 3.0 clear of the boss; d6 the amplifier's box and the port in section A-A; d7 the bookshelf's stale brace files and notes gone; d8 the drivers' screw holes (DRIVER_SCREWS, measure first) on sheet 1 and the baffle's DXF; d9 the plate's rebate 4.5 for EPDM tape, its screws and pilot holes; d10 the tweeter's heat-set holes in the CAD and on sheet 3; d11 the fixings' positions and fits; d12 the trim rings exported, a channel over the screw heads, held by silicone; d13 the port 5 mm too long; d14 the gland M25 / M20 everywhere; d15 the floorstander's cabinet lead 250 past the grommet; d16 the runs through the brace's window; d17 the build order; d18 28 mm dowels; d19, d30 sizes printed exactly; d20 sheet 6, panel details; d21 the bookshelf's shelf +8.3 dB; d22 tolerances in every title block; d24 cad.json's features; d25 no text under 6 pt; d26 the roof's dimensions drawn over the sections; d27 the cutting planes A-A and B-B; d28 the balloons on faces the view sees, the gable with its pocket, not to scale |
| 2026-10-09 | 2 | 4.5 | 1 block, 2 remake, 16 guess, 7 legibility; 5 owner questions | d1 the floorstander's tweeter held by a printed retaining sleeve over its motor, its flange screwed to the boss's back face outside the bore (no screw through the tweeter: SB's screws thread into the motor from the front), the pocket's bore 4 mm deeper for the flange; d2 the bookshelf's faceplate screws M2.5 low heads (0.65 clear of a 48 body) into bonded knurled inserts; d3 the fit toleranced (pocket +0.2/0, insert 0/-0.15) and the insert painted on its face only; d4 the trim rings dimensioned, their inner ø from the surround (+2, measure); d5 the printed gable in six resin-sized pieces keyed by 4 mm pins, the insert's halves by 3 mm pins in the BOM; d6 the pocket, bay, channel and dowel holes dimensioned on sheet 3; d7 the plate's pilots through 13.5, its corners; d8 the gland's counterbore in the lid's DXF, cut list and sheet 6; d9 the pins bonded (6.1 holes); d10 no heat-set in resin, the screws named; d11 the port printed 10 long and its fitting and trimming in the build; d12 the finish before anything is fitted; d13 T-nut barrels and button-head heights, fitted before the glue-up; d14 the bookshelf's lead 185; d15 a pull groove under the insert; d16 round-sheathed cable, the channel sealed with silicone (no grommet in 18 mm); d17 each rebate as flange + gasket + ring, measure first; d18 the FA122's cut-out 293; d19 the BOM and params agree with the sheets; d21 sheet 6's scale; d22 'n of 6', drawing numbers, revision C, the first-angle symbol, the README's six sheets; d23 balloon 10 on the port's flange; d24 the bookshelf's dimension under the top panel; d25 its Facts note under the view; d26 the throat a closed circle. d20 (10 pt text) waits for a notes sheet |
