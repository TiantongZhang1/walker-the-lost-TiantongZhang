#!/usr/bin/env bash
# scripts/run-test.sh <test-file.gd> <fps|realtime> [timeout-seconds]
#
# Assignment 6's wrapper, committed before Step 1. It does everything
# Assignment 5's did:
#
#   1. wraps the test in `timeout`, because a script error before quit()
#      leaves headless Godot running forever;
#   2. pins the frame rate with --fixed-fps, so a duration measured in
#      seconds can be compared across 30, 60 and 144 fps;
#   3. keeps a log per test per mode;
#   4. fails on SHADER ERROR and SCRIPT ERROR lines, because Godot exits 0
#      having printed them. That rule has already earned its keep here: a
#      GDScript type-inference error killed the whole audio node on
#      2026-11-05 while the suite went on reporting 22 checks, 0 failures.
#
# and adds the two Assignment 6 asks for:
#
#   5. a `realtime` mode that runs WITHOUT --fixed-fps, for tests that wait
#      on audio. Timers follow game time and fire correctly at a fixed rate,
#      but audio playback runs on a real-time clock;
#   6. an optional third argument that sets the timeout, for the cost
#      script — `./scripts/run-test.sh cost_effects.gd 60 300`.
#
# An exit status of 124 means the test hung.
#
# TWO DEVIATIONS FROM THE ASSIGNMENT'S LISTING, both deliberate:
#
#   * The assignment's version calls `godot`. It is not on PATH on this
#     machine, and a wrapper that cannot find the engine runs nothing while
#     looking like it ran — which is the failure mode the whole course keeps
#     warning about. GODOT is resolved relative to the repository and may be
#     overridden:  GODOT=/path/to/godot ./scripts/run-test.sh test_foo.gd 60
#   * TEST_FPS is exported, because --fixed-fps is consumed by the engine
#     and never reaches OS.get_cmdline_args(). The trap suite cross-checks
#     it against the engine's own modal delta rather than believing either
#     on its own. CHANGE-BRIEF.md revision 5.0.3 records why.
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
  echo "usage: scripts/run-test.sh <test-file.gd> <fps|realtime> [timeout-seconds]" >&2
  exit 2
fi

cd "$here" || exit 1
mkdir -p logs

if [ "$2" = "realtime" ]; then
  fps_args=(); tag="realtime"
else
  fps_args=(--fixed-fps "$2"); tag="${2}fps"
fi

log="logs/$(basename "$1" .gd)_${tag}.log"
export TEST_FPS="$2"

timeout "${3:-120}" "$GODOT" --headless "${fps_args[@]}" --path godot \
  --script "res://tests/$1" 2>&1 | tee "$log"
status=$?

if grep -qE "SHADER ERROR|SCRIPT ERROR" "$log"; then status=1; fi
exit $status
