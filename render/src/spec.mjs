// The numbers from spec/geometry.md, in millimetres, in the frame that file defines:
// x across the width (0 left, 390 right), y depth (0 front face, 390 back face), z height (0 floor).
// If this file and spec/geometry.md disagree, spec/geometry.md wins and this file is wrong.

export const FS = {
  plan: 390,
  body: 860,
  gableRise: 150,
  fin: { height: 45, thick: 8 },
  wall: 18,
  woofer: { z: 290, frame: 310 },
  mid: { z: 690, frame: 170 },
  tweeter: { faceplateY: 170, z: 903.5, faceplate: 62, faceplateThick: 6, apexForward: 8, bodyDepth: 38, bodyHeight: 60 },
  bowl: { mouthWidth: 211, mouthLength: 118, mouthCenterS: 79, throat: 66 },
  back: {
    // 2026-10-02: no sleeve. Two shapes for the bare birch field on the finished back:
    //  'label' (default): the Facts panel plus a 26 margin all round; the port, the posts and the engraved wordmark sit on the finish outside it.
    //  'full': the field from above the plinth to 30 below the body's top, with the same 26 margin at the sides and above the plinth (was z 40 to 798 inside the sleeve frame).
    panel: 'label',
    window: { x0: 26, x1: 364, z0: 140, z1: 830 },
    labelMargin: 26,
    label: { w: 266, h: 240, top: 770 },
    port: { d: 100, z: 405, flange: 112, bore: 92 },
    posts: { w: 128, h: 64, z: 150, zFull: 185, postD: 24, spacing: 64 }, // 150 clears the plinth's shadow line (was 144); 185 sits inside the full field
  },
  sleeve: { board: 1.5 },
  // 2026-10-02: no sleeve. The colour is a finish on the birch; the skin keeps the sleeve's outer dimensions.
  plinth: { height: 110, shadowLine: 3 },
  badge: { type: 44, relief: 2.5, z: 55 }, // cast metal letters, no plate: the wordmark itself in relief on the plinth's front
  backWordmark: { size: 36, baseline: 812, baselineFull: 788 }, // on the finish above the label field, or inside the full field
  // As drawn on the Sleeves and Hero artboards.
  print: {
    front: { size: 47, baselineBelowTop: 43 },
    side: { size: 64, baselineBelowTop: 94, fromFront: 35 },
    trackingEm: -0.035,
  },
};

// Pint: parked. Fin thickness and bowl are not specified; both are the floorstander's scaled by the plan ratio.
export const PINT = {
  plan: 100,
  body: 200,
  gableRise: 35,
  fin: { height: 12, thick: 2 },
  driver: { z: 95, frame: 68 },
  bowlScale: 100 / 390,
  board: 0.6,
  wall: 5,
};

export const CRATE = { w: 340, d: 250, h: 130, cols: 3, rows: 2, wall: 10 };

export function derived(s) {
  const run = s.plan / 2;
  const slope = Math.hypot(run, s.gableRise);
  return {
    run,
    slope,
    angle: Math.atan2(s.gableRise, run),
    dirY: run / slope,
    dirZ: s.gableRise / slope,
    ridgeZ: s.body + s.gableRise,
    total: s.body + s.gableRise + s.fin.height,
  };
}

// A point on the front slope at distance s from the front top edge, on the centreline.
export function slopePoint(spec, s) {
  const d = derived(spec);
  return { x: spec.plan / 2, y: d.dirY * s, z: spec.body + d.dirZ * s };
}
