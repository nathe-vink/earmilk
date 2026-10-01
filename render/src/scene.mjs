// Rooms, lights and cameras for the shot list. Scene units: metres. Speakers are built in mm and scaled by 0.001.
import { buildSpeaker, buildCrate } from './model.mjs';

function sun(THREE, scene, { color = 0xffdcb4, intensity = 3, position, target = [0, 0.4, 0], bounds = 4, mapSize = 2048, soft = false }) {
  const l = new THREE.DirectionalLight(color, intensity);
  l.position.set(...position); l.target.position.set(...target);
  l.castShadow = true;
  l.shadow.mapSize.set(mapSize, mapSize);
  Object.assign(l.shadow.camera, { left: -bounds, right: bounds, top: bounds, bottom: -bounds, near: 0.2, far: 30 });
  l.shadow.bias = -0.00035; l.shadow.normalBias = 0.015;
  if (soft) l.shadow.radius = 6;
  scene.add(l); scene.add(l.target);
  return l;
}

function fillRect(THREE, scene, { color = 0xffffff, intensity = 5, w = 1.4, h = 1.5, position, lookAt }) {
  const l = new THREE.RectAreaLight(color, intensity, w, h);
  l.position.set(...position); l.lookAt(...lookAt); scene.add(l); return l;
}

function floorMesh(THREE, tex, { size = 8, planks, repeat }) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshStandardMaterial({ map: tex.planks(planks), roughness: 0.62, metalness: 0 }));
  m.material.map.repeat.set(size / 1.2, size / 1.2);
  m.rotation.x = -Math.PI / 2; m.receiveShadow = true; return m;
}

function wallMesh(THREE, { w, h, color, roughness = 0.95 }) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ color, roughness, metalness: 0 }));
  m.receiveShadow = true; return m;
}

// A side wall at x = X with a window opening, mullions and a bright sky behind it.
function windowWall(THREE, scene, { x, zRange = [-2.5, 3.5], h = 2.7, color, win = { z0: 0.3, z1: 1.7, sill: 0.8, head: 2.3 }, sky = 0xfff3dc, mullion = 0xf4f1ea }) {
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.95 });
  const add = (w, hh, cz, cy) => { const m = new THREE.Mesh(new THREE.BoxGeometry(0.12, hh, w), mat); m.position.set(x, cy, cz); m.receiveShadow = true; m.castShadow = true; scene.add(m); };
  const [z0, z1] = zRange;
  add(win.z0 - z0, h, (z0 + win.z0) / 2, h / 2);
  add(z1 - win.z1, h, (win.z1 + z1) / 2, h / 2);
  add(win.z1 - win.z0, win.sill, (win.z0 + win.z1) / 2, win.sill / 2);
  add(win.z1 - win.z0, h - win.head, (win.z0 + win.z1) / 2, (win.head + h) / 2);
  const mm = new THREE.MeshStandardMaterial({ color: mullion, roughness: 0.6 });
  const v = new THREE.Mesh(new THREE.BoxGeometry(0.05, win.head - win.sill, 0.04), mm); v.position.set(x, (win.sill + win.head) / 2, (win.z0 + win.z1) / 2); v.castShadow = true; scene.add(v);
  const hz = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.04, win.z1 - win.z0), mm); hz.position.set(x, (win.sill + win.head) / 2, (win.z0 + win.z1) / 2); hz.castShadow = true; scene.add(hz);
  const skyM = new THREE.Mesh(new THREE.PlaneGeometry(6, 5), new THREE.MeshBasicMaterial({ color: sky }));
  skyM.position.set(x + 0.6 * Math.sign(x), 2, (win.z0 + win.z1) / 2); skyM.rotation.y = Math.sign(x) > 0 ? -Math.PI / 2 : Math.PI / 2; scene.add(skyM);
}

