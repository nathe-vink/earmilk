// Page entry: sets up the renderer and exposes window.earmilk.renderShot(cfg) -> PNG data URL.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { ParametricGeometry } from 'three/addons/geometries/ParametricGeometry.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { makeTextures } from './textures.mjs';
import { makeMaterials } from './model.mjs';
import { buildScene } from './scene.mjs';

const addons = { ParametricGeometry, RoundedBoxGeometry };
let renderer, ctx;

async function init() {
  await Promise.all([document.fonts.load('10px "Archivo Black"'), document.fonts.load('400 10px "Archivo"'), document.fonts.load('700 10px "Archivo"')]);
  const colorways = await (await fetch('/spec/colorways.json')).json();
  const canvas = document.getElementById('c');
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  RectAreaLightUniformsLib.init();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const tex = makeTextures(THREE);
  const matCache = new Map();
  ctx = {
    tex, env, colorways,
    flavor: key => { const f = colorways.flavors[key]; if (!f) throw new Error(`unknown flavor ${key}`); return { key, ...f }; },
    materials: flavor => { if (!matCache.has(flavor.key)) matCache.set(flavor.key, makeMaterials(THREE, tex, flavor)); return matCache.get(flavor.key); },
  };
  window.earmilk = { ready: true, renderShot, info: { three: THREE.REVISION, renderer: renderer.getContext().getParameter(renderer.getContext().RENDERER) } };
}

async function renderShot(cfg) {
  const [w, h] = cfg.size;
  renderer.setSize(w, h, false);
  const { scene, camera, exposure, toneMapping } = buildScene(THREE, addons, ctx, cfg);
  renderer.toneMappingExposure = exposure;
  const tm = toneMapping === 'neutral' ? THREE.NeutralToneMapping : THREE.ACESFilmicToneMapping;
  if (renderer.toneMapping !== tm) { renderer.toneMapping = tm; scene.traverse(o => { if (o.material) o.material.needsUpdate = true; }); }
  renderer.render(scene, camera);
  const url = renderer.domElement.toDataURL('image/png');
  scene.traverse(o => { if (o.geometry) o.geometry.dispose(); });
  return url;
}

init().catch(e => { window.earmilk = { error: String((e && e.stack) || e) }; });
