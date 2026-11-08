# walker-the-lost-TiantongZhang

**CSYE 7270, Building Virtual Environments — Fall 2026.**
Tiantong Zhang · `zhang.tiant@northeastern.edu` · GitHub `TiantongZhang1`

**The Lost** — a 2D side-view dungeon crawler. Four themed floors, one boss
each, and the boss drops the key to the floor below. You do not kill the
bosses: each is an adventurer who went down before you and was corrupted by the
dungeon's miasma, and beating one purifies them back into a person who joins
your hub. Progress is not a percentage in a save file; it is the number of
people standing in the room you come home to.

| | |
|---|---|
| Repository | <https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang> |
| Engine | Godot **4.7.2.stable.official** `ed1daf0bf` |
| Renderer | **Forward+** — Vulkan 1.4.357, NVIDIA GeForce RTX 5080 Laptop GPU, Windows 11 |
| Resolution | 640 × 360 logical, 1280 × 720 windowed, `canvas_items` stretch, nearest filtering |
| Scale convention | 16 px = 1 m |
| Design document | `../the-lost-gdd/GDD.md` — moves into `design/` when A4 lands |
| Current tag | `a6` |

---

## What this repository is at the `a6` tag

**Assignment 6 — Creating Particle Effects with Godot and Claude.** Three
particle effects in the three-trap room, each with an intent block written
before it was built, a frame strip read at the project's own window size, and
a headless suite that proves what a headless suite can prove and says so about
the rest.

| | **A — the grit burst** | **B — the dungeon motes** | **C — the step dust** |
|---|---|---|---|
| Job | one-shot, on the game's own event | ambience | one-shot, on a **derived** event |
| Event or condition | `signal fired`, `spike_trap.gd:98` | starts with the scene, stops on `signal died` | **none exists** — one puff per 24 px travelled |
| Node type | **`GPUParticles2D` × 3** under one `Node2D` | **× 1** | **× 2** under one `Node2D` |
| Scene | `godot/effects/hit_burst.tscn` | `godot/effects/dungeon_motes.tscn` | `godot/effects/step_dust.tscn` |
| Retrigger | **overlap** — one instance per event | n/a | overlap; the trail is 2–3 puffs |
| Feature the others lack | — | **`preprocess = 8.0`**, Box emission | **`amount_ratio`** — 0.6 stride, 1.0 landing |

**What this assignment added**, file by file: three effect scenes and three
preview scenes under `godot/effects/` and `godot/previews/`; two drivers
(`hit_burst_spawner.gd` and `step_dust_driver.gd`) that read game state and
write none; `godot/game/debug_keys.gd`, the F9 vsync toggle; six test suites;
`godot/tests/cost_effects.gd`, which runs the assignment's four named
conditions with an empty-scene control and a twice-run baseline;
`godot/tests/capture_particles.gd`, the film's capture driver; and
`godot/shaders/particles_generated.gdshader`, extracted from a material the
author converted in the editor and loaded by nothing.

**No game script was changed.** `player.gd`, the input map and the trap's
state machine and timings are out of scope in `CHANGE-BRIEF.md` §3 and stayed
out; the effects hang off signals that already existed, or off a position
delta they measure themselves.

**No texture is used by any of the six emitters.** The look is colour ramps,
scale curves and a blend mode, so there is nothing to credit and nothing to
license for this assignment's own work.

**249 checks, 301 results, 0 failures** — the step-dust state suite's 26 run
at 30, 60 and 144 fps, because a cadence measured at one rate has not been
measured.

---

## What this repository is at the `a5` tag

**Assignment 5 — Shaders, Materials, and the Godot Shading Language.** Three
shaders written by hand, a 2D slice for the first one to live in, Assignment
3's 3D scene for the other two, and the measurements that settle what they do.

### Where it started

This repository was created on **2026-10-17** for the course's one permitted
change of game, and held **no game at all**. Assignment 5 assumes a game exists
from Assignment 2, so the 2D slice — a player who walks and jumps, a floor, and
three spike traps — is prerequisite work, built *after* `CHANGE-BRIEF.md` was
committed and before Assignment 5's Step 1. `FRICTIONAL.md` records the change
of game and the reasoning; the shaders themselves were still specified before
they were written, which is what the rule protects.

