# Shot 02 · Two rooms, years apart · v16

v16: after refinement round 2. The cabinet's corners eased at last: the path tracer joins each cabinet's finish into one object before rendering, because the shader's bevel only sees its own object and every panel was its own mesh. The shared camera a little more frontal (about 25 degrees off the axis), so the tweeter sits further into the bowl's opening. The old room: the window taller (sill 0.35), so the beam takes the whole front from gable to plinth and lays a crisp patch on the boards; env, bounce, the lamp, the window's sky and the exposure up, so the room, the chair and the wordmark read and the red stays red.
v15: after refinement round 1. In both rooms the window moves to the left wall, so a low sun crosses the baffle and the gable and the side the camera sees falls a stop into shade; the cabinet's own shadow runs back-right across the boards. The neutral fill, the bounce and the old room's lamp down, exposure down so the white sits below clipping. The camera lower (0.95 m) with the speaker left of the centre line; the chair at the right for balance. Eased edges 4 mm in the shader (silhouette unchanged). The dust caps are round domes (until now squashed across their axis: pills).
v14: render polish (owner, 2026-10-05): the tweeter's polished chamfer and textile dome, orange peel in the lacquer, paper cones, grain and plaster, dining chairs. Nothing on the product's geometry changed.
v13: in both rooms the window moves to the right wall, the camera's side, so the sun lights the faces the camera sees and the cabinet's own shadow falls back-left, attached to its base; the chair moves out of that shadow. The old room's window glows more against its lamp. Paper cones matte; plank grain stronger; the eased arris 2 mm. Path-traced round 2 asked for a shadow that belongs to the cabinet.
v12: both rooms are closed boxes (ceiling, right wall, a wall behind the camera), so in the path-traced pass the only daylight is the window's: sun patch, sky glow, the fill inside the opening; the old room keeps its lamp. Nothing on the product changed. Path-traced round 1 on v11 asked for a key the room agrees with and a cabinet with weight on the floor.
v11: the window's mullion removed in both rooms so no bar crosses the hero face (critic rounds 1 to 3). The brief is the rebriefed one: the same pair in two homes, years apart. No critic round: the cap for this look is reached.
v8: the plate is gone. The wordmark on the plinth is cast metal letters standing on the lacquer with no plate behind them, the way the lettering sits on a La Marzocco machine: 44 mm type size, 2.5 mm proud, polished faces, satin sides. Nothing else changed.
v7: after critic round 1 on v6 (shot 01's note that the badge read as grey type on a grey rectangle at room distance). The badge is now a chrome rim around a dark inset field with polished raised letters, the way a cast espresso-machine badge reads; nothing else changed.
v6: the 2026-10-02 direction. No sleeve, so no skin change: both rooms show the same Whole, finished white and red with the plinth and the badge, until the shot is rebriefed (its point was the swap). Camera and light as v5.
v5: after critic round 4. The old room's low sun raised so the fin's shadow lands on the slope and not across the front between the spout and the mid driver. Whole by day and Oat by night is the shot's point and stays.
v4: the locked look from the 2026-10-01 amendments: lids in the print colour on Whole, 2% and Skim, a printed 110 mm base band carrying the wordmark on the front and the right side, nothing printed under the gable. The stand and the owner's panel are optional and not in this shot.
v3: after critic round 2. Occlusion pass, fold and crimp lines, glossier board, shaded cones, a cool sky ambient in the old room so the shadows are not sepia, chair moved clear of the carton's edge, 2x supersampling. The Oat print is dark brown by spec.
v2: after critic round 1. Windows moved to the front-left so the sun lights the faces the camera sees; a chair in each room for scale (the room changes, the speaker does not); contact shadows; floor bounce; driver hardware and board materials rebuilt. The colour change between a and b is the point of the shot and stays.
v1: first brief, from the README shot list.

**Proves:** the sleeve argument. One object, one floor spot, two skins, years apart. It must read as the same speaker that changed its skin, not as two products.

## Frames
- **a.** **Whole** in a bright apartment: white walls, daylight, a new floor.
- **b.** **Oat** in a darker, older room: warmer and lower light, older floor and walls, the same floor spot.

## Scene
- One speaker, not the pair. Same position on the floor in both frames.
- The room changes around it; the speaker's position, size and camera do not.

## Camera
- Identical in both frames: same height, lens, framing and distance. Lock it before rendering either frame.
- Three-quarter view, the speaker fully in frame.

## Must show
- Pixel-matched silhouette between a and b. Overlaying the two frames should align the speaker exactly.
- The sleeve colour and the room are the only differences.

## Must not
- Anything in the list in `prompts/README.md`.
- Move the camera, the speaker, or change its size between frames.

## Text-to-image form
Constant block, then, for a: One of them in a bright apartment, white board with the red wordmark, daylight from a large window, white walls, a light wood floor, three-quarter view. For b: The same speaker in the same spot years later, now unbleached oat-coloured board with a dark brown wordmark, in an older room with warm low lamplight, a darker worn floor and aged walls, the camera unchanged.

## Acceptance
- A viewer sees one object that changed its skin, not two speakers.
- Overlay test passes.
