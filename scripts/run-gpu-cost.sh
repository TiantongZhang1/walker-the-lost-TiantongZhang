#!/usr/bin/env bash
# scripts/run-gpu-cost.sh [timeout-seconds]
#
# The one measurement in this assignment that CANNOT be taken headless.
#
# `scripts/run-test.sh` passes --headless, which is right for every other
# test here and wrong for this one: a headless run uses a dummy renderer, so
# `viewport_get_measured_render_time_gpu()` would return 0.000 ms for every
# condition and the report would look like three effects that cost nothing.
# `tests/gpu_cost_effects.gd` checks `DisplayServer.get_name()` and refuses,
# so the mistake fails loudly rather than producing evidence.
#
# This is a SEPARATE script rather than a flag on run-test.sh deliberately.
# `CLAUDE.md` requires `git diff --stat scripts/run-test.sh` to print nothing
# after an agent session, and a measurement that needed the wrapper edited
# would be a measurement nobody could check that against.
#
# A REAL 1280 x 720 WINDOW OPENS for about ten seconds and then closes by
# itself. Leave it alone while it runs: the readings are GPU timestamps, and
# anything else drawing on the same card lands in them. (The script re-presses
# its held key every frame, so if you do click away the walking conditions
# still walk -- the same focus-loss defence the film's capture driver carries,
# for the same reason.)
#
# An exit status of 124 means it hung; 1 means a condition came in over its
# budget, which is a result and not a crash -- read the table.
set -o pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${GODOT:=$here/../Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64.exe}"

if [ ! -x "$GODOT" ] && [ ! -f "$GODOT" ]; then
  echo "Could not find Godot at: $GODOT" >&2
  echo "Set GODOT=/path/to/godot, or keep this repository beside the Godot download." >&2
  exit 127
fi

cd "$here" || exit 1
mkdir -p logs evidence/a6

log="logs/gpu_cost_effects.log"

# --fixed-fps pins the delta so a duration in seconds means the same thing it
# means in the headless sibling. It does NOT throttle: the frames are drawn as
# fast as the card will draw them, which is what keeps the clocks up and the
# per-frame readings comparable. No --rendering-driver, ever: CLAUDE.md.
timeout "${1:-300}" "$GODOT" --fixed-fps 60 --path godot \
  --script res://tests/gpu_cost_effects.gd 2>&1 | tee "$log"
status=$?

if grep -qE "SHADER ERROR|SCRIPT ERROR" "$log"; then status=1; fi

# Two runs are kept, as the headless cost script keeps two, because the
# difference between them is part of the finding: RUN_TAG=-run1, -run2.
out="evidence/a6/gpu-cost-effects${RUN_TAG:-}.txt"
cp "$log" "$out"
echo "report: $out"
exit $status
