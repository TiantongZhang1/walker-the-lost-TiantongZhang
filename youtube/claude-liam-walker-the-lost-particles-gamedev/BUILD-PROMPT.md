# BUILD-PROMPT.md — how this reel is rebuilt from the repository

Everything below runs from the repository root,
`walker-the-lost-TiantongZhang`, against game-source revision **`31fb5a7`** —
the revision every code panel, hash and capture in the film was taken from.
Commits after it add film documentation only; `git diff 31fb5a7..a6 -- godot/`
is the check that says so.

`$GODOT` is the editor binary. It is not on PATH on the machine this was built
on; `scripts/run-test.sh` resolves it relative to the repository and `GODOT=`
overrides it.

```bash
export GODOT="../Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64.exe"
export ART="../brutalist.art-main"
export REEL="$PWD/youtube/claude-liam-walker-the-lost-particles-gamedev"
```

---

## 0. Start from a clean engine cache

```bash
rm -rf godot/.godot
"$GODOT" --headless --path godot --import
```

Zero import errors is part of the claim, not a precondition.

## 1. The suites that back every number

Always through the wrapper. It is the only thing that fails on a
`SHADER ERROR` or `SCRIPT ERROR` line, which Godot prints while still
exiting 0.

```bash
./scripts/run-test.sh test_hit_burst_config.gd 60        # 80 checks
./scripts/run-test.sh test_hit_burst_state.gd 60         # 22
./scripts/run-test.sh test_dungeon_motes_config.gd 60    # 39
./scripts/run-test.sh test_dungeon_motes_state.gd 60     # 19
./scripts/run-test.sh test_step_dust_config.gd 60        # 63
./scripts/run-test.sh test_step_dust_state.gd 30         # 26, each rate
./scripts/run-test.sh test_step_dust_state.gd 60
./scripts/run-test.sh test_step_dust_state.gd 144
./scripts/run-test.sh test_input_map.gd 60               # 5
```

249 checks, 301 results. Assignment 5's suites still run and still pass and
are not part of this film's ledger; `COMPONENTS.md` says why.

## 2. The cost figures, on an idle machine

```bash
./scripts/run-test.sh cost_effects.gd 60 300 > evidence/a6/cost-effects-run1.txt 2>&1
./scripts/run-test.sh cost_effects.gd 60 300 > evidence/a6/cost-effects-run2.txt 2>&1
```

**Both runs, and nothing else running.** The first attempt at this was taken
while a 4K Movie Maker render was using the CPU and read Effect A at +26.5 µs
against +17.8 on an idle machine. It was discarded and is not in the
repository. Two runs are kept because the difference between them is the
finding: the ordering holds and the microseconds do not.

## 2a. The GPU figures — a real window, not headless

```bash
RUN_TAG=-run1 ./scripts/run-gpu-cost.sh
RUN_TAG=-run2 ./scripts/run-gpu-cost.sh
```

**A 1280 x 720 window opens for about ten seconds per run.** This is the one
measurement in the assignment that cannot be taken headless, and
`scripts/run-test.sh` is therefore the wrong wrapper for it — it passes
`--headless`, a dummy renderer draws nothing, and every reading would be
`0.000` ms, which is indistinguishable from three effects that cost nothing.
`tests/gpu_cost_effects.gd` checks `DisplayServer.get_name()` and refuses.

It is a separate script rather than a flag on `run-test.sh` because
`CLAUDE.md` requires `git diff --stat scripts/run-test.sh` to print nothing
after an agent session.

**Read the containment line at the bottom of the output before reading any
number above it.** The run measures Effect B twice and checks that "all
three" is not cheaper than B alone. It is cheaper, in every run so far, which
places the per-effect differences below the instrument's floor. The figure
that holds is the whole frame at the ceiling: 0.022 ms against 0.60 ms.

## 3. The three takes — real motion, 4K

```bash
python -I scripts/render_takes.py p r c --out "$REEL/capture" \
    --driver res://tests/capture_particles.gd
python -I scripts/encode_captures.py --frames "$REEL/capture" --reel "$REEL"
```

