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
