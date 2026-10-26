# FACTCHECK.md — every number the film says out loud, and where it came from

One row per spoken claim. "Where" is a file a reviewer can re-read or a
command they can re-run, not a memory of having seen it. Paths are relative to
the repository root unless they start with `godot/`.

Source revision `0b45339`. Godot **4.7.2.stable.official** `ed1daf0bf`,
**Forward+**, NVIDIA GeForce RTX 5080 Laptop GPU.

---

## B00 — the ask

| claim | evidence |
|---|---|
| "The prompt on screen is a reconstruction … It is not a transcript." | True by construction, and the beat carries a `RECONSTRUCTION` label on screen as well as in the narration. No build receipt is shown. |
| "a dungeon slice in Godot four" | `godot/project.godot:15` — `config/features=PackedStringArray("4.7", "Forward Plus")`. |
| "three hand-written shaders" | `godot/shaders/` holds four `.gdshader` files; three are hand-written and the fourth is Godot's own output, recorded as such in `SOURCES.md` and excluded from this count. Commits `f28d2de`, `3225e38`, `d161da9`, all authored by TiantongZhang1. |

## B01 — what was built

| claim | evidence |
|---|---|
| "ramps red across four tenths of a second" | `godot/features/traps/spike_trap.gd:39` — `const WARN_SECONDS := 0.40`. Measured at 0.417 s at 60 fps, within one frame: `TEST-REPORT.md`, R2 table. |
| "Two materials from one shader, on two identical slimes" | `godot/assets/materials/stone_dry.tres` and `stone_flooded.tres`, both `shader = ExtResource` pointing at `dungeon_surface.gdshader`. `test_materials.gd` asserts they hold the **same `Shader` object**, by identity. |
| "a three-pixel image" | `godot/assets/textures/hint_bands.png`, 3 × 1, read back by `test_materials.gd` as 64, 128, 192. |
| "Ninety-nine automated checks" | 48 + 24 + 22 + 5 = 99: `test_materials.gd` 48, `test_trap_shader_driver.gd` 24, `test_trap_warning.gd` 22, `test_input_map.gd` 5. `check_assets_3d.gd` reports ALL PASSED over 12 measurements and is **not** in the 99. |
| "four deliberate breakages" | `evidence/a5-mutations/`: semicolon deleted, uniform renamed, `source_color` deleted from `bands_srgb`, and again from `stone_albedo`. Each exited 1; logs are in that folder. |

## B02 — the colour line

| claim | evidence |
|---|---|
| "four lines of declaration and one line that changes a colour" | `godot/shaders/trap_warning.gdshader`, 7 lines: `shader_type`, two `uniform`s, blank, `void fragment() {`, the `mix()` line, `}`. The panel shows all 7. |
| "COLOR already carries the sprite's texture multiplied by its modulate" | Godot 4 canvas_item docs, fragment built-ins: *"`COLOR` from the `vertex()` function multiplied by the `TEXTURE` color."* Consulted 2026-10-25; recorded in `SOURCES.md`. |
| "a trap the game had faded out would ignore the fade entirely" | The reasoning is `CHANGE-BRIEF.md` §10, written before the shader existed. **Not measured** — no fade exists in the game to test it against. Stated as a consequence of the built-in's definition, not as an observation. |
| "The number is not time — it is game state" | `trap_warning.gdshader:2` declares `warn_amount`; `spike_trap.gd:68` advances it from `delta`. `TIME` appears in none of the three shaders. |

## B03 — the ramp in motion

| claim | evidence |
|---|---|
| "the detection box that starts it is one seven five" (B02) | `capture/logs/take-w-inputs.jsonl`, first frame where `warn[0] > 0`: t 1.82, `player_x: 174.4`. Trap 1 at x = 208 with a 66 px `DetectArea` gives 175. |
| "the detection box begins at one seven five" | Trap 1 at x = 208, `DetectArea` 66 px wide → 208 − 33 = 175. Asserted by `test_trap_warning.gd`'s geometry scenario, which also derives the half-width as `SPEED × WARN_SECONDS − 5`. |
| "that edge was derived from the warning length, not chosen" | `CHANGE-BRIEF.md` revision 5.0.3, and the comment above `WARN_SECONDS` in `spike_trap.gd:31-38`. |
| "The window is four tenths of a second" (B02) | `spike_trap.gd:39`. In the take, trap 1 is lit for 35 frames at 60 fps = 0.583 s, which is WARN_SECONDS 0.40 plus FIRE_SECONDS 0.18; the **ramp** is the first 24. |
| "Red before the player arrives, spikes while they are standing on it" | `test_trap_warning.gd` F6: −33.6 px at the warning, +6.4 px at the strike, hurt box ±13. Identical at 30, 60 and 144 fps. |
| The take is 11.80 s with pauses between traps | `capture_shader.gd` releases the key between legs. The pauses are the key being released; nothing is slowed, looped or retimed, and `SHOTLIST.md` records both window spans. |