`render_takes.py` writes a temporary `godot/override.cfg` and removes it
again: Movie Maker fixes its output size from the window size at engine
startup, before `--resolution` and before any script runs, so without the
override the same command silently records 1280 × 720.

**A render is evidence only if it printed `CAPTURE OK`.** Each take asserts
its own outcome — `SOURCES.md` §1 lists what each one asserts.

**You can use the machine while this runs.** The driver re-presses its held
keys every frame, because Godot releases every pressed key when the window
loses focus and a 4K take needs a real window for minutes. A take written the
obvious way came back with 1 burst and 9 puffs instead of 4 and 25 when the
author switched applications, and nothing but the take's own assertions
noticed.

**Per-driver `--quit-after`.** Takes p and c share their letters with
Assignment 1 and 2's takes, whose bounds are 600 and 900 frames; this driver's
are 638 and 1216. A bound that is too low does not fail loudly — the engine
quits mid-take, the frames already written look normal, and the only symptom
is a missing `CAPTURE OK`. `render_takes.py` now keeps a separate table for
this driver.

## 4. The evidence cards

```bash
python -X utf8 scripts/compose_particles_evidence.py
```

Writes `media/{B05,B07,B09,B11B}.png` and the measurement reports in
`evidence/a6/`. Every figure on those cards is computed here from the
committed capture frames; nothing is typed in. Delete a frame and the script
stops rather than drawing a stale number.

## 5. The beat sheet, the audio, the clips

```bash
python -X utf8 scripts/build_particles_beat_sheet.py        # first pass
cd "$ART" && PYTHONUTF8=1 python -X utf8 \
    runtime/scripts/generate_audio_kokoro.py "$REEL"
cd - && python -X utf8 scripts/build_particles_beat_sheet.py  # second pass
python scripts/build_media_clips.py "$REEL"
python -X utf8 scripts/frame_particles_footage.py
```

**Run the beat sheet builder twice, and not a third time.** Its cue times and
`show` markers are fractions of a beat, not absolute seconds, and the second
pass turns them into seconds against the measured narration. It also fits
every footage window to the measured length, clamped to the take, and prints
what it did.

**A third pass, after `build_media_clips.py`, corrupts a duration by one
hundredth of a second.** `build_media_clips.py` refines `actual_duration_s`
to the real file's length — B08's is 38.415 — and the builder then rounds
that to 38.41, where the second pass had written 38.42 from the audio
generator's own rounding. Nothing errors. The only symptom is that the beat
loses its Remotion stamp, because its props no longer match, and the batch
would silently re-render a beat that did not change. Caught on 2026-11-08 by
diffing the stamps after a rebuild; B08 was restored from the committed sheet
rather than re-rendered, because nothing about it had changed.

**To edit one beat after the batch, edit the sheet in place** — see §7.

**There is no timing step, and `scripts/finalise_beat_timing.py` must not be
run.** It and `scripts/fit_beat_panels.py` are carried-over scripts that
`chdir` into **walker-ninja-TiantongZhang**; on 2026-10-28 running one of them
rewrote that repository's beat sheet. Both now refuse to run and `TOOLCHAIN.md`
marks them **Reshape**.

`-I` is wrong for the toolkit's scripts: it implies `-E`, which drops
`PYTHONUTF8`. Use `-X utf8` and no `-I`.

## 6. The ledger and the official check — before rendering and again at handoff

```bash
python -X utf8 scripts/build_particles_ledger.py
cd "$ART"
PYTHONUTF8=1 bash art godot-gamedev --check "$REEL" --game "<abs>/godot"
```

Expected:

```json
{"status": "PASS", "source_files": 67, "exclusions": 40, "components": 6,
 "exact_excerpts": 6, "teaching_contract": "code-then-result-v1",
 "code_result_pairs": 6}
```

