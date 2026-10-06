---
name: new-product
description: Start and develop a new product in the earmilk family (a spin-off like earworm or earwig) from idea to path-traced renders, critic round and vibe-fab notes. Use when the user names a new product idea or asks to continue one in spinoffs/.
---

# New product in the earmilk family

The family rule: one joke, said once, on a product that would be good without it. Voice is deadpan. Everything you
add is a **proposal** until the owner signs it; say so in the brief and in `params.py`.

## Steps

1. **Scaffold.** `python3 studio/new_product.py NAME --title NAME --kind "What it is"` creates `spinoffs/NAME/` with
   `README.md` (the brief), `params.py`, `model.py`, `shots.json`, `critic/LOG.md`, `out/`, `renders/`. It refuses to
   overwrite.
2. **Brief first.** Fill `README.md`: the idea in four lines, decisions (proposals), geometry, colourways, shots, what
   a render must not do, open questions. Keep the joke on one surface per surface.
3. **Numbers.** Put every dimension in `params.py`, marked PROPOSAL or PLACEHOLDER (a bought part). Nothing is SPEC
   until the owner says so.
4. **Model.** Write `model.py` in build123d (runs in `.venv-fab`): `build()` returns `{part: (solid, material)}`; export
   STL and STEP to `out/`, and a `parts.json` with volumes and any facts the scene needs. Patterns that work:
   revolve a filleted 2D profile for round parts (cups, tips, plugs); loft ellipses for organic bodies (earwig's bud);
   `mirror(part, Plane.YZ)` for left/right; text from `studio/typeset.py` (`set_line`, `pieces`) for debossed or cast
   lettering (extrude glyph faces with `both=True`: TrueType outlines run clockwise, so a one-sided extrude can cut air). Keep separate solids a hair apart or overlapping, never coplanar (Cycles renders coplanar faces black).
5. **Scene.** Write `scene.py` that writes `shots.json` for `studio/pathtrace.py` from `params.py` and `out/parts.json`:
   materials (presets), meshes, generated tubes (cables, worms) and Python hooks (hair). Solve poses numerically when
   a part must rest on the floor (`studio/poses.py`; `spinoffs/earworm/scene.py` shows it). See the `pathtrace` skill.
6. **Proofs.** `python3 studio/pathtrace.py spinoffs/NAME/shots.json --shot hero --samples 32 --scale 0.4 --out
   <scratchpad>/p1.png`, about 20 to 50 s. Look at every proof. Iterate framing, scale of the joke, and materials.
7. **Finals.** Full size, default samples, into `renders/hero-v1.png` and `renders/detail-v1.png` (about 8 minutes
   each on 4 CPUs). Run them in the background and do other work meanwhile.
8. **Critic.** One round per shot per look with the `critic-round` skill; log it in `critic/LOG.md`.
9. **Vibe fab.** In the brief, a section on how to make one: printable parts from `out/stl`, bought parts with sizes,
   what is a placeholder until a part is in hand.
10. **Commit** the brief, code, renders and the critic log together. Never commit a key or a token.

## Reference products

- `spinoffs/earworm/`: wired in-ear earphones; revolved earphone parts, solved resting poses, worm cables drawn by
  the path tracer's tube with overlapping segments, a blended saddle and a radius profile by distance.
- `spinoffs/earwig/`: true-wireless buds; a lofted bud, a flexible tail of overlapping plates (a tube with shingle rings, like the earworm's cable) draped to the forceps, a case with a wing-case lid. (Its wig, grown by a hair hook, is in git history.)
