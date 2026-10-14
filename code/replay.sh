#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
pixi run --frozen python code/analyze_rt.py
pixi run --frozen python code/verify_rt.py
snapper --config /dev/null --max-width 80 --in-place reports/report.md
