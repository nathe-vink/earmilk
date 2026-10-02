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

// A board slab of thickness t with rounded edges, spanning z 0..t in its own frame.
function slab(THREE, shape, t, segs = 64) {
  const bev = Math.min(0.5, t * 0.33);
  const g = new THREE.ExtrudeGeometry(shape, { depth: Math.max(t - 2 * bev, 0.05), bevelEnabled: true, bevelThickness: bev, bevelSize: bev, bevelOffset: 0, bevelSegments: 2, curveSegments: segs });
  g.translate(0, 0, bev);
  return g;
}

export function makeMaterials(THREE, tex, flavor) {
  const M = THREE;
  // Coated carton board: matte body with a soft poly sheen that lets the faces pick up the room.
  const board = new M.MeshPhysicalMaterial({ color: flavor.board, roughness: 0.55, metalness: 0, clearcoat: 0.3, clearcoatRoughness: 0.4, sheen: 0.15, sheenRoughness: 0.9, sheenColor: new M.Color(0xffffff), side: M.DoubleSide });
  const birch = new M.MeshStandardMaterial({ map: tex.birch(), roughness: 0.6, metalness: 0, side: M.DoubleSide });
  const bowl = new M.MeshPhysicalMaterial({ map: tex.gradient(flavor.throat.mouth, flavor.throat.throat), roughness: 0.4, metalness: 0, clearcoat: 0.3, clearcoatRoughness: 0.45, side: M.DoubleSide });
  const decal = (t) => new M.MeshPhysicalMaterial({ map: t, transparent: true, roughness: 0.7, metalness: 0, clearcoat: 0.15, clearcoatRoughness: 0.5, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, depthWrite: false });
  const boardPrint = new M.MeshPhysicalMaterial({ color: flavor.print, roughness: 0.55, metalness: 0, clearcoat: 0.3, clearcoatRoughness: 0.4, sheen: 0.15, sheenRoughness: 0.9, sheenColor: new M.Color(0xffffff), side: M.DoubleSide });
  const printArea = new M.MeshPhysicalMaterial({ color: flavor.print, roughness: 0.58, metalness: 0, clearcoat: 0.25, clearcoatRoughness: 0.45, side: M.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
  const standPaint = new M.MeshPhysicalMaterial({ color: flavor.print, roughness: 0.5, metalness: 0, clearcoat: 0.2, clearcoatRoughness: 0.5 });
  // 2026-10-02, no sleeve: a satin lacquer on the birch, in the body colour and the accent colour; a dark shadow line; a cast metal badge.
  const finishBody = new M.MeshPhysicalMaterial({ color: flavor.board, roughness: 0.38, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.2, side: M.DoubleSide });
  const finishAccent = new M.MeshPhysicalMaterial({ color: flavor.print, roughness: 0.38, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.2, side: M.DoubleSide });
  const finishAccentArea = new M.MeshPhysicalMaterial({ color: flavor.print, roughness: 0.38, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.2, side: M.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
  const shadowLine = new M.MeshStandardMaterial({ color: 0x141210, roughness: 0.95, metalness: 0, side: M.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
  const badgePlate = new M.MeshStandardMaterial({ color: 0xd8d5ce, roughness: 0.28, metalness: 1.0, envMapIntensity: 2.4 });
  const badgeField = new M.MeshStandardMaterial({ color: 0x1d1c1b, roughness: 0.55, metalness: 0.6, envMapIntensity: 1.2 });
  const badgeLetters = (t) => new M.MeshStandardMaterial({ color: 0xffffff, roughness: 0.12, metalness: 1.0, envMapIntensity: 3.2, alphaMap: t, transparent: true, alphaTest: 0.4, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  const badgeShade = (t) => new M.MeshBasicMaterial({ color: 0x000000, alphaMap: t, transparent: true, opacity: 0.7, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  const mark = (t) => new M.MeshPhysicalMaterial({ map: t, transparent: true, roughness: 0.5, metalness: 0, clearcoat: 0.4, clearcoatRoughness: 0.25, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, depthWrite: false });
  return {
    board, birch, bowl, decal, boardPrint, printArea, standPaint,
    finishBody, finishAccent, finishAccentArea, shadowLine, badgePlate, badgeField, badgeLetters, badgeShade, mark,
    cone: new M.MeshStandardMaterial({ color: 0x202020, roughness: 0.55 }),
    frame: new M.MeshStandardMaterial({ color: 0x1e1e1e, roughness: 0.4, metalness: 0.55 }),
    surround: new M.MeshPhysicalMaterial({ color: 0x141414, roughness: 0.3, clearcoat: 0.5, clearcoatRoughness: 0.3 }),
    dustcap: new M.MeshStandardMaterial({ color: 0x141414, roughness: 0.35 }),
    screw: new M.MeshStandardMaterial({ color: 0x4a4a4a, roughness: 0.35, metalness: 0.8 }),
    faceplate: new M.MeshStandardMaterial({ color: 0x2b2b2b, roughness: 0.28, metalness: 0.85 }),
    dome: new M.MeshStandardMaterial({ color: 0x0f0f0f, roughness: 0.42 }),
    dark: new M.MeshStandardMaterial({ color: 0x060606, roughness: 1, side: M.DoubleSide }),
    throatSeal: new M.MeshPhysicalMaterial({ color: flavor.throat.throat, roughness: 0.45, clearcoat: 0.3, clearcoatRoughness: 0.45, side: M.DoubleSide }),
    portFlange: new M.MeshStandardMaterial({ color: 0x2c2c2c, roughness: 0.4, metalness: 0.6 }),
    plate: new M.MeshStandardMaterial({ color: 0x1b1b1b, roughness: 0.45, metalness: 0.5 }),
    postRed: new M.MeshPhysicalMaterial({ color: 0xc62828, roughness: 0.35, clearcoat: 0.4, clearcoatRoughness: 0.3 }),
    postBlack: new M.MeshPhysicalMaterial({ color: 0x2e2e2e, roughness: 0.35, metalness: 0.3, clearcoat: 0.4, clearcoatRoughness: 0.3 }),
    shadow: new M.MeshBasicMaterial({ color: 0x000000, alphaMap: tex.radialShadow(), transparent: true, depthWrite: false, opacity: 0.5 }),
    crease: new M.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.16, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 }),
  };
}

// A soft contact shadow on the floor under a footprint w x d (mm), centred at the origin of the parent.
export function contactShadow(THREE, mats, w, d, opacity = 0.5, y = 0.6) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w * 1.3, d * 1.3), mats.shadow.clone());
  m.material.opacity = opacity;
  m.rotation.x = -Math.PI / 2; m.position.y = y; m.renderOrder = 1;
  return m;
}

// A fold or crimp line: a faint dark strip lying on a surface. In its own frame it lies in XY along X, facing +Z.
function crease(THREE, mats, len, thick) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(len, thick), mats.crease); m.renderOrder = 2; return m;
}

// state: { sleeve, lid, cabinet, lidLift, tubeLift, lidOffset [x,y,z], lidRotY, tubeOffset [x,y,z], tubeRotY } in mm and radians.
export function buildSpeaker(THREE, addons, ctx, { kind = 'fs', flavor, state = {} }) {
  const S = specFor(kind);
  const kk = S.plan / 390;
  const st = { sleeve: true, lid: true, cabinet: true, lidLift: 0, tubeLift: 0, lidOffset: [0, 0, 0], lidRotY: 0, tubeOffset: [0, 0, 0], tubeRotY: 0, ...state };
  // look: { lid: 'board'|'print', band: null|'print'|'stand', wordmark: 'gable'|'band', panel: null|{...}, knob: false, style }.
  // style is the first exploration's shorthand: 'cap' = lid print, 'band' = printed band, 'rings', 'side'.
  // mode: 'finish' (2026-10-02 on: no sleeve, the colour a finish on the birch, plinth, badge) or 'sleeve' (the printed sleeve, kept for the dated explorations).
  const look = { mode: 'finish', style: 'wordmark', lid: flavor.lid || 'board', band: 'print', wordmark: 'band', panel: null, knob: false, ...(state.look || {}) };
  if (look.style === 'cap') look.lid = 'print';
  if (look.style === 'band' && !look.band) look.band = 'print';
  const standH = look.band === 'stand' ? 110 * kk : 0;
  const rise = standH ? standH + 6 * kk : 0;
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
  if (st.cabinet) g.add(contactShadow(THREE, mats, S.plan, S.plan, 0.55));
  const body = new THREE.Group(); body.position.y = rise; g.add(body);
  // Optional stand: a painted block in the print colour under the carton, with a dark reveal between them.
  if (standH) {
    const stand = mesh(new addons.RoundedBoxGeometry(S.plan, standH, S.plan, 2, 2 * kk).translate(0, standH / 2, 0), mats.standPaint); g.add(stand);
    const reveal = mesh(new THREE.BoxGeometry(S.plan - 24 * kk, 6 * kk, S.plan - 24 * kk).translate(0, standH + 3 * kk, 0), mats.dark); g.add(reveal);
    if (look.wordmark === 'band') {
      const bw = ctx.tex.wordmark({ sizeMm: 52 * kk, color: flavor.board, trackingEm: S.print.trackingEm });
      const f = mesh(new THREE.PlaneGeometry(bw.widthMm, bw.heightMm), mats.decal(bw.texture), false); f.position.set(0, standH / 2 + 0.35 * 52 * kk - 0.65 * 52 * kk + bw.heightMm / 2, half + 0.3); g.add(f);
      const sd = mesh(new THREE.PlaneGeometry(bw.widthMm, bw.heightMm), mats.decal(bw.texture), false); sd.rotation.y = Math.PI / 2; sd.position.set(half + 0.3, f.position.y, 0); g.add(sd);
    }
    if (look.knob) {
      const kr = 14 * kk;
      const knob = mesh(new THREE.CylinderGeometry(kr, kr, 10 * kk, 48), mats.frame); knob.rotation.x = Math.PI / 2; knob.position.set(140 * kk, standH / 2, half + 5 * kk); g.add(knob);
      const tick = mesh(new THREE.BoxGeometry(1.6 * kk, kr * 0.6, 0.6 * kk), mats.board); tick.position.set(140 * kk, standH / 2 + kr * 0.6, half + 10.4 * kk); g.add(tick);
    }
  }

  if (st.cabinet) {
    // Cabinet: a real box of birch panels (baffle with driver cut-outs, back with the port hole, sides, top, bottom), the carved block, the fin.
    const cab = new THREE.Group(); body.add(cab);
    const wall = S.wall;
    const baffle = rectShape(THREE, -half, 0, half, S.body);
    for (const dr of S.drivers) baffle.holes.push(circleHole(THREE, 0, dr.z, dr.frame / 2 * 0.86));
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
    const bowlMesh = mesh(bowlGeom, mats.bowl);
    if (st.bowlShadow === false) bowlMesh.receiveShadow = false; // close-up: the lip's hard shadow-map edge read as a kink, so the bowl shades by its normals alone
    cab.add(bowlMesh);
    const seal = mesh(new THREE.CircleGeometry(throatR + 1, 64), S.tweeter ? mats.dark : mats.throatSeal); seal.position.set(0, axisY, throatZ - 0.6); cab.add(seal);

    // Tweeter at the throat (floorstander only): faceplate, dome with its apex 8 mm forward, a soft ring.
    if (S.tweeter) {
      const tw = S.tweeter, pr = tw.faceplate / 2;
      const plate = mesh(new THREE.CylinderGeometry(pr, pr, tw.faceplateThick, 64), mats.faceplate);
      plate.rotation.x = Math.PI / 2; plate.position.set(0, axisY, throatZ - tw.faceplateThick / 2); cab.add(plate);
      const baseR = 12.7, h = tw.apexForward, sr = (baseR * baseR + h * h) / (2 * h);
      const dome = mesh(new THREE.SphereGeometry(sr, 48, 24, 0, Math.PI * 2, 0, Math.acos((sr - h) / sr)), mats.dome);
      dome.rotation.x = Math.PI / 2; dome.position.set(0, axisY, throatZ + h - sr); cab.add(dome);
      const ring = mesh(new THREE.TorusGeometry(baseR + 1.5, 1.5, 12, 64), mats.dome); ring.position.set(0, axisY, throatZ + 0.6); cab.add(ring);
    }

    // Drivers: basket flange standing proud of the board with screws, a rolled surround, a shaded paper cone, a dust cap.
    for (const dr of S.drivers) {
      const R = dr.frame / 2;
      const grp = new THREE.Group(); grp.position.set(0, dr.z, half + S.board); cab.add(grp);
      const lip = Math.max(2.5, R * 0.025);
      const flange = mesh(new THREE.CylinderGeometry(R, R, lip, 64, 1, true), mats.frame); flange.rotation.x = Math.PI / 2; flange.position.z = lip / 2; grp.add(flange);
      const top = mesh(new THREE.RingGeometry(R * 0.88, R, 64), mats.frame); top.position.z = lip; grp.add(top);
      const inner = mesh(new THREE.CylinderGeometry(R * 0.88, R * 0.88, lip + 1, 64, 1, true), mats.frame); inner.rotation.x = Math.PI / 2; inner.position.z = lip / 2 - 0.5; grp.add(inner);
      const n = R > 60 ? 8 : 6;
      for (let i = 0; i < n; i++) {
        const a = (i + 0.5) * Math.PI * 2 / n, sr = Math.max(1.6, R * 0.02);
        const screw = mesh(new THREE.CylinderGeometry(sr, sr, 1.2, 16), mats.screw); screw.rotation.x = Math.PI / 2;
        screw.position.set(Math.cos(a) * R * 0.94, Math.sin(a) * R * 0.94, lip + 0.6); grp.add(screw);
      }
      const sur = mesh(new THREE.TorusGeometry(R * 0.83, R * 0.055, 16, 64), mats.surround); sur.position.z = lip - 0.5; grp.add(sur);
      const pts = []; for (let i = 0; i <= 10; i++) { const f = i / 10; pts.push(new THREE.Vector2(R * 0.78 - (R * 0.78 - R * 0.18) * f, lip - 1 - R * 0.36 * Math.pow(f, 0.85))); }
      pts.push(new THREE.Vector2(0.001, lip - 1 - R * 0.36));
      const cone = mesh(new THREE.LatheGeometry(pts, 64), mats.cone); cone.rotation.x = Math.PI / 2; grp.add(cone);
      const cap = mesh(new THREE.SphereGeometry(R * 0.2, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), mats.dustcap);
      cap.rotation.x = Math.PI / 2; cap.scale.z = 0.6; cap.position.z = lip - 1 - R * 0.33; grp.add(cap);
    }

    // Back of the cabinet: engraved label, port, binding posts (floorstander only).
    if (S.back) {
      const B = S.back;
      const lab = ctx.tex.engravedLabel();
      const labelMesh = mesh(new THREE.PlaneGeometry(lab.widthMm, lab.heightMm), mats.decal(lab.texture), false);
      labelMesh.rotation.y = Math.PI; labelMesh.position.set(0, B.label.top - lab.heightMm / 2, -half - 0.3); cab.add(labelMesh);
      const flange = mesh(new THREE.CylinderGeometry(B.port.flange / 2, B.port.flange / 2, 3, 64), mats.portFlange); flange.rotation.x = Math.PI / 2; flange.position.set(0, B.port.z, -half - 1.5); cab.add(flange);
      const bore = mesh(new THREE.CylinderGeometry(B.port.bore / 2, B.port.bore / 2, 100, 64, 1, true), mats.dark); bore.rotation.x = Math.PI / 2; bore.position.set(0, B.port.z, -half + 45); cab.add(bore);
      const boreEnd = mesh(new THREE.CircleGeometry(B.port.bore / 2, 64), mats.dark); boreEnd.rotation.y = Math.PI; boreEnd.position.set(0, B.port.z, -half + 90); cab.add(boreEnd);
      const plate = mesh(new addons.RoundedBoxGeometry(B.posts.w, B.posts.h, 5, 2, 1.5), mats.plate); plate.position.set(0, B.posts.z, -half - 2.5 - 0.3); cab.add(plate);
      for (const [x, mat] of [[B.posts.spacing / 2, mats.postRed], [-B.posts.spacing / 2, mats.postBlack]]) {
        const post = mesh(new THREE.CylinderGeometry(B.posts.postD / 2, B.posts.postD / 2 * 0.85, 16, 48), mat); post.rotation.x = Math.PI / 2; post.position.set(x, B.posts.z, -half - 5.3 - 8); cab.add(post);
        const collar = mesh(new THREE.CylinderGeometry(B.posts.postD / 2 * 0.55, B.posts.postD / 2 * 0.55, 4, 32), mats.screw); collar.rotation.x = Math.PI / 2; collar.position.set(x, B.posts.z, -half - 5.3 - 16 - 2); cab.add(collar);
        const hole = mesh(new THREE.CircleGeometry(4.5, 32), mats.dark); hole.rotation.y = Math.PI; hole.position.set(x, B.posts.z, -half - 5.3 - 20.2); cab.add(hole);
      }
    }
  }

  if (!st.sleeve) return g;
  const P = S.print, bd = S.board, ct = 1.2 * kk, cn = bd + 0.3;

  if (look.mode === 'finish') {
    // No sleeve. The same outer skin, as a satin finish on the birch: the body colour, the gable and fin in the accent colour where
    // the flavour says so, a built-in plinth in the accent colour with a shadow line above it, a cast metal badge on the plinth's
    // front, and the wordmark engraved on the bare birch panel at the back. Nothing on the sides, nothing under the gable.
    const skin = new THREE.Group(); body.add(skin);
    const frontShape = rectShape(THREE, -half, 0, half, S.body);
    for (const dr of S.drivers) frontShape.holes.push(circleHole(THREE, 0, dr.z, dr.frame / 2));
    skin.add(mesh(slab(THREE, frontShape, bd).translate(0, 0, half), mats.finishBody));
    const backShape = rectShape(THREE, -half, 0, half, S.body);
    if (S.back) { const w = S.back.window; const hole = new THREE.Path(); hole.moveTo(w.x0 - half, w.z0); hole.lineTo(w.x0 - half, w.z1); hole.lineTo(w.x1 - half, w.z1); hole.lineTo(w.x1 - half, w.z0); hole.closePath(); backShape.holes.push(hole); }
    skin.add(mesh(slab(THREE, backShape, bd, 4).translate(0, 0, -half - bd), mats.finishBody));
    for (const sx of [-1, 1]) skin.add(mesh(new addons.RoundedBoxGeometry(bd, S.body, S.plan, 2, Math.min(0.5, bd * 0.33)).translate(sx * (half + bd / 2), S.body / 2, 0), mats.finishBody));

    // Plinth: the bottom 110 on all four sides in the accent colour, flush, with a 3 mm shadow line where it meets the body.
    const ph = FS.plinth.height * kk, sl = FS.plinth.shadowLine * kk, off = half + bd + 0.3;
    const face = (w, h, mat) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); m.receiveShadow = true; m.renderOrder = 1; return m; };
    for (const [x, z, ry] of [[0, off, 0], [0, -off, Math.PI], [off, 0, Math.PI / 2], [-off, 0, -Math.PI / 2]]) {
      const p = face(S.plan + 2 * bd, ph, mats.finishAccentArea); p.rotation.y = ry; p.position.set(x, ph / 2, z); skin.add(p);
      const l = face(S.plan + 2 * bd, sl, mats.shadowLine); l.rotation.y = ry; l.position.set(x, ph + sl / 2, z); skin.add(l);
    }

    // Badge: a cast metal plate centred on the plinth's front, the wordmark in relief (polished letters over a satin field).
    const Bz = FS.badge, bw = Bz.w * kk, bh = Bz.h * kk, bt = Bz.t * kk;
    const badge = new THREE.Group(); badge.position.set(0, Bz.z * kk, off); skin.add(badge);
    const plate = mesh(new addons.RoundedBoxGeometry(bw, bh, bt, 3, Bz.r * kk), mats.badgePlate); plate.position.z = bt / 2; badge.add(plate);
    // A dark field inset in the chrome rim, the way the cast badge on an espresso machine reads: bright letters on a dark ground.
    const fieldT = 0.6 * kk, rim = 4 * kk;
    const field = mesh(new addons.RoundedBoxGeometry(bw - 2 * rim, bh - 2 * rim, fieldT, 2, Math.max(0.5, (Bz.r - 2) * kk)), mats.badgeField); field.position.z = bt + fieldT / 2; badge.add(field);
    const wm = ctx.tex.wordmark({ sizeMm: Bz.type * kk, color: '#FFFFFF', trackingEm: P.trackingEm });
    const shade = new THREE.Mesh(new THREE.PlaneGeometry(wm.widthMm, wm.heightMm), mats.badgeShade(wm.texture)); shade.position.set(-0.9 * kk, -1.3 * kk, bt + fieldT + 0.05); shade.renderOrder = 2; badge.add(shade);
    const letters = new THREE.Mesh(new THREE.PlaneGeometry(wm.widthMm, wm.heightMm), mats.badgeLetters(wm.texture)); letters.position.z = bt + fieldT + Bz.relief * kk; letters.renderOrder = 3; letters.castShadow = true; badge.add(letters);

    // Back: the wordmark engraved in the birch panel above the Nutrition Facts (floorstander only).
    if (S.back && FS.backWordmark) {
      const ew = ctx.tex.wordmark({ sizeMm: FS.backWordmark.size * kk, color: '#6B5232', trackingEm: P.trackingEm });
      const e = mesh(new THREE.PlaneGeometry(ew.widthMm, ew.heightMm), mats.decal(ew.texture), false);
      e.rotation.y = Math.PI; e.position.set(0, FS.backWordmark.baseline * kk + 0.35 * FS.backWordmark.size * kk, -half - 0.3); skin.add(e);
    }

    // Gable and fin: the same shells as the lid, in the accent or the body colour, with no creases or crimp lines.
    const gableMat = look.lid === 'print' ? mats.finishAccent : mats.finishBody;
    // Exploration marks (explore/2026-10-02): common milk-carton print, none of it about the owner. Not spec.
    const inkOnGable = look.lid === 'print' ? flavor.board : flavor.print;
    const decalMesh = (t, w, h) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mats.mark(t)); m.renderOrder = 3; return m; };
    for (const id of look.marks || []) {
      if (id === 'open-other-side') {
        // On the back slope, the way the spout instruction sits on a carton: caps with an arrow, in the gable's other colour.
        const t = ctx.tex.label({ text: 'OPEN OTHER SIDE', sizeMm: 27 * kk, color: inkOnGable, weight: 700, arrow: true });
        const m = decalMesh(t.texture, t.widthMm, t.heightMm); m.geometry.translate(0, L / 2, bd + 0.35); m.geometry.applyMatrix4(backBasis); skin.add(m);
      }
      if (id === 'best-before') {
        // An inkjet date stamp on the fin's front, dot matrix.
        const t = ctx.tex.dotText({ text: 'BEST BEFORE  NEVER', sizeMm: 18 * kk, color: '#1a1a1a' });
        const m = decalMesh(t.texture, t.widthMm, t.heightMm); m.position.set(0, ridgeZ + S.fin.height / 2, S.fin.thick / 2 + bd + 0.35); skin.add(m);
      }
      if (id === 'grade-a') {
        // A stamped roundel on the right side, upper third, in the accent colour.
        const t = ctx.tex.roundel({ top: 'GRADE A', bottom: 'PASTEURIZED · HOMOGENIZED', diameterMm: 130 * kk, color: flavor.print });
        const m = decalMesh(t.texture, t.widthMm, t.heightMm); m.rotation.y = Math.PI / 2; m.position.set(half + bd + 0.35, 680 * kk, 0); skin.add(m);
      }
      if (id === 'shake-well') {
        const t = ctx.tex.label({ text: 'SHAKE WELL', sizeMm: 30 * kk, color: flavor.print, weight: 700 });
        const m = decalMesh(t.texture, t.widthMm, t.heightMm); m.rotation.y = Math.PI / 2; m.position.set(half + bd + 0.35, 790 * kk, 0); skin.add(m);
      }
      if (id === 'volume') {
        // The carton's own line, under the badge: the gross internal volume from spec/check-spec.
        const t = ctx.tex.label({ text: '103 L (27 GAL)', sizeMm: 12 * kk, color: flavor.board, weight: 700 });
        const m = decalMesh(t.texture, t.widthMm, t.heightMm); m.position.set(0, 14 * kk, off + 0.1); skin.add(m);
      }
    }
    skin.add(mesh(slab(THREE, slopeWithMouth(), bd).applyMatrix4(frontBasis), gableMat));
    skin.add(mesh(slab(THREE, slopeRect(), bd, 4).applyMatrix4(backBasis), gableMat));
    skin.add(mesh(slab(THREE, endTri(), bd, 4).applyMatrix4(rightBasis), gableMat));
    skin.add(mesh(slab(THREE, endTri(), bd, 4).applyMatrix4(leftBasis), gableMat));
    const coverH = S.fin.height + bd + 2;
    skin.add(mesh(new addons.RoundedBoxGeometry(S.plan + 2 * bd, coverH, S.fin.thick + 2 * bd, 2, Math.min(1.0, bd * 0.66)).translate(0, ridgeZ - 2 + coverH / 2, 0), gableMat));
    return g;
  }

  // Tube: four boards around the body; the front is die-cut for the drivers, the back is a frame around the window.
  const tube = new THREE.Group();
  tube.position.set(st.tubeOffset[0], st.tubeOffset[1] + st.tubeLift, st.tubeOffset[2]); tube.rotation.y = st.tubeRotY; body.add(tube);
  const frontShape = rectShape(THREE, -half, 0, half, S.body);
  for (const dr of S.drivers) frontShape.holes.push(circleHole(THREE, 0, dr.z, dr.frame / 2));
  tube.add(mesh(slab(THREE, frontShape, bd).translate(0, 0, half), mats.board));
  const backShape = rectShape(THREE, -half, 0, half, S.body);
  if (S.back) { const w = S.back.window; const hole = new THREE.Path(); hole.moveTo(w.x0 - half, w.z0); hole.lineTo(w.x0 - half, w.z1); hole.lineTo(w.x1 - half, w.z1); hole.lineTo(w.x1 - half, w.z0); hole.closePath(); backShape.holes.push(hole); }
  tube.add(mesh(slab(THREE, backShape, bd, 4).translate(0, 0, -half - bd), mats.board));
  for (const sx of [-1, 1]) tube.add(mesh(new addons.RoundedBoxGeometry(bd, S.body, S.plan, 2, Math.min(0.5, bd * 0.33)).translate(sx * (half + bd / 2), S.body / 2, 0), mats.board));
  // Corner folds of the tube: faint lines just inside each vertical edge.
  for (const sx of [-1, 1]) {
    for (const sz of [-1, 1]) { const c = crease(THREE, mats, ct, S.body); c.material = mats.crease.clone(); c.material.opacity = 0.09; c.position.set(sx * (half - ct), S.body / 2, sz * (half + cn)); if (sz < 0) c.rotation.y = Math.PI; tube.add(c); }
    for (const sz of [-1, 1]) { const c = crease(THREE, mats, ct, S.body); c.material = mats.crease.clone(); c.material.opacity = 0.09; c.rotation.y = sx * Math.PI / 2; c.position.set(sx * (half + cn), S.body / 2, sz * (half - ct)); tube.add(c); }
  }
  if (st.tubeOffset[1] === 0 && (st.tubeOffset[0] !== 0 || st.tubeOffset[2] !== 0)) tube.add(contactShadow(THREE, mats, S.plan, S.plan, 0.5));

  // Exploration looks: flavour colour as a base band, rings around the drivers, or whole side panels.
  const area = (w, h) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mats.printArea); m.receiveShadow = true; m.renderOrder = 1; return m; };
  if (look.band === 'print') {
    const bh = 110 * kk;
    const f = area(S.plan, bh); f.position.set(0, bh / 2, half + bd + 0.25); tube.add(f);
    const bb = area(S.plan, Math.min(bh, S.back ? S.back.window.z0 : bh)); bb.rotation.y = Math.PI; bb.position.set(0, bb.geometry.parameters.height / 2, -half - bd - 0.25); tube.add(bb);
    for (const sx of [-1, 1]) { const m = area(S.plan, bh); m.rotation.y = sx * Math.PI / 2; m.position.set(sx * (half + bd + 0.25), bh / 2, 0); tube.add(m); }
  }
  if (look.style === 'rings') {
    for (const dr of S.drivers) { const R = dr.frame / 2; const m = new THREE.Mesh(new THREE.RingGeometry(R + 3 * kk, R + 30 * kk, 96), mats.printArea); m.position.set(0, dr.z, half + bd + 0.25); m.renderOrder = 1; tube.add(m); }
  }
  if (look.style === 'side') {
    for (const sx of [-1, 1]) { const m = area(S.plan, S.body); m.rotation.y = sx * Math.PI / 2; m.position.set(sx * (half + bd + 0.25), S.body / 2, 0); tube.add(m); }
  }
  const sideInk = look.style === 'side' ? flavor.board : flavor.print;

  if (look.wordmark === 'band' && look.band === 'print') {
    // The wordmark sits in the printed band, reversed in the board colour, centred on the front and on the right side.
    const bw = ctx.tex.wordmark({ sizeMm: 52 * kk, color: flavor.board, trackingEm: P.trackingEm });
    const cy = 55 * kk - 0.65 * 52 * kk + bw.heightMm / 2;
    const f = mesh(new THREE.PlaneGeometry(bw.widthMm, bw.heightMm), mats.decal(bw.texture), false); f.position.set(0, cy, half + bd + 0.35); tube.add(f);
    const sd = mesh(new THREE.PlaneGeometry(bw.widthMm, bw.heightMm), mats.decal(bw.texture), false); sd.rotation.y = Math.PI / 2; sd.position.set(half + bd + 0.35, cy, 0); tube.add(sd);
  } else if (look.wordmark === 'gable' || look.band !== 'stand') {
    // Print as specified: the wordmark on the front, above the mid, and larger on the right side reading front to back.
    const fw = ctx.tex.wordmark({ sizeMm: P.front.size, color: flavor.print, trackingEm: P.trackingEm });
    const front = mesh(new THREE.PlaneGeometry(fw.widthMm, fw.heightMm), mats.decal(fw.texture), false);
    front.position.set(0, S.body - P.front.baselineBelowTop + 0.35 * P.front.size, half + bd + 0.3); tube.add(front);
    const sw = ctx.tex.wordmark({ sizeMm: P.side.size, color: sideInk, trackingEm: P.trackingEm });
    const side = mesh(new THREE.PlaneGeometry(sw.widthMm, sw.heightMm), mats.decal(sw.texture), false);
    side.rotation.y = Math.PI / 2;
    side.position.set(half + bd + 0.3, S.body - P.side.baselineBelowTop + 0.35 * P.side.size, half - P.side.fromFront - sw.widthMm / 2); tube.add(side);
  }
  // The owner's panel on the right side, below the wordmark.
  if (look.panel) {
    const hp = ctx.tex.heardPanel({ ...look.panel, ink: sideInk, W: 300 * kk, H: 330 * kk });
    const pm = mesh(new THREE.PlaneGeometry(hp.widthMm, hp.heightMm), mats.decal(hp.texture), false);
    pm.rotation.y = Math.PI / 2; pm.position.set(half + bd + 0.35, 460 * kk, 0); tube.add(pm);
  }

  if (!st.lid) return g;
  // Lid: boards over the gable and the fin, die-cut at the mouth, with fold lines at the ridge and the bottom edge and crimp lines on the fin.
  const lid = new THREE.Group();
  lid.position.set(st.lidOffset[0], st.lidOffset[1] + st.lidLift, st.lidOffset[2]); lid.rotation.y = st.lidRotY; body.add(lid);
  const lidMat = look.lid === 'print' ? mats.boardPrint : mats.board;
  lid.add(mesh(slab(THREE, slopeWithMouth(), bd).applyMatrix4(frontBasis), lidMat));
  lid.add(mesh(slab(THREE, slopeRect(), bd, 4).applyMatrix4(backBasis), lidMat));
  lid.add(mesh(slab(THREE, endTri(), bd, 4).applyMatrix4(rightBasis), lidMat));
  lid.add(mesh(slab(THREE, endTri(), bd, 4).applyMatrix4(leftBasis), lidMat));
  const coverH = S.fin.height + bd + 2;
  lid.add(mesh(new addons.RoundedBoxGeometry(S.plan + 2 * bd, coverH, S.fin.thick + 2 * bd, 2, Math.min(1.0, bd * 0.66)).translate(0, ridgeZ - 2 + coverH / 2, 0), lidMat));
  for (const basis of [frontBasis, backBasis]) {
    for (const v of [ct, L - ct]) { const c = crease(THREE, mats, S.plan, ct); c.position.set(0, v, cn); c.applyMatrix4(basis); lid.add(c); }
  }
  for (const sz of [-1, 1]) for (const k of [0.25, 0.5, 0.75]) {
    const c = crease(THREE, mats, S.plan + 2 * bd, ct * 0.8); c.position.set(0, ridgeZ + S.fin.height * k, sz * (S.fin.thick / 2 + bd + 0.3)); if (sz < 0) c.rotation.y = Math.PI; lid.add(c);
  }
  if (st.lidOffset[1] !== 0) { const sh = contactShadow(THREE, mats, S.plan, S.plan, 0.45); sh.position.y = S.body + 0.6; lid.add(sh); }
  return g;
}

