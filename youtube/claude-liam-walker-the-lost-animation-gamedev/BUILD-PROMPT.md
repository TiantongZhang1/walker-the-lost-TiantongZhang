# BUILD-PROMPT.md — how this reel is rebuilt from the repository

Everything below runs from the repository root,
`walker-the-lost-TiantongZhang`, against game-source revision **`b33b06c`** —
the revision every code panel, hash and capture in the film was taken from.
Commits after it add film documentation and film scripts only;
`git diff b33b06c..a7 -- godot/` is the check that says so.

`$GODOT` is the editor binary. It is not on PATH on the machine this was built
on; `scripts/run-test.sh` resolves it relative to the repository and `GODOT=`
overrides it.

```bash
export GODOT="../Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64.exe"
export ART="../brutalist.art-main"
export REEL="$PWD/youtube/claude-liam-walker-the-lost-animation-gamedev"
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
`SHADER ERROR`, `SCRIPT ERROR` or **`Failed loading resource`** line, all of
which Godot prints while still exiting 0.

```bash
./scripts/run-test.sh test_player_clips.gd 60      # 82 checks
./scripts/run-test.sh test_swing_clip.gd 60        # 79
./scripts/run-test.sh test_player_states.gd 60     # 26
./scripts/run-test.sh test_swing_edges.gd 60       # 60
./scripts/run-test.sh pin_player_states.gd 60      # 15
./scripts/run-test.sh test_input_map.gd 60         # 13
./scripts/run-test.sh measure_clocks.gd 60         # 5
./scripts/run-test.sh test_step_dust_state.gd 30   # 26, each rate
./scripts/run-test.sh test_step_dust_state.gd 60
./scripts/run-test.sh test_step_dust_state.gd 144
python -I tools/check_claude_refs.py               # 61 assertions, 0 problems
```

280 checks. Assignments 5 and 6's suites still run and still pass and are not
part of this film's ledger; `COMPONENTS.md` says why.

## 2. The recorded evidence files

```bash
./scripts/run-test.sh measure_clocks.gd 60 > evidence/a7/clocks.txt 2>&1
./scripts/run-test.sh test_swing_edges.gd 60 \
    | grep -E "jump in|IDENTICAL|same frames|airborne|NO new swing|own clock|baseline|checks, " \
    > evidence/a7/swing-edges-e.txt
```

`evidence/a7/mutations.txt` is written by hand from seven runs, each of which
mutates one thing and names the assertion that must fire. **M6 and M7 were run
against the working tree rather than a fresh worktree**, and the file says so:
weaker in one way, stronger in another, because a warm import cache means
neither could exit 1 on "the sheet is loaded" — the exact failure the first
attempt at the M1–M5 re-run had.

## 3. The three takes — real play, 4K

```bash
python -I scripts/render_takes.py c s m --out "$REEL/capture" \
    --driver res://tests/capture_animation.gd
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
loses focus and a 4K take needs a real window for minutes.

**Per-driver `--quit-after`.** This driver's take `c` shares its letter with
Assignment 1's and Assignment 6's, and all three mean different things.
`render_takes.py` keeps a separate table per driver path. A bound that is too
low does not fail loudly — the engine quits mid-take, the frames already
written look normal, and the only symptom is a missing `CAPTURE OK`.

> **`encode_captures.py` used to carry a hard-coded tuple of take letters.**
> On this film's first run it encoded take `c`, printed "no frames" for seven
> letters nobody had asked about, and **silently did not encode `s` or `m`.**
> It discovers takes from the render root now. If you are rebuilding an
> earlier film, nothing changes: each renders into its own reel directory.

> **Run `python -I tools/check_reel_tracked.py` instead of checking by
> hand.** `take-c.mp4` was un-excluded by luck — Assignment 6's take `c`
> shares the letter — and `take-s.mp4` and `take-m.mp4` were not. The file is
> present, `git status` is clean, the ledger hashes it, and a fresh clone of
> the tag can verify nothing. That is the `take-w.mp4` failure of 2026-10-28
> by a new door.
>
> **And then it happened a third time, in this film, to `media/B13.png` and
> `media/B14.png`** — because the hand check above was pointed at the takes
> and nobody thought about the cards. B07 and B09 survived by luck too:
> Assignment 5's film has stills with the same filenames. That is what the
> script is for; it reads every reel's ledger **and** beat sheet and asks git
> about every media path either of them names.

## 4. The evidence cards

```bash
python -X utf8 scripts/compose_animation_evidence.py
```

Writes `media/{B07,B09,B13,B14}.png` and the measurement reports in
`evidence/a7/`. Every figure on those cards is computed here from the
committed resources, the committed take logs and the recorded evidence files;
nothing is typed in. Delete a frame and the script stops rather than drawing a
stale number.

**This step needs the 4K PNG sequences**, which are not committed. Run step 3
first in a fresh clone.

## 5. The beat sheet, the audio, the clips

```bash
python -X utf8 scripts/build_animation_beat_sheet.py        # first pass
cd "$ART" && PYTHONUTF8=1 python -X utf8 \
    runtime/scripts/generate_audio_kokoro.py "$REEL"
cd - && python -X utf8 scripts/build_animation_beat_sheet.py  # second pass
python scripts/build_media_clips.py "$REEL"
python -X utf8 scripts/frame_animation_footage.py
```

**Run the beat sheet builder twice, and not a third time.** Its cue times and
`show` markers are fractions of a beat, not absolute seconds, and the second
pass turns them into seconds against the measured narration. It also fits
every footage window to the measured length, clamped to the take, and prints
what it did.

