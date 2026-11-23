<!-- GENERATED COPY. The original is
     youtube/claude-liam-walker-the-lost-pitch-gdd/BUILD-PROMPT.md
     Rebuild with: python -X utf8 scripts/assemble_pitch_folder.py
     Do not edit this copy; edit the original. -->

# BUILD-PROMPT.md — how this reel is rebuilt from the repository

Everything below runs from the repository root,
`walker-the-lost-TiantongZhang`. **Assignment 8 changed no game code**, so
there is no game-source revision to pin for this assignment's own work; the
two captures are at **`b33b06c`**, which is Assignment 7's, and
`git diff b33b06c..a8 -- godot/` is the check that says nothing under
`godot/` moved.

```bash
export GODOT="../Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64.exe"
export ART="../brutalist.art-main"
export REEL="$PWD/youtube/claude-liam-walker-the-lost-pitch-gdd"
export BRIEF="$PWD/pitch/PROJECT-BRIEF.md"
```

---

## 0. The prompts

`PROMPTS.md` holds them. The first one is the only one that matters: the brief
was written before the film, the author corrected it, and the film was built
from the corrected brief. **No beat was authored before the brief existed.**

## 1. The document

`pitch/PROJECT-BRIEF.md`. The film walks **the brief**, not
`../the-lost-gdd/GDD.md` — `SOURCES.md` §1 says why, and `gdd-evidence.json`
hashes the brief.

> **The brief's line numbers are load-bearing.** Three scripts read it by
> line: the sheet builder quotes it, the ledger re-reads the same lines and
> compares them with what the beat displays, and the checker compares all
> three. Edit a quoted paragraph and the build stops; it does not draw a
> stale quotation. The ranges live in exactly two dictionaries, both named
> `EXCERPT*` and both in `scripts/`.

## 2. The captures

**Not re-rendered.** `capture/take-c.mp4`, `capture/take-s.mp4` and their
input logs are copied from Assignment 7's reel, where they were produced by:

```bash
python -I scripts/render_takes.py c s m --out <a7 reel>/capture \
    --driver res://tests/capture_animation.gd
python -I scripts/encode_captures.py --frames <a7 reel>/capture --reel <a7 reel>
```

Same game, same revision, same driver. Re-recording would have produced
different frames of identical evidence. **If you do re-record them**, the
cards rebuild themselves: every figure on both is read out of the take's own
log at build time.

## 3. The sheet, the audio, the clips, the framing

```bash
python -X utf8 scripts/build_pitch_beat_sheet.py            # pass 1
cd "$ART" && PYTHONUTF8=1 python -X utf8 \
    runtime/scripts/generate_audio_kokoro.py "$REEL"
cd - && python -X utf8 scripts/build_pitch_beat_sheet.py    # pass 2
python scripts/build_media_clips.py "$REEL"
python -X utf8 scripts/frame_pitch_footage.py
```

**Run the sheet builder twice and not a third time.** Its cue positions are
fractions of a beat; the second pass turns them into seconds against the
measured narration. A third pass after the Remotion batch rewrites a duration
by a hundredth of a second, the beat loses its `shot.remotion.rendered`
stamp, and the compiler refuses it.

**There is no timing step, and `scripts/finalise_beat_timing.py` must not be
run.** It and `scripts/fit_beat_panels.py` `chdir` into
**walker-ninja-TiantongZhang**; on 2026-10-28 running one of them rewrote
that repository's beat sheet. Both refuse to run now and `TOOLCHAIN.md` marks
them **Reshape**.

`-I` is wrong for the toolkit's scripts: it implies `-E`, which drops
`PYTHONUTF8`. Use `-X utf8` and no `-I`.

> **The hold label is an overlaid PNG, not `drawtext`.** The first version of
> `frame_pitch_footage.py` used `drawtext`; this ffmpeg build has no
> fontconfig and the filter **crashed the process with an access violation**
> rather than erroring, so the label would have gone missing silently — on
> exactly the machines where it was most needed.
>
> **And both overlays need `shortest=1`.** The label is an endlessly looped
> still. With the second overlay unbounded, ffmpeg encoded 37 MB of a
> ten-second clip before it was stopped and would not have finished. There is
> a `-t` on the output as well now, because a filter graph that can run
> forever should be stopped in two places.

## 4. The ledger and the official check — before rendering and again at handoff

```bash
python -X utf8 scripts/build_pitch_ledger.py
cd "$ART" && PYTHONUTF8=1 bash art godot-gdd --check "$REEL" --gdd "$BRIEF"
```

Expected:

```
GDD evidence check PASS: {"sections": 9, "excerpts": 7, "evidence_files": 4}
```

The checker verifies the document's hash, that **every** `## ` heading is
covered by a narrated beat or carries a written exclusion, that every excerpt
is an exact line range whose text matches both the document and the beat's
own props, that every BODY beat carries a design status, and that every
evidence file is inside the reel, hashed, and carries a method and a claim.