Assignments 1–3 are **not** here. They were submitted from
`walker-ninja-TiantongZhang` under the tags `a2-submitted` and `a3`, and that
repository has not been modified since. Per the assignment rule the tags
continue here, and `a5` is this repository's first.

### What Assignment 5 added

| | |
|---|---|
| **`trap_warning.gdshader`** | `canvas_item`. Mixes the trap sprite toward `#D63C2F` across the 0.40 s before the spikes fire — one line inside `fragment()`, driven by `warn_amount` from the trap's own state machine. |
| **`hint_bands.gdshader`** | `spatial`, `unshaded`. Two samplers bound to the same 3-texel PNG, one with `source_color` and one without, to measure what the hint is worth. |
| **`dungeon_surface.gdshader`** | `spatial`. A colour texture and a data mask, four non-texture uniforms in two `group_uniforms` groups, two materials — the same stone above and below floor 1's waterline. |
| **`standard_generated.gdshader`** | Godot's own output from *Convert to ShaderMaterial*, saved unedited, read and cited in `LANGUAGE-NOTES.md`. |
| The driver | `trap_warning_driver.gd` duplicates the `ShaderMaterial` per instance and writes one uniform at `process_priority = 100`. It reads game state and never writes it. |
| Four test suites | 99 checks, the trap suites at 30, 60 and 144 fps. |
| Four deliberate breakages | each caught by a different net — see `TEST-REPORT.md`. |
| An explainer film, 18 beats | `youtube/claude-liam-walker-the-lost-gamedev/` |

### The two findings worth the trouble

1. **`source_color` does not change the value a 2D `canvas_item` shader
   receives.** All eight predicted pixel values landed exactly, worst channel
   difference 0. H1 held; H2 was out by 20–43 counts per channel.
2. **The engine does not report `source_color` on a sampler at all** — while
   reporting it plainly on a `vec3`. Both come back from
   `get_shader_uniform_list()` as type 24, hint 17, "Texture2D". Deleting
   `source_color` from a sampler is therefore invisible to every runtime check
   and visible only in the source text and in the pixels.

`hint_range` also does not clamp a value set from code: `warn_amount = 2.0`
passed straight through and `mix()` extrapolated, so pixel B went pure
`255, 0, 0` where a clamp would have given `214, 60, 47`.

## Run it

Double-click **`run-game.bat`**, or:

```bash
godot --path godot
```

There is no standalone `.exe` — this is a Godot project, so the editor binary
runs it from `godot/project.godot`. The `.bat` finds Godot by a path relative
to itself, so moving the whole course folder is fine; separating this
repository from the Godot download is not.

The main scene is `res://game/main.tscn`: the three-trap room.

### Controls

| | |
|---|---|
| Walk | **A** / **D**, or **←** / **→** |
| Jump | **Space**, **W**, or **↑** |
| **Toggle vsync** | **F9** — prints the mode and the current FPS to the console |

**F9 is a debug key, not a project setting.** Assignment 6 asks for the frame
rate to be compared with the effects off and on, and for that comparison to be
made without shipping the game under different settings than the one that was
measured. It reads the raw keycode off the event and adds no input action:
`test_input_map.gd` asserts that the map still holds exactly three non-`ui_`
actions with `DebugKeys` in the tree.


Walk into a trap's detection zone and keep walking. The trap turns red for
0.40 s and then fires; a player who does not react is hit, which is the point —
`CHANGE-BRIEF.md` revision 5.0.2 records the version of this trap that could
not hit anybody and the arithmetic that proved it.

The 3D scene is `godot/scenes/asset_showcase.tscn` (two slimes, two materials)
and the hint experiment is `godot/scenes/hint_experiment.tscn`.

## Run the checks

```bash
godot --headless --path godot --import     # once after cloning
./scripts/run-test.sh test_materials.gd 60
./scripts/run-test.sh test_trap_warning.gd 30
./scripts/run-test.sh test_trap_shader_driver.gd 144
```

**Always through the wrapper.** It is the only thing that fails on a
`SHADER ERROR` or `SCRIPT ERROR` line, which Godot prints while still exiting
0. `godot` is not on PATH on the machine this was built on; the wrapper
resolves it relative to the repository and `GODOT=` overrides it.

