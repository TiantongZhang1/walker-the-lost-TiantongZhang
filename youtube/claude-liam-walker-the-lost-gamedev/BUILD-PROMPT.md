# BUILD-PROMPT.md — how this reel is rebuilt from the repository

Everything below runs from the repository root,
`walker-the-lost-TiantongZhang`, against source revision `e8aee89` — the revision every code
panel, hash and capture in the film was taken from.

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
 "exact_excerpts": 6, "teaching_contract": "code-then-result-v1",
 "code_result_pairs": 6}
```

It checks hashes, inventory, source lines and associations. It does not check
whether a mechanism was explained clearly or whether an exclusion is honest.
Those are `FACTCHECK.md`'s and `COMPONENTS.md`'s job.

## 6. Narration, pilot, batch, master

```bash
cd "$ART"
PYTHONUTF8=1 python -X utf8 runtime/scripts/generate_audio_kokoro.py <reel>
PYTHONUTF8=1 python -X utf8 runtime/scripts/remotion_scenes.py <reel> --only B02 --force
PYTHONUTF8=1 python -X utf8 runtime/scripts/remotion_scenes.py <reel>
./art final <reel> --height 2160 --fps 30 --out <reel>/exports/landscape
```

**There is no timing step, and `scripts/finalise_beat_timing.py` must not be
run.** An earlier version of this file told you to, and on 2026-10-28 doing so
rewrote **walker-ninja-TiantongZhang**'s beat sheet: that script was copied
across unreshaped and still `chdir`s into the other repository. It and
`scripts/fit_beat_panels.py` now refuse to run; `TOOLCHAIN.md` marks both
**Reshape**. Nothing is lost by skipping them —
`generate_audio_kokoro.py` writes `actual_duration_s` and `audio_file` back
into the beat sheet itself, and this reel's cue times are authored in
`scripts/build_lost_beat_sheet.py` against that measured narration, so step 4
is rerun after the audio rather than a separate pass editing the sheet in
place.

`-I` is wrong for the toolkit's scripts: it implies `-E`, which drops
`PYTHONUTF8`. Use `-X utf8` and no `-I`.

The flag is `--only <BID>`, not `--beat`. Without `--force`,
`remotion_scenes.py` skips any beat that already has an `media/<BID>.mp4`,
whatever changed in its props — so after editing a beat, force that one beat
by name. Render one new component as a pilot and **extract a frame and look at
it** before batching. The B11A pilot was clipped: eighteen lines were asked for
at font 20 and the panel showed thirteen, so the second half of the comparison
and two of three notes were off-screen, and no automatic check noticed.
Preserve every approval, audio and QC gate.

**Panel capacities, every one measured off a rendered frame.** None of these
is enforced by a schema, and overflowing any of them clips silently.

| Surface | Holds | What overflowing looks like |
|---|---|---|
| `GodotDevWorkbench` code panel | about **13 wrapped rows** at `codeFontSize` 23 — count ROWS, not source lines; a long `uniform` line wraps to two | the excerpt stops mid-file and a cue can point at a line nobody can see |
| `GodotDevWorkbench` notes column | **2** cards, about **8 wrapped rows of value text between them** — roughly 160 characters of value in total, wrapping near 21 characters a row | the second card is cut off mid-sentence |
| `ClaudeVerdictArtifact` | about **8** `artifactLines`; the card is sized from its content with no cap, at ~69 px a line over a ~283 px chrome | the card grows past 1080, clips top and bottom, and covers the handle |
| `BrutalistHesitantWriter` context card | **2** rows of `detail` at about 37 characters each | the third row sets on and below the card's bottom border |

Bring the content down to the panel. Do not shrink `codeFontSize` below 23 to
fit more in — Remotion accepts a smaller value without complaint and the panel
clips anyway, which is how the first B11A lost half its comparison.

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
