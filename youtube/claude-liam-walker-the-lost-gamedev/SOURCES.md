# SOURCES.md — where every frame and every file in this film came from

The repository's own `../../SOURCES.md` records the game's provenance. This
file records the **film's**: the captures, their hashes, the revision they
were taken at, and the documentation consulted. No secrets, no `.env`, no
absolute developer paths inside anything reusable.

Source revision **`0b45339`**. Godot **4.7.2.stable.official** `ed1daf0bf`,
**Forward+**, Vulkan 1.4.357, NVIDIA GeForce RTX 5080 Laptop GPU, Windows 11.

---

## 1. Native engine captures

| File | What it is | sha256 |
|---|---|---|
| `capture/take-w.mp4` | 3840 × 2160, 60 fps, 362 frames, 6.03 s, engine audio carried through | `7cf23f5e2d23dcaa197095797937300ca82340908b7b13cbc80eb8a058c59800` |
| `capture/logs/take-w-inputs.jsonl` | 361 rows: game time, player x, all three `warn_amount` values | recorded by the take itself |

**Method.** `scripts/render_takes.py w --driver res://tests/capture_shader.gd`,
which writes a temporary `godot/override.cfg` because Movie Maker fixes its
output size from the window size at engine startup — before `--resolution`
and before any script runs. Without it the same command silently records
1280 × 720. The override is removed when the render finishes.

**Nothing was teleported.** The only input is `KEY_D` held through the real
input map. No position or velocity is written, and no state is set. The
driver asserts its own outcome and the render is only evidence because it
printed `CAPTURE OK`.

**Time intervals used.** B03 takes 1.40–2.45 s; B05 takes 1.40–4.70 s. Both
are windows on the one take, not separate recordings, and the beat sheet says
so in `window_s`.

## 2. Still captures, taken before this film

All four were produced for `TEST-REPORT.md` and are reused here with their
hashes. Same build, same hardware, same renderer.

| In the reel | Original | Taken |
|---|---|---|
| `media/B07-hint-experiment.png` | `captures/a5/hint_experiment.png` | 2026-10-25, `tools/capture_hint.gd` |
| `media/B09-two-materials.png` | `captures/a5/materials/00-baseline.png` | 2026-10-25, `tools/capture_materials.gd` |
| `media/B11-hint-mutated.png` | `evidence/a5-mutations/mutation3a-hint-sampler_capture.png` | 2026-10-25, same rig with the mutation in place |

Hashes for all three are in `gamedev-evidence.json` under `code_result_pairs`.

**B11 is a capture of deliberately broken source.** The shader was restored
immediately afterwards; `git diff HEAD -- godot/shaders/` prints nothing. The
beat says out loud that the source was mutated.

## 3. Why in-engine and not a screenshot tool

An OS screenshot goes through the display colour profile and desktop scaling.
`get_viewport().get_texture()` reads the rendered frame before any of that.

The comparison was made once and recorded: on this machine the OS screenshot
agreed **exactly** — 728 pixels of `214, 60, 47`, no shift. That was not
expected. It held because of four properties of this desktop (100 % scaling,
sRGB with no transform, no HDR, nearest filtering at an integer 2×), none of
which are properties of the game. One agreeing sample shows a method was
sound once, not that it is sound. `TEST-REPORT.md` carries the reasoning.

## 4. Art, audio and models

| | |
|---|---|
| Sprites in the take | **Written by code** — `tools/make_sprites.py`, committed. The script asserts the two prediction pixels and fails if a future edit moves them. |
| Textures in the hint and material beats | **Written by code** — `godot/tools/write_textures.gd`, committed. |
| The slime | Assignment 3's own Blender work by the author; carried across with `asset_showcase.tscn` and credited in `../../SOURCES.md` §2. |
| Generative models used for anything in this film | **None.** |
| Third-party textures or audio | **None**, so there is nothing to license. |
| Narration | Local Kokoro, voice `am_onyx`. No paid call. |
| Music on the outro | The existing stock jingle the locked outro supplies. Nothing new. |

## 5. Documentation actually consulted

Read while building this film, not cited from memory:

- Godot 4 *Spatial shaders*, Fragment built-ins — confirmed `COLOR` is
  `in vec4` in `fragment()` and `inout` in `vertex()`, "COLOR that comes from
  the `vertex()` function". Consulted 2026-10-25.
- Godot 4 *CanvasItem shaders*, Vertex and Fragment built-ins — confirmed
  `COLOR` in `vertex()` is the primitive colour times modulate and
  self-modulate, and that the fragment value is that *multiplied by the
  `TEXTURE` colour*; `TEXTURE` is not available in `vertex()`. Consulted
  2026-10-25.

Both settle claims the film makes out loud in B02 and B08.

## 6. Human and AI contribution

| | |
|---|---|
| **The author, Tiantong Zhang** | All three hand-written shaders; every mutation and restore; the in-engine captures of §2 and the playtest behind them; `LANGUAGE-NOTES.md`; the decisions recorded in `CHANGE-BRIEF.md` revisions. Four commits touch `godot/shaders/` and all four are theirs with no co-author trailer. |
| **Claude Code (Claude Opus 5)** | The material driver, four test suites, three capture rigs, the material audit, this film's beat sheet, ledger and documents. |
| **Godot's editor** | `godot/shaders/standard_generated.gdshader`, saved unedited. Neither the author's nor Claude's. |

## 7. What a reviewer should check first

1. `python -I scripts/build_lost_ledger.py` — rebuilds the ledger from the
   repository and refuses if any panel's text has drifted from its file.
2. `./art godot-gamedev --check <reel> --game <project>` — hashes, inventory,
   source lines, associations. Needs `PYTHONUTF8=1` on a non-UTF-8 locale.
3. `git log --format='%h %an' -- godot/shaders/` — every commit, one author.
4. `FACTCHECK.md` — one row per spoken claim, including the four that are
   reasoning rather than measurement.
