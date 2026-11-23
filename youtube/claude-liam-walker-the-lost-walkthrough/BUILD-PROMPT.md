# BUILD-PROMPT.md — how this reel is rebuilt from the repository

Everything runs from the repository root, `walker-the-lost-TiantongZhang`,
against game-source revision **`5042a6b`** — the revision every capture in
this film was recorded at, and the one `SOURCE-SNAPSHOT.json`'s `build_id`
hashes. `git diff 5042a6b..a8 -- godot/` is the check that nothing under
`godot/` moved afterwards.

```bash
export GODOT="../Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64.exe"
export ART="../brutalist.art-main"
export REEL="$PWD/youtube/claude-liam-walker-the-lost-walkthrough"
```

---

## 0. Clean cache, and the suites

```bash
rm -rf godot/.godot && "$GODOT" --headless --path godot --import
./scripts/run-test.sh test_player_clips.gd 60      # 82
./scripts/run-test.sh test_swing_clip.gd 60        # 79
./scripts/run-test.sh test_player_states.gd 60     # 26
./scripts/run-test.sh test_swing_edges.gd 60       # 60
./scripts/run-test.sh pin_player_states.gd 60      # 15  (12 INVARIANT, 3 TIMING)
./scripts/run-test.sh test_input_map.gd 60         # 13
./scripts/run-test.sh measure_clocks.gd 60         # 5
./scripts/run-test.sh test_pickup_clip.gd 60       # 20
./scripts/run-test.sh test_step_dust_state.gd 30   # 26, each rate
./scripts/run-test.sh test_step_dust_state.gd 60
./scripts/run-test.sh test_step_dust_state.gd 144
python -I tools/check_claude_refs.py               # 61 assertions, 0 problems
python -I tools/check_sword_reach.py               # 0 mismatches
python -I tools/check_reel_tracked.py              # OK for every reel
```

300 checks.

## 1. The four takes, and the snapshot

```bash
python -I scripts/render_takes.py a b c d --out "$REEL/capture" \
    --driver res://tests/capture_walkthrough.gd
python -X utf8 scripts/build_walkthrough_snapshot.py
python -I scripts/encode_captures.py --frames "$REEL/capture" --reel "$REEL"
```

`render_takes.py` writes a temporary `godot/override.cfg` for the 4K window
and removes it again. **A render is evidence only if it printed
`CAPTURE OK`** — see `CAPTURE.md` for what each take asserts.

**The snapshot must be built from a clean `godot/`.** It prints `DIRTY` and
warns if not; a `build_id` taken over uncommitted changes describes a tree
nobody else has.

> **The takes are long on purpose.** The first cut made each one a few
> seconds and the beats carried nineteen to thirty-four seconds of frozen
> frame. If you shorten them, the builder in §2 will tell you.

## 2. The beat sheet, the coverage, the audio, the clips

```bash
python -X utf8 scripts/build_walkthrough_reel.py          # first pass
cd "$ART" && PYTHONUTF8=1 python -X utf8 \
    runtime/scripts/generate_audio_kokoro.py "$REEL"
cd - && python -X utf8 scripts/build_walkthrough_reel.py  # second pass
python -X utf8 scripts/compose_walkthrough_card.py        # media/B08.png
python scripts/build_media_clips.py "$REEL"
python -X utf8 scripts/frame_walkthrough_footage.py
```

**`build_walkthrough_reel.py` writes `beat_sheet.json` AND `coverage.json`
from one table**, so a feature cannot name a beat that does not play its
moment. It refuses to write if one does.

**Run it twice, not three times.** The cue times are fractions of a beat
until the second pass turns them into seconds against the measured
narration. `scripts/finalise_beat_timing.py` and `scripts/fit_beat_panels.py`
must **not** be run at all — both `chdir` into `walker-ninja-TiantongZhang`.

**Watch the hold column.** Every gameplay beat prints its action, its
narration and its hold, and flags any hold over five seconds or longer than
the action it follows. **If a beat is flagged, cut the narration** — do not
widen the window to cover it. The window is the action and the action is the
evidence.

> That rule took three shapes before it was right: *narration ≤ 1.15 ×
> action* (wrong shape — 1.15× of a long beat is a long still); *…and ≤ 30 %
> of the action* (flagged 2.8-second holds); then the one above.

**`frame_walkthrough_footage.py` is not optional.** Without it the compile is
refused — see §4.

