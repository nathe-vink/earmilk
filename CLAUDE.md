# earmilk — notes for sessions working in this repo

Read `README.md` first. It is the handoff and the brief. The canvas it links to is the source of truth for layout, copy and proportions. This file adds only what a session needs to know about working in this repo and in this environment.

## Before any render or edit

1. Re-read the **Geometry** and **Decisions** sections of `README.md`, then `spec/geometry.md`.
2. If a change to either seems necessary, stop and ask. Do not improvise a mechanism, a flavor, a driver layout, or a pint design.
3. Open questions stay open. `[PAIR PRICE]`, `[SLEEVE PRICE]` and `[CRATE PRICE]` stay as placeholders.

## Where things live

| Path | What |
|---|---|
| `spec/geometry.md` | The README's numbers expanded into one coordinate frame, with derived values and as-drawn details from the canvas. A model is built from this file. |
| `spec/colorways.json` | The five flavors, birch, drivers and ground as machine-readable hex, plus the print layout (which flavours carry the lid colour, the band, the optional stand and panel). The model reads its default look from here. |
| `explore/` | Design questions rendered as options, one dated section per question in its README. Not shots. |
| `copy/label.md` | The printed Nutrition Facts copy and the shorter engraved version on the back window. |
| `copy/hero.md` | Every other line of copy on the canvas, by surface. |
| `prompts/shot-NN-vN.md` | One brief per shot, versioned. A version is frozen once a render has been made from it; changes go in vN+1. |
| `renders/YYYY-MM-DD/shot-NN-vN.png` | Output. NN and vN match the prompt file that produced it. |
| `critic/PROMPT.md` | The critic prompt, verbatim, so every round is judged against the same bar. |
| `critic/LOG.md` | One row per critic round. |

## Rendering in a Claude Code cloud session (checked 2026-10-01, path tracer added 2026-10-03)

- There is **no image-generation key** in the environment and no diffusion stack. If a provider key is ever added, it belongs in the environment's settings, never in this repo. The free Gemini tier refuses image calls (checked 2026-10-03).
- **Blender is available as the `bpy` wheel** (`pip install bpy`, about 350 MB, Blender 5.0, Cycles on the CPU). `render/pathtrace.py` renders a GLB exported by `node render.mjs --glb` with the light rig from its sidecar. About four minutes per 1800 × 1200 frame at 128 samples; test at `--scale 0.5 --samples 48`. The `-pt` frames are the deliverable; the real-time frames are the layout check.
- **Headless Chromium has WebGL 2** through SwiftShader (software rendering, max texture 8192). Verified launch: `playwright-core` with `executablePath: '/opt/pw-browsers/chromium'` and the args `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`. Node 22, ffmpeg and ImageMagick `convert` are present. Do not run `playwright install`.
- So renders made here are **a 3D model built from `spec/geometry.md`, lit and screenshotted in the browser**. One model, one set of dimensions, every shot. That is what satisfies the brief's hardest rule, no proportion drift between shots.
- A browser render is clean product visualization, not a photograph. The photoreal pass is the path tracer: same model, same rig, real light. Chat image models could not hold the carton's proportions or the cast letters (2026-10-03, `explore/2026-10-03/`).
- Light units differ between the two renderers and the conversion lives in `pathtrace.py`: a DirectionalLight intensity is an irradiance like a Cycles sun strength; a RectAreaLight is a radiance, so a Cycles area lamp gets intensity × area × π watts; a PointLight is in candela, × 4π; a HemisphereLight is an irradiance, so a dome gets it ÷ π. The rooms are closed boxes so the dome stays outside; the studio's key is a softbox. Material overrides key on material names (`finish*`, `bronze`, `*sky*`), which `makeMaterials` sets so the glTF carries them. A `KHR_materials_unlit` surface imports as emission for camera rays only, transparent to the rest: it lights nothing until rebuilt as a plain emitter.
- Coplanar faces of two solids render black in Cycles (the ray from one face hits the other). Keep boards inside walls, decals a hair off their surface.
- If a render pipeline is added, keep it in one folder (`render/`) with its own README and no build step beyond `npm install`.
- Keep every PNG under about 5 MB. If `renders/` grows past a few hundred MB, move it to Git LFS before clones get slow.

## Critic protocol

- Runs after each render batch, never in the context that made the render. Spawn a fresh subagent and give it only the image(s) and the text of `critic/PROMPT.md`. It must not see `README.md`, the prompt files, the spec, or this file.
- At most three rounds per shot per look: a change to the printed look (as on 2026-10-01) restarts the count, because the critic is judging a different object. Log every round in `critic/LOG.md` before starting the next.
- A new render path (the path tracer, 2026-10-03) restarts the count too: the critic is judging different light and surfaces on the same object.
- A critic note that would change geometry or a Decision is not a critic fix. It is a spec change: stop and ask.

## Commits

- Commit a render together with the prompt version that produced it and its critic log row.
- The canvas is edited on the canvas, not here. If the canvas and this repo disagree, say so and ask which is right; do not silently update either. The canvas carries the 2026-10-02 direction since its version 10, the cast-letter wordmark (no plate) since version 11, the contained back panel since version 12, the bronze plate, the back letters and the two spec marks since version 13, and SHAKE WELL on the plinth with the Facts footnote inside its border since version 14: no sleeve, the colour a finish, the plinth, the metal letters, the engraved back wordmark, the Sleeves board redrawn as Finish, and the Facts row changed to Finish. Its copy changes are drafts (marked in `copy/hero.md`) until the owner approves them.
