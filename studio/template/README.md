# {{TITLE}}: handoff for design, renders and critic

{{KIND}} in the earmilk family. One joke, said once, on a product that would be good without it. This file is the
brief: the idea, the decisions, the numbers, the shots. `params.py` holds the numbers the model is built from.

Status: concept. Everything below marked *proposal* waits on the owner.

## The idea in four lines

- 
- 
- 
- 

Voice: deadpan, like earmilk's Nutrition Facts. One joke per surface, maximum.

## Decisions (proposals until the owner signs them)

- 

## Geometry (mm)

| | |
|---|---|
| | |

## Colourways

| Name | Body | Accent | Notes |
|---|---|---|---|

## Shots

1. **Hero.**
2. **Detail.**

## What a render must not do

- Change the proportions in `params.py`, soften what is meant to be crisp, or add a second joke to a surface.

## Open questions (do not assume answers)

- 

## Files

- `params.py` the numbers (SPEC, PROPOSAL, PLACEHOLDER, as in earmilk's fab/params.py)
- `model.py` builds the parts in build123d and exports `out/stl`, `out/step`, `out/parts.json`
- `scene.py` writes `shots.json`, the scene for `studio/pathtrace.py` (cables, hair hooks, solved poses go here); renders land in `renders/`
- `critic/LOG.md` one row per critic round, as in earmilk's critic/LOG.md
