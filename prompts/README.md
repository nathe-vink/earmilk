# Shot prompts

One file per shot, versioned: `prompts/shot-NN-vN.md`. A version is frozen once a render has been made from it. Changes go in the next version with a line at the top saying what changed and which critic round asked for it. The render a version produced is `renders/YYYY-MM-DD/shot-NN-vN.png`, same NN and vN; multi-frame shots add a letter (`shot-02-v1a.png`, `shot-02-v1b.png`).

| NN | Shot | Flavor(s) | Frames |
|---|---|---|---|
| 01 | Hero pair in a room | Whole | 1 |
| 02 | Two rooms, years apart | Whole, then Oat | 2 |
| 03 | Bowl close-up | Whole | 1 |
| 04 | Back, straight on | Whole | 1 |
| 05 | Five flavors lineup | all five, in order | 1 |
| 06 | Mixed crate on a desk (pints) | all five across six pints | 1 |
| 07 | Sleeve swap | Whole to Oat | 3 |

Priority is the NN order.

## The constant block

Every prompt includes this unchanged. It is the part that must not drift. If the render path is the 3D model, the model is the constant block and a prompt file carries only camera, light, scene and the acceptance list.

> A floorstanding speaker that is exactly a half-gallon gable-top milk carton scaled up: square plan 390 mm, body 860 mm tall, a gable rising 150 mm to a centred ridge, a 45 mm fin on top, 1,055 mm overall. Two black paper-cone drivers on the front, a 12 in woofer low and a 6.5 in mid above it. On the front slope of the gable, an elliptical opening into a smooth, concave, painted bowl; a 1 in dome tweeter sits at the bowl's throat, 170 mm back, facing forward. The outer skin is matte printed carton board with visible fold creases at the gable and the fin. The only print is the lowercase wordmark "earmilk", on the front above the mid and larger on the side. No grille, no glossy plastic, no flavor word, no label on the sleeve. Birch shows only through the window on the back.

Proportions come from `spec/geometry.md`, colors from `spec/colorways.json`, copy from `copy/`.

## What a render must not do

- Change the carton's proportions, soften its edges, taper it, or otherwise "improve" the silhouette.
- Add a grille, glossy plastic, a cap, tuning plates, or a second tweeter.
- Angle the tweeter up, square the bowl, or sink it vertically.
- Show bare birch anywhere but the back window and the exploded or section views (shot 07 is the exploded view).
- Put a flavor word under the wordmark, or a label on the sleeve.
