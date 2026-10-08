# Shot 03 · Bowl close-up · v21

v21: the owner's 2026-10-07 changes. The body's vertical corners and the gable's hips rounded 3 mm in the model (the fin's edges 1.5), so the corners take a highlight and the outline softens by that much; a 3 mm shadow line where the gable meets the body, like the plinth's; no lip at the scoop, the mouth the finish's own eased edge, and the tweeter's ring and seat black; the shader eases what is left by 1.5 mm (was 6). A new look, so the critic count starts again at round 1. Light and camera as v19.
v19: after round 2 of the v17 batch (5: a wash bleaching the red; the white body the sweep's value; the bowl's left a murk). A mid-grey set, so the white body stands off it; half the environment, so the slope keeps its red beside the strip's band; the card into the bowl brighter and aimed at its far side; the tweeter's seat ring satin metal. The last round in this batch.
v18: after round 1 of the v17 batch (4: neither hero nor detail; the driver an eye). Back to the brief: gable height (0.97 m) and close, 25 degrees off the axis, so the mouth fills much of the frame and the camera looks along the throat at the tweeter, face on inside the polished lip, with its seat ring, surround and screws; the fin across the top, the mouth left of centre; the top strip narrower and further, a line on the slope rather than a haze; edges eased 6 mm.
v17: the owner's 2026-10-06 changes, and refinement round 3's carries. A polished stainless lip rings the scoop's mouth (the owner), and the tweeter's faceplate sits in a moulded ring where the throat ends. Framed wider and from higher (about 21 degrees down, a 90 mm lens), so the fin and the gable's outline say carton (tight on the bowl alone it read as a basin), the mid driver clear of the bottom edge; the top light a strip box (0.25 x 1.4 m) further up, so the red slope mirrors it as a band instead of a milky sheen; a low card in front lighting the bowl's back wall; the key on the same axis but further and smaller. A new batch for the critic (round 1 again).
v16: after refinement round 2. A 0.9 m softbox high to the left, where the red slope mirrors it, so a highlight band grades across the slope and its light reaches the bowl's floor: the bowl fills with its own red (it bottomed out near black, darker than the faceplate) and the darkest values in the frame are the driver's. The crop up and tighter, so the mid driver's rim leaves the bottom edge and the fin stands whole at the top. The corners eased at last: the path tracer joins each cabinet's finish into one object before its bevel (every panel was its own mesh, so the bevel never reached a corner).
v15: after refinement round 1. The overhead rake replaced by a large soft key from the front-left at about 18 degrees, the one direction that reaches a tweeter facing forward under the bowl's upper lip, so its faceplate, chamfer, screws and dome read instead of an eye socket; environment and fill down; the camera pulled back with the cabinet's front-left corner inside the frame and the mid's rim showing for scale. Eased edges 4 mm. The dust caps are round domes (until now squashed across their axis: pills).
v14: render polish (owner, 2026-10-05): the tweeter's faceplate carries a polished chamfer and its dome is coated textile, so the bowl's throat shows a driver instead of a black hole; a faint orange peel in the lacquer; two tall strips behind the subject for edge lines.
v13: the studio key softbox is placed from the real-time key's distance, so for the rake it is closer and smaller and the red takes a highlight gradient; the dome drops to fill strength; the eased arris 2 mm. Path-traced round 2 asked for one decisive source the red, the dome and the bowl each answer differently.
v12: the studio floor sweeps up into a backdrop behind the subject, so there is no horizon line in the frame; in the path-traced pass the key is a softbox and the dome is a gradient, so the lacquer has something to reflect, and the cabinet's arrises are eased by about a millimetre in the shader. Nothing on the product changed. Path-traced round 1 on v11 called the red a vector fill with a rendered hole in it.
v11: camera a hair further back on a 95 mm lens, aimed so both the top lip and the mid's flange stay out of frame (critic rounds 1 to 3). No critic round: the cap for this look is reached.
v8: the plate is gone. The wordmark on the plinth is cast metal letters standing on the lacquer with no plate behind them, the way the lettering sits on a La Marzocco machine: 44 mm type size, 2.5 mm proud, polished faces, satin sides. Nothing else changed.
v7: after critic round 1 on v6 (shot 01's note that the badge read as grey type on a grey rectangle at room distance). The badge is now a chrome rim around a dark inset field with polished raised letters, the way a cast espresso-machine badge reads; nothing else changed.
v6: the 2026-10-02 direction. The gable is finished birch, not a die-cut lid: the mouth edge is the finish's edge on the carved bowl, no crease above it. Camera and light as v5.
v5: after critic round 4. The bowl no longer receives the key's shadow map, so the lip's hard terminator (read as a kink) becomes the smooth falloff of the loft; camera tilted down a hair so the top lip leaves the frame and more of the white body shows below.
v4: the locked look from the 2026-10-01 amendments: lids in the print colour on Whole, 2% and Skim, a printed 110 mm base band carrying the wordmark on the front and the right side, nothing printed under the gable. The stand and the owner's panel are optional and not in this shot. Camera note from critic round 3: the camera offset a few degrees so the faceplate shows its edge.
v3: after critic round 2. Key steeper and more frontal so the slope reads brighter than the front; occlusion pass; glossier board so the edge and faces separate; the side wordmark sliver cropped out; 2x supersampling. The ground stays #F8F7F4 by spec.
v2: after critic round 1. One key from above-left with the environment as the white card; the faceplate made reflective so it is not a void; camera pulled back so the wordmark baseline and the top edge clear the frame.
v1: first brief, from the README shot list.

**Proves:** the bowl is a real carved waveguide with a tweeter at its throat, and the lid is die-cut board, not paint.

## Scene
- One speaker, **Whole**. The bowl interior carries the Whole throat gradient, #C62828 at the mouth to #8E1B1B at the throat.
- Studio or window light that rakes across the slope so the bowl's concavity reads.

## Camera
- Front three-quarter at gable height, roughly `z` 900 to 1000 mm, close enough that the mouth fills much of the frame.
- Focus on the throat and the dome. Shallow depth of field is fine; the dome must be sharp.

## Must show
- The smooth loft from the mouth ellipse to the throat circle: no flats, no edges.
- The painted gradient, light at the mouth, dark at the throat.
- The faceplate ring at the throat and the dome, 170 mm back.
- The fold of the lid's die-cut at the mouth edge: the board's cut edge and its thickness, the lid's crease above, the board sitting on the birch.

## Must not
- Anything in the list in `prompts/README.md`.
- Show bare birch beyond the cut edge of the board at the mouth.

## Text-to-image form
Constant block, then: Close up on the top of one of them, white board with the red print, three-quarter from the front at the height of the gable, looking into the elliptical opening on the slope: a smooth concave painted bowl, red at its rim shading to a deep dark red at the throat, where a small one-inch dome tweeter sits in a round faceplate, 170 mm back. The opening's edge shows the cut thickness of the printed board and the fold of the lid above it. Shallow depth of field, the dome sharp. Photoreal, matte board, no grille.

## Acceptance
- The bowl reads as concave and smooth, and the tweeter reads as set back inside it, facing forward.
- The die-cut edge reads as board, with thickness.
