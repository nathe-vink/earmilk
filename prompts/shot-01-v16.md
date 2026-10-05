# Shot 01 · Hero pair in a room · v16

v16: after refinement round 2. The exposure down about half a stop, so the sunlit white sides (measured at 249) and the coral plinths stop clipping and the white faces separate as the coral ones do; the chair turned toward the window, set down rather than posed facing the camera. The corners eased at last: the path tracer joins each cabinet's finish into one object before its bevel (every panel was its own mesh, so the bevel never reached a corner).
v15: after refinement round 1. The window and sun moved so the beam falls across both cabinets from the right: each throws its own long shadow across the boards, the near one's lit side a stop above its front, and no sun patch on the blank wall. Fill and bounce down so the plinths sit in contact shadow. The chair against the wall between the pair, clear of both cabinets' edges. Eased edges 4 mm in the shader (silhouette unchanged). The dust caps are round domes (until now squashed across their axis: pills).
v14: render polish (owner, 2026-10-05: more photoreal): the tweeter's faceplate carries a polished chamfer so the driver deep in the bowl reads; coated-textile domes; a faint orange peel in the lacquer; pressed-paper cones; grain in the floor, plaster on the walls; the chair is a dining chair with tapered legs and a curved back. Nothing on the product's geometry changed.
v13: the window moves to the right wall, the camera's side, and widens to 2.6 m: the sun now lights the faces the camera sees and each cabinet's own shadow falls across the floor where the viewer can see it, both cabinets inside the same band of sun. The chair stands clear of the left cabinet. Paper cones matte; plank grain and gaps stronger; the shader's eased arris 2 mm. Path-traced round 2 asked for one sun that the cabinets, floor and wall agree on.
v12: the room is now a closed box (ceiling, right wall, a wall behind the camera), so in the path-traced pass the only daylight is what the window admits: the sun's patch across the floor, the sky's glow through the opening and the fill standing inside it. The window's mullion is gone, as in the two rooms. The chair stands fully in frame at the left. Nothing on the product changed. Path-traced round 1 on v11 asked for one light the wall, floor and cabinets all obey; this is that.
v11: the pair toed in 0.2 rad toward the listening spot and the camera lower on a 60 mm lens from a step further back, so the two read as a pair (critic rounds 1 to 3 on the finish look). No critic round: the cap for this look is reached.
v8: the plate is gone. The wordmark on the plinth is cast metal letters standing on the lacquer with no plate behind them, the way the lettering sits on a La Marzocco machine: 44 mm type size, 2.5 mm proud, polished faces, satin sides. Nothing else changed.
v7: after critic round 1 on v6 (shot 01's note that the badge read as grey type on a grey rectangle at room distance). The badge is now a chrome rim around a dark inset field with polished raised letters, the way a cast espresso-machine badge reads; nothing else changed.
v6: the 2026-10-02 direction. No sleeve: the cabinet is birch finished in Whole's colours, white body, red gable and fin, a built-in red plinth with a shadow line, and a cast metal badge on the plinth's front. Nothing on the sides. Camera and light as v5.
v5: after critic round 4. Fill and bounce cut and the sun raised so the pair's cast shadows read as the same light that makes the wall wedge; the chair moved clear of the left speaker's silhouette. Surface and penumbra asks stay with the photoreal pass.
v4: the locked look from the 2026-10-01 amendments: lids in the print colour on Whole, 2% and Skim, a printed 110 mm base band carrying the wordmark on the front and the right side, nothing printed under the gable. The stand and the owner's panel are optional and not in this shot. Camera note from critic round 3: the window wall moved out so the room's corner line clears the left speaker.
v3: after critic round 2. Ambient occlusion pass; glossier coated board so the faces pick up the room; fold lines at the ridge and the lid's bottom edge and crimp lines on the fin; lighter shaded cones with highlights on cap and surround; reflective floor; finer shadow maps; rendered at 2x and downscaled. The sun stays on the left window because the pair faces the room.
v2: after critic round 1. Sun stronger and fills cut back so the cartons throw hard shadows that agree with the wall light; contact shadows; warm floor bounce; skirting; a wooden chair by the back wall replaces the sofa arm; camera recentred on the pair; coated-board sheen and rounded board edges; driver baskets rebuilt with flange, screws and a glossy surround.
v1: first brief, from the README shot list.

**Proves:** a serious speaker and a half gallon of milk at the same time, at room scale.

## Scene
- Two speakers, both **Whole**, about 2 m apart on the floor of a living room, facing the room.
- A chair or a sofa arm in frame for scale. Nothing else that competes with the pair.
- Late-afternoon window light from one side; soft, long shadows across the floor.

## Camera
- Height 1.2 m. A ~50 mm look. Three-quarter view so the front and one side of each speaker show.
- Both speakers fully in frame, fin to floor contact. Do not crop the fin.

## Must show
- The full silhouette of both: fin, ridge, both slopes, both drivers, the bowl mouth reading as a dark ellipse on the front slope.
- Fold creases at the gable catching the window light.
- The front wordmark on both; the side wordmark on the visible side.

## Must not
- Anything in the list in `prompts/README.md`.

## Text-to-image form
Constant block, then: Two of them in a living room, white board with the red wordmark, standing about two metres apart on a wooden floor, the arm of a sofa at the edge of the frame for scale, late-afternoon sun through a window on one side, soft long shadows, photographed from a three-quarter angle with the camera at 1.2 m and a 50 mm lens. Photoreal, physically plausible materials, matte board, no grille.

## Acceptance
- Reads as a milk carton at first glance and as a speaker at second.
- The pair are identical and match `spec/geometry.md`: 2.7 widths tall from floor to fin.
- Light and shadow are consistent between the two speakers and the room.
