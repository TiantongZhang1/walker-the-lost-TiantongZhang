# SOURCES.md — where everything in this repository came from

Every tracked file falls into exactly one section below. A reader should be
able to take any file and find it here.

**"I" is Tiantong Zhang. "Claude" is Claude Code.** They are scored apart, so
they are never blended.

---

## 1. Starter code

None in this repository. The Assignment 1 starter,
[walker-jumpman](https://github.com/nikbearbrown/walker-jumpman), is credited in
`walker-ninja-TiantongZhang`, which is where it was actually used. Its
`SOURCES.md` states that public availability is not a licence grant for its
inherited art; nothing of its art is here.

## 2. Carried over from walker-ninja-TiantongZhang

My own earlier work in this course, **copied, not moved**.
`walker-ninja-TiantongZhang` has not been modified, and the `a3` tag still
hashes exactly what it hashed at submission.

| File | What it is | When |
|---|---|---|
| `godot/assets/models/slime.glb` | Assignment 3 asset, built by me in Blender through the MCP | copied 2026-10-23 |
| `godot/assets/models/spike_trap.glb` | Assignment 3 asset, same | copied 2026-10-23 |
| `godot/assets/models/torch.glb` | Assignment 3 asset, same | copied 2026-10-23 |
| `godot/assets/models/*.glb.import` | their import settings | copied 2026-10-23 |
| `godot/scenes/asset_showcase.tscn` | the Assignment 3 3D scene | copied 2026-10-23 |
| `godot/tests/check_assets_3d.gd` | Assignment 3's geometry check | copied 2026-10-23 |
| `scripts/`, `tools/` | the film and evidence build chain | copied 2026-10-17 |
| `run-game.bat`, `.gitignore` | infrastructure | copied 2026-10-17 |

Assignment 5 says to do its parts 3 and 4 "in the 3D scene you added in
Assignment 3 or 4", so this is that scene. `TOOLCHAIN.md` classifies every
copied script as generic, needing reshaping, or kept only as a reference.

The Blender build scripts that produced the three `.glb`
(`tools/blender/build_*.py`) came across too; they were written by Claude and
run by me in Blender during Assignment 3, and are documented there.

## 3. Original work — mine, not generated

| File | |
|---|---|
| `CHANGE-BRIEF.md` | the Assignment 5 specification. The colour line and several rules were proposed by Claude and are tagged **[proposal]** in the file; I adopted them, typed them in, and must be able to explain them. The decisions in Revision 5.0.1 are mine. |
| `../the-lost-gdd/GDD.md` | the game's design (Assignment 4). Not yet in this repository; it moves into `design/`. |
| `godot/shaders/trap_warning.gdshader` | **written by me, 2026-10-24, commit `f28d2de`** — on its own, before the driver existed. Four lines of my own typing from `CHANGE-BRIEF.md` §2; the colour line is the **[proposal]** I adopted there and can explain. Claude reviewed a draft of it in chat and listed six errors (a misspelt `shader_type`, a shader *mode* filled in as if it were a name, a stray backtick, `==` for `=`, and `warm_` for `warn_` twice); I fixed all six and typed the file myself. It did not write or edit the file. |
| `godot/shaders/hint_bands.gdshader` | **written by me**, the same way — the two samplers of `CHANGE-BRIEF.md` section 7, one with `source_color` and one without. |
| `godot/shaders/dungeon_surface.gdshader` | **written by me**, the same way — two samplers and four non-texture uniforms in two `group_uniforms` groups, to section 8's table. Its comments are in Chinese, which is why the toolkit's checker needs `PYTHONUTF8=1`. |
| All four `.gdshader` | No agent creates, edits or reformats one. `CLAUDE.md` states this; `git diff --stat godot/shaders/` across any agent commit is the check, and `git log --format='%h %an' -- godot/shaders/` returns four commits, all mine, with no co-author trailer. |
| `LANGUAGE-NOTES.md` | **written by me**, in my own words, partly in Chinese. An agent may check that its line references point where it says; it does not write the answers. |
| `godot/shaders/standard_generated.gdshader` | **neither mine nor Claude's — Godot wrote it.** Produced by the editor's *Convert to ShaderMaterial* on a StandardMaterial3D with albedo, normal-map and roughness textures enabled, as Assignment 5 Step 4 instructs, and saved unedited. Nothing in the game loads it; it exists to be read and cited in `LANGUAGE-NOTES.md`. The scratch scene that produced it was discarded. |

## 4. Written by code

Not "generated" in the generative-model sense — these are drawn by a script
that is committed, so their provenance is the source.

| File | Written by | Why |
|---|---|---|
| `godot/assets/sprites/spike_trap.png` | `tools/make_sprites.py` | `CHANGE-BRIEF.md` §6 fixed the trap's colours *before* anything was drawn, so the hand-computed pixel predictions describe the sprite rather than the reverse. The script asserts both prediction pixels and fails if a future edit moves them. |
| `godot/assets/sprites/spike_trap_fired.png` | same | the spikes driven out |
| `godot/assets/sprites/floor_tile.png` | same | flat `#16242B`, the background §6 assumes |
| `godot/assets/sprites/player.png` | same | 16 × 28 px = 1.75 m at 16 px = 1 m |
| `godot/assets/textures/stone_albedo.png` | `godot/tools/write_textures.gd` | the wet dungeon stone's colour; sampled as colour, with `source_color` |
| `godot/assets/textures/wetness_mask.png` | same | where water pools; a scalar per texel, sampled as **data**, deliberately without `source_color` |
| `godot/assets/textures/hint_bands.png` | same | 3 x 1 px, texels 64 / 128 / 192, imported lossless with no mipmaps — the hint experiment's whole input |

No normal map, by the decision in `CHANGE-BRIEF.md` section 8: code-written
textures forgo the Poly Haven calibration pair, so Step 3's curl check does
not apply. That cost is in the specification rather than discovered here.

## 5. Generated by a model

**Nothing in the game.** No generative model produced any file under `godot/`:
every texture and sprite is written by the committed scripts in section 4 and
every model is my own Blender work from Assignment 3. A5's asset libraries and
3D generators were not used at all.

**One generative model is used in the film**, and it is the narration:
**Kokoro** text-to-speech, voice `am_onyx`, run locally through the course
toolkit at no cost. It supplies a voice and nothing else — every sentence is
written by hand in the film's `beat_sheet.json` and checked line by line in
its `FACTCHECK.md`. The outro card's mascot and jingle come from the toolkit
and are the instructor's.

`ATTRIBUTION.md` is the full licence accounting and keeps the game and the
film apart, because the answer differs between them. No prompt anywhere here
names a living artist, a brand, a copyrighted character or existing music.

## 6. Placeholders

None. Every asset here is the real one.

## 7. Written by Claude, reviewed by me

Claude Code assistance is expected for everything except the shaders and the
language notes. What it wrote:

| File | |
|---|---|
| `godot/features/traps/spike_trap.gd` | the trap's state machine, to `CHANGE-BRIEF.md` |
| `godot/features/player/player.gd` | move, jump, `take_damage` |
| `godot/features/*/**.tscn`, `godot/game/main.tscn` | the scenes |
| `godot/tests/test_trap_warning.gd` | the R1–R6 test |
| `godot/features/traps/trap_warning_driver.gd` | the driver: reads `warn_amount`, writes the uniform. Never writes game state. |
| `godot/tests/test_trap_shader_driver.gd` | the driver and uniform-interface test, 24 checks |
| `godot/tests/test_input_map.gd` | the input-map smoke test |
| `godot/tools/setup_input_map.gd` | one-off, wrote the input map through the engine |
| `tools/make_sprites.py` | the sprite script |
| `scripts/run-test.sh` | adapted from the assignment's version for this machine |
| `CLAUDE.md` | **the agent draft.** My review and corrections are committed separately, as the assignment requires. |
| `TOOLCHAIN.md`, `README.md`, this file | documentation |

## 8. Tools

| | |
|---|---|
| Godot | 4.7.2.stable.official `ed1daf0bf`, Forward+ |
| Blender | 5.2.2 LTS — used in Assignment 3; the three `.glb` it produced are here, carried across with `asset_showcase.tscn` |
| Python | with Pillow, for `tools/make_sprites.py` |
| Claude Code | Claude Opus 5 |

## 9. What a reader should check first

1. `git log --oneline` — the order the work happened in, which is the evidence
   of who wrote which lines.
2. `git diff --stat godot/shaders/` across any agent commit — must be empty.
3. `tools/make_sprites.py` — run it; it re-derives the sprites and asserts the
   prediction pixels in `CHANGE-BRIEF.md` §6 still hold.
4. `CHANGE-BRIEF.md`'s commit date against the first `.gdshader` commit date.
