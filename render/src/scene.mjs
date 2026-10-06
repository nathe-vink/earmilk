// Rooms, lights and cameras for the shot list. Scene units: metres. Speakers are built in mm and scaled by 0.001.
import { buildSpeaker, buildCrate } from './model.mjs';

function sun(THREE, scene, { color = 0xffdcb4, intensity = 3, position, target = [0, 0.4, 0], bounds = 4, mapSize = 4096, softbox, spread }) {
  const l = new THREE.DirectionalLight(color, intensity);
  if (softbox) l.userData.softbox = softbox; // the path-traced studio softbox's size in m (default 0.55 of its distance)
  if (spread) l.userData.spread = spread;   // and its grid: the beam's spread in degrees, so the light stays on the subject
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
  m.material.name = 'floor';
  m.material.map = m.material.map.clone(); m.material.map.repeat.set(size / 1.2, size / 1.2); m.material.map.needsUpdate = true;
  m.rotation.x = -Math.PI / 2; m.receiveShadow = true; return m;
}

function wallMesh(THREE, { w, h, color, roughness = 0.95 }) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ color, roughness, metalness: 0 }));
  m.material.name = 'wall';
  m.receiveShadow = true; return m;
}

function skirting(THREE, scene, { w, z, color = 0xf2efe8, h = 0.12 }) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.018), new THREE.MeshStandardMaterial({ color, roughness: 0.6 }));
  m.material.name = 'skirting';
  m.position.set(0, h / 2, z + 0.009); m.receiveShadow = m.castShadow = true; scene.add(m);
}

// The rest of the box: ceiling, right wall and front wall (behind the camera), so the only daylight is what the window admits
// and the lacquer has a room to reflect. Out of frame in every shot; in the path tracer they are what makes the light one story.
function enclose(THREE, scene, { x0, x1, z0, z1, h, color, roughness = 0.95, window = 'right' }) {
  const mat = new THREE.MeshStandardMaterial({ color, roughness, metalness: 0 }); mat.name = 'wall';
  const add = (geom, pos, rot) => { const m = new THREE.Mesh(geom, mat); m.position.set(...pos); m.rotation.set(...rot); m.receiveShadow = m.castShadow = true; scene.add(m); };
  add(new THREE.PlaneGeometry(x1 - x0, z1 - z0), [(x0 + x1) / 2, h, (z0 + z1) / 2], [Math.PI / 2, 0, 0]);  // ceiling, facing down
  if (window !== 'left') add(new THREE.PlaneGeometry(z1 - z0, h), [x0, h / 2, (z0 + z1) / 2], [0, Math.PI / 2, 0]);    // left wall, facing +x
  if (window !== 'right') add(new THREE.PlaneGeometry(z1 - z0, h), [x1, h / 2, (z0 + z1) / 2], [0, -Math.PI / 2, 0]);  // right wall, facing -x
  if (window !== 'front') add(new THREE.PlaneGeometry(x1 - x0, h), [(x0 + x1) / 2, h / 2, z1], [0, Math.PI, 0]);      // front wall, facing -z
}

// A studio sweep: the floor curves up into a backdrop on the far side of the subject from the camera, so there is no horizon line.
function sweep(THREE, scene, { color, roughness = 0.5, sign = -1, dist = 2.6, radius = 1.5, height = 6, width = 40, segs = 24, rotY = 0 }) {
  const prof = [];
  for (let i = 0; i <= segs; i++) { const t = (i / segs) * Math.PI / 2; prof.push([sign * (dist + radius * Math.sin(t)), radius - radius * Math.cos(t)]); }
  prof.push([sign * (dist + radius), height]);
  const pos = [], idx = [];
  prof.forEach(([z, y]) => { pos.push(-width / 2, y, z, width / 2, y, z); });
  for (let i = 0; i < prof.length - 1; i++) { const a = 2 * i, b = a + 1, c = a + 2, d = a + 3; if (sign < 0) idx.push(a, b, c, b, d, c); else idx.push(a, c, b, b, c, d); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color, roughness, metalness: 0, side: THREE.DoubleSide }));
  m.rotation.y = rotY;   // v18: turned to face a camera that looks across the set at an angle (it showed the curve as a horizon)
  m.receiveShadow = true; scene.add(m);
}

