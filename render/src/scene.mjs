// Rooms, lights and cameras for the shot list. Scene units: metres. Speakers are built in mm and scaled by 0.001.
import { buildSpeaker, buildCrate } from './model.mjs';

function sun(THREE, scene, { color = 0xffdcb4, intensity = 3, position, target = [0, 0.4, 0], bounds = 4, mapSize = 4096 }) {
  const l = new THREE.DirectionalLight(color, intensity);
  l.position.set(...position); l.target.position.set(...target);
  l.castShadow = true;
  l.shadow.mapSize.set(mapSize, mapSize);
  Object.assign(l.shadow.camera, { left: -bounds, right: bounds, top: bounds, bottom: -bounds, near: 0.2, far: 30 });
  l.shadow.bias = -0.0003; l.shadow.normalBias = 0.012;
  scene.add(l); scene.add(l.target);
  return l;
}

function fillRect(THREE, scene, { color = 0xffffff, intensity = 5, w = 1.4, h = 1.5, position, lookAt }) {
  const l = new THREE.RectAreaLight(color, intensity, w, h);
  l.position.set(...position); l.lookAt(...lookAt); scene.add(l); return l;
}

function bounce(THREE, scene, { sky = 0xffffff, ground = 0xb8905f, intensity = 0.35 }) {
  scene.add(new THREE.HemisphereLight(sky, ground, intensity));
}

function floorMesh(THREE, tex, { size = 9, planks, roughness = 0.34 }) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshStandardMaterial({ map: tex.planks(planks), roughness, metalness: 0 }));
  m.material.map = m.material.map.clone(); m.material.map.repeat.set(size / 1.2, size / 1.2); m.material.map.needsUpdate = true;
  m.rotation.x = -Math.PI / 2; m.receiveShadow = true; return m;
}

function wallMesh(THREE, { w, h, color, roughness = 0.95 }) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ color, roughness, metalness: 0 }));
  m.receiveShadow = true; return m;
}

function skirting(THREE, scene, { w, z, color = 0xf2efe8, h = 0.12 }) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.018), new THREE.MeshStandardMaterial({ color, roughness: 0.6 }));
  m.position.set(0, h / 2, z + 0.009); m.receiveShadow = m.castShadow = true; scene.add(m);
}

// The rest of the box: ceiling, right wall and front wall (behind the camera), so the only daylight is what the window admits
// and the lacquer has a room to reflect. Out of frame in every shot; in the path tracer they are what makes the light one story.
function enclose(THREE, scene, { x0, x1, z0, z1, h, color, roughness = 0.95, window = 'right' }) {
  const mat = new THREE.MeshStandardMaterial({ color, roughness, metalness: 0 });
  const add = (geom, pos, rot) => { const m = new THREE.Mesh(geom, mat); m.position.set(...pos); m.rotation.set(...rot); m.receiveShadow = m.castShadow = true; scene.add(m); };
  add(new THREE.PlaneGeometry(x1 - x0, z1 - z0), [(x0 + x1) / 2, h, (z0 + z1) / 2], [Math.PI / 2, 0, 0]);  // ceiling, facing down
  if (window === 'right') add(new THREE.PlaneGeometry(z1 - z0, h), [x0, h / 2, (z0 + z1) / 2], [0, Math.PI / 2, 0]);   // left wall, facing +x
  else add(new THREE.PlaneGeometry(z1 - z0, h), [x1, h / 2, (z0 + z1) / 2], [0, -Math.PI / 2, 0]);                     // right wall, facing -x
  add(new THREE.PlaneGeometry(x1 - x0, h), [(x0 + x1) / 2, h / 2, z1], [0, Math.PI, 0]);                  // front wall, facing -z
}

// A studio sweep: the floor curves up into a backdrop on the far side of the subject from the camera, so there is no horizon line.
function sweep(THREE, scene, { color, roughness = 0.5, sign = -1, dist = 2.6, radius = 1.5, height = 6, width = 40, segs = 24 }) {
  const prof = [];
  for (let i = 0; i <= segs; i++) { const t = (i / segs) * Math.PI / 2; prof.push([sign * (dist + radius * Math.sin(t)), radius - radius * Math.cos(t)]); }
  prof.push([sign * (dist + radius), height]);
  const pos = [], idx = [];
  prof.forEach(([z, y]) => { pos.push(-width / 2, y, z, width / 2, y, z); });
  for (let i = 0; i < prof.length - 1; i++) { const a = 2 * i, b = a + 1, c = a + 2, d = a + 3; if (sign < 0) idx.push(a, b, c, b, d, c); else idx.push(a, c, b, b, c, d); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color, roughness, metalness: 0, side: THREE.DoubleSide }));
  m.receiveShadow = true; scene.add(m);
}

