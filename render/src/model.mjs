// Builds the carton speaker from spec/geometry.md (via spec.mjs). Units: millimetres.
// Local frame: origin at the floor under the centre of the plan, X to the right, Y up, Z toward the front.
// Spec (x, y, z) maps to local (x - plan/2, z, plan/2 - y).
import { FS, PINT, derived } from './spec.mjs';

export function specFor(kind) {
  if (kind === 'pint') {
    const k = PINT.bowlScale;
    return {
      kind, plan: PINT.plan, body: PINT.body, gableRise: PINT.gableRise, fin: PINT.fin, board: PINT.board, wall: PINT.wall,
      drivers: [{ z: PINT.driver.z, frame: PINT.driver.frame }],
      bowl: { mouthWidth: FS.bowl.mouthWidth * k, mouthLength: FS.bowl.mouthLength * k, mouthCenterS: FS.bowl.mouthCenterS * k, throat: FS.bowl.throat * k, setback: FS.tweeter.faceplateY * k, axisZ: PINT.body + (FS.tweeter.z - FS.body) * k, bulge: 4.5 * k },
      tweeter: null, back: null,
      print: {
        front: { size: FS.print.front.size * k, baselineBelowTop: FS.print.front.baselineBelowTop * k },
        side: { size: FS.print.side.size * k, baselineBelowTop: FS.print.side.baselineBelowTop * k, fromFront: FS.print.side.fromFront * k },
        trackingEm: FS.print.trackingEm,
      },
    };
  }
  return {
    kind: 'fs', plan: FS.plan, body: FS.body, gableRise: FS.gableRise, fin: FS.fin, board: FS.sleeve.board, wall: FS.wall,
    drivers: [{ z: FS.woofer.z, frame: FS.woofer.frame }, { z: FS.mid.z, frame: FS.mid.frame }],
    bowl: { ...FS.bowl, setback: FS.tweeter.faceplateY, axisZ: FS.tweeter.z, bulge: 4.5 },
    tweeter: FS.tweeter, back: FS.back, print: FS.print,
  };
}

function rectShape(THREE, x0, y0, x1, y1) {
  const s = new THREE.Shape(); s.moveTo(x0, y0); s.lineTo(x1, y0); s.lineTo(x1, y1); s.lineTo(x0, y1); s.closePath(); return s;
}
function circleHole(THREE, cx, cy, r) { const p = new THREE.Path(); p.absarc(cx, cy, r, 0, Math.PI * 2, true); return p; }
function ellipseHole(THREE, cx, cy, rx, ry) { const p = new THREE.Path(); p.absellipse(cx, cy, rx, ry, 0, Math.PI * 2, true, 0); return p; }

export function makeMaterials(THREE, tex, flavor) {
  const M = THREE;
  const board = new M.MeshPhysicalMaterial({ color: flavor.board, roughness: 0.93, metalness: 0, sheen: 0.25, sheenRoughness: 0.9, sheenColor: new M.Color(0xffffff), side: M.DoubleSide });
  const birch = new M.MeshStandardMaterial({ map: tex.birch(), roughness: 0.7, metalness: 0, side: M.DoubleSide });
  const bowl = new M.MeshPhysicalMaterial({ map: tex.gradient(flavor.throat.mouth, flavor.throat.throat), roughness: 0.42, metalness: 0, clearcoat: 0.25, clearcoatRoughness: 0.5, side: M.DoubleSide });
  const decal = (t) => new M.MeshStandardMaterial({ map: t, transparent: true, roughness: 0.93, metalness: 0, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, depthWrite: false });
  return {
    board, birch, bowl, decal,
    cone: new M.MeshStandardMaterial({ color: 0x0b0b0b, roughness: 0.96 }),
    frame: new M.MeshStandardMaterial({ color: 0x1c1c1c, roughness: 0.55, metalness: 0.35 }),
    surround: new M.MeshStandardMaterial({ color: 0x101010, roughness: 0.75 }),
    dustcap: new M.MeshStandardMaterial({ color: 0x141414, roughness: 0.9 }),
    faceplate: new M.MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.4, metalness: 0.6 }),
    dome: new M.MeshStandardMaterial({ color: 0x111111, roughness: 0.55 }),
    dark: new M.MeshStandardMaterial({ color: 0x060606, roughness: 1, side: M.DoubleSide }),
    portFlange: new M.MeshStandardMaterial({ color: 0x2c2c2c, roughness: 0.6, metalness: 0.2 }),
    plate: new M.MeshStandardMaterial({ color: 0x1b1b1b, roughness: 0.6, metalness: 0.3 }),
    postRed: new M.MeshStandardMaterial({ color: 0xc62828, roughness: 0.45, metalness: 0.1 }),
    postBlack: new M.MeshStandardMaterial({ color: 0x2e2e2e, roughness: 0.45, metalness: 0.2 }),
  };
}

