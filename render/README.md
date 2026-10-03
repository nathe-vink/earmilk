# render

One Three.js model of the carton speaker, built from `spec/geometry.md` through `src/spec.mjs`, one room and camera rig per shot brief in `prompts/`, screenshotted through headless Chromium. The same model renders every shot, so the proportions cannot drift between frames.

    cd render
    npm install
    npm run check                 # derived numbers against spec/geometry.md; fails on drift
    node render.mjs               # every shot, v1, into renders/<today>/
    node render.mjs --only 01,03 --v 2
    node render.mjs --scale 2     # supersample 2x and downscale (uses ImageMagick convert)

| File | What |
|---|---|
| `src/spec.mjs` | The numbers, in the frame `spec/geometry.md` defines. |
| `src/check-spec.mjs` | Prints the derived values and exits non-zero if any drift. |
| `src/model.mjs` | Cabinet, carved block, bowl loft, tweeter, drivers, sleeve tube and lid, print decals, back details; the pint and the crate. |
| `src/textures.mjs` | Canvas textures: wordmarks, the engraved label, the bowl gradient, birch grain, floor planks. |
| `src/scene.mjs` | Rooms, lights and cameras. |
| `src/shots.mjs` | One entry per shot, plain data, matching `prompts/`. |
| `src/app.mjs`, `page.html` | The page that renders a shot config to a PNG data URL. |
| `render.mjs` | Node harness: static server plus playwright-core driving the preinstalled Chromium. |
| `fonts/` | Archivo and Archivo Black, SIL Open Font License. |

Rendering here runs on SwiftShader (software WebGL 2) at 1800 x 1200 in a few seconds per frame.

Assumptions the model makes beyond the spec, all also noted in `spec/geometry.md`: the sleeve board sits outside the spec dimensions, so the sleeved speaker is 393 mm wide, invisible at any shot scale; the pint's bowl is the floorstander's scaled by the plan ratio, with its throat closed, since the pint has one full-range driver and no tweeter; the pint's walls are 5 mm and its fin 2 mm.

## Photoreal pass (`photo.py`)

Sends a rendered frame to Google's Gemini image model as the layout and asks for light and materials only, writing `renders/<date>/shot-NN-vN-photo-X.png` beside it. The prompt is the shot's text-to-image paragraph under the constant block from `prompts/`. The key is read from `IMAGE_API_KEY` or the file named by `IMAGE_API_KEY_FILE`; keep it in the environment's settings, never in the repo.

    IMAGE_API_KEY=... python3 render/photo.py --shots 01,04 --variants 2 --date 2026-10-03

On a free-tier Google key the image models return "quota exceeded" (free daily limit of zero for image generation, as of 2026-10-03); the project needs pay-as-you-go billing for the call to succeed.

## Path-traced pass (`--glb` and `pathtrace.py`)

The real-time renderer hits a ceiling the critic named in every round: one light the whole frame obeys, penumbra, bounce, contact occlusion. The path-traced pass renders the same model in Blender's Cycles on the CPU, so nothing drifts.

    cd render && npm install          # three + playwright-core
    pip install bpy                   # Blender as a Python module, about 350 MB
    node render.mjs --v 11 --glb render/out/glb                    # export each frame as GLB + a sidecar with the light rig
    python3 render/pathtrace.py --glb render/out/glb/shot-01-v11.glb --out renders/2026-10-03/shot-01-v11-pt.png --samples 128

`--glb` exports the scene with its camera; fake contact-shadow decals are dropped and alpha-only decals become colour maps so glTF carries them. The sidecar lists the sun, area fills, hemisphere and point lamps, the exposure and the room's `skyGlow`; `pathtrace.py` rebuilds them in Cycles units (sun strength = the real-time intensity; area power = intensity × area × π; point power = candela × 4π; dome radiance = hemisphere ÷ π), keeps the glTF materials, and renders with denoising and the AgX view. `render/out/` is not committed.

What the path tracer does differently from the real-time scene, and why (round 1 of its critic, 2026-10-03):

- The rooms are closed boxes (`enclose` in `scene.mjs`), so the only daylight is the window's: the sun (at twice the real-time strength, because AgX keeps the highlights ACES clipped), the sky plane glowing outside the opening (`1.5 × sun × skyGlow`, the rig's suns being cinematic rather than solar) and the area fill inside it. Cycles bounces the rest; the dome stays outside. glTF marks the sky plane unlit and Blender's importer builds that as emission for camera rays only, mixed with transparency for every other ray, so it lit nothing until `pathtrace.py` rebuilt it as a plain emitter.
- The studio's directional lights become softboxes on the same axis (square area lamps, 2.6 m at 4.5 m for the key), its dome a vertical gradient from white overhead to the backdrop tone at the horizon, and the floor sweeps up into a backdrop (`sweep`), so lacquer and metal have something to reflect and there is no horizon seam.
- Materials named `finish*` and `bronze` get a shader-space bevel of 2 mm on their normals (eased arrises, silhouette unchanged); `bronze` is rendered as a metal (the real-time renderer fakes it part-diffuse against one pale environment map); `*sky*` planes emit and cast no shadow.
- Flags: `--samples`, `--scale`, `--time-limit`, `--sun-strength`, `--area-strength`, `--world-strength`, `--sky-strength`, all multipliers on the sidecar values. Full frames take about four minutes on four cores; `--scale 0.5 --samples 48` is a one-minute proof.