| Suite | fps | Checks |
|---|---|---|
| `test_hit_burst_config.gd` | 60 | 80 |
| `test_hit_burst_state.gd` | 60 | 22 |
| `test_dungeon_motes_config.gd` | 60 | 39 |
| `test_dungeon_motes_state.gd` | 60 | 19 |
| `test_step_dust_config.gd` | 60 | 63 |
| `test_step_dust_state.gd` | 30 · 60 · 144 | 26 each |
| `cost_effects.gd` | `60 300` | a table, not a pass/fail |
| `test_materials.gd` | 60 | 48 |
| `test_trap_shader_driver.gd` | 30 · 60 · 144 | 24 each |
| `test_trap_warning.gd` | 30 · 60 · 144 | 22 each |
| `test_input_map.gd` | 60 | 5 |
| `check_assets_3d.gd` | 60 | ALL PASSED, 12 measurements |

**Assignment 6's own suites are 249 checks and 301 results, 0 failures**;
Assignment 5's are 99 more and still pass unchanged. All of it from a fresh
cache with zero import errors. The step-dust and trap suites run at three
pinned frame rates because a duration or a cadence measured at one rate has
not been measured. Never add `--rendering-driver` to a test command.

**`cost_effects.gd` is not a budget.** It measures CPU wall clock in a run
that draws nothing, which is the control on a prediction — `CHANGE-BRIEF.md`
§5 predicts every effect reads ≈ 0 ms over an empty scene *by construction*,
because a `GPUParticles2D`'s process step is a shader on the card. The budgets
are GPU time from the Visual Profiler, and §4 puts that row under HUMAN.

A headless run uses a dummy renderer and draws nothing: it can show that a
shader parses, what it declares, and a float on a given frame — never colour.
Everything about colour in this repository was measured in a real windowed run
and the captures are in `captures/a5/`.

## The film

`youtube/claude-liam-walker-the-lost-particles-gamedev/` —
**TheLostParticles_TiantongZhang.mp4**, 3840 × 2160, 30 fps, 20 beats, 9:51.
Six code-then-result pairs: every code panel is followed by the thing those
lines produce, and no beat shows both at once. Five beats are engine footage
from three 4K Movie Maker takes, each of which asserted its own outcome before
a frame of it counted; four are evidence cards whose every figure is
recomputed from committed capture frames at build time. Its evidence ledger
passes the course checker — 66 source files, 40 exclusions, 6 components.

The link, the exact length and the SHA-256 are in `SUBMISSION.md`, which is
the one place they are recorded so they cannot disagree. Rebuild it with that
reel's `BUILD-PROMPT.md`.

**Assignment 5's film is still here and still builds:**
`youtube/claude-liam-walker-the-lost-gamedev/` —
**TheLostShaders_TiantongZhang.mp4**, 3840 × 2160, 30 fps, 18 beats. Six
code-then-result pairs: every code panel is followed by the thing those lines
produce, and no beat shows both at once. Its evidence ledger passes the course
checker.

The link, the exact length and the SHA-256 are in `SUBMISSION.md`, which is the
one place they are recorded so they cannot disagree.

Rebuild it with `youtube/claude-liam-walker-the-lost-gamedev/BUILD-PROMPT.md`,
which is the actual command sequence, including the two carried-over scripts
that must **not** be run.

## Ownership — who wrote what

**`godot/shaders/` is written by hand by the author and never by an agent.** No
agent creates, edits or reformats a `.gdshader`;
`git diff --stat godot/shaders/` across any agent commit must print nothing,
and `git log --format='%h %an' -- godot/shaders/` returns four commits, all
mine, with no co-author trailer. `LANGUAGE-NOTES.md` is mine too.

Everything else — the trap's state machine, the driver, the four test suites,
the capture rigs, the film's beat sheet and these documents — is Claude Code's
work under my review, and `SOURCES.md` §7 lists it file by file.

## Layout

```
godot/            the Godot project
  game/           main.tscn, the three-trap room
  scenes/         asset_showcase.tscn, hint_experiment.tscn
  features/       player, traps, the material driver
  shaders/        the four .gdshader files      (hand-written; see Ownership)
  assets/         sprites, textures, models
  tests/          headless check scripts
  tools/          in-engine capture and texture rigs
captures/a5/      the windowed-run captures and their reports
evidence/         the four deliberate breakages and what each one printed
scripts/          film and evidence build chain      (see TOOLCHAIN.md)
tools/            sprite, Blender and audit scripts  (see TOOLCHAIN.md)
youtube/          the explainer film and its documents
```