**A third pass, after `build_media_clips.py`, corrupts a duration by one
hundredth of a second** and the beat silently loses its Remotion stamp, so the
batch will not re-render it and the compiler will refuse it. To edit one beat
after the batch, edit the sheet in place and force that beat by name.

**There is no timing step, and `scripts/finalise_beat_timing.py` must not be
run.** It and `scripts/fit_beat_panels.py` are carried-over scripts that
`chdir` into **walker-ninja-TiantongZhang**; on 2026-10-28 running one of them
rewrote that repository's beat sheet. Both now refuse to run and
`TOOLCHAIN.md` marks them **Reshape**.

`-I` is wrong for the toolkit's scripts: it implies `-E`, which drops
`PYTHONUTF8`. Use `-X utf8` and no `-I`.

**Watch the fit lines the second pass prints.** Every footage beat must say
`fits`. The first build of this sheet printed `HOLD 8.40 s` for B05 — eight
and a half seconds of frozen frame — because the narration outran the take.
The fix is to shorten the narration or move its content into the code beat
before it, never to pad the beat.

## 6. The ledger and the official check — before rendering and again at handoff

```bash
python -X utf8 scripts/build_animation_ledger.py
cd "$ART"
PYTHONUTF8=1 bash art godot-gamedev --check "$REEL" --game "<abs>/godot"
```

Expected:

```json
{"status": "PASS", "source_files": 72, "exclusions": 64, "components": 6,
 "exact_excerpts": 6, "teaching_contract": "code-then-result-v1",
 "code_result_pairs": 6}
```

**A file added under `godot/` that is in no component and in no exclusion
stops the ledger builder.** It prints `unassociated files:` and writes
nothing, which is the behaviour you want: the alternative is a checker failure
at handoff with no hint about which file caused it. This repository is
cumulative, so each new assignment's film has a longer exclusion list than the
last — 40 for Assignment 6, 64 here.

It checks hashes, inventory, source lines and associations. **It does not
check whether a mechanism was explained clearly, whether an exclusion is
honest, or whether a figure in the narration is right.** Those are
`COMPONENTS.md`'s and `FACTCHECK.md`'s job, and `FACTCHECK.md` caught a wrong
one in this film.

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
a beat that has a pattern and no stamp.

**Render one code beat as a pilot and extract a frame and LOOK at it before
batching.** This is not ceremony. The panel capacities below are measured off
rendered frames, none of them is enforced by a schema, and overflowing any of
them clips silently.

| Surface | Holds | What overflowing looks like |
|---|---|---|
| `GodotDevWorkbench` code panel | **exactly 13 wrapped rows** at `codeFontSize` 24 — count ROWS, not source lines | the excerpt stops mid-file and a cue points at a line nobody can see |
| `GodotDevWorkbench` notes column | **2** cards, about 160 characters of value in total | the second card is cut off mid-sentence |
| `ClaudeVerdictArtifact` | about **8** `artifactLines` | the card grows past 1080 and clips top and bottom |
| `BrutalistHesitantWriter` context card | **2** rows of `detail` at about 37 characters | the third row sets below the card's border |

> **This film's pilot clipped.** B02 was cut at `legs.tres` 24–38, fifteen
> rows; thirteen rendered, row fourteen was drawn in half and row fifteen not
> at all — **and the cue at 0.72 pointed at row fourteen.** Both over-long
> panels were re-cut. A7's measurement sharpens A6's "about 13" to exactly 13
> at font 24.

Do not shrink `codeFontSize` below 23 to fit more in. Remotion accepts a
smaller value without complaint and the panel clips anyway.

## 8. What must be true at handoff

- `./art godot-gamedev --check` passes again, after the render.
- `git diff --stat godot/shaders/ scripts/run-test.sh` prints nothing for
  every agent commit.
- `git diff b33b06c..a7 -- godot/` prints nothing.
- `python -I tools/check_claude_refs.py` reports 0 problems and `CLAUDE.md` is
  under 120 lines.
- **`python -I tools/check_reel_tracked.py` reports OK for every reel.** It
  checks the thing a clean `git status` cannot tell you.
- The master plays: code at reading size, the highlights land on the lines the
  cues name, every footage beat is labelled PLAYED, and the outro is the
  locked card with no narration over it.
- `FACTCHECK.md` still matches what the narration says, including the rows
  marked REASONING rather than MEASURED and the one correction it records.
- **The checker passes in a FRESH CLONE of the tag, not only here.** That is a
  different check and it has failed twice in this repository's history, both
  times on line endings that `git status` and `git diff` cannot show you:

  ```bash
  git clone --branch a7 --single-branch <repo> /tmp/verify-a7
  cd /tmp/verify-a7 && "$GODOT" --headless --path godot --import
  cd "$ART" && PYTHONUTF8=1 bash art godot-gamedev --check \
      /tmp/verify-a7/youtube/claude-liam-walker-the-lost-animation-gamedev \
      --game /tmp/verify-a7/godot
  ```

  Before any tag, re-measure every file in `.gitattributes`'s per-file
  `eol=crlf` list against its bytes on disk. An attribute that was right when
  it was written goes stale the moment a script rewrites that file.

## Not done, and not implied

- **No frame cost was measured.** Assignment 6 priced its effects and stated
  what the instrument could not resolve. This assignment did not measure frame
  cost at all, and the film says nothing about it.
- **The hitbox hits nothing.** This room has no enemy. The window is real,
  measured and tested at both tick settings; what it would *do* is a later
  assignment, and `CHANGE-BRIEF.md` §11.3 said so before any of it was built.
- **Three HUMAN rows are open**, and they are listed as open rather than
  covered by the author's general verdict: both clips over the darkest and
  lightest level art, whether a moving swing reads after revision 7.0.9
  changed the answer, and whether a braced stance hanging in mid-air reads.