// A side wall at x = X with a window opening, mullions and a bright sky behind it.
function windowWall(THREE, scene, { x, zRange = [-2.5, 4.5], h = 2.7, color, win = { z0: 0.3, z1: 1.7, sill: 0.8, head: 2.3 }, sky = 0xfff3dc, mullion = 0xf4f1ea }) {
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.95 });
  const add = (w, hh, cz, cy) => { const m = new THREE.Mesh(new THREE.BoxGeometry(0.12, hh, w), mat); m.position.set(x, cy, cz); m.receiveShadow = true; m.castShadow = true; scene.add(m); };
  const [z0, z1] = zRange;
  add(win.z0 - z0, h, (z0 + win.z0) / 2, h / 2);
  add(z1 - win.z1, h, (win.z1 + z1) / 2, h / 2);
  add(win.z1 - win.z0, win.sill, (win.z0 + win.z1) / 2, win.sill / 2);
  add(win.z1 - win.z0, h - win.head, (win.z0 + win.z1) / 2, (win.head + h) / 2);
  if (mullion !== null) {
    const mm = new THREE.MeshStandardMaterial({ color: mullion, roughness: 0.6 });
    const v = new THREE.Mesh(new THREE.BoxGeometry(0.05, win.head - win.sill, 0.04), mm); v.position.set(x, (win.sill + win.head) / 2, (win.z0 + win.z1) / 2); v.castShadow = true; scene.add(v);
    const hz = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.04, win.z1 - win.z0), mm); hz.position.set(x, (win.sill + win.head) / 2, (win.z0 + win.z1) / 2); hz.castShadow = true; scene.add(hz);
  }
  const skyM = new THREE.Mesh(new THREE.PlaneGeometry(6, 5), new THREE.MeshBasicMaterial({ color: sky }));
  skyM.position.set(x + 0.6 * Math.sign(x), 2, (win.z0 + win.z1) / 2); skyM.rotation.y = Math.sign(x) > 0 ? -Math.PI / 2 : Math.PI / 2; scene.add(skyM);
}

// A plain wooden chair, for scale.
function chair(THREE, scene, { position, rotationY = 0, color = 0x8a6a46 }) {
  const wood = new THREE.MeshStandardMaterial({ color, roughness: 0.5 });
  const g = new THREE.Group();
  const add = (w, h, d, x, y, z) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), wood); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); };
  add(0.42, 0.035, 0.42, 0, 0.45, 0);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) add(0.035, 0.45, 0.035, sx * 0.19, 0.225, sz * 0.19);
  for (const sx of [-1, 1]) add(0.035, 0.45, 0.035, sx * 0.19, 0.69, -0.19);
  add(0.42, 0.06, 0.025, 0, 0.86, -0.19);
  add(0.42, 0.04, 0.025, 0, 0.66, -0.19);
  g.position.set(...position); g.rotation.y = rotationY; scene.add(g);
}

