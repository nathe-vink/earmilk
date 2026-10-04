#!/bin/bash
# Claude Code cloud sessions start from a fresh container: install the renderers and the CAD tools before work starts.
# Synchronous on purpose: renders and CAD scripts must not run before their tools exist. See studio/setup.sh.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"
studio/setup.sh

# Tools find each other through these.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export FAB_PY=\"$PWD/.venv-fab/bin/python\""
    echo "export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1"
  } >> "$CLAUDE_ENV_FILE"
fi
