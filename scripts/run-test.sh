#!/usr/bin/env bash
# scripts/run-test.sh <test-file.gd> <fps>
#
# The wrapper Assignment 5 requires, committed before Step 1. It does four
# things, all of them for a reason:
#
#   1. wraps the test in `timeout`, because a script error before quit()
#      leaves headless Godot running forever;
#   2. pins the frame rate with --fixed-fps, so a duration measured in
#      seconds can be compared across 30, 60 and 144 fps;
#   3. keeps a log per test per frame rate;
#   4. fails on SHADER ERROR and SCRIPT ERROR lines, because Godot exits 0
#      having printed them.
#
# An exit status of 124 means the test hung.
#
# ADAPTED FOR THIS MACHINE (the assignment's version assumes `godot` is on
# PATH; here it is not). GODOT may be overridden from the environment:
#
#   GODOT=/path/to/godot ./scripts/run-test.sh test_foo.gd 60
#
set -o pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${GODOT:=$here/../Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64.exe}"

if [ ! -x "$GODOT" ] && [ ! -f "$GODOT" ]; then
  echo "Could not find Godot at: $GODOT" >&2
  echo "Set GODOT=/path/to/godot, or keep this repository beside the Godot download." >&2
  exit 127
fi

if [ $# -lt 2 ]; then
  echo "usage: scripts/run-test.sh <test-file.gd> <fps>" >&2
  exit 2
fi

cd "$here" || exit 1
mkdir -p logs
log="logs/$(basename "$1" .gd)_${2}fps.log"

timeout 120 "$GODOT" --headless --path godot --script "res://tests/$1" --fixed-fps "$2" 2>&1 | tee "$log"
status=$?

if grep -qE "SHADER ERROR|SCRIPT ERROR" "$log"; then status=1; fi
exit $status
