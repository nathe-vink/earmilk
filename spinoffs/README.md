# The earmilk family

Products that share earmilk's rule: one joke, said once per surface, on a product that would be good without it.
Each folder holds a brief (`README.md`), its numbers (`params.py`), a parametric model (`model.py`, build123d), a
scene for the path tracer (`scene.py`), renders and a critic log. All of it is a proposal until the owner signs it.

| Product | What it is | The joke | Status |
|---|---|---|---|
| [earmilk](../README.md) | floorstanding three-way speaker | a half-gallon milk carton | spec, renders, fabrication package |
| [earworm](earworm/README.md) | wired over-ear headphones | the cable is an earthworm; its saddle is the remote | concept: model, printable cups, renders, critic |
| [earwig](earwig/README.md) | true-wireless earbuds | flexible tails of overlapping plates ending in forceps (pinch to play); a lid split like wing covers | concept: model, renders, critic |
| [earnest](earnest/README.md) | valve amplifier, by the pack of 6, 12 or 24 | an egg crate whose eggs are the valves; a white egg turns the volume | concept: model, renders |
| [barkhorn](barkhorn/README.md) | two-way hybrid horn loudspeaker, after Friendly Pressure | none: birch bark or eucalyptus bark, each horn painted from its bark's colours | concept: fab package (studio/fabkit), proof renders |

Start the next one with `python3 studio/new_product.py NAME --title NAME --kind "What it is"`, then follow the
`new-product` skill (`.claude/skills/new-product/SKILL.md`).
