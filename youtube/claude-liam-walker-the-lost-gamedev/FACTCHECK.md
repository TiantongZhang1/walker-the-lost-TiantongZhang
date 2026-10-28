# FACTCHECK.md — every number the film says out loud, and where it came from

One row per spoken claim. "Where" is a file a reviewer can re-read or a
command they can re-run, not a memory of having seen it. Paths are relative to
the repository root unless they start with `godot/`.

Source revision `e8aee89`. Godot **4.7.2.stable.official** `ed1daf0bf`,
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

## B03A — the four controlled values

| claim | evidence |
|---|---|
| "Nought. Nought point five. One. And two" | `captures/a5/REPORT.txt`, rows at `warn_amount` 0.0, 0.5, 1.0 and 2.0; the frames are `captures/a5/warn_0_0.png`, `warn_0_5.png`, `warn_1_0.png`, `warn_2_0.png`, written by `godot/tools/capture_rig.gd` in a real windowed run on 2026-10-24. |
| "All eight pixel values were written into the brief before the capture rig existed" | The 0.0 / 0.5 / 1.0 rows are `CHANGE-BRIEF.md` §6, committed 2026-10-23. The 2.0 row is revision 5.0.4, dated 2026-10-24 and written **before** the rig could run — the revision says so in its own first line. |
| "all eight landed exact — worst channel difference, zero" | `captures/a5/REPORT.txt`: every `delta` column reads `+0, +0, +0`, and the report's own summary line is `worst channel difference: 0`. |
| "Two point zero went straight through the hint" | Pixel A measured `255, 78, 43` and pixel B `255, 0, 0`, both matching revision 5.0.4's prediction. A clamp to 1.0 anywhere between `set_shader_parameter` and the shader would have given `214, 60, 47` for both. |
| "two of the spike tip's channels go negative, the write to COLOR clamps them" | `mix(c, w, 2.0)` is `2w − c`; for pixel B that is G `−0.0941` and B `−0.2627` before the clamp at `COLOR.rgb`. The arithmetic is revision 5.0.4's table and it reproduces §6's three existing rows exactly, so it is the brief's own formula extended rather than a second method. |
| "a result no other explanation produces by accident" | Reasoning, not measurement: it rests on two channels going negative, which only extrapolation does. Listed at the end with the others. |

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

## B11A — what Godot writes itself

| claim | evidence |
|---|---|
| "the only shader here I did not write … saved what Godot produced without touching it" | `godot/shaders/standard_generated.gdshader:1` is the engine's own header: *"Shader automatically converted from Godot Engine 4.7.2.stable's StandardMaterial3D."* `SOURCES.md` §3 records that the scratch scene that produced it was discarded and that nothing in the game loads it. |
| "The Godot shading language is GLSL ES three point oh with the scaffolding taken away" | The Godot 4 *Shading language* page states the basis. **Partly reasoning:** "scaffolding taken away" is a characterisation, supported on screen by the absence of `main()` and by `shader_type` on line 3. |
| "There is no main function anywhere in this file" | `grep -c "void main" godot/shaders/standard_generated.gdshader` returns 0. |
| "Line three declares a shader type instead" | `standard_generated.gdshader:3` — `shader_type spatial;`, highlighted on screen at that line number. |
| "that one word decides which built-ins exist and which outputs you are allowed to write" | Godot 4 *Shading language*: the shader type selects the built-in set. Demonstrated inside this repository too — `trap_warning.gdshader:1` is `canvas_item` and writes `COLOR`; `dungeon_surface.gdshader:1` is `spatial` and writes `ALBEDO`. |
| "line seven against line twelve. Both are sampler two D, and both carry a hint" | `standard_generated.gdshader:7` — `uniform sampler2D texture_albedo : source_color, filter_linear_mipmap, repeat_enable;` and `:12` — `uniform sampler2D texture_metallic : hint_default_white, filter_linear_mipmap, repeat_enable;`. Both are inside the 3–12 excerpt on screen. |
| "The metallic texture's hint only says what to assume when no texture is bound" | That is what `hint_default_white` means: the fallback when the sampler has no texture. It performs no sRGB decode, and `source_color` does not appear on that line. |
| "the same split I drew by hand: colour sampler on line three … data mask on line four" | `dungeon_surface.gdshader:3` — `uniform sampler2D stone_albedo : source_color, filter_linear_mipmap;` and `:4` — `uniform sampler2D wetness_mask : filter_linear_mipmap, hint_default_black;`. Both are quoted verbatim in the beat's two notes, and both carry a `hint_default_*` against Godot's own `hint_default_white` — the same hint family, not a loose analogy. |
| "Godot's own generator puts the line in exactly the place I put it" | The comparison above. The decision predates seeing the generated file: `CHANGE-BRIEF.md` §8, committed 2026-10-23, specifies the mask as data *without* `source_color` and says why. |

## B11B — the interface sweep

