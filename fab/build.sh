#!/usr/bin/env bash
# Regenerates every fabrication file from fab/params.py. See fab/README.md, "Regenerating".
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${FAB_PY:-.venv-fab/bin/python}"
"$PY" fab/cad.py          # solids, STEP, STL, volumes (port at its last computed length)
"$PY" fab/acoustics.py    # port length for 32 Hz, simulation, charts
"$PY" fab/cad.py          # again, with the new port length
"$PY" fab/acoustics.py    # and settle
"$PY" fab/flats.py        # DXF panels, nesting, cut list
"$PY" fab/typeset.py      # letters, plate, stencils, templates
"$PY" fab/drawings.py     # shop drawings
python3 fab/render_views.py --samples "${SAMPLES:-96}"   # exploded and section views (system Python with bpy)