// A side wall at x = X with a window opening, mullions and a bright sky behind it.
function windowWall(THREE, scene, { x, zRange = [-2.5, 4.5], h = 2.7, color, win = { z0: 0.3, z1: 1.7, sill: 0.8, head: 2.3 }, sky = 0xfff3dc, mullion = 0xf4f1ea, bars = null }) {
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.95 }); mat.name = 'wall';
  const add = (w, hh, cz, cy) => { const m = new THREE.Mesh(new THREE.BoxGeometry(0.12, hh, w), mat); m.position.set(x, cy, cz); m.receiveShadow = true; m.castShadow = true; scene.add(m); };
  const [z0, z1] = zRange;
  add(win.z0 - z0, h, (z0 + win.z0) / 2, h / 2);
  add(z1 - win.z1, h, (win.z1 + z1) / 2, h / 2);
  add(win.z1 - win.z0, win.sill, (win.z0 + win.z1) / 2, win.sill / 2);
  add(win.z1 - win.z0, h - win.head, (win.z0 + win.z1) / 2, (win.head + h) / 2);
  if (bars) {
    // v17: glazing bars at the given z, full height, no transom: their shadows cross the sun's patch on the wall, not the speaker
    const mm = new THREE.MeshStandardMaterial({ color: bars.color, roughness: 0.6 });
    for (const bz of bars.at) { const v = new THREE.Mesh(new THREE.BoxGeometry(0.06, win.head - win.sill, 0.05), mm); v.position.set(x, (win.sill + win.head) / 2, bz); v.castShadow = true; scene.add(v); }
  } else if (mullion !== null) {
    const mm = new THREE.MeshStandardMaterial({ color: mullion, roughness: 0.6 });
    const v = new THREE.Mesh(new THREE.BoxGeometry(0.05, win.head - win.sill, 0.04), mm); v.position.set(x, (win.sill + win.head) / 2, (win.z0 + win.z1) / 2); v.castShadow = true; scene.add(v);
    const hz = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.04, win.z1 - win.z0), mm); hz.position.set(x, (win.sill + win.head) / 2, (win.z0 + win.z1) / 2); hz.castShadow = true; scene.add(hz);
  }
  const skyM = new THREE.Mesh(new THREE.PlaneGeometry(6, 5), new THREE.MeshBasicMaterial({ color: sky }));
  skyM.position.set(x + 0.6 * Math.sign(x), 2, (win.z0 + win.z1) / 2); skyM.rotation.y = Math.sign(x) > 0 ? -Math.PI / 2 : Math.PI / 2; scene.add(skyM);
}

// The same on the front wall at z = Z (behind the camera), facing -z: the opening and the sky outside it. No mullions.
function windowWallZ(THREE, scene, { z, xRange, h = 2.7, color, win, sky }) {
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.95 }); mat.name = 'wall';
  const add = (w, hh, cx, cy) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, hh, 0.12), mat); m.position.set(cx, cy, z); m.receiveShadow = true; m.castShadow = true; scene.add(m); };
  const [x0, x1] = xRange;
  add(win.x0 - x0, h, (x0 + win.x0) / 2, h / 2);
  add(x1 - win.x1, h, (win.x1 + x1) / 2, h / 2);
  add(win.x1 - win.x0, win.sill, (win.x0 + win.x1) / 2, win.sill / 2);
  add(win.x1 - win.x0, h - win.head, (win.x0 + win.x1) / 2, (win.head + h) / 2);
  const skyM = new THREE.Mesh(new THREE.PlaneGeometry(8, 5), new THREE.MeshBasicMaterial({ color: sky }));
  skyM.position.set((win.x0 + win.x1) / 2, 2, z + 0.6); skyM.rotation.y = Math.PI; scene.add(skyM);
}

