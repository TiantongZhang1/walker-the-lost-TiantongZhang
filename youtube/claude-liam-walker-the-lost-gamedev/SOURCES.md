# SOURCES.md — where every frame and every file in this film came from

The repository's own `../../SOURCES.md` records the game's provenance. This
file records the **film's**: the captures, their hashes, the revision they
were taken at, and the documentation consulted. No secrets, no `.env`, no
absolute developer paths inside anything reusable.

Source revision **`e8aee89`**. Godot **4.7.2.stable.official** `ed1daf0bf`,
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

## 2. The five evidence cards

Each is a full-frame 3840 x 2160 PNG composed by
`scripts/compose_lost_evidence.py` from an engine capture plus the recorded
report that goes with it, and rendered as a STILL with `motion: "hold"`.
Nothing is retouched: the capture is pasted at its own pixels and the table
beneath it is read out of the report file at build time and drawn verbatim.
Change a report and the card changes with it.

| In the reel | Capture it frames | Numbers it draws | Capture taken |
|---|---|---|---|
| `media/B03A.png` | `captures/a5/controlled_grid.png` — the four controlled values, 2x2 | `captures/a5/REPORT.txt` | 2026-10-24, `godot/tools/capture_rig.gd` |
| `media/B07.png` | `captures/a5/hint_experiment.png` | `captures/a5/HINT-REPORT.txt` | 2026-10-25, `godot/tools/capture_hint.gd` |
| `media/B09.png` | `captures/a5/materials/00-baseline.png` | `captures/a5/materials/SWEEP-REPORT.txt` | 2026-10-25, `godot/tools/capture_materials.gd` |
| `media/B11.png` | `evidence/a5-mutations/mutation3a-hint-sampler_capture.png` | `evidence/a5-mutations/mutation3a-hint-sampler_report.txt` | 2026-10-25, same rig with the mutation in place |
| `media/B11B.png` | `captures/a5/materials/sweep_grid.png` — four uniforms, both ends | `captures/a5/materials/SWEEP-REPORT.txt` | 2026-10-25, `godot/tools/capture_materials.gd` |

The two grids (`controlled_grid.png`, `sweep_grid.png`) are laid out by
`scripts/compose_a5_extras.py` from captures already committed; it crops and
tiles and alters no pixel value.

Hashes are in `gamedev-evidence.json` under `code_result_pairs`.

**B11 is a capture of deliberately broken source.** The shader was restored
immediately afterwards; `git diff HEAD -- godot/shaders/` prints nothing. The
beat says out loud that the source was mutated.

**Why these are cards and not `GodotDevWorkbench` asset beats** is in
`SHOTLIST.md`: the workbench's own check forbids a non-source table in its
code panel, and its chrome would label an engine capture a reconstruction.

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
| The slime | Assignment 3's own Blender work by the author; carried across with `asset_showcase.tscn` and credited in `../../SOURCES.md` section 2. |
| Every frame of the film | Composed by committed code: the five evidence cards by `scripts/compose_lost_evidence.py`, the two footage frames by `scripts/frame_footage_beats.py`, the eleven graphic beats by the toolkit's Remotion components. No image model produced any frame. |
| Third-party textures or images | **None**, so there is nothing to license. |
| **Narration** | **A generative model: Kokoro TTS, run locally, voice `am_onyx`**, through the toolkit's `generate_audio_kokoro.py`. Every word it speaks is written in `beat_sheet.json` as `narration_text`; the model supplies the voice and nothing else. No paid call and no cloud call. |
| Music on the outro | The stock jingle the locked `ClaudeTitleOutro` card supplies, from the toolkit. Nothing new, and no existing music. |
| The outro mascot | Drawn by the same locked card, seeded from the reel slug. From the toolkit. |

**On "no generative model".** `../../SOURCES.md` section 5 says no generative
model produced any asset **in the game**, and that is still true: every sprite,
texture and model under `godot/` is either code-written or the author's own
Blender work. The film is a different matter and is recorded as such — the
narration audio is a neural TTS model's output. Saying "none" of the film would
have been wrong, and an earlier draft of this table did say it two rows above
the row naming Kokoro.

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

1. `python -X utf8 scripts/build_lost_ledger.py` — rebuilds the ledger from
   the repository and refuses if any panel's text has drifted from its file.
   From a clean clone of `a5` it rewrites `gamedev-evidence.json`
   byte-identically. (`-I` is wrong here: it implies `-E`, which drops
   `PYTHONUTF8`, and `dungeon_surface.gdshader` carries Chinese comments.)
2. `./art godot-gamedev --check <reel> --game <project>` — hashes, inventory,
   source lines, associations. Needs `PYTHONUTF8=1` on a non-UTF-8 locale.
3. `git log --format='%h %an' -- godot/shaders/` — every commit, one author.
4. `FACTCHECK.md` — one row per spoken claim, including the four that are
   reasoning rather than measurement.
