#!/usr/bin/env python3
"""Write the A3 reel's documents: COMPONENTS, SHOTLIST, FACTCHECK, SOURCES,
RIFF, PROMPTS, BUILD-PROMPT. The skill names all seven."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REEL = os.path.join(ROOT, "youtube", "claude-liam-walker-ninja-a3-blender")


def put(name, text):
    io.open(os.path.join(REEL, name), "w", encoding="utf-8", newline="\n").write(
        text.lstrip("\n"))
    print("  wrote %-18s %5d bytes" % (name, len(text)))


put("COMPONENTS.md", """
# COMPONENTS.md — what this film takes apart

Five units, each one a thing that exists in the repository and can be opened.
This is Assignment 3's layer only; the 2D game is Assignment 2's film.

## 1. `tools/blender/build_spike_trap.py` — the trap

Four primitives: a cube plate and three cones. The tooth count is derived, not
chosen — the 2D `spike_count()` is `rect.size.x / SPIKE_PITCH`, 24 / 8 = 3 —
and the pitch in the script is the width over that same count, so the asset
and the thing it represents come out of one number.

**Data in:** `levels/first_steps.json` trap rect `[1160, 304, 24, 16]`, at the
project's 16 px = 1 m. **Out:** `godot/assets/models/spike_trap.glb`, 54
triangles. **Trade-off:** 8-sided cones are visibly faceted close up; a cone
costs `2N − 2` triangles and the budget is 500.

## 2. `tools/blender/build_slime.py` — the slime, and `fit_to_size()`

Three primitives: an icosphere bisected at z = 0 and hole-filled, plus two eye
cubes. The unit worth teaching is `fit_to_size()`: an icosphere is a faceted
solid with no vertex ring on the cut plane, so a dome built at a nominal
1.375 m measured 1.171. The function measures the mesh after the cut and
scales it to the brief.

**Trade-off:** six lines and one extra pass over the vertices, against a size
that no longer depends on the subdivision level. It paid for itself the same
day, when `SUBDIV` went 1 → 2 and the size did not move.

## 3. `tools/blender/export_glb.py` — the export settings, written once

Shared by all three so they cannot drift. Two settings are passed explicitly
rather than inherited: `export_format='GLB'`, whose operator default is the
**empty string** — calling the exporter from Python without it produces no
file — and `export_yup=True`, which is already the default here but which the
brief's first prediction depends on.

## 4. `godot/tests/check_assets_3d.gd` — the check, and what it cannot do

Loads each `.glb`, walks it accumulating local transforms, and prints the
bounding box, the longest axis, the node scale and the distance from the floor
against the brief. Exits non-zero on any mismatch.

Its first version read `global_transform` from nodes that a script running in
`_init()` has not put in the tree, got identity back for every one, and
reported a correct asset as sunk 0.425 m into the floor. That is in the film
because the assignment warns an agent's check can prove less than it claims.

## 5. `godot/scenes/asset_showcase.tscn` — the scene

Floor, one `DirectionalLight3D`, one `Camera3D`, three assets 1.9 m apart, all
at y = 0. The `WorldEnvironment` supplies flat ambient and is not a second
light; without it an unlit face reads as a hole and the human check cannot be
performed.

## Not in this film

The 2D slice — level, sprites, audio, gameplay. Assignment 2's film covers it
and nothing in A3 changed it. `BLENDER-NOTES.md`'s six interface parts are
coursework, not a component. The three `.blend` files are sources, shown
through their build scripts rather than as files.
""")


put("SHOTLIST.md", """
# SHOTLIST.md — what is on screen, beat by beat

`godot-gamedev walker` · 13 beats · **4:13 estimated**, to be replaced with
the measured length after the master renders. Durations follow the narration.

Teaching contract **`code-then-result-v1`**: three code excerpts, each
immediately followed by the result those lines produce, bound by hash in
`gamedev-evidence.json`.

