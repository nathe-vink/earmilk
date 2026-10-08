---
name: critic-round
description: Run the studio's fresh-context critic on a render and log it (earmilk, earworm, earwig or any product here). Use after every render batch, or when the user asks how good a render is.
---

# Critic round

The critic judges only what is in the image, against a shipping bar. It must never see the brief, the README, the
prompt files, the spec or CLAUDE.md, and never the context that made the render.

1. **Stage the round.** `python3 critic/round.py stage IMAGE.png --shot-id shot-02a --tag e1` copies the image
   under a neutral name with its part mask, writes the shot card (`critic/card.py`: purpose, what is fixed and why,
   every knob with its value, unit and range, the parts it can measure) and the message for the critic.
2. **Spawn a fresh subagent** (general-purpose, in the background) and give it the message file's text verbatim. No
   other words about the product. Stage 1 is blind (the image only); stage 2 reads the card and measures with the
   tool before it prescribes.
3. **Save and apply.** Save its JSON with `critic/round.py save REPLY --shot-id ... --version ... --round N`
   (critic/rounds/DATE/), log the stage-1 score in the LOG, render with `studio/engine/render.py SHOT --apply
   ROUND.json`, and check the accept tests on the new render with `critic/round.py check NEW.png ROUND.json`.
   A change of kind "asset" is built by hand (a prop, a texture); everything else applies by machine.
4. **Limits.** At most three rounds per shot per look. A new look or a new render path restarts the count.
5. **What to act on.** Light, camera, material and composition notes are render fixes. A note that would change
   geometry or a decision is a spec change: stop and ask the owner. Never change what the object is to please the
   critic.