It was 66 until 2026-11-08, when `tests/gpu_cost_effects.gd` was added to the
`evidence-harness` component. **A file added under `godot/` that is in no
component and in no exclusion stops the ledger builder** — it prints
`unassociated files:` and writes nothing, which is the behaviour you want:
the alternative is a checker failure at handoff with no hint about which file
caused it.

It checks hashes, inventory, source lines and associations. It does not check
whether a mechanism was explained clearly or whether an exclusion is honest —
those are `FACTCHECK.md`'s and `COMPONENTS.md`'s job.

`godot/override.cfg` must not exist when the ledger is built. The builder
stops if it does, because inventorying it would put a file in the film's
evidence that no clone has.

## 7. Pilot, batch, master

```bash
cd "$ART"
PYTHONUTF8=1 python -X utf8 runtime/scripts/remotion_scenes.py "$REEL" --only B02 --force
PYTHONUTF8=1 python -X utf8 runtime/scripts/remotion_scenes.py "$REEL"
bash art final "$REEL" --height 2160 --fps 30 --out "$REEL/exports/landscape"
```

The flag is `--only <BID>`, not `--beat`. Without `--force`,
`remotion_scenes.py` skips any beat that already has a `media/<BID>.mp4`,
whatever changed in its props — so after editing a beat, force that one beat
by name.

**Do not re-run the beat sheet builder after the Remotion batch.** The batch
stamps `shot.remotion.rendered.at` into the sheet and `compile.py:485` refuses
a beat that has a pattern and no stamp. Editing one beat after the batch means
editing the sheet in place and re-rendering that beat with `--force`.

**Render one new component as a pilot and extract a frame and look at it
before batching.** This is not ceremony. The panel capacities below are all
measured off rendered frames, none of them is enforced by a schema, and
overflowing any of them clips silently.

| Surface | Holds | What overflowing looks like |
|---|---|---|
| `GodotDevWorkbench` code panel | about **13 wrapped rows** at `codeFontSize` 23–26 — count ROWS, not source lines | the excerpt stops mid-file and a cue points at a line nobody can see |
| `GodotDevWorkbench` notes column | **2** cards, about 160 characters of value in total | the second card is cut off mid-sentence |
| `ClaudeVerdictArtifact` | about **8** `artifactLines` | the card grows past 1080 and clips top and bottom |
| `BrutalistHesitantWriter` context card | **2** rows of `detail` at about 37 characters | the third row sets below the card's border |

Do not shrink `codeFontSize` below 23 to fit more in. Remotion accepts a
smaller value without complaint and the panel clips anyway.

## 8. What must be true at handoff

- `./art godot-gamedev --check` passes again, after the render.
- `git diff --stat godot/shaders/ scripts/run-test.sh` prints nothing for
  every agent commit.
- `git diff 31fb5a7..a6 -- godot/` prints nothing.
- `python tools/check_claude_refs.py` reports 0 problems.
- The master plays: code at reading size, the highlights land on the lines the
  cues name, take r is labelled SCRIPTED in its own title card, the two mote
  beats are uncropped, and the outro is the locked card with no narration
  over it.
- `FACTCHECK.md` still matches what the narration says, including the claims
  marked REASONING rather than MEASURED and the one correction it records.
- **The checker passes in a FRESH CLONE of the tag, not only here.** That is
  a different check and it has failed twice in this repository's history, both
  times on line endings that `git status` and `git diff` cannot show you:

  ```bash
  git clone --branch a6 --single-branch <repo> /tmp/verify-a6
  cd /tmp/verify-a6 && "$GODOT" --headless --path godot --import
  cd "$ART" && PYTHONUTF8=1 bash art godot-gamedev --check       /tmp/verify-a6/youtube/claude-liam-walker-the-lost-particles-gamedev       --game /tmp/verify-a6/godot
  ```

  Before any tag, re-measure every file in `.gitattributes`'s per-file
  `eol=crlf` list against its bytes on disk. An attribute that was right when
  it was written goes stale the moment a script rewrites that file.

## Not done, and not implied

No Short, no vertical companion, no publication, no paid call, and no change
to the game to make it film better.
