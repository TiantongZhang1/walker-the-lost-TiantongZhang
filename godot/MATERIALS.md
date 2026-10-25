# MATERIALS.md — Assignment 5 part 3 audit

**Agent draft.** Written without changing any `.gdshader`, material, scene or
`.import` file. Every number below was read out of the engine or the file, not
remembered: the dump that produced it is reproduced by `test_materials.gd`,
which asserts the same facts and exits 1 when one of them moves.

Godot **4.7.2.stable.official** `ed1daf0bf`, **Forward+**, audited
**2026-10-25** from a **fresh cache** (`godot/.godot` deleted, reimported,
0 import errors).

The author's review and corrections are a separate commit, as the assignment
requires.

---

## 1. Materials

| Resource | Shader | Uniform values it sets | Textures it binds |
|---|---|---|---|
| `res://assets/materials/stone_dry.tres` | `res://shaders/dungeon_surface.gdshader` | `tint` `(1, 1, 1, 1)` · `roughness_dry` `0.85` · `water_darkening` `0.00` · `water_roughness` `0.85` | `stone_albedo` → `stone_albedo.png` · `wetness_mask` → `wetness_mask.png` |
| `res://assets/materials/stone_flooded.tres` | same | `tint` `(0.85, 1, 0.9, 1)` · `roughness_dry` `0.85` · `water_darkening` `0.55` · `water_roughness` `0.08` | same two files |
| `res://assets/materials/hint_with_source_color.tres` | `res://shaders/hint_bands.gdshader` | `use_source_color` `true` | `bands_srgb` → `hint_bands.png` · `bands_data` → **the same file** |
| `res://assets/materials/hint_without_source_color.tres` | same | `use_source_color` `false` | same file in both slots |

No material leaves a uniform unset, so none of them is currently showing a
shader default.

The two stone materials differ in exactly **three** values — `tint`,
`water_darkening`, `water_roughness` — which is one more than the assignment
asks for, and matches `CHANGE-BRIEF.md` §8's table. The hint pair differs in
exactly **one**, the bool, which is the point of the experiment.

## 2. Samplers

Hints are quoted **as written in the shader source**, because the engine does
not report them for a sampler — see finding 1.

| Shader | Sampler | Declaration in the source | Bound by every material to | `compress/mode` | `compress/normal_map` | `mipmaps/generate` |
|---|---|---|---|---|---|---|
| `dungeon_surface` | `stone_albedo` | `source_color, filter_linear_mipmap` | `stone_albedo.png` | `2` VRAM Compressed | `2` Disabled | `true` |
| `dungeon_surface` | `wetness_mask` | `filter_linear_mipmap, hint_default_black` | `wetness_mask.png` | `0` Lossless | `2` Disabled | `true` |
| `hint_bands` | `bands_srgb` | `source_color, filter_nearest` | `hint_bands.png` | `0` Lossless | `2` Disabled | `false` |
| `hint_bands` | `bands_data` | `filter_nearest` | `hint_bands.png` | `0` Lossless | `2` Disabled | `false` |

Read with `ConfigFile` from each `.import`'s `[params]` section, not grepped:
a flat key the importer ignores looks the same as a real one in a text search,
and the assignment lists that as a recorded mistake. `test_materials.gd` also
fails on a key that is **absent**, since an absent key means the importer used
its own default and the file never said so.

`hint_bands.png` is 3 × 1 and stores exactly **64, 128, 192**, read back from
the file. `wetness_mask.png` is Lossless on purpose: it is data, and a
block-compressed mask would move the waterline.

**No normal map exists in this project**, so `normal_map_check.gd` and the
curl ratio do not apply. `CHANGE-BRIEF.md` §8 says why and what it forgoes.

## 3. Lights and environment

Everything below changes what a capture measures.

### `res://scenes/asset_showcase.tscn` — the two stone slimes

| | |
|---|---|
| Lights | one `DirectionalLight3D` named `Sun`, **energy 1.0**, white, shadows on |
| Ambient | source 2 (colour), energy **0.25**, `(0.455, 0.443, 0.514)` |
| Background | mode 1, `(0.106, 0.086, 0.125)` |
| Tonemap | **0 — Linear**, exposure **1.0** |
| Off | glow, fog, volumetric fog, adjustments, SSAO, SSR, SDFGI |
| Cameras | `Camera3D` (current, perspective, fov 45) frames A3's three assets; `CameraMaterials` (not current, same fov) frames the two slimes |

Matches §8's "one `DirectionalLight3D` at energy 1.0, ambient 0.25 … SSAO
stays off".

### `res://scenes/hint_experiment.tscn` — the two quads

| | |
|---|---|
| Lights | **none** |
| Ambient | source 0 (background), background black — so nothing adds light |
| Tonemap | **0 — Linear**, exposure **1.0** |
| Off | glow, fog, volumetric fog, adjustments, SSAO, SSR, SDFGI |
| Camera | orthogonal, size 2.0, square on to both quads |

