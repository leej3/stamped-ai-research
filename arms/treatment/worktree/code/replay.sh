#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
pixi run --frozen --no-install python code/analyze_rt.py
pixi run --frozen --no-install python code/verify_replay.py