## 3. The skill's own check

```bash
cd "$ART"
PYTHONUTF8=1 bash art godot-waikthrough --check "$REEL"
```

Expected:

```json
{"status": "PASS", "game": "walker-the-lost-TiantongZhang",
 "implemented_features": 16, "planned_features": 5,
 "evidence_intervals": 16}
```

It validates hashes, dimensions, time ranges, input-log presence and beat
references. **It cannot judge whether the inventory is complete, whether a
window contains what its observation says, or whether a `planned` feature is
really unbuilt.** Those are `_qc/REPORT.md`, `COMPONENTS`-equivalent prose in
`CAPTURE.md`, and `FACTCHECK.md`.

## 4. Render, and the gate that refused twice

```bash
cd "$ART"
PYTHONUTF8=1 python -X utf8 runtime/scripts/remotion_scenes.py "$REEL"
bash art final "$REEL" --height 2160 --fps 30 --out "$REEL/exports/landscape"
```

**Gate V refused the first compile: 14 BLOCKER, 13 MAJOR, every one on the
gameplay.** Both reasons were true of the footage rather than faults in it —
full-bleed gameplay crosses the title-safe edge by definition, and this room
is `#16242B` against `#17141B`, a channel difference of 16 against the gate's
threshold of 28. §2's framing step is the fix and it is why that step exists.

**It then refused a second time, on the LOCKED OUTRO**, for an edge-bleed on
the right. The outro card is not mine to change — `OUTRO-LOCK.md` fixes its
layout, mascot and handle — but the **episode title is**, and
`TheLostWalkthrough_TiantongZhang` was two characters too long for the
title-safe box. It is `TheLostPlayed_TiantongZhang` now.

**Then LOOK at `_qc/contact_sheet.png`.** The gate passing is not the check.
The third framing decision in this film came from looking at that sheet and
noticing the character was four per cent of the frame height in a film about
its legs.

## 5. What must be true at handoff

- `bash art godot-waikthrough --check "$REEL"` passes **after** the render.
- `_qc/REPORT.md` reports **0 BLOCKER, 0 MAJOR**.
- `git diff 5042a6b..a8 -- godot/` prints nothing.
- `git diff --stat godot/shaders/` prints nothing for every agent commit.
- `python -I tools/check_reel_tracked.py` reports OK — it reads every reel's
  evidence file **and** beat sheet and asks git whether each media path is
  actually tracked. Three times in this repository a file the evidence needed
  was silently `.gitignore`d, and a clean `git status` cannot tell you.
- The checker passes **in a fresh clone of the tag**, not only here, and
  **every suite is re-run there with the time step pinned**:

  ```bash
  cd /tmp/verify-a8
  for t in test_player_clips test_swing_clip test_player_states \
           test_swing_edges pin_player_states test_input_map \
           measure_clocks test_pickup_clip; do
    timeout 180 ./scripts/run-test.sh "$t".gd 60
  done
  ```

  > **If `test_player_clips.gd` reports `FAIL the sheet is loaded`, import
  > again and re-run.** That happened once, in one fresh clone, on
  > 2026-11-22: the first `--import` left `godot/.godot/imported/` without
  > the sheet's entry, the suite failed its first assertion, a second
  > `--import` fixed it, and the suite passed 82/0.
  >
  > **It did not reproduce.** A clean clone imported once gave 56 imported
  > entries and 82/0 on the first try. So this is an observation with a
  > remedy, not a rule — the cause is unknown and naming one would be
  > inventing it. What it does show is why the suite's *first* assertion is
  > that the sheet is loaded: Godot prints import failures while exiting 0.

```bash
git clone --branch a8 --single-branch <repo> /tmp/verify-a8
cd /tmp/verify-a8 && "$GODOT" --headless --path godot --import
cd "$ART" && PYTHONUTF8=1 bash art godot-waikthrough --check \
    /tmp/verify-a8/youtube/claude-liam-walker-the-lost-walkthrough
```

## Not done, and not implied

- **No Short.** A 9:16 cut is a different beat sheet, not this one cropped,
  and the assignment does not ask for one.
- **No upload, no publish, no push.** The master is a file; what happens to
  it is the author's.
- **No performance number.** Movie Maker renders offline.
- **Three HUMAN rows are still open** in `CHANGE-BRIEF.md` §9 and the film's
  verdict names one of them out loud.