| claim | evidence |
|---|---|
| "all four of them at both ends … Tint. Dry roughness. Water darkening. Water roughness" | `dungeon_surface.gdshader`, `group_uniforms surface` (`tint`, `roughness_dry`) and `group_uniforms water` (`water_darkening`, `water_roughness`) — the four of `CHANGE-BRIEF.md` §8's table. The card shows each at min and max; the default of each is in the report. |
| "two groups, four uniforms, twelve frames" | `captures/a5/materials/SWEEP-REPORT.txt` has 4 uniforms × 3 values = **12** sweep rows, and `captures/a5/materials/sweep-*.png` is 12 files. An earlier cut of this narration said *sixteen*, counting every PNG in the folder including the baseline, the two material-edit frames and the composed grid — while B09 said twelve, so the film contradicted itself. Corrected 2026-10-28. |
| "across the whole sweep it does not move: fifty, fifty six, fifty five, twelve times" | The `dry` column of all twelve sweep rows in `SWEEP-REPORT.txt` reads `50, 56, 55`. The baseline row reads the same, and the two-material check records `dry 50, 56, 55 -> 50, 56, 55   moved 0`. |
| "Only the flooded one changes" | The `flooded` column in the same table moves for every one of the four uniforms — widest for `tint` (43, 46, 42 → 57, 62, 61) and `roughness_dry` (32, 43, 39 → 52, 60, 56). |
| "it is the one thing in this assignment I am still recording as open" | `TEST-REPORT.md` known limitation 3 and `SUBMISSION.md` limitation 3: whether any setting *breaks* the look rather than merely changing it is a human judgement, and the verdict is not written. Recorded as open rather than quietly dropped. |

## B12 — verdict

| claim | evidence |
|---|---|
| "three shaders and the language notes" written by hand | Commits `f28d2de`, `3225e38`, `d161da9`, `f1109f4`, all authored by TiantongZhang1 with no co-author trailer. `git log -- godot/shaders/` lists four commits, all theirs. |
| "the driver, four test suites, the capture rigs and the material audit" by Claude | `SOURCES.md` §7, and every one of those commits carries the Claude trailer. |
| "eight predicted pixels exact, six predicted bands exact" | `captures/a5/REPORT.txt` and `captures/a5/HINT-REPORT.txt`. |
| "two point zero passed straight through and the pixel went pure red" | Pixel B at `warn_amount = 2.0` measured `255, 0, 0`; a clamp to 1.0 would have given `214, 60, 47`. `CHANGE-BRIEF.md` revision 5.0.4 predicted it first. |
| "R6 held 709 of 709 frames" (panel) | The take's own probe, above. |
| "the slice has no audio and no art beyond code-drawn blocks" | `TEST-REPORT.md` known limitation 3, with the dated decision to port after `a5`. |
| "no normal map, so no curl check" (panel) | `CHANGE-BRIEF.md` §8 says so and says what it forgoes, and names it as the next step rather than as an oversight. |
| "Every texture in this repository was written by code — two committed generators, nothing downloaded, no generative model, nothing to license" | `godot/tools/write_textures.gd` and `tools/make_sprites.py`; `ATTRIBUTION.md` §1 lists all seven files beside the script that draws each. The claim is scoped to **textures** and to the **game**. The film's narration is itself a generative model's output (Kokoro TTS) and is recorded as such in `ATTRIBUTION.md` §2.1 and `SOURCES.md` §5. |
| "one game source revision, e eight a e e eight nine" (panel: `revision e8aee89`) | `SUBMISSION.md` records it, and `git diff e8aee89..a5 -- godot/` confirms every later commit changes film documentation only and no file under `godot/`. |
| "a capture rig that sampled the window's clear colour instead of the frame" | The first of the two mistakes caught in Claude's own work, found by pulling a frame out and looking at it rather than by a check. |
| "a framing pass that … quietly put a card inside a card — which the automatic gate passed" | `scripts/frame_footage_beats.py`, the docstring on `frame_beat()`: the first version read `media/<bid>.mp4` and wrote back to it, so a second run framed its own output. Gate V passed it, because a nested card still fills the frame and still has contrast. Each step now keeps its own input. |
| "Both were found by pulling a frame out and looking at it" | True of both — and of two more found on 2026-10-28, after this line was written: a code panel that clipped half its excerpt, and every Remotion beat freezing at its composition's default length because nothing set `durationSeconds`. `SHOTLIST.md` records the first and `bind_timing_to_audio` in `scripts/build_lost_beat_sheet.py` the second. Neither was caught by a check either. |
| "The next step for the shaders themselves is a normal map" | A stated intention, not a measurement. |

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

Marked **not measured** above, and repeated here so they are easy to find.
This list was **four** until B03A and B11A were written on 2026-10-28, each
of which added one. Leaving them off to keep B12's on-screen count true
would have been the exact dishonesty this section exists to prevent, so the
panel was corrected to **six** and re-rendered instead.

1. That a faded-out trap would ignore the fade if the shader re-sampled the
   texture. No fade exists in the game.
2. That linear filtering would blend the hint bands. The arithmetic is plain;
   no capture was taken with it.
3. That the driver never writes game state. A reviewable property of an
   88-line file, not an assertion.
4. That plain GLSL would make you write the reflectance model. General.
5. That pure red at `warn_amount = 2.0` is "a result no other explanation
   produces by accident" (B03A). The measurement is exact and recorded; the
   claim about *other* explanations is an argument about what else could have
   produced it.
6. That the Godot shading language is "GLSL ES 3.0 with the scaffolding taken
   away" (B11A). The basis is documented; the characterisation is mine, and
   what is on screen supports it rather than proving it.