| # | act | surface | on screen |
|---|---|---|---|
| B00 | ASK | `ClaudeComposerAsk` | The reconstructed prompt, labelled **reconstruction — illustrative, not a transcript**. Three result lines: built not generated, sizes from the 2D game, no library or generator. |
| B01 | RESULT | `BrutalistHesitantWriter` | "Claude **generated** three assets." — **generated** struck, **built** written in its place. Three cards: built, off-by-rule, unchanged. |
| B02 | BUILD | `GodotDevWorkbench` code | `build_spike_trap.py` 98–111, the tooth loop. Four cues: the derived pitch, the x placement, the location tuple, the transform apply. |
| B03 | RESULT | `GodotDevWorkbench` asset | `blender-spike-angles.png` — four views of the trap, captured from the live Blender session through the MCP `look` tool. |
| B04 | BUILD | `GodotDevWorkbench` code | `build_slime.py` 98–109, `fit_to_size()`. Cues on the measured bounds, the target, the factor, the vertex pass. |
| B05 | RESULT | `GodotDevWorkbench` asset | `slime-before-after.png` — subdivision 1 beside subdivision 2, both from the live session. |
| B06 | BUILD | `GodotDevWorkbench` code | `check_assets_3d.gd` 150–161, `_collect()`. Cues on the accumulated transform, the root exception, the AABB, the recursion. |
| B07 | RESULT | `GodotDevWorkbench` asset | `check-output.png` — the headless run's own stdout, twelve measurements, ALL CHECKS PASSED. |
| B08 | RESULT | `GodotDevWorkbench` asset | `hand-edit-slime-eye.png` — **the author's own Blender window**, screenshotted by them. Not a reconstruction. |
| B09 | RESULT | `GodotDevWorkbench` asset | `godot-showcase.png` — a frame from a real run of `asset_showcase.tscn`. |
| B10 | VERDICT | `ClaudeVerdictArtifact` | Eight lines: built not generated, the six services off, sizes traced, 12 measurements, the broken check, two revisions on sight, the one-sentence human check, and what is not shown. |
| B11 | TURN | `ClaudeComposerAsk` | One bounded change — give the torch a light — with the predicted range derived from the 2D glow, and the note that the check will not notice either way. Liam signs off. |
| B12 | OUTRO | `ClaudeTitleOutro` | Locked card. `NewWalker3D_TiantongZhang`, `@NikBearBrown`, one mascot, no subline, no narration. |

## Labels carried on screen

- B00 is labelled a reconstruction, in the running text and in the narration's
  first sentence.
- B03 and B05 say **captured from the live Blender session through the MCP**.
  They are renders of the author's running Blender, not screen recordings and
  not redraws.
- B07 says **headless output**. It is the run's own stdout.
- B08 says **my own session — a photograph of the window, not a
  reconstruction**, because it is the one frame nobody else could produce.

## A known limitation, carried over from Assignment 2

B03, B05, B07, B08 and B09 use `GodotDevWorkbench` in `asset` mode, which lays
out `{code}{image}`. Their `code` is empty, because the teaching contract says
a result beat may not carry a source excerpt, so the left panel renders as a
dark box with one blank line number. Every evidence image is composed to the
panel's measured **1529 × 987** so the right half is at least full. The empty
left half is the cost of reusing the shared component correctly, and it is
recorded rather than hidden. Assignment 2's `SHOTLIST.md` has the longer
version and the three alternatives that were rejected.

## What this film does not show

- The 2D game. Covered by the Assignment 2 film, unchanged by A3.
- The torch and the slime building, step by step. One asset is taught in
  depth — the trap — and the other two through the two decisions that were
  actually interesting: the fit, and the subdivision.
- The assets inside the 2D game. Not asked for until later assignments.
""")


put("FACTCHECK.md", """
# FACTCHECK.md — every number the narration says, and where it came from

One row per claim. "Where" is a thing a reviewer can re-run or re-read.

## B00 — the ask

| claim | evidence |
|---|---|
| "a reconstruction, not a transcript" | True by construction; the running text says it on screen and the narration says it in the first sentence. No build receipt is shown. |
| "three things it already draws in code" | `_draw_torch()`, `_draw_spikes()`, `_draw_slime()` in `game/session.gd`. |

## B01 — built, not generated

| claim | evidence |
|---|---|
| "eleven primitives" | 4 + 4 + 3, reported by each build script's `report()`. |
| "two hundred and ten triangles for all three" | 84 + 54 + 72 = 210, from `mesh.calc_loop_triangles()`. |
| "a 3D generator was available in the same add-on" | `get_addon_status` lists `hyper3d`, `hunyuan3d`, `tripo`. All report off. |

## B02 / B03 — the trap