## B04 — the driver

| claim | evidence |
|---|---|
| "a sub-resource inside a packed scene is shared by every instance" | `godot/features/traps/trap_warning_driver.gd:62-64` says so in a comment; `test_trap_shader_driver.gd` asserts three **distinct instance ids** after `_ready()`. Without the duplicate the ids would be one. |
| "once a frame, it copies the trap's state into the uniform" | `trap_warning_driver.gd:73-76`, `_process`. |
| "It reads game state and never writes it" | Every reference to `_trap.` in that file is a read; `CHANGE-BRIEF.md` §4 states the boundary. **Not mechanically enforced** — it is a reviewable property of an 88-line file, not an assertion. |
| "setting a name the shader does not declare writes nowhere and reports nothing" | Measured: mutation 2 renamed the uniform, `test_trap_warning.gd` still passed 22/22 and exited **0**, while "the uniform never differed from the state" passed with worst gap 0.000000000. `TEST-REPORT.md`, the mutation table. |

## B05 — one trap at a time

| claim | evidence |
|---|---|
| "seven hundred and nine frames, zero with more than one lit" | `godot/tests/capture_shader.gd`'s probe counts both and prints them. The recorded render says `CAPTURE OK take w: three warnings, 3 hit(s), R6 held every frame`, with `frames sampled: 709` and `frames with >1 trap lit: 0`. Recomputed from the committed log: 709 rows, 0 with more than one trap above zero. |
| "The headless suite asserts the same rule once per scenario" | `test_trap_shader_driver.gd`: "traps 2 and 3 never lit while trap 1 warned", peak 0.000000 over 408 state/uniform pairs. |

## B06 — the hint experiment

| claim | evidence |
|---|---|
| "The same file is bound to both" | `hint_with_source_color.tres` and `hint_without_source_color.tres` each set `bands_srgb` and `bands_data` to `hint_bands.png`. `test_materials.gd` asserts all four sampler slots resolve to one path. |
| "four words on line four — source colour" | `godot/shaders/hint_bands.gdshader:4`. |
| "without it the light would scale the result" | `render_mode unshaded` on line 2. The claim is about what unshaded prevents; the scene also has **no light at all**, asserted by `capture_hint.gd`. |
| "the image is three pixels wide and linear filtering would blend the answer" | 3 × 1 confirmed by `test_materials.gd`. The blending consequence is arithmetic, **not measured** — no capture was taken with linear filtering. |

## B07 — the numbers

| claim | evidence |
|---|---|
| "sixty four, one twenty eight and one ninety two" out; "one thirty seven, one eighty eight, two twenty five" | `captures/a5/HINT-REPORT.txt`, the author's run 2026-10-25: all six exact, worst channel difference 0. |
| "decoding and the display's encoding are inverses" | The explanation in `CHANGE-BRIEF.md` §7, with the sRGB transfer function written out. |
| "predicted in writing two days before anything could render them" | §7 is in the original `CHANGE-BRIEF.md`, committed 2026-10-23. The scene and capture rig are from 2026-10-25. |

## B08 — the textured shader

| claim | evidence |
|---|---|
| "Albedo gets the stone darkened where the mask says water pools" | `dungeon_surface.gdshader:23`. |
| "Roughness is mixed between a dry value and a wet one by the same mask" | `:26`. |
| "in plain GLSL the whole reflectance model would be yours to write" | General, and the author's own answer in `LANGUAGE-NOTES.md` Q8. Not a measurement. |
| "its numbers mean how submerged, not how bright" | `:4` omits `source_color`; `MATERIALS.md` finding 1 explains why that is checked from the source text and not from the engine. |

## B09 — two materials

