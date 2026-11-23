# CAPTURE.md — how the footage was made, and what it is not

**Game source:** `walker-the-lost-TiantongZhang`, git revision **`5042a6b`**,
working tree clean under `godot/`.

**`build_id`** (the content hash every capture carries in `coverage.json`):

```
11af9145937e56f29c393d2120c75f4c13d3f916dfe1a3d044fab1e12f5c1cb1
```

**Hash method.** `sha256` of each of the 141 files under `godot/`, excluding
`.godot/` (an engine cache) and the generated `.uid` files; `.import`
sidecars are included, because they carry authored import settings. The
`build_id` is `sha256` of that files map serialised as canonical JSON
(`sort_keys=True`, `separators=(',', ':')`, UTF-8).
`scripts/build_walkthrough_snapshot.py` writes it and
`SOURCE-SNAPSHOT.json` holds the whole map.

**Why a content hash and not a commit SHA.** A commit SHA changes when a
document changes. The film's claim is about the *game*, and the assignment
asks for exactly this property: *"verify that the final commit does not
change the demonstrated game source."* A commit that adds film documentation
leaves this id alone.

---

## Engine and settings

| | |
|---|---|
| Engine | Godot **4.7.2.stable.official** `ed1daf0bf`, Forward+ |
| Recorder | Godot **Movie Maker**, `--write-movie` PNG sequence + WAV |
| Resolution | **native 3840 × 2160** |
| Logical canvas | **640 × 360**, nearest-neighbour. The capture is an exact **6×** of it |
| Frame rate | `--fixed-fps 60`, which is this project's physics tick |
| Window override | `scripts/render_takes.py` writes a temporary `godot/override.cfg` and removes it again |

**Movie Maker is offline rendering. It is not evidence of real-time frame
rate** and no claim in this film depends on one.

**The 4K is real, not an upscale.** Movie Maker fixes its output size from
the window size at engine startup — before `--resolution` and before any
script runs — so without the override the same command silently records
1280 × 720. The override is why `3840×2160` appears in the recorder's own
banner line, which is kept in the render log.

**Pixel-art disclosure, as the reference asks for separately.** The game's
intended logical canvas is 640 × 360. What you see is that canvas drawn at
6× with nearest-neighbour filtering by the engine itself — not a recorded
video enlarged afterwards. No frame is rescaled, cropped, retimed,
brightened or composited anywhere in this film's chain.

---

## The driver, and what it may and may not do

`godot/tests/capture_walkthrough.gd`, invoked through
`scripts/render_takes.py`.

**Every take is scripted input through the real input map.** Each key is an
`InputEventKey` with a physical keycode, pushed through
`Input.parse_input_event` and flushed — the same path a player's keyboard
takes. The driver:

- does **not** teleport, set positions, or write velocity;
- does **not** call a state method, `travel()`, or any `AnimationPlayer` API;
- does **not** disable collision, grant invulnerability, or set completion;
- does **not** seek a clip or force a state.

**The one thing it does that a player cannot** is read the player's position
and the clip's playhead in order to decide when to press a key and to write
the log. The skill allows that explicitly. Every value it read is in the
input log, frame by frame, so a reviewer can check every decision it made.

**Held keys are re-pressed every frame.** Godot releases every pressed key
when the window loses focus, and a 4K take needs a real window for minutes.
Assignment 6's `BUILD-PROMPT.md` records a take that came back with a sixth
of the events it should have had because the author switched applications.

**A completed render is not success.** Each take asserts its own outcome and
exits non-zero otherwise; only a `CAPTURE OK` line counts. Merely exhausting
`--quit-after` is not a result, and the per-driver bounds are set well above
the measured tick counts for that reason.

---

## The four takes

| take | frames | length | what it asserts before a frame of it counts |
|---|---|---|---|
| `a` | 1572 | 26.20 s | 4 clips incl. idle/run/rising/falling, ≥3 cycle wraps (18 measured), both facings, **0 swings**, **0 traps crossed** |
| `b` | 976 | 16.27 s | **8 swings from 10 attack presses** — the two missing ones are the two pressed inside a startup — and the window opening 8 times |
| `c` | 1096 | 18.27 s | ≥2 swings, travelling and jumped |
| `d` | 1517 | 25.28 s | ≥3 trap firings (8 measured), health reaching 0, `dead` played |

**Every take also asserts that the floating key is animating** — that it
bobbed more than a pixel and turned more than twenty degrees. It is the one
feature that needs nobody to do anything, so a take that did not check it is
exactly where that silence would hide.

**Take `a` never crosses a trap, deliberately.** Its first cut ran east after
the jump, walked onto the first trap, and cost a point of health — so a take
about the *states* also showed a hit. The hazard is take `d`'s subject and
has it to itself.

**The takes are long on purpose.** The first cut made each one a few seconds
— just the moment a feature happens — and the beats built on them carried
nineteen to thirty-four seconds of frozen final frame apiece. Each take now
runs about as long as the narration laid over it. Repetition is the content:
a cycle has to be seen wrapping several times before anyone can say whether
it wraps cleanly, and the ignored attack has to happen twice before it reads
as a rule rather than a glitch.

---

## Timing and audio

**The real precondition → input → result interval plays at normal simulation
speed, uncut.** No gameplay clip is retimed, centre-cut or speed-changed.
`scripts/build_media_clips.py` pre-trims each beat's clip to its window and
adds a **labelled final-frame hold** for any narration that outruns it:
**81.45 s of action against 17.77 s of hold**, and no single hold exceeds
5 seconds or the action it follows.

**No `pantry` intake was used on any capture.**

**Audio.** Liam's narration (Kokoro `am_onyx`, generated locally, $0.00) is
the primary and only audio over the body. The engine's own audio is carried
in each `capture/take-*.mp4` so the capture stays faithful to the run, and
it is **muted in the compiled film** — this game's audio is a music loop and
four short effects, and under narration it added nothing but a bed. That is
a decision, recorded here rather than left to be inferred. All of it stops
before the locked outro, which carries only the stock jingle.

---

## What this capture method cannot establish

- **That any of it reads.** A capture shows what the engine drew; whether a
  braced stance in mid-air looks right is a human judgement and
  `CHANGE-BRIEF.md` §9 keeps three of them open.
- **Real-time performance.** Movie Maker renders offline.
- **That the inventory is complete.** `coverage.json` lists what was found by
  reading the source and playing it. A feature nobody thought of is not
  listed and no check can say so.