The shader is `render_mode unshaded`, so `ALBEDO` reaches the screen without
being scaled by anything. That plus Linear/1.0 is what makes §7's predicted
band values predictions about the sampler rather than about the lighting.

## 4. Findings

**1 — the engine cannot see `source_color` on a sampler, and F4 depends on
that.** Probed with `get_shader_uniform_list()` on 4.7.2:

```
stone_albedo  type 24  hint 17  hint_string "Texture2D"
wetness_mask  type 24  hint 17  hint_string "Texture2D"
```

Identical, although one declares `source_color` and the other does not. The
same keyword on a `vec3` **is** visible — `tint` comes back as `TYPE_COLOR`
with `PROPERTY_HINT_COLOR_NO_ALPHA` instead of `TYPE_VECTOR3` — which is
exactly what makes the sampler case easy to assume away. A uniform-list
assertion would therefore pass with `source_color` deleted from the colour
sampler, which is the mutation this part exists to fail. `test_materials.gd`
reads the declaration out of the source text, and asserts the blindness
itself so that a later "simplification" back to the uniform list fails loudly.

**2 — `hint_default_black` on `wetness_mask` is not in `CHANGE-BRIEF.md` §8.**
Evidence: `uniform sampler2D wetness_mask : filter_linear_mipmap,
hint_default_black;`. The author added it while writing the shader. It is an
improvement rather than a defect: with no texture bound the sampler returns
black, which for this mask means *dry*, whereas the default white would mean
*every surface fully submerged*. Recorded here because the brief does not
mention it and `SOURCES.md` should say it was the author's.

**3 — `wetness_mask` is bound but inert in `stone_dry.tres`.** With
`water_darkening = 0.00` the mask contributes nothing to `ALBEDO`, and with
`water_roughness = 0.85` equal to `roughness_dry` the `mix()` returns 0.85
whatever the mask says. A reviewer could reasonably call that an unused
texture binding. It is deliberate: the two materials must come from the same
shader with the same samplers filled, and "dry" is expressed as *the mask
turned off by its parameters*, not as *a different shader*. Both materials
sampling the same two files is what makes the side-by-side comparison a
material difference.

**4 — only the body of the second slime is shadered.** `SlimeFlooded`'s
`Slime_Body` carries `stone_flooded.tres`; `Slime_Eye_1` and `Slime_Eye_2`
still carry the imported `A3_SlimeEye` `StandardMaterial3D`. Intentional —
the eyes keep the slime readable as a slime — but it means a capture of that
object shows two materials, only one of which is this assignment's.

**5 — the first slime has no node override, and that is the point.**
`Slime/Slime_Body` reports `override0 = none`: its material arrives on the
**mesh surface** from the importer, through `use_external` on `A3_SlimeBody`
in `slime.glb.import`. That is what the assignment asks for on an imported
scene, and it is what survives a reimport. `test_materials.gd` asserts the
material that comes out of the import, not the setting that asked for it.

**6 — `Sun`'s energy is 1.0 but the scene file does not say so.** 1.0 is the
`DirectionalLight3D` default, so the editor deleted the line on its last save,
along with every `;` comment in the file. §8's "energy 1.0" is therefore
confirmed at runtime only, which is how the audit above read it. The same
mechanism has now removed `renderer/rendering_method` from `project.godot`
three times.

**Nothing inconsistent with `CHANGE-BRIEF.md` §8 was found.** Findings 2 to 6
are things the brief does not mention, not things it contradicts.

## 5. What this audit cannot establish

A headless run uses a dummy renderer and draws nothing. Everything above is a
declared interface, a resource path, a parameter value or an import setting.
**None of it says the materials look right**, that the flooded slime reads as
wet, or that the two hint quads differ on screen. Those are human checks, and
their captures are in `captures/a5/` with the measured band values in
`HINT-REPORT.txt`.

## 6. Attribution

Taken from `CHANGE-BRIEF.md`, which the author wrote and checked.

| | |
|---|---|
| `trap_warning.gdshader`, `dungeon_surface.gdshader`, `hint_bands.gdshader` | **hand-written by Tiantong Zhang.** No agent creates or edits a `.gdshader`; `git diff --stat godot/shaders/` across any agent commit prints nothing |
| `stone_albedo.png`, `wetness_mask.png`, `hint_bands.png` | **written by code** — `godot/tools/write_textures.gd`, committed. The assignment allows this (*"Textures written by code are fine; show the code"*). No download, no licence to track |
| Generative models used for any texture | **none** |
| Third-party textures | **none**, so there is nothing to credit under §8's provenance rules |
| The four `.tres` materials, both scenes, `test_materials.gd`, this file | Claude Code (Claude Opus 5), to §8's specification, reviewed by the author |
| `A3_SlimeBody` / `A3_SlimeEye`, the `.glb` | Assignment 3's own work, built in Blender by the author; `SOURCES.md` §2 records the carry-over |
