# BUILD-PROMPT.md — how this reel is rebuilt from the repository

Everything below runs from the repository root,
`walker-the-lost-TiantongZhang`, against source revision `0b45339`.

`$GODOT` is the editor binary. It is not on PATH on the machine this was
built on; `scripts/run-test.sh` resolves it relative to the repository and
`GODOT=` overrides it.

```bash
export GODOT="../Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64.exe"
export ART="../brutalist.art-main"
```

---

## 0. Start from a clean engine cache

```bash
rm -rf godot/.godot
"$GODOT" --headless --path godot --import
```

Zero import errors is part of the claim, not a precondition.

## 1. The suites that back every number

```bash
./scripts/run-test.sh test_materials.gd 60             # 48 checks
./scripts/run-test.sh test_trap_shader_driver.gd 30    # 24, each rate
./scripts/run-test.sh test_trap_shader_driver.gd 60
./scripts/run-test.sh test_trap_shader_driver.gd 144
./scripts/run-test.sh test_trap_warning.gd 30          # 22, each rate
./scripts/run-test.sh test_trap_warning.gd 60
./scripts/run-test.sh test_trap_warning.gd 144
./scripts/run-test.sh test_input_map.gd 60             # 5
./scripts/run-test.sh check_assets_3d.gd 60            # ALL PASSED
```

Always through the wrapper. It is the only thing that fails on a
`SHADER ERROR` line, which Godot prints while still exiting 0.

## 2. The take — real motion, 4K

```bash
python -I scripts/render_takes.py w \
    --out youtube/claude-liam-walker-the-lost-gamedev/capture \
    --driver res://tests/capture_shader.gd
python -I scripts/encode_captures.py \
    --frames youtube/claude-liam-walker-the-lost-gamedev/capture \
    --reel   youtube/claude-liam-walker-the-lost-gamedev
```

`render_takes.py` writes a temporary `godot/override.cfg` and removes it
again: Movie Maker fixes its output size from the window size at engine
startup, before `--resolution` and before any script runs, so without the
override the same command silently records 1280 × 720.

The render is evidence only if it printed `CAPTURE OK`. The driver asserts
three traps fired, at least one hit landed, and no frame had more than one
trap lit.

## 3. The stills, if they need retaking

Both need a **real window**; they refuse to run headless, where a dummy
renderer would save black frames that look like measurements.

```bash
"$GODOT" --path godot --script res://tools/capture_hint.gd        # B07
"$GODOT" --path godot --script res://tools/capture_materials.gd   # B09
```

B11's still is a capture of deliberately broken source: delete
`source_color` from `hint_bands.gdshader:4`, re-run `capture_hint.gd`, copy
the result, then **restore the line**. `git diff HEAD -- godot/shaders/`
must print nothing afterwards. That edit is the author's; no agent touches a
`.gdshader`.

## 4. The beat sheet and the ledger

```bash
python -I scripts/build_lost_beat_sheet.py
python -I scripts/build_lost_ledger.py
```

Both read the repository rather than a copy. Every code panel's text is
re-read from its file and compared with what the beat displays; the ledger
refuses to write if they differ, and the excerpt line ranges are derived
from the panel text rather than typed.

## 5. The official check — before rendering and again at handoff

```bash
cd "$ART"
PYTHONUTF8=1 ./art godot-gamedev --check <abs reel> --game <abs godot dir>
```

`PYTHONUTF8=1` is needed on a non-UTF-8 locale: the checker reads source with
the platform encoding and `dungeon_surface.gdshader` carries the author's
comments in Chinese. Expected:

```json
{"status": "PASS", "source_files": 44, "exclusions": 14, "components": 7,
 "exact_excerpts": 5, "teaching_contract": "code-then-result-v1",
 "code_result_pairs": 5}
```

It checks hashes, inventory, source lines and associations. It does not check
whether a mechanism was explained clearly or whether an exclusion is honest.
Those are `FACTCHECK.md`'s and `COMPONENTS.md`'s job.

## 6. Narration, pilot, batch, master

```bash
cd "$ART"
python -I runtime/scripts/generate_audio_kokoro.py <reel>     # am_onyx, local
python -I scripts/finalise_beat_timing.py <reel>              # measured, not estimated
python -I runtime/scripts/remotion_scenes.py <reel> --beat B02   # pilot, inspect it
python -I runtime/scripts/remotion_scenes.py <reel>              # the rest
./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape
```

Render one new component as a pilot and look at it before batching. Preserve
every approval, audio and QC gate.

## 7. What must be true at handoff

- `./art godot-gamedev --check` passes again, after the render.
- `git diff --stat godot/shaders/` prints nothing for every agent commit.
- The master plays: code at reading size, the highlights land on the lines
  the cues name, the two footage beats show three traps with only one lit,
  and the outro is the locked card with no narration over it.
- `FACTCHECK.md` still matches what the narration says, including the four
  claims marked as reasoning rather than measurement.

## Not done, and not implied

No Short, no vertical companion, no publication, no paid call, and no change
to the game to make it film better.
