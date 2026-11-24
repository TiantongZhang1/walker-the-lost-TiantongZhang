# pitch/ — Assignment 8, Final Project Pitch Film

**Tiantong Zhang** · `zhang.tiant@northeastern.edu` · GitHub `TiantongZhang1`
CSYE 7270, Fall 2026 · assembled 2026-11-24

| | |
|---|---|
| **Working title** | **The Lost: Floor One** |
| **Target role** | **Gameplay programmer** |
| **Runtime (the project's, not the film's)** | Godot **4.7.2.stable.official** `ed1daf0bf`, **Forward+** (Vulkan 1.4.357), Windows 11 desktop export, 640 × 360 logical at 16 px = 1 m. **No web export** — `PROJECT-BRIEF.md` §6 says what that buys and what it costs |
| **Repository** | <https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang> |
| **Git tag** | **`a8`** |
| **Game-source revision in the film** | **`b33b06c`** — `git diff b33b06c..a8 -- godot/` is empty. **Assignment 8 changed no game code** |

## The film

| | |
|---|---|
| **Filename** | `TheLostPitch_TiantongZhang.mp4` |
| **Length** | **3:54.20** — 234.200 s. Assignment 8 asks for 2–4 minutes |
| **Size** | 15,815,467 bytes |
| **Format** | 3840 × 2160, 30 fps, h264 + aac 48 kHz |
| **Beats** | 14, of which 13 are narrated · 825 narrated words |
| **Workflow** | Brutalist `godot-gdd` with the `walker` modifier. Narration: Kokoro `am_onyx`, local, **$0.00** |
| **In the repository as** | `youtube/claude-liam-walker-the-lost-pitch-gdd/exports/landscape/claude-liam-walker-the-lost-pitch-gdd.mp4` — **not committed**; `.gitignore` keeps MP4s out |

**Film URL:** <https://northeastern-my.sharepoint.com/:v:/g/personal/zhang_tiant_northeastern_edu/IQATPsrbUQAEQrfpPFtYnt5hAZVWs8cd66-_PUQjD3tXSE8?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=DXya9m>

**Film SHA-256:**

```
fc2ebbe4f632dc7155cc21a1e66aaef762a393e0f0933c35f1b0859728527de5
```

> **Download the file; do not hash a web preview.** OneDrive re-encodes for
> its in-browser player, so the preview's bytes will not match the hash above.

## What is in this folder

| File | What it is |
|---|---|
| `PROJECT-BRIEF.md` | **the pitch in text** — the seven questions, ending with §A *exists today* and §B *will exist*. Hand-written; the film is a walk through it |
| `FRICTIONAL.md` | dated entries from the day this was built. Hand-written |
| `README.md` | this file. **Generated** — every figure above is measured from the master at assembly time |
| `beat_sheet.json` | the narration and visual plan. Generated copy |
| `gdd-evidence.json` | the ledger the official checker reads. Generated copy |
| `BUILD-PROMPT.md`, `SOURCES.md`, `SHOTLIST.md`, `FACTCHECK.md`, `GDD-COVERAGE.md` | generated copies; the originals live in the reel |
| `CHECKS-REPORT.md` | the checks, **run at assembly time rather than remembered** |
| `REPORT.md` | the toolkit's Gate V visual QC report, as it ran |

Every generated copy carries a header saying so. Edit the original in
`youtube/claude-liam-walker-the-lost-pitch-gdd/` and re-run the assembler; a hand-edited copy is how a
sentence outlives its facts, and this repository has been back for eleven of
those.

## How to rebuild the film

`BUILD-PROMPT.md` has the commands in order. Three things in it are not
optional reading:

1. **The toolkit needs a two-number patch.** `GodotDesignBoard.tsx` draws its
   footer outside the title-safe inset and fails the toolkit's own Gate V on
   every frame. The patch is in `BUILD-PROMPT.md` §5. Without it the master
   will not compile.
2. **Run the beat-sheet builder exactly twice**, and never after the Remotion
   batch.
3. **`scripts/finalise_beat_timing.py` and `scripts/fit_beat_panels.py` must
   not be run.** They `chdir` into `walker-ninja-TiantongZhang`. Both refuse
   to run now; `TOOLCHAIN.md` marks them **Reshape**.

## Honesty, in one place

- **Everything in `PROJECT-BRIEF.md` §B does not exist.** No enemy, no boss,
  no shrine, no title screen, no end screen, and **no export of any kind** —
  there is no `godot/export_presets.cfg` in this repository.
- **Both gameplay beats are real played capture** at `b33b06c`, hashed in
  `gdd-evidence.json`, with their per-frame input logs committed beside them.
- **3.57 s of the film is a held final frame**, and both holds are labelled
  on screen for exactly the seconds they are frozen.
- **Hollow Knight is named as a comparable the author has played.** No
  footage, art or audio of it appears, and no market claim is made.
- **The fact-check changed three numbers before the master was rendered**, and
  `FACTCHECK.md` lists all three rather than quietly fixing them.