const ROOMS = {
  // Living room, late-afternoon sun through a window on the front-right (the camera's side, so it sees the lit faces and the shadows); a chair by the back wall for scale.
  hero(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.18;
    scene.background = new THREE.Color(0xe6e1d6);
    scene.add(floorMesh(THREE, ctx.tex, { size: 10, planks: { base: '#b8905f', dark: '#ab8456', light: '#c2996a' }, roughness: 0.42 }));
    const back = wallMesh(THREE, { w: 10, h: 2.7, color: 0xebe6dc }); back.position.set(0, 1.35, -2.5); scene.add(back);
    skirting(THREE, scene, { w: 10, z: -2.5 });
    windowWall(THREE, scene, { x: 3.5, color: 0xe8e3d9, mullion: null, win: { z0: 1.4, z1: 4.0, sill: 0.8, head: 2.4 } }); // 2.6 m wide: at this sun angle the band across the floor has to be that wide to take in both cabinets (path-traced round 2)
    sun(THREE, scene, { color: 0xffd8ac, intensity: 5.2, position: [7, 2.6, 5.5], target: [-0.3, 0.3, -0.3], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xfff0dc, intensity: 1.3, w: 2.6, h: 1.6, position: [2.95, 1.6, 2.7], lookAt: [0, 1.0, 2.7] });
    bounce(THREE, scene, { sky: 0xe8e4dc, ground: 0xb8905f, intensity: 0.28 });
    enclose(THREE, scene, { x0: -5, x1: 3.5, z0: -2.5, z1: 4.5, h: 2.7, color: 0xebe6dc, window: 'right' });
    chair(THREE, scene, { position: [-3.1, 0, -1.7], rotationY: 0.45 }); // clear of the left cabinet from the hero camera, inside the frame's left edge
    return { exposure: 1.0, skyGlow: 2.0 }; // skyGlow: the path tracer's sky through this window, relative to the sun; a low sun admits little, so the shade needs more
  },
  // Bright apartment: white walls, cool daylight from the front-right, pale floor, a pale chair.
  apartmentBright(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.4;
    scene.background = new THREE.Color(0xf2f0eb);
    scene.add(floorMesh(THREE, ctx.tex, { size: 10, planks: { base: '#d8ccb2', dark: '#cfc2a7', light: '#dfd4bc' }, roughness: 0.32 }));
    const back = wallMesh(THREE, { w: 10, h: 2.7, color: 0xf4f2ee }); back.position.set(0, 1.35, -2.0); scene.add(back);
    skirting(THREE, scene, { w: 10, z: -2.0, color: 0xfaf9f6 });
    windowWall(THREE, scene, { x: 2.6, color: 0xf4f2ee, sky: 0xf6fbff, mullion: null, win: { z0: 1.4, z1: 3.2, sill: 0.7, head: 2.4 } });
    sun(THREE, scene, { color: 0xffffff, intensity: 3.4, position: [7, 4.5, 5.5], target: [-0.2, 0.3, -0.3], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xeef4ff, intensity: 5, w: 1.8, h: 1.7, position: [2.55, 1.55, 2.3], lookAt: [0, 1.0, 2.3] });
    bounce(THREE, scene, { sky: 0xf4f2ee, ground: 0xd8ccb2, intensity: 0.4 });
    enclose(THREE, scene, { x0: -5, x1: 2.6, z0: -2.0, z1: 4.5, h: 2.7, color: 0xf4f2ee, window: 'right' });
    chair(THREE, scene, { position: [-2.4, 0, -1.1], rotationY: 0.5, color: 0xd9c9ad }); // left of the cabinet's shadow, which now falls back-left
    return { exposure: 1.05 };
  },
  // Older, darker room: aged plaster, dark worn floor, skirting, warm low light from the right, a dark chair.
  oldRoom(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.12;
    scene.background = new THREE.Color(0x4f4a42);
    scene.add(floorMesh(THREE, ctx.tex, { size: 10, planks: { base: '#5a4330', dark: '#4f3a29', light: '#634a35' }, roughness: 0.4 }));
    const back = wallMesh(THREE, { w: 10, h: 2.9, color: 0x7a7362, roughness: 1 }); back.position.set(0, 1.45, -2.0); scene.add(back);
    skirting(THREE, scene, { w: 10, z: -2.0, color: 0x8c8470, h: 0.14 });
    windowWall(THREE, scene, { x: 2.6, color: 0x7a7362, sky: 0xc6d3e6, mullion: null, win: { z0: 1.6, z1: 2.8, sill: 0.95, head: 2.1 } }); // dusk sky, cool, so the lamp's warmth has a neutral to read against (path-traced round 2)
    sun(THREE, scene, { color: 0xffc080, intensity: 2.4, position: [7, 3.2, 4.6], target: [-0.2, 0.3, -0.2], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xcbd7ea, intensity: 2.2, w: 1.0, h: 1.1, position: [2.55, 1.5, 2.2], lookAt: [0, 1.0, 2.2] });
    bounce(THREE, scene, { sky: 0x8fa0bb, ground: 0x5a4330, intensity: 0.3 });
    const lamp = new THREE.PointLight(0xffcf9e, 10, 0, 2); lamp.position.set(1.7, 1.5, 1.3); scene.add(lamp); // a warm-white bulb, not tungsten amber: the white body stays white under it
    enclose(THREE, scene, { x0: -5, x1: 2.6, z0: -2.0, z1: 4.5, h: 2.9, color: 0x7a7362, roughness: 1, window: 'right' });
    chair(THREE, scene, { position: [-2.4, 0, -1.1], rotationY: 0.5, color: 0x3d2a1c });
    return { exposure: 0.95, skyGlow: 2.0 }; // dusk through the window against the lamp, so the room is not only the lamp
  },
  // Studio: #F8F7F4 ground sweeping up into a backdrop behind the subject, horizon faded with fog. Key light per shot.
  studio(THREE, addons, ctx, scene, o) {
    const ground = 0xf8f7f4;
    scene.environmentIntensity = o.env ?? 0.6;
    scene.background = new THREE.Color(ground);
    scene.fog = new THREE.Fog(ground, 6, 40);
    const fl = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: ground, roughness: o.groundRoughness ?? 0.5 }));
    fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true; scene.add(fl);
    sweep(THREE, scene, { color: ground, roughness: o.groundRoughness ?? 0.5, sign: (o.camera && o.camera.position[2] < 0) ? 1 : -1 });
    const key = o.key || 'even';
    if (key === 'even') sun(THREE, scene, { color: 0xffffff, intensity: 2.4, position: [-5, 5, 4], target: [0, 0.5, 0], bounds: 3, mapSize: 4096 });
    if (key === 'rake') sun(THREE, scene, { color: 0xfff8f0, intensity: 3.2, position: [-0.9, 3.4, 1.5], target: [0, 0.9, 0.1], bounds: 1.2, mapSize: 4096 });
    if (key === 'back') sun(THREE, scene, { color: 0xffffff, intensity: 2.2, position: [3.6, 4.0, -2.4], target: [0, 0.5, 0], bounds: 2.5, mapSize: 4096 }); // raking from upper right, so the back face falls off and the cast letters and port take an edge (path-traced round 2)
    if (key === 'swap') sun(THREE, scene, { color: 0xfff4e6, intensity: 2.6, position: [-1.2, 7, 1.8], target: [0, 0.8, 0], bounds: 3, mapSize: 4096 });
    const fill = new THREE.DirectionalLight(0xffffff, o.fill ?? 0.5); fill.position.set(5, 3, 3); scene.add(fill);
    bounce(THREE, scene, { sky: 0xffffff, ground: 0xf8f7f4, intensity: 0.25 });
    return { exposure: o.exposure ?? 1.0, toneMapping: 'neutral' };
  },
  // A desk against a white wall, daylight from the left.
  desk(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.4;
    scene.background = new THREE.Color(0xe9eaec); // neutral, so the fill is cooler than the sun and the pale cartons lift off the set (path-traced round 2)
    const top = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.03, 1.3), new THREE.MeshStandardMaterial({ map: ctx.tex.planks({ base: '#cdb48c', dark: '#c6ac83', light: '#d3bb95' }), roughness: 0.35 }));
    top.material.map = top.material.map.clone(); top.material.map.repeat.set(3.9, 1.8); top.material.map.needsUpdate = true;
    top.position.set(0, 0.72 - 0.015, 0.1); top.receiveShadow = top.castShadow = true; scene.add(top);
    const back = wallMesh(THREE, { w: 8, h: 2.7, color: 0xf1eee8 }); back.position.set(0, 1.35, -0.55); scene.add(back);
    sun(THREE, scene, { color: 0xfff1dc, intensity: 3.0, position: [-3, 3.4, 2.0], target: [0, 0.75, 0], bounds: 1.5, mapSize: 4096 });
    fillRect(THREE, scene, { color: 0xdde6f3, intensity: 3.0, w: 1.5, h: 1.5, position: [-1.6, 1.4, 0.6], lookAt: [0, 0.8, 0] });
    bounce(THREE, scene, { sky: 0xf1eee8, ground: 0xcdb48c, intensity: 0.3 });
    return { exposure: 1.0 };
  },
};

