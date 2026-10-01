// Page entry: sets up the renderer and exposes window.earmilk.renderShot(cfg) -> PNG data URL.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { ParametricGeometry } from 'three/addons/geometries/ParametricGeometry.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
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
  window.earmilk = { ready: true, renderShot, info: { three: THREE.REVISION } };
}

async function renderShot(cfg) {
  const [w, h] = cfg.size;
  renderer.setSize(w, h, false);
  const { scene, camera, exposure, toneMapping } = buildScene(THREE, addons, ctx, cfg);
  renderer.toneMappingExposure = exposure;
  const tm = toneMapping === 'neutral' ? THREE.NeutralToneMapping : THREE.ACESFilmicToneMapping;
  if (renderer.toneMapping !== tm) { renderer.toneMapping = tm; scene.traverse(o => { if (o.material) o.material.needsUpdate = true; }); }
  const composer = new EffectComposer(renderer);
  composer.setSize(w, h);
  composer.addPass(new RenderPass(scene, camera));
  const ao = cfg.ao || {};
  if (ao.enabled !== false) {
    const gtao = new GTAOPass(scene, camera, w, h);
    gtao.output = GTAOPass.OUTPUT.Default;
    gtao.updateGtaoMaterial({ radius: ao.radius ?? 0.16, distanceExponent: 1, thickness: ao.thickness ?? 1, distanceFallOff: 1, scale: ao.scale ?? 1.1, samples: 16, screenSpaceRadius: false });
    gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, radiusExponent: 1, rings: 2, samples: 16 });
    gtao.blendIntensity = ao.intensity ?? 1;
    composer.addPass(gtao);
  }
  composer.addPass(new OutputPass());
  composer.render();
  const url = renderer.domElement.toDataURL('image/png');
  composer.dispose();
  scene.traverse(o => { if (o.geometry) o.geometry.dispose(); });
  return url;
}

init().catch(e => { window.earmilk = { error: String((e && e.stack) || e) }; });