// state: { sleeve, lid, lidLift, tubeLift } in mm.
export function buildSpeaker(THREE, addons, ctx, { kind = 'fs', flavor, state = {} }) {
  const S = specFor(kind);
  const st = { sleeve: true, lid: true, lidLift: 0, tubeLift: 0, ...state };
  const mats = ctx.materials(flavor);
  const d = derived(S);
  const half = S.plan / 2, L = d.slope, dy = d.dirY, dz = d.dirZ, ridgeZ = d.ridgeZ;
  const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
  const mesh = (geom, mat, shadow = true) => { const m = new THREE.Mesh(geom, mat); m.castShadow = shadow; m.receiveShadow = shadow; return m; };

  const frontBasis = new THREE.Matrix4().makeBasis(V3(1, 0, 0), V3(0, dz, -dy), V3(0, dy, dz)).setPosition(V3(0, S.body, half));
  const backBasis = new THREE.Matrix4().makeBasis(V3(-1, 0, 0), V3(0, dz, dy), V3(0, dy, -dz)).setPosition(V3(0, S.body, -half));
  const rightBasis = new THREE.Matrix4().makeBasis(V3(0, 0, -1), V3(0, 1, 0), V3(1, 0, 0)).setPosition(V3(half, 0, 0));
  const leftBasis = new THREE.Matrix4().makeBasis(V3(0, 0, 1), V3(0, 1, 0), V3(-1, 0, 0)).setPosition(V3(-half, 0, 0));

  const b = S.bowl, rx = b.mouthWidth / 2, ry = b.mouthLength / 2;
  const slopeRect = () => rectShape(THREE, -half, 0, half, L);
  const slopeWithMouth = () => { const s = slopeRect(); s.holes.push(ellipseHole(THREE, 0, b.mouthCenterS, rx, ry)); return s; };
  const endTri = () => { const s = new THREE.Shape(); s.moveTo(-half, S.body); s.lineTo(half, S.body); s.lineTo(0, ridgeZ); s.closePath(); return s; };

  const g = new THREE.Group();
  g.name = `speaker-${kind}-${flavor.name}`;

  // Cabinet: body box, carved gable block, fin. Birch.
  const cab = new THREE.Group(); g.add(cab);
  // The body is a real box of panels: a baffle with driver cut-outs, back, sides, top and bottom.
  const wall = S.wall;
  const baffle = rectShape(THREE, -half, 0, half, S.body);
  for (const dr of S.drivers) baffle.holes.push(circleHole(THREE, 0, dr.z, dr.frame / 2 * 0.88));
  cab.add(mesh(new THREE.ExtrudeGeometry(baffle, { depth: wall, bevelEnabled: false, curveSegments: 64 }).translate(0, 0, half - wall), mats.birch));
  const backPanel = rectShape(THREE, -half, 0, half, S.body);
  if (S.back) backPanel.holes.push(circleHole(THREE, 0, S.back.port.z, S.back.port.bore / 2));
  cab.add(mesh(new THREE.ExtrudeGeometry(backPanel, { depth: wall, bevelEnabled: false, curveSegments: 64 }).translate(0, 0, -half), mats.birch));
  for (const sx of [-1, 1]) cab.add(mesh(new THREE.BoxGeometry(wall, S.body, S.plan - 2 * wall).translate(sx * (half - wall / 2), S.body / 2, 0), mats.birch));
  cab.add(mesh(new THREE.BoxGeometry(S.plan - 2 * wall, wall, S.plan - 2 * wall).translate(0, S.body - wall / 2, 0), mats.birch));
  cab.add(mesh(new THREE.BoxGeometry(S.plan - 2 * wall, wall, S.plan - 2 * wall).translate(0, wall / 2, 0), mats.birch));
  cab.add(mesh(new THREE.ShapeGeometry(slopeWithMouth(), 64).applyMatrix4(frontBasis), mats.birch));
  cab.add(mesh(new THREE.ShapeGeometry(slopeRect(), 4).applyMatrix4(backBasis), mats.birch));
  cab.add(mesh(new THREE.ShapeGeometry(endTri(), 4).applyMatrix4(rightBasis), mats.birch));
  cab.add(mesh(new THREE.ShapeGeometry(endTri(), 4).applyMatrix4(leftBasis), mats.birch));
  cab.add(mesh(new THREE.BoxGeometry(S.plan, S.fin.height, S.fin.thick).translate(0, ridgeZ + S.fin.height / 2, 0), mats.birch));

  // Bowl: smooth loft from the mouth ellipse (in the slope plane) to the throat circle (in the plane of the faceplate).
  const throatR = b.throat / 2, throatZ = half - b.setback, axisY = b.axisZ;
  const mouthPt = th => V3(rx * Math.cos(th), b.mouthCenterS + ry * Math.sin(th), 0).applyMatrix4(frontBasis);
  const radial = th => V3(Math.cos(th), Math.sin(th), 0).transformDirection(frontBasis);
  const bowlGeom = new addons.ParametricGeometry((u, v, target) => {
    const th = u * Math.PI * 2, t = v;
    const m = mouthPt(th), T = V3(throatR * Math.cos(th), axisY + throatR * Math.sin(th), throatZ);
    const amp = (b.bulge + (b.bulge / 3) * Math.sin(th)) * Math.sin(Math.PI * t);
    const r = radial(th);
    target.set(m.x * (1 - t) + T.x * t + r.x * amp, m.y * (1 - t) + T.y * t + r.y * amp, m.z * (1 - t) + T.z * t + r.z * amp);
  }, 128, 48);
  cab.add(mesh(bowlGeom, mats.bowl));
  // Seal the throat behind the faceplate.
  const seal = mesh(new THREE.CircleGeometry(throatR + 1, 64), mats.dark); seal.position.set(0, axisY, throatZ - 0.6); cab.add(seal);

  // Tweeter at the throat (floorstander only).
  if (S.tweeter) {
    const tw = S.tweeter, pr = tw.faceplate / 2;
    const plate = mesh(new THREE.CylinderGeometry(pr, pr, tw.faceplateThick, 64), mats.faceplate);
    plate.rotation.x = Math.PI / 2; plate.position.set(0, axisY, throatZ - tw.faceplateThick / 2); cab.add(plate);
    const baseR = 12.7, h = tw.apexForward, sr = (baseR * baseR + h * h) / (2 * h);
    const dome = mesh(new THREE.SphereGeometry(sr, 48, 24, 0, Math.PI * 2, 0, Math.acos((sr - h) / sr)), mats.dome);
    dome.rotation.x = Math.PI / 2; dome.position.set(0, axisY, throatZ + h - sr); cab.add(dome);
    const ring = mesh(new THREE.RingGeometry(baseR, baseR + 3, 64), mats.dome); ring.position.set(0, axisY, throatZ + 0.2); cab.add(ring);
  }

  // Drivers on the baffle, proud of the board.
  for (const dr of S.drivers) {
    const R = dr.frame / 2;
    const grp = new THREE.Group(); grp.position.set(0, dr.z, half + S.board); cab.add(grp);
    const ring = mesh(new THREE.RingGeometry(R * 0.9, R, 64), mats.frame); ring.position.z = 1.2; grp.add(ring);
    const rim = mesh(new THREE.CylinderGeometry(R, R, 3, 64, 1, true), mats.frame); rim.rotation.x = Math.PI / 2; rim.position.z = -0.3; grp.add(rim);
    const sur = mesh(new THREE.TorusGeometry(R * 0.85, R * 0.055, 16, 64), mats.surround); sur.position.z = 0.6; grp.add(sur);
    const pts = []; for (let i = 0; i <= 10; i++) { const f = i / 10; pts.push(new THREE.Vector2(R * 0.8 - (R * 0.8 - R * 0.18) * f, -R * 0.36 * Math.pow(f, 0.85))); }
    pts.push(new THREE.Vector2(0.001, -R * 0.36));
    const cone = mesh(new THREE.LatheGeometry(pts, 64), mats.cone); cone.rotation.x = Math.PI / 2; grp.add(cone);
    const cap = mesh(new THREE.SphereGeometry(R * 0.2, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), mats.dustcap);
    cap.rotation.x = Math.PI / 2; cap.scale.z = 0.6; cap.position.z = -R * 0.33; grp.add(cap);
  }

  // Back of the cabinet: engraved label, port, binding posts (floorstander only).
  if (S.back) {
    const B = S.back;
    const lab = ctx.tex.engravedLabel();
    const labelMesh = mesh(new THREE.PlaneGeometry(lab.widthMm, lab.heightMm), mats.decal(lab.texture), false);
    labelMesh.rotation.y = Math.PI; labelMesh.position.set(0, B.label.top - lab.heightMm / 2, -half - 0.3); cab.add(labelMesh);
    const flange = mesh(new THREE.RingGeometry(B.port.bore / 2, B.port.flange / 2, 64), mats.portFlange); flange.rotation.y = Math.PI; flange.position.set(0, B.port.z, -half - 0.4); cab.add(flange);
    const bore = mesh(new THREE.CylinderGeometry(B.port.bore / 2, B.port.bore / 2, 90, 64, 1, true), mats.dark); bore.rotation.x = Math.PI / 2; bore.position.set(0, B.port.z, -half + 45); cab.add(bore);
    const boreEnd = mesh(new THREE.CircleGeometry(B.port.bore / 2, 64), mats.dark); boreEnd.rotation.y = Math.PI; boreEnd.position.set(0, B.port.z, -half + 90); cab.add(boreEnd);
    const plate = mesh(new THREE.BoxGeometry(B.posts.w, B.posts.h, 5), mats.plate); plate.position.set(0, B.posts.z, -half - 2.5 - 0.3); cab.add(plate);
    for (const [x, mat] of [[B.posts.spacing / 2, mats.postRed], [-B.posts.spacing / 2, mats.postBlack]]) {
      const post = mesh(new THREE.CylinderGeometry(B.posts.postD / 2, B.posts.postD / 2, 16, 48), mat); post.rotation.x = Math.PI / 2; post.position.set(x, B.posts.z, -half - 5.3 - 8); cab.add(post);
      const hole = mesh(new THREE.CircleGeometry(4.5, 32), mats.dark); hole.rotation.y = Math.PI; hole.position.set(x, B.posts.z, -half - 5.3 - 16.2); cab.add(hole);
    }
  }

  if (!st.sleeve) return g;
  const P = S.print, bd = S.board;

  // Tube: four boards around the body; the front is die-cut for the drivers, the back is a frame around the window.
  const tube = new THREE.Group(); tube.position.y = st.tubeLift; g.add(tube);
  const frontShape = rectShape(THREE, -half, 0, half, S.body);
  for (const dr of S.drivers) frontShape.holes.push(circleHole(THREE, 0, dr.z, dr.frame / 2));
  tube.add(mesh(new THREE.ExtrudeGeometry(frontShape, { depth: bd, bevelEnabled: false, curveSegments: 64 }).translate(0, 0, half), mats.board));
  const backShape = rectShape(THREE, -half, 0, half, S.body);
  if (S.back) { const w = S.back.window; const hole = new THREE.Path(); hole.moveTo(w.x0 - half, w.z0); hole.lineTo(w.x0 - half, w.z1); hole.lineTo(w.x1 - half, w.z1); hole.lineTo(w.x1 - half, w.z0); hole.closePath(); backShape.holes.push(hole); }
  tube.add(mesh(new THREE.ExtrudeGeometry(backShape, { depth: bd, bevelEnabled: false }).translate(0, 0, -half - bd), mats.board));
  for (const sx of [-1, 1]) tube.add(mesh(new THREE.BoxGeometry(bd, S.body, S.plan).translate(sx * (half + bd / 2), S.body / 2, 0), mats.board));

  // Print: the wordmark on the front, above the mid, and larger on the right side reading front to back.
  const fw = ctx.tex.wordmark({ sizeMm: P.front.size, color: flavor.print, trackingEm: P.trackingEm });
  const front = mesh(new THREE.PlaneGeometry(fw.widthMm, fw.heightMm), mats.decal(fw.texture), false);
  front.position.set(0, S.body - P.front.baselineBelowTop + 0.35 * P.front.size, half + bd + 0.3); tube.add(front);
  const sw = ctx.tex.wordmark({ sizeMm: P.side.size, color: flavor.print, trackingEm: P.trackingEm });
  const side = mesh(new THREE.PlaneGeometry(sw.widthMm, sw.heightMm), mats.decal(sw.texture), false);
  side.rotation.y = Math.PI / 2;
  side.position.set(half + bd + 0.3, S.body - P.side.baselineBelowTop + 0.35 * P.side.size, half - P.side.fromFront - sw.widthMm / 2); tube.add(side);

  if (!st.lid) return g;
  // Lid: boards over the gable and the fin, die-cut at the mouth.
  const lid = new THREE.Group(); lid.position.y = st.lidLift; g.add(lid);
  const ex = (shape, segs = 64) => new THREE.ExtrudeGeometry(shape, { depth: bd, bevelEnabled: false, curveSegments: segs });
  lid.add(mesh(ex(slopeWithMouth()).applyMatrix4(frontBasis), mats.board));
  lid.add(mesh(ex(slopeRect(), 4).applyMatrix4(backBasis), mats.board));
  lid.add(mesh(ex(endTri(), 4).applyMatrix4(rightBasis), mats.board));
  lid.add(mesh(ex(endTri(), 4).applyMatrix4(leftBasis), mats.board));
  lid.add(mesh(new THREE.BoxGeometry(S.plan + 2 * bd, S.fin.height + bd, S.fin.thick + 2 * bd).translate(0, ridgeZ + (S.fin.height + bd) / 2, 0), mats.board));
  return g;
}