// The pint crate: a plain open box of boards holding 2 x 3 pints. Units mm, origin at the crate's floor centre.
export function buildCrate(THREE, addons, ctx, { flavors }) {
  const C = { w: 340, d: 250, h: 130, wall: 10 };
  const g = new THREE.Group();
  const mats = ctx.materials(ctx.flavor('whole'));
  const face = (rot) => { const m = new THREE.MeshStandardMaterial({ map: ctx.tex.birch({ seed: 11 }).clone(), color: 0xcdb58e, roughness: 0.65, side: THREE.DoubleSide }); m.map.center.set(0.5, 0.5); m.map.rotation = rot; m.map.needsUpdate = true; return m; };
  const end = new THREE.MeshStandardMaterial({ map: ctx.tex.endGrain(), color: 0xb89c72, roughness: 0.8 });
  const along = face(Math.PI / 2), up = face(0);
  // BoxGeometry material order: +x, -x, +y, -y, +z, -z. Long boards run along x; the rim (+y) shows end grain.
  const longBoard = [end, end, end, along, along, along];
  const shortBoard = [up, up, end, up, end, end];
  const mesh = (geom, mat) => { const m = new THREE.Mesh(geom, mat); m.castShadow = m.receiveShadow = true; return m; };
  g.add(contactShadow(THREE, mats, C.w, C.d, 0.5));
  g.add(mesh(new THREE.BoxGeometry(C.w, C.wall, C.d).translate(0, C.wall / 2, 0), [along, along, along, along, end, end]));
  for (const sz of [-1, 1]) g.add(mesh(new THREE.BoxGeometry(C.w, C.h, C.wall).translate(0, C.h / 2, sz * (C.d / 2 - C.wall / 2)), longBoard));
  for (const sx of [-1, 1]) g.add(mesh(new THREE.BoxGeometry(C.wall, C.h, C.d - 2 * C.wall).translate(sx * (C.w / 2 - C.wall / 2), C.h / 2, 0), shortBoard));
  const cols = 3, pitchX = 110, pitchZ = 110;
  flavors.forEach((fl, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const p = buildSpeaker(THREE, addons, ctx, { kind: 'pint', flavor: ctx.flavor(fl) });
    p.position.set((col - 1) * pitchX, C.wall, (row - 0.5) * pitchZ);
    g.add(p);
  });
  return g;
}