| claim | evidence |
|---|---|
| The excerpt is `build_spike_trap.py` 98–111 verbatim | `gamedev-evidence.json` → `excerpts[B02]`, hash-bound. Sliced from the file by line range at build time. |
| "spike_count is the rect width over the pitch, twenty-four over eight, three" | `session.gd:213` `maxi(1, int(rect.size.x / SPIKE_PITCH))`, `SPIKE_PITCH = 8`, rect width 24. |
| "fifty-four triangles" | `report()` output, and the Godot check. |
| "one point five metres wide and one metre tall" | `levels/first_steps.json` `[1160, 304, **24, 16**]` at 16 px = 1 m. |

## B04 / B05 — the slime

| claim | evidence |
|---|---|
| The excerpt is `build_slime.py` 98–109 verbatim | `excerpts[B04]`, hash-bound. |
| "missed its own brief by fifteen per cent" | Measured 1.171 against 1.375 = 14.8 % under. The first build's own output. |
| "a dome built at one point three seven five measured one point one seven" | Same. The `fit:` line prints both. |
| "twenty more triangles" | 52 → 72, both from `report()`. |
| "still inside the budget the brief wrote down" | `CHANGE-BRIEF.md` 3.0.0 budgets 120 for this asset. |
| "Every check passed on the one on the left" | It did. The pointed version passed size, axis, scale and origin; that is the point of the beat. |

## B06 / B07 — the check

| claim | evidence |
|---|---|
| The excerpt is `check_assets_3d.gd` 150–161 verbatim | `excerpts[B06]`, hash-bound. |
| "reported a correct asset as sunk four hundred millimetres into the floor" | The failing run: `lowest point y = -0.4250 m`. `TEST-REPORT.md` §A8. |
| "0.850 m tall and -0.425 m low: exactly the cone's local half-height" | Tooth height 0.85, centred on its own origin → ±0.425. |
| "Twelve measurements, no failures" | 3 assets × 4 (size, axis, scale, origin). The run's output is B07's image. |

## B08 — the hand edit

| claim | evidence |
|---|---|
| "my own Blender" | `design/blender/hand-edit-slime-eye.png`, the author's screenshot; the title bar names the file. |
| "scale 1.526 … 1.570 … about 27 mm lower" | Measured through the MCP before the transform was applied; the screenshot's Properties panel shows the resulting position to five decimals. |
| "a scale of one, because the transform was applied afterwards" | Visible in the same screenshot: 缩放 1.000 on all three axes. |

## B09 — the scene

| claim | evidence |
|---|---|
| "one point nine metres apart" | `asset_showcase.tscn`, the three transforms at x −1.9, 0, +1.9. |
| "each origin is at the centre of its underside" | `CHANGE-BRIEF.md` 3.0.0, and the check's `lowest point y = +0.0000 m` on all three. |
| "the WorldEnvironment is ambient, not a second light" | The scene has one light node. The environment sets `ambient_light_energy = 0.25`. |

## B10 / B11 — verdict and turn

| claim | evidence |
|---|---|
| "all six libraries and generators off" | `get_addon_status`, quoted in `SOURCES.md` §9. |
| "one human check, one sentence long" | `TEST-REPORT.md` §A6, which quotes it in full and says it is one sentence. |
| "sixteen nested discs with an outer radius of sixty pixels" | `session.gd` `_draw_torch()`: `range(16)`, `60.0 - i * 3.6`. |
| "three point seven five metres of reach" | 60 px ÷ 16 px/m = 3.75 m. Stated as a prediction for the viewer to test, not as a measurement. |

## Corrections made while building this film

| | |
|---|---|
| The slime's subtitle ran under its own image | Caught by looking at the composed evidence file; the images start 26 px lower now. |
| An earlier note said add-on 1.8 has no Tripo | True of the N-panel, false of the software. `get_addon_status` lists it as Premium-gated and off. Corrected in `SOURCES.md` §9 and `FRICTIONAL.md`. |
""")


put("SOURCES.md", """
# SOURCES.md — this film's own materials

The game's provenance is `../../SOURCES.md`, §9 for Assignment 3. This file
covers what the **film** is made of.

## Images

| | what it is |
|---|---|
| `media/blender-spike-angles.png` | Four views of the trap, rendered from the **live Blender session** by the MCP's `look` tool. Not a screen recording and not a redraw. |
| `media/blender-slime-subdiv1.png` | The slime at subdivision 1, same method. Kept because the film compares it with what replaced it. |
| `media/blender-slime-subdiv2.png` | The slime at subdivision 2, same method. |
| `media/slime-before-after.png` | The two above, composed side by side by `tools/compose_a3_evidence.py`. |
| `media/check-output.png` | The headless check's own stdout, set in Consolas by the same script. Values verbatim. |
| `media/hand-edit-slime-eye.png` | **The author's own Blender window**, screenshotted by them. The only frame in this film that a person had to produce. |
| `media/godot-showcase.png` | A frame from a real run of `asset_showcase.tscn`, captured by a short script that renders eight frames and saves the viewport. |

