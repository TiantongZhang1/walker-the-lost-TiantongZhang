# COMPONENTS.md — the playable system this film takes apart

Seven components, each with where it lives, what enters it, the lines that
matter, what changes, what you see, why it was built that way, and one
trade-off it cost. The ledger in `gamedev-evidence.json` binds each to its
files and beats and hashes all 44 of them.

Godot **4.7.2.stable.official** `ed1daf0bf`, **Forward+**, 640 × 360 logical
at nearest filtering, 16 px = 1 m.

---

## 1. `warning-shader` — the thing being announced · B02, B03, B03A

**Where** `godot/shaders/trap_warning.gdshader`,
`godot/features/traps/spike_trap.{gd,tscn}`

**What enters** One float, `warn_amount`, 0 to 1, written from outside once a
frame. Nothing else. There is no sampler: the sprite's own texture arrives
already multiplied into `COLOR`.

**The lines that matter** `trap_warning.gdshader:6` is the whole effect —
`COLOR.rgb = mix(COLOR.rgb, warn_color, warn_amount)`. The state behind it is
`spike_trap.gd:68`, which advances the ramp from `delta` rather than from a
frame count, and `:39`, which fixes the window at 0.40 s.

**What changes, and what you see** The trap is `#2A2A33` against a `#16242B`
floor — a contrast ratio of 1.12 : 1, very nearly invisible, which is
deliberate. Across the window it reaches `#D63C2F`, 3.44 : 1. The warning
multiplies the ratio by 3.08.

**Why** The game's design rule is that hazards announce themselves. A trap
with no tell is not difficulty, it is a coin flip. The duration has to be the
same at 30, 60 and 144 fps or a player on a fast monitor gets a shorter
warning, which is why the ramp uses seconds.

**Trade-off** `Area2D.body_entered` fires on entry, not continuously, so a
player who steps off the detection zone and back on restarts the warning
every time and is never hit. That is the price of "every trigger gets its own
full warning". It is recorded in `CHANGE-BRIEF.md` revision 5.0.1 as an
accepted exploit rather than discovered later.

**Not shown** `disarm()` and the time-scale behaviour. Both are covered by
`test_trap_warning.gd` R4 and R5 and neither has a visible result worth a
beat.

---

## 2. `material-driver` — how state reaches the GPU · B04, B05

**Where** `godot/features/traps/trap_warning_driver.gd`, a `WarningDriver`
child node of every trap. Tested by `godot/tests/test_trap_shader_driver.gd`.

**What enters** The parent `SpikeTrap`'s `warn_amount`, read.

**The lines that matter** `:65` duplicates the `ShaderMaterial`; `:68` asks
the shader whether the uniform it is about to write exists; `:76` writes it.
`:42` sets `process_priority = 100` so the write happens after the state
machine (priority 0) and before any sampler.

**What changes, and what you see** Without `:65` all three traps share one
material and one `warn_amount`, so triggering one lights all three. With it,
the red moves from trap to trap and the other two stay flush.

**Why** Presentation reads game state and never writes it. The trap does not
know a shader exists; the driver does not know when the trap fires. Either can
be replaced without touching the other.

**Trade-off** One `set_shader_parameter` per trap per frame whether or not the
value changed. Three traps at 144 fps is 432 writes a second for a number that
is 0.0 most of the time. Cheap here; it would not scale to hundreds of
objects, and a dirty flag would be the fix.

---

## 3. `hint-experiment` — what a hint does to a number · B06, B07, B10, B11

**Where** `godot/shaders/hint_bands.gdshader`,
`godot/scenes/hint_experiment.tscn`, two materials in `assets/materials/`,
`assets/textures/hint_bands.png` written by `tools/write_textures.gd`,
captured by `tools/capture_hint.gd`.

**What enters** One 3 × 1 PNG storing 64, 128, 192, bound to **both**
samplers of one shader. A bool picks which one writes `ALBEDO`.

**The lines that matter** `:2` `render_mode unshaded`, without which the light
scales the answer. `:4` declares `source_color`; `:5` does not. That is the
entire independent variable.

**What changes, and what you see** Left quad: 64, 128, 192 — the file's own
numbers. Right quad: 137, 188, 225. Decoding and the display's encoding are
inverses, so the decoding sampler returns what went in; the other hands a
stored value to `ALBEDO` as though it were already linear and the display
encodes it anyway, one encode too many.

**Why** `source_color` is the one hint in this assignment suspected of
changing the value the shader receives rather than only the Inspector. Two
samplers on one file is the only arrangement where nothing else can differ.

**Trade-off** The experiment needs a scene whose entire pipeline is pinned —
Linear tonemap at exposure 1.0, no light, every post effect off. Those are all
engine defaults, so the editor deletes them from the `.tscn` on save.
`capture_hint.gd` therefore asserts all eight at runtime instead of reading
the file, which is more code than reading would have been and is the only
version that survives an editor save.

---

## 4. `textured-surface` — one shader, two materials · B08, B09, B11B

**Where** `godot/shaders/dungeon_surface.gdshader`, `stone_dry.tres` and
`stone_flooded.tres`, two textures and their `.import` sidecars,
`godot/scenes/asset_showcase.tscn`, audited in `godot/MATERIALS.md`.

**What enters** A colour texture sampled **with** `source_color` and a data
texture sampled **without**, plus four parameters in two groups.