// The pint crate: a plain open box holding 2 x 3 pints. Units mm, origin at the crate's floor centre.
export function buildCrate(THREE, addons, ctx, { flavors }) {
  const C = { w: 340, d: 250, h: 130, wall: 10 };
  const g = new THREE.Group();
  const wood = new THREE.MeshStandardMaterial({ map: ctx.tex.birch(), color: 0xcdb58e, roughness: 0.8, side: THREE.DoubleSide });
  const mesh = (geom) => { const m = new THREE.Mesh(geom, wood); m.castShadow = m.receiveShadow = true; return m; };
  g.add(mesh(new THREE.BoxGeometry(C.w, C.wall, C.d).translate(0, C.wall / 2, 0)));
  for (const sz of [-1, 1]) g.add(mesh(new THREE.BoxGeometry(C.w, C.h, C.wall).translate(0, C.h / 2, sz * (C.d / 2 - C.wall / 2))));
  for (const sx of [-1, 1]) g.add(mesh(new THREE.BoxGeometry(C.wall, C.h, C.d - 2 * C.wall).translate(sx * (C.w / 2 - C.wall / 2), C.h / 2, 0)));
  const cols = 3, rows = 2, pitchX = 110, pitchZ = 110;
  flavors.forEach((fl, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const p = buildSpeaker(THREE, addons, ctx, { kind: 'pint', flavor: ctx.flavor(fl) });
    p.position.set((col - 1) * pitchX, C.wall, (row - 0.5) * pitchZ);
    g.add(p);
  });
  return g;
}
