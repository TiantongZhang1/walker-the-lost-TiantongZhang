# TOOLCHAIN.md — what was carried over from walker-ninja, and what state it is in

This repository is a continuation, not a fresh start. Assignments 4–10 each need
a Brutalist explainer film and a headless check run, and that machinery already
exists in `walker-ninja-TiantongZhang`. Rewriting it would have cost days and
taught nothing, so `scripts/`, `tools/` and the two generic Godot test harness
files were copied across on 2026-10-17.

**None of walker-ninja's game content was copied** — no scenes, no sprites, no
audio, no level data, no `test_game.gd`. Only build and documentation machinery.

## How to read the table

The "ninja refs" column is a mechanical count: occurrences of `ninja`, `slime`,
`spike`, `horse`, `cyber`, `dash`, `b05`, `b09`, `death_laugh`, `a3_` in the
file. It is a signal, not a verdict — a script can score 1 and still be useless
here because its *purpose* was walker-ninja-specific. The status column is the
verdict.

| Status | Meaning |
|---|---|
| **Generic** | Runs here unchanged. Parameterised by arguments or by data files. |
| **Reshape** | The logic is reusable; the data inside it is walker-ninja's and must be replaced. |
| **Reference** | Kept only as a worked example. Its purpose was specific to walker-ninja's A2 or A3 deliverable. |

## scripts/

| File | Lines | ninja refs | Status | What it does |
|---|---|---|---|---|
| `build_source_snapshot.py` | 87 | 0 | **Generic** | Records the exact playable source revision behind a film |
| `encode_captures.py` | 101 | 0 | **Generic** | Encodes raw frame sequences from Movie Maker into capture MP4s |
| `render_takes.py` | 127 | 0 | **Generic** | Drives Godot to render gameplay takes as lossless frames |
| `build_media_clips.py` | 116 | 0 | **Generic** | Builds the compositor's working clips from captures |
| `build_char_sheet.py` | 107 | 0 | **Generic** | Lays a character's poses out into one contact sheet |
| `import_pose.py` | 326 | 0 | **Generic** | Imports a generated pose image into the Godot asset layout |
| `record-build.cjs` | 36 | 0 | **Generic** | Records source + existing evidence without mutating game state |
| `finalise_beat_timing.py` | 95 | 2 | **Reshape** | Binds beat durations to the narration's `timings.json` |
| `fit_beat_panels.py` | 156 | 6 | **Reshape** | Fits evidence images to the workbench panel (1529 × 987) |
| `synth_placeholder_sfx.py` | 201 | 1 | **Reshape** | Synthesises placeholder SFX before real ones exist |
| `check_enemy_visibility.py` | 77 | 2 | **Reshape** | Asserts an enemy is readable against its background |
| `build_beat_bookends.py` | 105 | 17 | **Reshape** | Builds the Walker opening/summary bookend beats |
| `build_beat_sheet.py` | 522 | 25 | **Reshape** | Slices code excerpts by line range into film beats |
| `build_gamedev_ledger.py` | 322 | 27 | **Reshape** | Builds the evidence ledger the checker validates |
| `build_coverage.py` | 494 | 44 | **Reshape** | Builds `coverage.json` — the film's claim-to-evidence map |
| `build_level_map.py` | 123 | 15 | **Reference** | Draws walker-ninja's level as a map image |
| `check_trap_visibility.py` | 73 | 14 | **Reference** | Asserts walker-ninja's spike trap is visible before it fires |
| `mix_death_laugh.py` | 99 | 1 | **Reference** | Mixes one specific walker-ninja death sound |
| `compose_b05_evidence.py` | 83 | 4 | **Reference** | Composed one A2 beat's evidence image |
| `compose_b09_evidence.py` | 106 | 4 | **Reference** | Composed one A2 beat's evidence image |

## tools/

| File | Lines | ninja refs | Status | What it does |
|---|---|---|---|---|
| `blender/export_glb.py` | 48 | 0 | **Generic** | Saves the Blender scene and exports `.glb` — pass `export_format='GLB'` explicitly, it defaults to an empty string |
| `build_a3_ledger.py` | 210 | 14 | **Reshape** | A3's evidence ledger builder |
| `compose_a3_evidence.py` | 307 | 26 | **Reshape** | A3's evidence image compositor |
| `build_a3_beat_sheet.py` | 408 | 36 | **Reshape** | A3's beat sheet builder |
| `write_a3_reel_docs.py` | 475 | 51 | **Reference** | Wrote A3's reel documentation |
| `blender/build_torch.py` | 167 | 7 | **Reference** | Built A3's wall torch from four primitives |
| `blender/build_slime.py` | 205 | 13 | **Reference** | Built A3's slime; contains the reusable `fit_to_size()` helper |
| `blender/build_spike_trap.py` | 146 | 15 | **Reference** | Built A3's pop-up floor trap |

## godot/tests/

| File | Status | What it does |
|---|---|---|
| `route_driver.gd` | **Generic** | Feeds a scripted input route into a running scene |
| `test_keyboard.gd` | **Generic** | Synthesises key events for headless runs |

`test_game.gd` (49 KB of walker-ninja assertions), `check_assets_3d.gd`,
`capture_*.gd` and `capture_walkthrough.gd` were **not** copied. They assert
against scenes that do not exist here.

## Outside the repository

The Brutalist film toolkit itself is not vendored. It lives at
`D:\Graduate\2026Fall\7270\brutalist.art-main\` and is driven by the `./art`
CLI and the `godot-gamedev` skill. The scripts above are the glue between this
repository and that toolkit.

Also outside: Godot **4.7.2.stable.official** and Blender **5.2.2 LTS**, both
beside this repository in the course folder. `run-game.bat` finds Godot by a
path relative to itself, so moving the whole course folder is fine and
separating this repository from the Godot download is not.
