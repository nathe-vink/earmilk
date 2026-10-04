---
name: fab-package
description: Regenerate or extend earmilk's fabrication package (CAD, DXF cut files, drawings, acoustics, crossover, parts list) from fab/params.py. Use when a dimension, a driver or a part changes, or the user asks for build files.
---

# earmilk fabrication package

- **Source of truth:** `spec/geometry.md`, copied into `fab/params.py`. Numbers there are SPEC, DERIVED, PROPOSAL or
  PLACEHOLDER. Changing a SPEC number is a spec change: stop and ask. Change the spec first, then `params.py`.
- **Rebuild everything:** `fab/build.sh` (uses `.venv-fab`, about two minutes plus the Cycles views; set `SAMPLES` to
  change those). The order matters: CAD and acoustics alternate twice so the port length settles, then the crossover,
  cut files, typesetting, drawings, and the exploded and section views.
- **Never edit `fab/out/` by hand.** Regenerate it.
- **Crossover:** `fab/crossover.py` builds a starting network from driver models with `studio/xover/xover.py`
  (nodal analysis, delays from the drivers' positions, least-squares fit to Linkwitz-Riley targets, values snapped to
  parts you can buy). It is for budgeting and for seeing the problem, not for building: the real network is fitted
  to measured FRD and ZMA files (`"frd"` and `"zma"` on each driver in the design JSON).
- **Drivers:** `fab/drivers.json` came from web searches without opening the pages (supplier sites are blocked from
  the container). Confirm every number before buying.
- **Check:** `python3 studio/doctor.py` runs every tool once, small; `cd render && npm run check` checks the earmilk
  model against the spec.