**The lines that matter** `:3` and `:4` — the colour/data distinction, which
Godot's own generated shader makes the same way on its lines 7 and 19. `:23`
writes `ALBEDO`, `:26` writes `ROUGHNESS`, and the engine does the lighting
from there.

**What changes, and what you see** Two slimes, identical geometry under
identical light. Three values apart: `water_darkening` 0.00 / 0.55,
`water_roughness` 0.85 / 0.08, tint white / `(0.85, 1, 0.90)`. The flooded one
is darker, green-shifted and carries a sharp highlight the dry one does not.

**Why** The game needs the same stone above and below floor 1's waterline.
Expressing "dry" as *the mask turned off by its parameters* rather than as a
second shader is what makes the comparison a material difference.

**Trade-off** In `stone_dry.tres` the mask is bound but inert: with
`water_darkening` 0 and `water_roughness` equal to `roughness_dry`, it
contributes nothing. A reviewer could fairly call that an unused binding.
`MATERIALS.md` finding 3 states it and defends it.

**The surprising measurement** `roughness_dry = 0.0` makes the stone *darker*,
not shinier: at roughness 0 the surface is a mirror and the background is
nearly black, so a diffuse response is replaced by a reflection of nothing.

---

## 5. `the-room` — what the effect is attached to · B03, B05

**Where** `godot/game/main.{tscn,gd}`, `godot/features/player/player.{gd,tscn}`,
four code-drawn sprites, `project.godot`, `tools/capture_rig.gd`.

**What enters** One held key through the real input map.

**The lines that matter** `player.gd:19` `const SPEED := 96.0`. Trap spacing
112 px, from which the three detection zones are 175–241, 287–353, 399–465 —
no overlap, so R6 can fail if it is wrong.

**What changes, and what you see** A player who walks and jumps, a floor, and
three traps. No combat, no magic, no dodge roll: the brief's boundaries say
movement and input do not change.

**Why** The sprites are drawn by `tools/make_sprites.py` and not by hand,
because `CHANGE-BRIEF.md` §6 fixed the trap's two prediction pixels *before*
anything was drawn. The predictions drive the art rather than describing it.

**Trade-off** The slice has no audio and no character art. Both exist in the
previous repository with provenance already recorded, and both were kept out
deliberately: the player, the HUD and the audio are outside this change's
boundaries. The port is Assignment 6's first job, dated in `FRICTIONAL.md`.

---

## 6. `evidence-harness` — what the claims rest on · B03, B03A, B05, B12

**Where** `godot/tests/test_trap_warning.gd`, `test_input_map.gd`,
`check_assets_3d.gd`, `capture_shader.gd`, run through `scripts/run-test.sh`.

**The lines that matter** `test_trap_warning.gd:33` sets
`process_priority = 1000` so the sampler reads after everything else in the
frame. `run-test.sh:49` greps for `SHADER ERROR`, because Godot prints that
line and still exits 0.

**What it establishes** 99 checks across four suites, the trap suite at 30, 60
and 144 fps. `capture_shader.gd` records the warning as real motion and
asserts its own outcome: three traps fired, three hits, and **0 of 361 frames**
with more than one trap lit.

**Why three frame rates** A duration measured at one rate has not been
measured. A ramp advancing per frame would last 0.40 s at 60, 0.90 s at 30 and
0.19 s at 144 — and would pass a single-rate test.

**Trade-off, and the lesson** The suite once passed 22 of 22 against a shader
that did not parse. It exited 1 only because the wrapper greps the log. No
single check catches all four mutations: the semicolon needs the wrapper, the
rename needs the uniform list, and `source_color` needs the source text.

---

## 7. `generated-reference` — Godot's own answer · B10, B11A, B11B

**Where** `godot/shaders/standard_generated.gdshader`, 48 lines. Nothing
loads it.

**Why it is in the project** Line 7 marks the albedo sampler
`source_color`. Line 12 gives the metallic sampler `hint_default_white` and
no `source_color`, and line 19 does the same for the normal map. That is the
distinction the hand-written shader makes on its own lines 3 and 4 — and on
the same hint family, `hint_default_black` against Godot's
`hint_default_white` — so the engine's own code agrees with the author's,
which is stronger than either alone.

**What B11A shows** Lines 3–12, because the code panel holds about thirteen
wrapped rows and the pair worth comparing (7 against 12) both sit inside
them. The first cut asked for 3–20 and the render clipped at 17, taking the
second half of the comparison with it.

**Provenance** Produced by the editor's *Convert to ShaderMaterial* on a
StandardMaterial3D with albedo, normal-map and roughness textures enabled, and
saved unedited. Neither the author's writing nor Claude's; `SOURCES.md` says
so.

---

## Omissions, and why

`gamedev-evidence.json` lists 14 exclusions with reasons. The ones a reviewer
is most likely to ask about:

- **`MATERIALS.md`** sits inside the Godot project because Assignment 5 names
  that path, but it is a document about the game, not a file the game loads.
- **`tests/route_driver.gd`, `tests/test_keyboard.gd`** came across with
  Assignment 3's files and belong to the previous game's level.
- **`assets/models/torch.glb`, `spike_trap.glb`** appear as scenery in the
  showcase scene; no shader in this assignment touches them.
- **`tools/setup_input_map.gd`** is a one-off that wrote the input map through
  the engine on 2026-10-23.
