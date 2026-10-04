#!/usr/bin/env bash
# Installs everything the repo's tools need, starting from a bare container, and checks it.
# Idempotent: when everything is already there it finishes in a few seconds.
#
#   studio/setup.sh            install what is missing, then a quick import check
#   studio/setup.sh --doctor   the same, then studio/doctor.py (launches Chromium and Blender; about 20 s)
#
# What it installs, and why it is split:
#   render/node_modules   three.js and playwright-core for the real-time renderer (Chromium itself comes with the
#                         Claude Code cloud environment at /opt/pw-browsers; locally, point CHROMIUM at any Chromium)
#   bpy (system Python)   Blender as a Python module, for every path-traced render. bpy 5.0 needs numpy 1.
#   .venv-fab/            build123d, ezdxf, fonttools, uharfbuzz, matplotlib, scipy for CAD, cut files, drawings,
#                         acoustics and crossovers. build123d needs numpy 2, hence its own venv.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
log() { echo "[setup] $*" >&2; }
PIP=(python3 -m pip install --quiet --disable-pip-version-check)

# 1. Node dependencies for render/.
if [ ! -d render/node_modules/three ] || [ ! -d render/node_modules/playwright-core ]; then
  log "npm install in render/"
  (cd render && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-audit --no-fund --loglevel=error)
fi

# 2. Blender's bpy on the system Python, with numpy 1.
if ! python3 -c "import bpy" >/dev/null 2>&1; then
  log "pip install bpy 5.0.1 (about 350 MB, once)"
  "${PIP[@]}" "bpy==5.0.1" "numpy>=1.26,<2.0"
fi
if ! python3 -c "import numpy, sys; sys.exit(0 if numpy.__version__.startswith('1.') else 1)" >/dev/null 2>&1; then
  log "restoring numpy 1 for bpy (something installed numpy 2 on the system Python)"
  "${PIP[@]}" "numpy>=1.26,<2.0"
fi

# 3. The CAD venv.
VENV="$ROOT/.venv-fab"
if [ ! -x "$VENV/bin/python" ]; then
  log "creating .venv-fab"
  python3 -m venv "$VENV"
fi
if ! "$VENV/bin/python" -c "import build123d, ezdxf, fontTools, uharfbuzz, matplotlib, scipy" >/dev/null 2>&1; then
  log "pip install fab/requirements.txt into .venv-fab (build123d and OpenCascade, once)"
  "$VENV/bin/python" -m pip install --quiet --disable-pip-version-check -r fab/requirements.txt
fi

# 4. Chromium for the real-time renderer.
CHROMIUM="${CHROMIUM:-/opt/pw-browsers/chromium}"
if [ ! -x "$CHROMIUM" ]; then
  log "warning: no Chromium at $CHROMIUM; the real-time renderer (render/) needs one. Set CHROMIUM to a Chromium binary."
fi

# 5. Fonts the renders and the metal files are set in.
for f in Archivo-Regular.woff Archivo-Bold.woff ArchivoBlack-Regular.woff; do
  [ -f "render/fonts/$f" ] || log "warning: render/fonts/$f is missing"
done

# Quick check (imports only).
python3 -c "import bpy, numpy; assert numpy.__version__.startswith('1.')" && log "bpy ok"
"$VENV/bin/python" -c "import build123d, ezdxf, uharfbuzz" && log "CAD venv ok ($VENV)"
node -e "require('$ROOT/render/node_modules/three/package.json')" && log "render/ node modules ok"

if [ "${1:-}" = "--doctor" ]; then
  python3 studio/doctor.py
fi
log "done"