// A wooden dining chair, for scale: tapered round legs (the back pair raked and running up into the back), a seat with
// rounded edges, a curved top rail and a lower rail, stretchers. Path-traced round 1 called the old one a massing model.
function chair(THREE, addons, scene, { position, rotationY = 0, color = 0x8a6a46 }) {
  const wood = new THREE.MeshStandardMaterial({ color, roughness: 0.45 }); wood.name = 'chairwood';
  const g = new THREE.Group();
  const put = (m) => { m.castShadow = m.receiveShadow = true; g.add(m); return m; };
  const rod = (a, b, r0, r1) => {
    const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), len = A.distanceTo(B);
    const m = put(new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, len, 20), wood));
    m.position.copy(A).add(B).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
    return m;
  };
  const seat = put(new THREE.Mesh(new addons.RoundedBoxGeometry(0.44, 0.032, 0.42, 3, 0.012), wood)); seat.position.set(0, 0.45, 0);
  for (const sx of [-1, 1]) {
    rod([sx * 0.19, 0, 0.18], [sx * 0.185, 0.436, 0.175], 0.013, 0.017);           // front legs, tapering to the floor
    rod([sx * 0.19, 0, -0.21], [sx * 0.18, 0.88, -0.19], 0.013, 0.016);           // back legs, raked, up into the back
    rod([sx * 0.19, 0.16, 0.18], [sx * 0.19, 0.16, -0.205], 0.008, 0.008);        // side stretchers
  }
  rod([-0.19, 0.12, 0.18], [0.19, 0.12, 0.18], 0.008, 0.008);                      // front stretcher
  const rail = (y, h, t) => {                                                       // a curved rail between the back legs
    const geo = new THREE.CylinderGeometry(0.62, 0.62, h, 32, 1, true, -0.33, 0.66);
    const inner = new THREE.CylinderGeometry(0.62 - t, 0.62 - t, h, 32, 1, true, -0.33, 0.66);
    const a = put(new THREE.Mesh(geo, wood)); const b = put(new THREE.Mesh(inner, wood));
    for (const m of [a, b]) { m.material = wood; m.position.set(0, y, 0.40); m.rotation.y = Math.PI; }
  };
  rail(0.80, 0.075, 0.016); rail(0.62, 0.035, 0.014);
  g.position.set(...position); g.rotation.y = rotationY; scene.add(g);
}

