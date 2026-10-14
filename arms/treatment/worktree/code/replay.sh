#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -x .pixi/envs/default/bin/python ]; then
  exec .pixi/envs/default/bin/python -I -S code/analyze.py "$@"
fi
exec python3 -I -S code/analyze.py "$@"
