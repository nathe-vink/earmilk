# Shot 02 · Two rooms, years apart · v2

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