## The documents, and what each is for

| File | What is in it |
|---|---|
| `SUBMISSION.md` | The assignment's answers, the film link and its SHA-256 |
| `CHANGE-BRIEF.md` | The Assignment 5 specification, committed 2026-10-23 before any shader existed, with four dated revisions |
| `TEST-REPORT.md` | Every suite, every rate, every count, and the four mutations |
| `LANGUAGE-NOTES.md` | The language answers, in the author's own words |
| `ATTRIBUTION.md` | Every asset, its origin and its licence |
| `SOURCES.md` | Where every file came from — mine, Claude's, or Godot's |
| `FRICTIONAL.md` | Dated log of the design thinking, written the same day |
| `TOOLCHAIN.md` | What was carried over from walker-ninja and what state it is in — **two of those scripts rewrite the other repository; read it before running anything in `scripts/`** |
| `CLAUDE.md` | The agent brief. Drafted by the session that built the repository; the author's review is a separate commit, and `tools/check_claude_refs.py` asserts all 50 claims in it by content |
| `CONCEPT.md` | The game in one page, with dated revisions appended |
| `ASSET-LOG.md` | Per-asset log. Empty by fact, not by neglect: every asset here is code-written or the author's own, so there is no prompt or licence to log |
| `PROMPTS.md` | The build prompts used, archived |

## Known limitations

### Assignment 6

1. **No GPU time has been read.** Every budget in `CHANGE-BRIEF.md` §5 and
   §C.6 — 0.30, 0.20 and 0.10 ms — is still a prediction. The Visual Profiler
   is the only instrument that can settle them, §4 puts that row under HUMAN,
   and the film says so three times rather than burying it.
2. **Effect B and Effect C have not completed a tuning revision.** B's r0
   verdict was *keep*, with no setting changed; C has a reading and no author
   verdict. The assignment asks for at least one observation-driven revision
   per effect, and only Effect A has one.
3. **Both B and C drift dust below the floor line** — 14–22 % of the motes
   and 11–29 % of the step dust, measured against a field-off control.
   Neither is visible in play; both are in `TUNING.md` with candidate
   one-setting fixes.
4. **Three effects instead of the two the assignment asks for**, and Effect C
   is the least settled of them.
5. **A5's evidence checker fails on `main` by construction**, from the first
   file this assignment added under `godot/`. The `a5` tag is unaffected and a
   clone of it still passes; `CHANGE-BRIEF.md` §0.3 verified this by
   experiment before any of A6 was built.
6. **One claim in the A6 film overstates its reason.** `FACTCHECK.md` in the
   reel records it: three of the six emitters carry both a colour ramp and a
   scale curve, not one. The narration was corrected; `TEST-REPORT.md`, which
   said the same thing, carries a dated correction rather than a silent edit.

### Assignment 5, carried forward

1. **The slice has no audio and no art beyond code-drawn blocks.** Assignment
   5's boundaries put the player, the HUD and the audio outside this change,
   and "boundaries kept" is a scored line. The port from `walker-ninja` is
   Assignment 6's first work.
2. **No normal map, so no curl check.** `CHANGE-BRIEF.md` §8 chose code-written
   textures, which forgoes the Poly Haven calibration pair the check needs.
   Said in the specification, not discovered afterwards.
3. ~~**One human judgement is still open.**~~ **Closed 2026-10-28:**
   `tint` at 0 breaks the look — the albedo is multiplied to black and the
   flooded slime reads as a silhouette rather than as stone. The other three
   uniforms only change it. `TEST-REPORT.md` limitation 4 carries the full
   wording, and the film says it too.
4. **The retrigger exploit.** A player who steps off the detection zone and
   back on restarts the warning every time and is never hit. Accepted in
   revision 5.0.1 as the price of "every trigger gets its own full warning".
5. **Six claims in the film are reasoning, not measurement**, and
   `FACTCHECK.md` lists them in one place rather than leaving them mixed in.
   It was four until B03A and B11A were written on 2026-10-28, each of
   which added one; the list is the authority and the film's own verdict
   panel was corrected to match it, not the other way round.