function sofaArm(THREE, addons, scene, { position, color = 0x8a8775 }) {
  const fabric = new THREE.MeshStandardMaterial({ color, roughness: 1 });
  const arm = new THREE.Mesh(new addons.RoundedBoxGeometry(0.26, 0.62, 0.95, 4, 0.07), fabric);
  arm.position.set(position[0], 0.31, position[2]); arm.castShadow = arm.receiveShadow = true; scene.add(arm);
  const seat = new THREE.Mesh(new addons.RoundedBoxGeometry(0.9, 0.2, 0.85, 4, 0.06), fabric);
  seat.position.set(position[0] + 0.58, 0.42, position[2]); seat.castShadow = seat.receiveShadow = true; scene.add(seat);
  const back = new THREE.Mesh(new addons.RoundedBoxGeometry(0.9, 0.5, 0.22, 4, 0.06), fabric);
  back.position.set(position[0] + 0.58, 0.6, position[2] - 0.34); back.castShadow = back.receiveShadow = true; scene.add(back);
}

const ROOMS = {
  // Living room, late-afternoon window light from the left.
  hero(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.35;
    scene.background = new THREE.Color(0xe6e1d6);
    const floor = floorMesh(THREE, ctx.tex, { size: 9, planks: { base: '#b8905f', dark: '#a67f52', light: '#c49c6b' } }); scene.add(floor);
    const back = wallMesh(THREE, { w: 9, h: 2.7, color: 0xebe6dc }); back.position.set(0, 1.35, -2.5); scene.add(back);
    windowWall(THREE, scene, { x: -3, color: 0xe8e3d9, win: { z0: 1.6, z1: 3.0, sill: 0.8, head: 2.3 } });
    sun(THREE, scene, { color: 0xffd8ac, intensity: 3.2, position: [-7, 2.6, 5.5], target: [0.3, 0.3, -0.3], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xfff0dc, intensity: 4, position: [-2.95, 1.55, 2.3], lookAt: [0, 1.0, 2.3] });
    sofaArm(THREE, addons, scene, { position: [2.0, 0, 1.5] });
    return { exposure: 1.0 };
  },
  // Bright apartment: white walls, cool daylight, pale floor.
  apartmentBright(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.6;
    scene.background = new THREE.Color(0xf2f0eb);
    scene.add(floorMesh(THREE, ctx.tex, { size: 9, planks: { base: '#d8ccb2', dark: '#ccbfa3', light: '#e0d5bd' } }));
    const back = wallMesh(THREE, { w: 9, h: 2.7, color: 0xf4f2ee }); back.position.set(0, 1.35, -2.0); scene.add(back);
    windowWall(THREE, scene, { x: -2.6, color: 0xf4f2ee, sky: 0xf6fbff, win: { z0: 0.0, z1: 1.9, sill: 0.7, head: 2.4 } });
    sun(THREE, scene, { color: 0xffffff, intensity: 2.6, position: [-8, 5.5, 3.0], target: [0.3, 0.3, -0.3], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xeef4ff, intensity: 7, w: 1.9, h: 1.7, position: [-2.55, 1.55, 0.95], lookAt: [0, 1.0, 0.95] });
    return { exposure: 1.05 };
  },
  // Older, darker room: aged plaster, dark worn floor, skirting, warm low light.
  oldRoom(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.18;
    scene.background = new THREE.Color(0x4f4a42);
    scene.add(floorMesh(THREE, ctx.tex, { size: 9, planks: { base: '#5a4330', dark: '#4b3626', light: '#684e38' } }));
    const back = wallMesh(THREE, { w: 9, h: 2.9, color: 0x7a7362, roughness: 1 }); back.position.set(0, 1.45, -2.0); scene.add(back);
    const skirt = new THREE.Mesh(new THREE.BoxGeometry(9, 0.14, 0.025), new THREE.MeshStandardMaterial({ color: 0x8c8470, roughness: 0.7 })); skirt.position.set(0, 0.07, -1.99); skirt.receiveShadow = true; scene.add(skirt);
    windowWall(THREE, scene, { x: -2.6, color: 0x7a7362, sky: 0xffe2b8, mullion: 0x9a8f78, win: { z0: 0.5, z1: 1.5, sill: 0.95, head: 2.1 } });
    sun(THREE, scene, { color: 0xffc080, intensity: 1.5, position: [-8, 2.6, 3.4], target: [0.3, 0.3, -0.2], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xffd9a8, intensity: 2.0, w: 1.0, h: 1.1, position: [-2.55, 1.5, 1.0], lookAt: [0, 1.0, 1.0] });
    const lamp = new THREE.PointLight(0xffb469, 10, 0, 2); lamp.position.set(1.7, 1.5, 1.3); lamp.castShadow = false; scene.add(lamp);
    return { exposure: 0.95 };
  },
  // Flat studio ground, #F8F7F4, horizon faded with fog. Key light per shot.
  studio(THREE, addons, ctx, scene, o) {
    const ground = 0xf8f7f4;
    scene.environmentIntensity = o.env ?? 0.9;
    scene.background = new THREE.Color(ground);
    scene.fog = new THREE.Fog(ground, 6, 40);
    const fl = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: ground, roughness: 1 }));
    fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true; scene.add(fl);
    const key = o.key || 'even';
    if (key === 'even') { sun(THREE, scene, { color: 0xffffff, intensity: 2.0, position: [-3, 6, 7], target: [0, 0.5, 0], bounds: 3, soft: true, mapSize: 4096 }); }
    if (key === 'rake') { sun(THREE, scene, { color: 0xfff6ea, intensity: 3.0, position: [-1.8, 3.0, 0.9], target: [0, 0.9, 0.1], bounds: 1.2, mapSize: 4096 }); }
    if (key === 'back') { sun(THREE, scene, { color: 0xffffff, intensity: 1.5, position: [-2.5, 4, -4], target: [0, 0.5, 0], bounds: 2.5, soft: true, mapSize: 4096 }); }
    if (key === 'swap') { sun(THREE, scene, { color: 0xfff4e6, intensity: 2.0, position: [-3, 5, 4], target: [0, 0.8, 0], bounds: 3, soft: true, mapSize: 4096 }); }
    const fill = new THREE.DirectionalLight(0xffffff, o.fill ?? 0.7); fill.position.set(4, 3, 3); scene.add(fill);
    return { exposure: o.exposure ?? 1.0, toneMapping: 'neutral' };
  },
  // A desk against a white wall, daylight from the left.
  desk(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.5;
    scene.background = new THREE.Color(0xeeeae2);
    const top = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.03, 0.8), new THREE.MeshStandardMaterial({ map: ctx.tex.planks({ base: '#cdb48c', dark: '#c2a87e', light: '#d6bf99' }), roughness: 0.55 }));
    top.material.map.repeat.set(2.5, 1.1);
    top.position.set(0, 0.72 - 0.015, 0); top.receiveShadow = top.castShadow = true; scene.add(top);
    const back = wallMesh(THREE, { w: 6, h: 2.7, color: 0xf1eee8 }); back.position.set(0, 1.35, -0.42); scene.add(back);
    sun(THREE, scene, { color: 0xfff1dc, intensity: 2.6, position: [-3, 3.2, 2.2], target: [0, 0.75, 0], bounds: 1.5, mapSize: 4096 });
    fillRect(THREE, scene, { color: 0xffffff, intensity: 3, w: 1.5, h: 1.5, position: [-1.6, 1.4, 0.6], lookAt: [0, 0.8, 0] });
    return { exposure: 1.0 };
  },
};

export function buildScene(THREE, addons, ctx, cfg) {
  const scene = new THREE.Scene();
  scene.environment = ctx.env;
  const roomOut = ROOMS[cfg.room](THREE, addons, ctx, scene, cfg.roomOptions || {});
  for (const sp of cfg.speakers || []) {
    const g = buildSpeaker(THREE, addons, ctx, { kind: sp.kind || 'fs', flavor: ctx.flavor(sp.flavor), state: sp.state || {} });
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
  return { scene, camera, exposure: cfg.exposure ?? roomOut.exposure ?? 1.0, toneMapping: roomOut.toneMapping || 'aces' };
}