| claim | evidence |
|---|---|
| "the difference is three values in a text file" | `test_materials.gd`: "they differ in exactly tint, water_darkening, water_roughness". |
| "that highlight is roughness nought point nought eight" | `stone_flooded.tres`, `shader_parameter/water_roughness = 0.08`. |
| "Across twelve sweep captures the dry slime measured fifty, fifty six, fifty five every single time" | `captures/a5/materials/SWEEP-REPORT.txt`: four uniforms × three values, the dry column reads `50, 56, 55` in all twelve rows. |
| "one SHADER line moved both: dry 8 counts, flooded 7" (panel) | `evidence/a5-mutations/shader-edit_report.txt`. The author added `ALBEDO *= 0.5;` and removed it; `git diff HEAD -- godot/shaders/` prints nothing. |

## B10 — the hint the engine cannot see

| claim | evidence |
|---|---|
| "type twenty four, hint seventeen, texture two D … identical" | Probed on 4.7.2 and recorded in `MATERIALS.md` finding 1; `test_materials.gd`'s `_scenario_blind_spot` asserts the two sampler entries are indistinguishable. |
| "On a vector three it can" | Same test: `tint` comes back `TYPE_COLOR` with `PROPERTY_HINT_COLOR_NO_ALPHA` instead of `TYPE_VECTOR3`. |
| "a test built on the uniform list passes while the thing it protects is gone" | Measured: mutations 3a and 3b both left the uniform list **unchanged** and produced **0** `SHADER ERROR` lines. |

## B11 — the silent failure

| claim | evidence |
|---|---|
| "Both quads now read one thirty seven, one eighty eight, two twenty five" | `evidence/a5-mutations/mutation3a-hint-sampler_report.txt`, captured with the mutation in place. |
| "No error, no warning, no change in the uniform list" | Same run: `SHADER ERROR` count 0. `evidence/a5-mutations/mutation3a-hint-sampler_test_materials.log`. |
| "the suite now asserts the blindness itself" | `test_materials.gd`, `_scenario_blind_spot`, with the reason in its docstring. |

## B12 — verdict

| claim | evidence |
|---|---|
| "three shaders and the language notes" written by hand | Commits `f28d2de`, `3225e38`, `d161da9`, `f1109f4`, all authored by TiantongZhang1 with no co-author trailer. `git log -- godot/shaders/` lists four commits, all theirs. |
| "the driver, four test suites, the capture rigs and the material audit" by Claude | `SOURCES.md` §7, and every one of those commits carries the Claude trailer. |
| "eight predicted pixels exact, six predicted bands exact" | `captures/a5/REPORT.txt` and `captures/a5/HINT-REPORT.txt`. |
| "two point zero passed straight through and the pixel went pure red" | Pixel B at `warn_amount = 2.0` measured `255, 0, 0`; a clamp to 1.0 would have given `214, 60, 47`. `CHANGE-BRIEF.md` revision 5.0.4 predicted it first. |
| "R6 held 709 of 709 frames" (panel) | The take's own probe, above. |
| "the slice has no audio and no art beyond code-drawn blocks" | `TEST-REPORT.md` known limitation 3, with the dated decision to port after `a5`. |
| "no normal map, so no curl check" (panel) | `CHANGE-BRIEF.md` §8 says so and says what it forgoes. |

## B13 — your turn

| claim | evidence |
|---|---|
| "predict what the base plate pixel becomes at a warning of nought point five" | The answer exists and is `128, 51, 49` — `CHANGE-BRIEF.md` §6. The narration deliberately does not say it. |
| "capture the frame in engine, not with a screenshot tool" | The assignment's instruction, and `TEST-REPORT.md` records why the engine capture is trusted even though the OS screenshot agreed exactly on this machine. |

---

## What this film shows that no headless run established

Every colour claim above came from a windowed capture on real hardware. The
99 automated checks establish that shaders parse, that uniforms are declared
and driven as specified, and that materials are wired as audited. They
establish nothing about what the screen shows, and the film says so in B12.

## Claims that are reasoning, not measurement

Marked **not measured** above, and repeated here so they are easy to find:

1. That a faded-out trap would ignore the fade if the shader re-sampled the
   texture. No fade exists in the game.
2. That linear filtering would blend the hint bands. The arithmetic is plain;
   no capture was taken with it.
3. That the driver never writes game state. A reviewable property of an
   88-line file, not an assertion.
4. That plain GLSL would make you write the reflectance model. General.