Both composed images are made at **1529 × 987**, the `GodotDevWorkbench`
right-hand image area measured off a rendered master during Assignment 2.

## Narration

**Kokoro-82M**, local, Apache-2.0, voice `am_onyx`. No API, no account, no
cost. 12 of 13 beats; B12 is the locked outro and carries no narration by
rule.

## Editor views

Every code panel is `GodotDevWorkbench`, reused rather than redrawn —
`./art scenes` was run first and reported it as the match. Views are labelled
**"Godot editor reconstruction · source-backed teaching view"** on screen.
Every displayed line is sliced out of the file on disk by line range when the
beat sheet is built, so a beat cannot drift from its source.

Two of the three excerpts are Python rather than GDScript, because two of the
three components are Blender build scripts. The panel is a teaching view of a
source file, not a claim about which editor the file was written in.

## Outro

`ClaudeTitleOutro`, locked per `OUTRO-LOCK.md`: exact title, `@NikBearBrown`,
one slug-seeded mascot, no subline, existing stock jingle only, no narration.

## Upstream consulted

`skills/make/godot-gamedev/SKILL.md` and its `references/evidence.md`;
`RENDER-TARGETS.md`; `OUTRO-LOCK.md`. Assignment 2's reel was read for the
real prop shapes of `ClaudeComposerAsk`, `BrutalistHesitantWriter` and
`ClaudeVerdictArtifact` — in A2 two component names were invented and rejected
by `./art scenes --check`, and that is not being repeated.

No secrets, no `.env` contents and no absolute developer-machine paths are
embedded in any reusable skill or scene.
""")


put("RIFF.md", """
# RIFF.md — the commentary, and what it is allowed to say

Liam, in for Bear. Teardown register. The riff is on inspected output, never
on imagined work.

## The three things worth saying out loud

**1. The tooth count is not a decision.** `spike_count()` in the 2D game is
`rect.size.x / SPIKE_PITCH`. The 3D script derives its pitch from the same
count. That is the difference between an asset that represents the trap and an
asset that merely resembles it, and it costs one line.

**2. Measuring beats a constant.** The slime came out 14.8 % small. The quick
fix was a multiplier taken from that one measurement; the fix taken measures
the mesh and scales to the brief. Within the hour the subdivision level
changed and the size did not move. The riff is that the slower fix was cheaper
by the end of the afternoon.

**3. The check was wrong before any asset was.** It read `global_transform`
from nodes not yet in the tree, got identity, and accused a correct asset of
sinking into the floor. The assignment warns about exactly this. The riff is
that the warning was right and knowing it did not prevent it — only reading
the output did.

## What the riff refuses to do

- **Call any of this generated.** It is built. A generator was one tool call
  away and is off by rule, and the film says so in its second beat.
- **Present the MCP renders as a screen recording.** They are renders of the
  live session through the `look` tool, labelled as that on every beat.
- **Claim the checks prove the assets are right.** They measure geometry.
  Whether a thing reads as a torch is in `TEST-REPORT.md` §A6 and is one
  sentence long.
- **Inflate the human check.** One sentence was given; one sentence is shown.
- **Round a number up.** 14.8 %, not "about 15". 210 triangles, not "around
  200". 3.75 m is a prediction and is called one.

## The one joke

There isn't one. The register is Teardown and the subject is a student
assignment where the interesting events were three failures.
""")


put("PROMPTS.md", """
# PROMPTS.md — the prompts this film shows, and their status

## B00 — the composer ask

**Status: RECONSTRUCTION.** Illustrative. It is not a transcript, there is no
claim it was ever sent, and no build receipt is shown. The label is on screen
for the whole beat and the narration says it in the first sentence.

> Please use Walker to convert my game design document about a cyber-ninja in
> a torchlit dungeon into three simple 3D assets I can put in Godot: the wall
> torch, the pop-up spike trap and the slime. Build them in my open Blender
> through the MCP, from basic shapes only, at the sizes my 2D level already
> uses.

## B11 — Your Turn

**Status: USABLE.** Meant to be run, and bounded: one node, one prediction,
one look.

