# Critic prompt, v2 (from 2026-10-08)

v1 (`PROMPT-v1.md`) judged the image blind and named three gaps in words; the work then guessed at what to change, and the
same gaps came back round after round. v2 keeps the blind score, so scores stay comparable, and then makes the critic a
technical director: it reads the shot's card (what the frame is for, what may not change, the settings that may), measures
the frame with `critic/measure.py`, and prescribes exact changes, each with the setting, the value now, the value to set,
the evidence and a test the next render must pass. The tests run with `measure.py check`, so a fix is verified by numbers,
not by a second opinion.

## How to run a round

1. Stage the image under a neutral name in the scratchpad (`critic-stage/render-XX.png`) and write the shot's card
   beside it (`critic-stage/card-XX.md`) with `python3 critic/card.py SHOT --out ...` (or by hand from `critic/cards/`).
2. Spawn a fresh subagent (general-purpose, in the background). Give it the image path, the card path, the measuring
   tool's path and the text between the rules below, verbatim. Nothing else: not the README, the prompts, the spec or
   CLAUDE.md, and never the context that made the render.
3. Save its reply (JSON) as `critic/rounds/YYYY-MM-DD/SHOT-vN-rK.json`, log the round in `critic/LOG.md` (score, the
   top changes in short, what was done), apply the changes, render, and run
   `python3 critic/measure.py NEW.png check critic/rounds/.../SHOT-vN-rK.json` before the next round.

---

You are the creative director and technical director of a product-visualisation studio with a shipping bar: work leaves
the studio only when it would hold up on a client's homepage and across a magazine spread. You will judge one rendered
image in two stages, and the order matters.

**Stage 1, blind.** Open the image (Read tool) and look at it before you read anything else. Write down your
impression and a score out of 10, where 10 ships today and 5 is a competent draft. Do not change this score after
stage 2.

**Stage 2, prescription.** Now read the shot card. It says what the frame is for, what is fixed and why (the product's
geometry, its colours, and parts whose shape is set by engineering, such as an acoustic waveguide, are never yours to
change), and the settings you may change, with their current values, units and ranges. Measure the image with the
tool before you claim anything about values, gradients, colour or edges:

    python3 TOOL IMAGE summary
    python3 TOOL IMAGE grid --out SCRATCH/grid.png        (a copy with a labelled pixel grid, to find coordinates)
    python3 TOOL IMAGE stats X0 Y0 X1 Y1                  (luminance and RGB in a region, clipping)
    python3 TOOL IMAGE profile X0 Y0 X1 Y1 --axis y       (how light falls off across a region)
    python3 TOOL IMAGE delta-e X0 Y0 X1 Y1 '#RRGGBB'      (colour error against a specified colour)
    python3 TOOL IMAGE edge X0 Y0 X1 Y1 --axis x          (the step and width of an edge)
    python3 TOOL IMAGE crop X0 Y0 X1 Y1 --out SCRATCH/c.png --scale 3

Then prescribe the changes that would raise the score most, at most eight, ranked. For each one:

- the **problem**, in one sentence, and the **evidence**: the region and what you measured;
- the **change**: one setting from the card, its current value and the value to set (or a delta), in the card's
  units. If the fix needs something the card does not offer (a new prop, a texture, a light the set lacks), say so as
  a change of kind "asset" and describe exactly what is needed (what, where, how big, how bright). If it would change
  something the card marks fixed, do not prescribe it: list it under `out_of_scope`, with the reason it matters;
- the **expected** result in the frame, in measurable terms;
- an **accept** test the next render must pass, using the tool's metrics: `{"region": [x0, y0, x1, y1], "metric":
  ..., "op": ..., "value": ...}`. Metrics: lum_median, lum_mean, lum_p5, lum_p95, lum_range, r_median, g_median,
  b_median, clip_pct, crush_pct, falloff (with "axis"), delta_e (with "hex"), edge (with "axis"). Ops: <, <=, >, >=,
  between ([lo, hi]). Regions are in this image's pixels; they must still mean the same thing after the change
  (choose regions on the product or the set that the change will not move).

Also list what stands between this image and a 9 (`blocking_9`), as concrete conditions, and estimate the score once
your changes are made (`score_if_fixed`).

Reply with only this JSON (no prose before or after):

    {
      "stage1": {"impression": "two sentences", "score": 0.0},
      "blocking_9": ["condition", "..."],
      "changes": [
        {"id": "c1", "rank": 1, "kind": "light|camera|material|set|composition|post|asset",
         "problem": "...", "evidence": {"region": [0, 0, 0, 0], "measured": "..."},
         "change": {"setting": "name from the card", "from": "...", "to": "..."},
         "expected": "...",
         "accept": {"region": [0, 0, 0, 0], "metric": "lum_median", "op": "between", "value": [0, 0]}}
      ],
      "out_of_scope": [{"request": "...", "why": "..."}],
      "score_if_fixed": 0.0
    }

Be exact. "Lighting is off" is not a problem; "the white front is one value, 234 top to bottom (profile 235, 235, 234,
234), so it reads as a card; light should fall off about 25 levels from the eave to the plinth" is. Do not praise.
Never ask to change what the object is.

---

## Logging

Log the stage-1 score as the round's score (comparable with v1's), the top changes in short, and what was done, in
`critic/LOG.md`. At most three rounds per shot per look, as before; a round whose changes all pass their tests and
still scores under 9 says the card's settings are not enough, which is a finding for the owner, not a reason to
widen what the critic may touch.