export function buildScene(THREE, addons, ctx, cfg) {
  const scene = new THREE.Scene();
  scene.environment = ctx.env;
  const roomOut = ROOMS[cfg.room](THREE, addons, ctx, scene, { ...(cfg.roomOptions || {}), camera: cfg.camera });
  for (const sp of cfg.speakers || []) {
    const g = buildSpeaker(THREE, addons, ctx, { kind: sp.kind || 'fs', flavor: ctx.flavor(sp.flavor), state: sp.state || {} });
    if (sp.rotationY) g.rotation.y = sp.rotationY; // toe-in, radians, positive turns the front toward +x
    g.scale.setScalar(0.001);
    g.position.set(...sp.position);
    g.rotation.y = sp.rotationY || 0;
    scene.add(g);
  }
  if (cfg.crate) {
    const c = buildCrate(THREE, addons, ctx, { flavors: cfg.crate.flavors });
    c.scale.setScalar(0.001); c.position.set(...cfg.crate.position); c.rotation.y = cfg.crate.rotationY || 0; scene.add(c);
  }
  const [w, h] = cfg.size;
  const cam = cfg.camera;
  const vfov = 2 * Math.atan(12 / cam.focal) * 180 / Math.PI;
  const camera = new THREE.PerspectiveCamera(vfov, w / h, 0.05, 100);
  camera.position.set(...cam.position);
  camera.lookAt(new THREE.Vector3(...cam.lookAt));
  return { scene, camera, exposure: cfg.exposure ?? roomOut.exposure ?? 1.0, toneMapping: roomOut.toneMapping || 'aces', skyGlow: roomOut.skyGlow ?? 1 };
}
