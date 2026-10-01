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
    window: { x0: 26, x1: 364, z0: 40, z1: 798 },
    label: { w: 266, h: 240, top: 770 },
    port: { d: 100, z: 405, flange: 112, bore: 92 },
    posts: { w: 128, h: 64, z: 144, postD: 24, spacing: 64 },
  },
  sleeve: { board: 1.5 },
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
