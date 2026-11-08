#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root"
if [[ "$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" != "3.13" ]]; then
  echo 'Use a Python 3.13 environment for Pyodide 0.29.4.' >&2
  exit 1
fi
export PYODIDE_XBUILDENV_PATH="${PYODIDE_XBUILDENV_PATH:-$root/.cache/pyodide}"
pyodide xbuildenv install 0.29.4
pyodide xbuildenv install-emscripten
python tools/browser/install-sysroot.py
export RUSTUP_TOOLCHAIN=nightly-2025-02-01
mkdir -p "$root/.cache/wasm-wheels"
pyodide build packages/tuloma --outdir "$root/.cache/wasm-wheels" -C 'maturin.build-args=--locked'
python tools/browser/stage.py "$root/.cache/wasm-wheels"
