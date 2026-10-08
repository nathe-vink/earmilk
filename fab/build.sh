#!/usr/bin/env bash
# Regenerates every fabrication file from fab/params.py, for both sizes (fab/out/ the floorstander, fab/out-bookshelf/
# the bookshelf). See fab/README.md, "Regenerating". SIZES="floorstander" to build one.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${FAB_PY:-.venv-fab/bin/python}"
for SIZE in ${SIZES:-floorstander bookshelf}; do
  export EARMILK_SIZE=$SIZE
  echo "== $SIZE"
  "$PY" fab/cad.py            # solids, STEP, STL (the waveguide insert whole and halved), volumes
  "$PY" fab/acoustics.py      # the floorstander: port length for 32 Hz, simulation, charts; the bookshelf: the sealed box
  if [ "$SIZE" = floorstander ]; then
    "$PY" fab/cad.py          # again, with the new port length
    "$PY" fab/acoustics.py    # and settle
  fi
  "$PY" fab/dsp.py            # the active crossover's starting setup for the amplifier's DSP
  "$PY" fab/flats.py          # DXF panels, nesting, cut list
  "$PY" fab/typeset.py        # letters, the Facts print, stencils, templates
  "$PY" fab/sheets.py         # the drawings to build from (A3 sheets from the CAD)
  "$PY" fab/render_model.py   # the render model for the engine (studio/engine)
  "$PY" fab/horn_grid.py      # the waveguide's true surface, for the render model's shading
done