const ROOMS = {
  // Living room, late-afternoon sun through a window on the front-right (the camera's side, so it sees the lit faces and the shadows); a chair by the back wall for scale.
  hero(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = 0.18;
    scene.background = new THREE.Color(0xe6e1d6);
    // v19 (round 2 of the v17 batch: the wall's carton shadow joined to nothing across the boards; the white against a wall 4 %
    // darker): the room 3.0 m high with the window to 2.95, so the sun stands at 19 degrees (was 15) and lays more light on the
    // boards, each cabinet's shadow running dark from its plinth to the wall; less sky; the floor less glossy; the wall a warm grey
    scene.add(floorMesh(THREE, ctx.tex, { size: 10, planks: { base: '#b8905f', dark: '#ab8456', light: '#c2996a' }, roughness: 0.52 }));
    // v18 (round 1 of the v17 batch: the room's light and the cabinets' did not read as one sun): the back wall 1.3 m behind the
    // pair, so the low sun lays a band along its foot and each cabinet's shadow climbs into it, gable and all
    const back = wallMesh(THREE, { w: 10, h: 3.0, color: 0xddd6ca }); back.position.set(0, 1.5, -1.3); scene.add(back);
    skirting(THREE, scene, { w: 10, z: -1.3 });
    // v15 (refinement round 1): the beam falls across both cabinets from the right, so each throws its own long shadow
    // across the boards and the near one's lit side stands a stop above its front; no sun patch on the wall
    // v17 (refinement round 3: the sun spent itself on the blank sides while the fronts sat in fill): the window in the wall
    // behind the camera, so a low sun from the front-left (30 degrees off the axis, 15 up) takes the fronts and the spouts, the
    // sides the camera sees fall into shade, and the long shadows run back to the right across the boards. (From the front-right,
    // proofed first, it sat almost behind the camera: the sides lit nearly as the fronts and the shadows hidden.) The sky in the
    // window cool, so the shade reads cold against the warm boards; a tall card at camera-left for a hairline on each corner.
    // v18: the window behind the camera nearly the width of the wall, so the sun covers the whole floor in frame and only the
    // shadows break it (a narrow beam left pools on the right that read as a light from the right)
    windowWallZ(THREE, scene, { z: 4.5, xRange: [-5, 3.5], h: 3.0, color: 0xe8e3d9, sky: 0xc8daf4, win: { x0: -4.9, x1: 1.2, sill: 0.45, head: 2.95 } });
    sun(THREE, scene, { color: 0xffeedb, intensity: 5.2, position: [-3.78, 3.10, 6.55], target: [0, 0.5, 0], bounds: 4.5 });   // less amber: the white reads white against the boards
    fillRect(THREE, scene, { color: 0xd2e0f4, intensity: 0.3, w: 5.6, h: 2.2, position: [-1.85, 1.7, 4.4], lookAt: [-1.85, 1.0, 0] });
    fillRect(THREE, scene, { color: 0xffffff, intensity: 22, w: 0.3, h: 1.6, position: [-0.6, 1.1, 3.9], lookAt: [0, 0.6, 0] });
    bounce(THREE, scene, { sky: 0xe8e4dc, ground: 0xb8905f, intensity: 0.2 });
    enclose(THREE, scene, { x0: -5, x1: 3.5, z0: -1.3, z1: 4.5, h: 3.0, color: 0xddd6ca, window: 'front' });
    // v16 (refinement round 2): the chair turned toward the window, set down rather than posed facing the camera
    // v18: the chair against the wall left of the left cabinet, out of the middle (round 1: the centre went to the chair)
    chair(THREE, addons, scene, { position: [-2.62, 0, -1.02], rotationY: 0.35 });   // v19: clear of the left cabinet's edge
    // v16: exposure down about half a stop, so the sunlit white sides (249 at v15) and the coral plinths stop clipping and the
    // white faces separate the way the coral ones do
    return { exposure: 0.72, skyGlow: 0.7 };  // v18: less sky, the window being over twice as wide; v19 less again // skyGlow: the path tracer's sky through this window, relative to the sun; a low sun admits little, so the shade needs more
  },
  // Bright apartment: white walls, cool daylight from the front-right, pale floor, a pale chair.
  apartmentBright(THREE, addons, ctx, scene, o) {
    // v15 (refinement round 1): the window on the left wall, so the sun crosses the front face (the key the critic asked
    // for), the right side falls a stop into shade and the shadow runs back-right; exposure down so the white holds
    scene.environmentIntensity = 0.3;
    scene.background = new THREE.Color(0xf2f0eb);
    scene.add(floorMesh(THREE, ctx.tex, { size: 10, planks: { base: '#d8ccb2', dark: '#cfc2a7', light: '#dfd4bc' }, roughness: 0.32 }));
    // v19 (round 2: the shaded side nearly the wall's pale grey, that edge lost): the walls a light warm grey, still a bright room
    const back = wallMesh(THREE, { w: 10, h: 2.7, color: 0xe4dfd6 }); back.position.set(0, 1.35, -2.0); scene.add(back);
    skirting(THREE, scene, { w: 10, z: -2.0, color: 0xfaf9f6 });
    // v17 (refinement round 3: the sunlit boards outshone the front): the wall closer (x -2.0) and the window narrower and taller,
    // the sun higher and further round (40 degrees off the axis, 24 up), so its beam is a band that falls on the cabinet and the
    // floor around it stays in the room's light; exposure up a little, set off the white face
    // v18 (round 1 of the v17 batch: the floor followed one sun and the cabinet ignored it; its long thin shadow, cut by a narrow
    // beam, did not read as its own): a French door in a wall closer still (x -1.7), the sun higher (30 degrees, 45 off the axis),
    // so the beam is wide and the cabinet's shadow, gable and all, lies whole on the sunlit boards beside it
    windowWall(THREE, scene, { x: -1.7, color: 0xe4dfd6, sky: 0xf6fbff, mullion: null, win: { z0: 0.9, z1: 2.9, sill: 0.05, head: 2.6 } });
    sun(THREE, scene, { color: 0xffffff, intensity: 3.4, position: [-4.9, 4.5, 4.9], target: [0, 0.5, 0], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xeef4ff, intensity: 1.4, w: 1.8, h: 2.3, position: [-1.65, 1.35, 1.9], lookAt: [0, 1.0, 1.9] });
    bounce(THREE, scene, { sky: 0xf4f2ee, ground: 0xd8ccb2, intensity: 0.3 });
    enclose(THREE, scene, { x0: -1.7, x1: 5, z0: -2.0, z1: 4.5, h: 2.7, color: 0xe4dfd6, window: 'left' });
    chair(THREE, addons, scene, { position: [0.9, 0, -1.6], rotationY: -0.5, color: 0xd9c9ad }); // right of the cabinet, clear of it
    return { exposure: 0.95 };
  },
  // Older, darker room: aged plaster, dark worn floor, skirting, warm low light from the right, a dark chair.
  oldRoom(THREE, addons, ctx, scene, o) {
    // v15 (refinement round 1): the window on the left wall, so the low sun's beam sweeps the front face and gable and the
    // shadow runs back-right; the cool fill and the lamp down, so the beam is the light the speaker answers to
    // v16 (refinement round 2): the room lifted out of the murk (env, bounce and the lamp up, exposure up a little) and the window
    // taller, its sill at 0.35, so the beam takes the whole front from gable to plinth instead of cutting a diagonal across it
    // below the mid driver, and lays a crisp patch on the boards
    scene.environmentIntensity = 0.3;
    scene.background = new THREE.Color(0x4f4a42);
    scene.add(floorMesh(THREE, ctx.tex, { size: 10, planks: { base: '#5a4330', dark: '#4f3a29', light: '#634a35' }, roughness: 0.4 }));
    // v18: the back wall 0.8 m behind the cabinet, where a floorstander stands, so its shadow climbs the wall inside the sun's
    // patch, gable and all, beside the glazing bar's (round 1: the sun on the wall never seemed to reach the speaker)
    const back = wallMesh(THREE, { w: 10, h: 2.9, color: 0x7a7362, roughness: 1 }); back.position.set(0, 1.45, -0.8); scene.add(back);
    skirting(THREE, scene, { w: 10, z: -0.8, color: 0x8c8470, h: 0.14 });
    // v17 (refinement round 3: no window patch to explain the key; the amber turned the white cream and the red orange): the
    // window three panes wide (z 0.2 to 2.8), so past the cabinet the beam lays its patch, a glazing bar's shadow across it, on the
    // back wall behind the chair; the sun's colour less amber
    // v18 (round 1 of the v17 batch: the sun on the wall never seemed to reach the speaker, its front lit dead even and its shadow
    // a soft darkening): the window down to the floor, so the beam lies on the boards round the cabinet and its shadow starts hard
    // at its base; the sun a little higher (10 degrees), so that shadow runs across the frame
    // v19 (round 2: no shadow across the boards from the plinth to the wall's silhouette; the front not warm): the sun higher (18
    // degrees) and a touch warmer, the window wider and taller, so the whole cabinet stands in the beam, the sunlit boards are
    // bright enough to show its shadow running from the plinth to the wall, and the silhouette still climbs the wall
    windowWall(THREE, scene, { x: -2.6, zRange: [-0.8, 4.5], color: 0x7a7362, sky: 0xc6d3e6, mullion: null, bars: { at: [1.75], color: 0x8c8470 }, win: { z0: 1.15, z1: 2.8, sill: 0.05, head: 2.45 } });
    sun(THREE, scene, { color: 0xffcf9c, intensity: 2.6, position: [-5.83, 3.27, 4.89], target: [0, 0.8, 0], bounds: 4.5 });
    fillRect(THREE, scene, { color: 0xcbd7ea, intensity: 0.8, w: 1.0, h: 1.1, position: [-2.55, 1.5, 2.2], lookAt: [0, 1.0, 2.2] });
    bounce(THREE, scene, { sky: 0x8fa0bb, ground: 0x5a4330, intensity: 0.45 });
    const lamp = new THREE.PointLight(0xffcf9e, 7, 0, 2); lamp.position.set(1.7, 1.5, 1.3); scene.add(lamp);
    enclose(THREE, scene, { x0: -2.6, x1: 5, z0: -0.8, z1: 4.5, h: 2.9, color: 0x7a7362, roughness: 1, window: 'left' });
    chair(THREE, addons, scene, { position: [-1.05, 0, -0.42], rotationY: 0.5, color: 0x3d2a1c });   // v18: in the room's shade at the left
    return { exposure: 1.15, skyGlow: 2.6 };   // v16: the window's sky brighter, so the room's left side is not a void; v17: less, the window is twice as wide
  },
  // Studio: #F8F7F4 ground sweeping up into a backdrop behind the subject, horizon faded with fog. Key light per shot.
  studio(THREE, addons, ctx, scene, o) {
    const ground = o.ground ?? 0xf8f7f4;   // v19: a shot can set the set's tone (the close-up's white body sank into a white sweep)
    scene.environmentIntensity = o.env ?? 0.6;
    scene.background = new THREE.Color(ground);
    scene.fog = new THREE.Fog(ground, 6, 40);
    const fl = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: ground, roughness: o.groundRoughness ?? 0.5 }));
    fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true; scene.add(fl);
    // the sweep curves up on the far side from the camera; turned about the subject to face a camera that looks in at an angle
    const cp = o.camera ? o.camera.position : [0, 0, 5], ca = o.camera ? o.camera.lookAt : [0, 0, 0];
    const back = cp[2] < 0 ? 1 : -1, ang = Math.atan2(ca[0] - cp[0], (ca[2] - cp[2]) * back);
    sweep(THREE, scene, { color: ground, roughness: o.groundRoughness ?? 0.5, sign: back, rotY: o.turnSweep ? back * ang : 0 });
    const key = o.key || 'even';
    if (key === 'even') sun(THREE, scene, { color: 0xffffff, intensity: 2.4, position: [-5, 5, 4], target: [0, 0.5, 0], bounds: 3, mapSize: 4096 });
    if (key === 'rake') sun(THREE, scene, { color: 0xfff8f0, intensity: 3.2, position: [-0.9, 3.4, 1.5], target: [0, 0.9, 0.1], bounds: 1.2, mapSize: 4096 });
    // v15: a key from the front-left at about 18 degrees, the one direction that reaches a tweeter facing forward under the
    // bowl's upper lip (refinement round 1 on the close-up: the throat read as an eye socket under light from above)
    // v17 (refinement round 3): on the same axis but further and smaller (0.9 m at 3.2 m), so it reads as one source
    if (key === 'bowl') sun(THREE, scene, { color: 0xfff6ec, intensity: 3.0, position: [-1.64, 1.85, 2.67], target: [0, 0.9, 0.09], bounds: 1.2, mapSize: 4096, softbox: 0.9 });
    // v15 (refinement round 1 on the back): a smaller, closer softbox from the camera's right, 30 degrees up and 50 off the back
    // face, so the face falls off across its width, the posts, letters and port take an edge, and the cabinet's own shadow lands
    // in frame at its left instead of behind it
    if (key === 'back') sun(THREE, scene, { color: 0xffffff, intensity: 2.8, position: [-1.19, 1.45, -1.0], target: [0, 0.55, 0], bounds: 2.5, mapSize: 4096, softbox: 0.6 });
    // v17 (the owner, 2026-10-06: a three-quarter back view beside the straight one): the same softbox on the other side of the
    // back face, 50 degrees off it and 35 up, across from the camera, so the back takes the light, the side the camera sees falls
    // into shade, and the cabinet's shadow runs out to the right of it, in frame
    // v18 (round 1: a near-white patch on the empty floor beside the cabinet, its bounce lighting the shaded side as bright as the
    // back): 35 degrees off the back face (was 50), so the back takes more of it, with a grid so the beam stays on the cabinet
    // v19 (round 2: the back blown nearly to clipped white, each plane one value, a long low shadow across the empty half): a stop
    // less, a larger softbox (1.2 m) for falloff down the face, and higher (50 degrees), so the shadow falls short and behind
    if (key === 'back3q') sun(THREE, scene, { color: 0xffffff, intensity: 1.5, position: [0.75, 2.04, -1.07], target: [0, 0.55, 0], bounds: 2.5, mapSize: 4096, softbox: 1.2, spread: 60 });
    // v15 (refinement round 1 on the line-up): a softbox high at the front-left, 55 degrees up and 30 off the camera's axis, 3.5 m
    // out and aimed past the row's centre toward its right end so the five stay within a third of a stop: the gable slopes take the
    // most light, the fronts less, the sides the camera sees fall into shade, and the sweep, twice as far from it, a stop below the
    // white fronts
    // v16: a grid on it (75 degree spread) and aimed a little higher, so the cabinets take the beam's core while the floor in
    // front and the sweep behind fall off: the whites, not the empty floor, are the brightest thing in frame
    // v17 (refinement round 3: no edge took a line): the key further round, 52 degrees off the camera's axis and 40 up (was 36 and
    // 49), so the fronts fall off toward their far edges and the sides the lens shows stay dark
    // v18 (round 1 of the v17 batch: a broad wash, soft smudges for shadows): the softbox smaller (1.0 m), so each base throws a
    // tighter shadow and contact line
    if (key === 'lineup') sun(THREE, scene, { color: 0xffffff, intensity: 2.6, position: [-1.70, 2.94, 1.50], target: [0.35, 0.75, -0.1], bounds: 3, mapSize: 4096, softbox: 1.0, spread: 75 });
    if (key === 'swap') sun(THREE, scene, { color: 0xfff4e6, intensity: 2.6, position: [-1.2, 7, 1.8], target: [0, 0.8, 0], bounds: 3, mapSize: 4096 });
    const fill = new THREE.DirectionalLight(0xffffff, o.fill ?? 0.5); fill.position.set(...(o.fillPos || [5, 3, 3])); scene.add(fill);
    if (o.fillSoftbox) fill.userData.softbox = o.fillSoftbox; // path-traced: a sized softbox where the rig puts it, not a broad 3.5 m fill ([w, h] for a strip box)
    if (o.card) fillRect(THREE, scene, o.card);             // v17: a low card in front, lighting what faces forward and down (the bowl's back wall)
    bounce(THREE, scene, { sky: 0xffffff, ground: 0xf8f7f4, intensity: o.bounce ?? 0.25 });
    return { exposure: o.exposure ?? 1.0, toneMapping: 'neutral', reflector: o.reflector, strips: o.strips, stripAngle: o.stripAngle, backdropLight: o.backdropLight };
  },
  // A desk against a white wall, daylight from the left.
  desk(THREE, addons, ctx, scene, o) {
    scene.environmentIntensity = o.env ?? 0.4;
    scene.background = new THREE.Color(0xe9eaec); // neutral, so the fill is cooler than the sun and the pale cartons lift off the set (path-traced round 2)
    const top = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.03, 1.3), new THREE.MeshStandardMaterial({ map: ctx.tex.planks(o.desk || { base: '#cdb48c', dark: '#c6ac83', light: '#d3bb95' }), roughness: 0.35 }));
    top.material.name = 'desk';
    top.material.map = top.material.map.clone(); top.material.map.repeat.set(3.9, 1.8); top.material.map.needsUpdate = true;
    top.position.set(0, 0.72 - 0.015, 0.1); top.receiveShadow = top.castShadow = true; scene.add(top);
    const back = wallMesh(THREE, { w: 8, h: 2.7, color: o.wall ?? 0xf1eee8 }); back.position.set(0, 1.35, -0.55); scene.add(back);
    sun(THREE, scene, { color: 0xfff1dc, intensity: 3.0, position: [-3, 3.4, 2.0], target: [0, 0.75, 0], bounds: 1.5, mapSize: 4096 });
    fillRect(THREE, scene, { color: 0xdde6f3, intensity: o.fill ?? 3.0, w: 1.5, h: 1.5, position: [-1.6, 1.4, 0.6], lookAt: [0, 0.8, 0] });
    bounce(THREE, scene, { sky: 0xf1eee8, ground: 0xcdb48c, intensity: o.bounce ?? 0.3 });
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
  return { scene, camera, exposure: cfg.exposure ?? roomOut.exposure ?? 1.0, toneMapping: roomOut.toneMapping || 'aces', skyGlow: roomOut.skyGlow ?? 1, reflector: roomOut.reflector, strips: roomOut.strips, stripAngle: roomOut.stripAngle, backdropLight: roomOut.backdropLight };
}
