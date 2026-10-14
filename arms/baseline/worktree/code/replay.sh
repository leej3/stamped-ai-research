#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python code/analyze_rt.py
python code/verify_rt.py
