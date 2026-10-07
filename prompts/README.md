# Shot prompts

One file per shot, versioned: `prompts/shot-NN-vN.md`. A version is frozen once a render has been made from it. Changes go in the next version with a line at the top saying what changed and which critic round asked for it. The render a version produced is `renders/YYYY-MM-DD/shot-NN-vN.png`, same NN and vN; multi-frame shots add a letter (`shot-02-v1a.png`, `shot-02-v1b.png`). A path-traced render of the same version (see `render/README.md`) adds `-pt`: `shot-NN-vN-pt.png`.

| NN | Shot | Flavor(s) | Frames |
|---|---|---|---|
| 01 | Hero pair in a room | Whole | 1 |
| 02 | Two rooms, years apart | Whole in both: the same pair in two homes, a bright first apartment and a darker older house (rebriefed 2026-10-02) | 2 |
| 03 | Bowl close-up | Whole | 1 |
| 04 | Back, straight on | Whole | 1 |
| 05 | Five flavors lineup | all five, in order | 1 |
| 06 | Mixed crate on a desk (pints) | all five across six pints | 1 |
| 07 | Sleeve swap | Whole to Oat | 3 | retired 2026-10-02 with the sleeve; last render v5 |

Priority is the NN order.

## The constant block

Every prompt includes this unchanged. It is the part that must not drift. If the render path is the 3D model, the model is the constant block and a prompt file carries only camera, light, scene and the acceptance list.

> A floorstanding speaker that is exactly a half-gallon gable-top milk carton scaled up: square plan 390 mm, body 860 mm tall, a gable rising 150 mm to a centred ridge, a 45 mm fin on top, 1,055 mm overall. Two black paper-cone drivers on the front, a 12 in woofer low and a 6.5 in mid above it. On the front slope of the gable, an elliptical opening into a smooth, concave, painted bowl; a 1 in dome tweeter sits at the bowl's throat, 170 mm back, facing forward. The outer skin is matte printed carton board with visible fold creases at the gable and the fin. The only print is the lowercase wordmark "earmilk", on the front above the mid and larger on the side. No grille, no glossy plastic, no flavor word, no label on the sleeve. Birch shows only through the window on the back.

*Amended 2026-10-02 (v6 on): the skin is not board. The cabinet is birch finished in the flavour's colours, satin: the body in the board colour, the gable and fin in the accent colour on Whole, 2% and Skim, one colour all over on Chocolate and Oat, and the bottom 110 mm a built-in plinth in the accent colour with a fine shadow line above it. No creases, no folds, no print. The only wordmark is a cast metal badge with raised lettering, centred on the plinth's front, and an engraving on the bare birch back panel above the Nutrition Facts. Bare birch shows only on that back panel.* *Later the same day: the Facts are an engraved bronze plate on the finish, the back wordmark is the same cast letters as the front, and two printed marks are spec: OPEN OTHER SIDE with its arrow on the back slope, SHAKE WELL under the port. Bare birch shows nowhere on the product.* *2026-10-07: no plate; the Nutrition Facts are printed on the back's finish, black on the white flavours, like a carton's panel.*

Proportions come from `spec/geometry.md`, colors from `spec/colorways.json`, copy from `copy/`.

## What a render must not do

- Change the carton's proportions, soften its edges, taper it, or otherwise "improve" the silhouette.
- Add a grille, glossy plastic, a cap, tuning plates, or a second tweeter.
- Angle the tweeter up, square the bowl, or sink it vertically.
- Show bare birch anywhere but the back window and the exploded or section views (shot 07 is the exploded view). *2026-10-02: the back panel and the section views; there is no exploded view.*
- Put a flavor word under the wordmark, or a label on the sleeve.
- *2026-10-02:* put the wordmark anywhere but the badge and the back engraving, print anything on the cabinet, or show the colour as a wrap with a cut edge. *2026-10-07: the printed marks are the two above and the Nutrition Facts on the back; nothing else.*
