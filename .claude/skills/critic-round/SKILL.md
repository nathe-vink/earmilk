---
name: critic-round
description: Run the studio's fresh-context critic on a render and log it (earmilk, earworm, earwig or any product here). Use after every render batch, or when the user asks how good a render is.
---

# Critic round

The critic judges only what is in the image, against a shipping bar. It must never see the brief, the README, the
prompt files, the spec or CLAUDE.md, and never the context that made the render.

1. **Stage the image** under a neutral name in the scratchpad (for example `critic/render-a1.png`), so the path does
   not carry the product's name or the joke.
2. **Spawn a fresh subagent** (general-purpose, in the background). Tell it to read exactly that one image file and
   nothing else, then paste the text between the rules in `critic/PROMPT.md` verbatim. No other words about the
   product.
3. **Log the round** before starting the next one: date, shot, version, round, score, the three gaps (short), fix
   first, and what changed after. earmilk logs in `critic/LOG.md`; a spin-off logs in `spinoffs/NAME/critic/LOG.md`.
4. **Limits.** At most three rounds per shot per look. A new look or a new render path restarts the count.
5. **What to act on.** Light, camera, material and composition notes are render fixes. A note that would change
   geometry or a decision is a spec change: stop and ask the owner. Never change what the object is to please the
   critic.