> In walker-ninja, add an OmniLight3D as a child of the Torch in
> `scenes/asset_showcase.tscn`, with a range derived from the 2D glow in
> `_draw_torch`. Write the predicted range in the commit message before you
> run it, then look at the frame.

The prediction is the point. The 2D glow is 16 nested discs with an outer
radius of 60 px, and at 16 px = 1 m that is **3.75 m**. `check_assets_3d.gd`
measures geometry and a light is not geometry, so the check will pass whatever
range is used. The instruction is therefore to look — which is this film's
lesson restated as homework.

## The prompts that actually built the assets

Not shown on screen, because they are not prompts in the usual sense. Each
asset was built by the MCP executing a file:

```python
exec(compile(open(r"...\\tools\\blender\\build_spike_trap.py").read(), path, "exec"))
```

so the thing to read is the script, not a prompt. All three are in
`tools/blender/`, and the same files run standalone as the assignment's
script-route fallback. `../../FRICTIONAL.md` has the session they were written
in, including the three setup failures.
""")


put("BUILD-PROMPT.md", """
# BUILD-PROMPT.md — how to rebuild this film from the repository

From the repository root. The toolkit lives beside it at `../brutalist.art-main`.

## Environment

```
PYTHONUTF8=1
ART_NO_DRAWTEXT=1
ART_HOME=../brutalist.art-main
GODOT=.../Godot_v4.7.2-stable_win64.exe
BLENDER=.../Blender/blender.exe
```

Python 3.12 with Pillow. Node 22. `ffmpeg` on PATH.

## 1 — rebuild the assets, if you want to start from nothing

```bash
"$BLENDER" -b --factory-startup --python-exit-code 1 --python tools/blender/build_torch.py
```

Each script prints its own object count, triangle count, bounding box and base
height. Exporting needs `tools/blender/export_glb.py`, which the MCP path
calls; standalone, add a call to `save_and_export` at the end.

## 2 — check the assets before filming them

```bash
"$GODOT" --headless --path godot --import
"$GODOT" --headless --path godot --script res://tests/check_assets_3d.gd
```

Exit 0 or the film is about something that does not hold.

## 3 — evidence images, then the beat sheet

```bash
python tools/compose_a3_evidence.py
python tools/build_a3_beat_sheet.py
```

Order matters: the beat sheet embeds the images as data URIs, and it slices
every code excerpt out of the file on disk by line range. **If a build script
is edited, the line numbers in `build_a3_beat_sheet.py` must be re-checked** —
the script asserts the excerpt is ≤ 14 lines but cannot tell whether it still
starts in the right place.

## 4 — narration, then bind to it

```bash
python $ART_HOME/runtime/scripts/generate_audio_kokoro.py <REEL>
```

Narration first, timing second. Cue positions are fractions of the *measured*
audio.

## 5 — gate before rendering

```bash
cd $ART_HOME
./art godot-gamedev --check <REEL> --game <REPO>/godot < /dev/null
```

Expect `"status": "PASS"`. Note the `< /dev/null`: `./art` subcommands read
stdin, and inside a `while read` loop they consume the loop's input and report
every component as NOT RENDERABLE. That cost ten minutes during Assignment 2.

## 6 — pilot, then batch

```bash
python $ART_HOME/runtime/scripts/remotion_scenes.py <REEL> --only B02 --force
# LOOK AT IT. Then:
python $ART_HOME/runtime/scripts/remotion_scenes.py <REEL>
```

The pilot exists because the panel clips. **Excerpts ≤ 14 lines, note values
≤ 100 characters.** `codeFontSize` cannot go below 23.

Do **not** pass `--outro`: that builds `OutroSeries` / `OutroCTA` from
`ABOUT.MD` / `AUTHOR.MD`, which this reel does not have.

## 7 — master

```bash
cd $ART_HOME
./art final <REEL> --height 2160 --fps 30 --out <REEL>/exports/landscape
python runtime/qc/final_frame_check.py <REEL> --mp4 <REEL>/exports/landscape/<slug>.mp4
```

Gate V lives at `runtime/qc/`, not `runtime/scripts/`, and takes the reel
positionally with the master as `--mp4`.

## Known traps

- `./art final` rewrites `_qc/REPORT.md` and drops the human half. Re-append.
- It names the output after the reel **slug**, so rename to the locked title
  and recompute the SHA-256 afterwards.
- The title must stay **≤ 26 characters** or the outro card overflows Gate V's
  safe right edge. `NewWalker3D_TiantongZhang` is 25.
""")

print("done")