**It does not check whether anything said is true.** That is `FACTCHECK.md`'s
job, and `GDD-COVERAGE.md` records what each section's beat actually covers.

## 5. Pilot, batch, master

```bash
cd "$ART"
PYTHONUTF8=1 python -X utf8 runtime/scripts/remotion_scenes.py "$REEL" --only B03 --force
PYTHONUTF8=1 python -X utf8 runtime/scripts/remotion_scenes.py "$REEL"
bash art final "$REEL" --height 2160 --fps 30 --out "$REEL/exports/landscape"
```

**Pilot one board and LOOK at a frame before batching.** None of the panel
capacities below is enforced by a schema and overflowing any of them clips
silently. B03 was the pilot here because it carries the longest excerpt and
the longest card texts; `_qc/B03-pilot.png` is that beat, re-extracted from
the shipped render so the committed frame is the one in the film.

### Gate V will refuse this reel without the patch below

```diff
--- a/runtime/remotion/src/scenes/GodotDesignBoard.tsx
+++ b/runtime/remotion/src/scenes/GodotDesignBoard.tsx
-  <div style={{position:'absolute',left:pad,bottom:height*.045+(portrait?45:0),
+  <div style={{position:'absolute',left:pad,bottom:height*.075+(portrait?45:0),
-  <div style={{position:'absolute',right:pad,bottom:height*.04,
+  <div style={{position:'absolute',right:pad,bottom:height*.075,
```

The component draws its source line and its handle **outside the title-safe
inset**, which is 5% with a 0.4%-of-width tolerance: at 3840 x 2160 the
handle's ink lands about seven pixels over. That is **14 BLOCKER
`edge-bleed` defects, one per board frame**, and it is the component rather
than anything in this reel.

There is a declarative escape hatch - `qc.full_bleed: true` on a beat drops
the edge-bleed check - and **it is not used here**. It is documented for
compositions that fill the frame on purpose and this one does not; setting it
would be writing down something false to quiet a gate.

### Two things about B01 that cost an afternoon

- **`charMs` does not reach `BrutalistHesitantWriter`.** It is in the schema,
  it is in the props, `remotion_scenes.py` writes the whole props object to
  `props.json` - and renders at 12 and at 50 are **pixel-identical**. Do not
  try to fix a pacing problem with it.
- **The beat's length is the narration's, and the typing does not hurry to
  fit.** At about 138 ms per character event, a 12.0 s beat holds roughly 70
  characters including the correction's own backspacing. The four-line draft
  was still typing line two at 10.5 s, so **two of its four lines were never
  on screen**. Gate V passed that frame; a human looking at it did not.
  Render this beat and look at its last second, every time its text changes.

| Surface | Holds | What overflowing looks like |
|---|---|---|
| `GodotDesignBoard` excerpt panel | about **9** wrapped lines at the component's own font | the quotation runs under the "Reconstructed reading view" footer |
| `GodotDesignBoard` cards | **4**, hard-capped by the schema; about 2 wrapped lines of `text` each | a fifth card is rejected by zod, not clipped — the render fails loudly |
| `ClaudeVerdictArtifact` | about **8** `artifactLines` | the card grows past 1080 and clips top and bottom |
| `BrutalistHesitantWriter` | **4** short lines of `text` | the fifth sets below the frame |

Without `--force`, `remotion_scenes.py` skips any beat that already has a
`media/<BID>.mp4`, whatever changed in its props. After editing one beat,
force that one beat by name.

> **The excerpt panel shows the brief's Markdown as bytes.** It has to: the
> checker compares the displayed string with the document's lines exactly.
> So the six quoted paragraphs in the brief carry **no `**` emphasis and no
> backticks** — not because the film can strip them, but because the brief
> does not use them there. If you add emphasis to a quoted line, it appears
> on screen as asterisks.

## 6. Assemble the submission folder

```bash
python -X utf8 scripts/assemble_pitch_folder.py
```

Copies the beat sheet, the ledger, `SOURCES.md` and this file into `pitch/`
and writes `pitch/CHECKS-REPORT.md` from live runs. **The copies are
generated, never edited in place** — this repository has gone back for a
sentence that outlived its facts eleven times, and every one of them was a
second copy of something.

## 7. What must be true at handoff

- `./art godot-gdd --check` passes again, after the render.
- `git diff --stat godot/ scripts/run-test.sh` prints nothing for this
  assignment — no game code changed.
- `python -I tools/check_claude_refs.py` reports 0 problems.
- **`python -I tools/check_reel_tracked.py` reports OK for every reel**,
  including this one. It checks the thing a clean `git status` cannot: a file
  that is present, hashed by a ledger, and `.gitignore`d. That has happened
  three times in this repository.
- The master runs **2–4 minutes** and the length in `pitch/README.md` is the
  measured one.
- Every footage beat is labelled PLAYED and **every held frame is labelled on
  screen for the seconds it is held**.
- The outro is the locked card with no narration over it.
