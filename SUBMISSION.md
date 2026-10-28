# SUBMISSION.md

**Assignment:** Assignment 5 - Shaders, Materials, and the Godot Shading Language

**Student:** Tiantong Zhang · zhang.tiant@northeastern.edu · GitHub `TiantongZhang1`

**Project name:** The Lost

**GitHub repository URL:** <https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang>

**Git tag and submitted commit SHA:** tag `a5`. The commit the tag points at
cannot be written inside itself; it is in the Canvas note and is recoverable
with `git rev-list -n 1 a5`.

**Game-source revision shown in the film:** `e8aee89` — the revision every
code panel, hash and capture in the film was taken from. Commits after it add
film documentation only and change no file under `godot/`, which
`git diff e8aee89..a5 -- godot/` confirms.

**Godot version, renderer, and operating system:** Godot
**4.7.2.stable.official** `ed1daf0bf`, **Forward+** (Vulkan 1.4.357, NVIDIA
GeForce RTX 5080 Laptop GPU), Windows 11.

**Game state the shader from code communicates:** A spike trap is about to
fire. The trap lies flush with the floor and harmless; for `WARN_SECONDS =
0.40` before the spikes come up it is lethal to stand on. `warn_amount` ramps
0 → 1 across that window in `godot/features/traps/spike_trap.gd` and the
shader mixes the sprite's colour toward `#D63C2F` in one line. The contrast
against the floor goes from 1.12 : 1 to 3.44 : 1, a 3.08× rise.

**3D object and scene given the textured shader:** Two slimes in
`godot/scenes/asset_showcase.tscn` — Assignment 3's model, carried across.
`Slime` takes `stone_dry.tres` from the importer (`use_external` on
`A3_SlimeBody`); `SlimeFlooded` overrides the node with `stone_flooded.tres`.
One `DirectionalLight3D` at energy 1.0, ambient 0.25, SSAO off. The hint
experiment has its own scene, `godot/scenes/hint_experiment.tscn`.

**Texture sources and licences (or model, version, and terms):**

| Texture | Source | Licence |
|---|---|---|
| `stone_albedo.png`, `wetness_mask.png`, `hint_bands.png` | **Written by code** — `godot/tools/write_textures.gd`, committed. The assignment allows this (*"Textures written by code are fine; show the code"*). | Mine. No download, nothing to license. |
| `spike_trap.png`, `spike_trap_fired.png`, `player.png`, `floor_tile.png` | **Written by code** — `tools/make_sprites.py`, committed. The script asserts the two prediction pixels `CHANGE-BRIEF.md` §6 fixed before anything was drawn. | Mine. |
| `slime.glb` and its materials | My own Blender work from Assignment 3, carried across. | Mine. |

**No generative model produced any asset in the game**, so there is no model,
version or terms to record for it, and no third-party texture to credit.

**One generative model is used, and it is the film's narration:** Kokoro TTS,
voice `am_onyx`, run locally at no cost. It supplies the voice only — every
sentence it speaks is written by hand in the beat sheet and checked line by
line in the reel's `FACTCHECK.md`. The outro card's mascot and jingle come
from the course toolkit and are the instructor's. `ATTRIBUTION.md` is the full
accounting, game and film kept apart because the answer differs.

**Final film URL and filename:** `TheLostShaders_TiantongZhang.mp4` — <https://northeastern-my.sharepoint.com/:u:/g/personal/zhang_tiant_northeastern_edu/IQAnbVS5_1aSRKanWn1XDlFrAS2uCaavkNFX0FcELukDiLY?e=0RMDwY>

The compiler writes it under the reel slug as `youtube/claude-liam-walker-the-lost-gamedev/exports/landscape/claude-liam-walker-the-lost-gamedev.mp4`; it was renamed for submission and not re-encoded, so the SHA-256 below is the compiler's own output. 3840 x 2160, 30 fps, 478.0 s, 29.9 MB. The file is **not in this repository** — `.gitignore` keeps MP4s out — so the hash below is how you check that the download is the film this tag describes.

**Final film SHA-256:** `6ee3fb47064b2004caa433bdcbc8bf5d1570669df8f8b06051b26b41829c5c7d`

---

## Verified from a clean clone of the tag

Not from this machine. `git clone --branch a5` into an empty directory, then,
in that directory:

| Step | Result |
|---|---|
| `./art godot-gamedev --check` (the course checker) | **PASS** — 44 source files, 14 exclusions, 7 components, 6 exact excerpts, 6 code-result pairs |
| `godot --headless --path godot --import` | **0 import errors** from a cold cache |
| `test_materials.gd` 60 | 48 checks, 0 failures |
| `test_trap_warning.gd` 144 | 22 checks, 0 failures |
| `test_trap_shader_driver.gd` 30 | 24 checks, 0 failures |
| `test_input_map.gd` 60 | 5 checks, 0 failures |
| `check_assets_3d.gd` 60 | ALL CHECKS PASSED |
| `scripts/build_lost_ledger.py` | rebuilds `gamedev-evidence.json` **byte-identical** to the committed one |
| `scripts/compose_a5_extras.py` then `scripts/compose_lost_evidence.py` | rebuilds all five evidence cards and both grids **byte-identical** |

**It did not pass the first four times, and that is the point of doing it.**
The machine the film was built on had the right bytes, so every check run
there was green while a clone was unverifiable:

1. `core.autocrlf` rewrote every LF to CRLF on checkout, so the first file
   the checker hashed was 1004 bytes against the 982 it expected.
2. With that fixed, seven files went the other way — they are CRLF in my
   working tree and LF in the repository, and the ledger hashed the bytes on
   disk. They now carry an explicit `text eol=crlf`. **No shader blob was
   rewritten to achieve this**; renormalising them would have put an agent
   commit into `git log -- godot/shaders/`, which is the clearest evidence of
   authorship this assignment has.
3. A `*.gdshader` glob in that fix over-reached onto
   `standard_generated.gdshader`, which Godot wrote with LF. The rule is per
   file because the split is per file.
4. `capture/take-w.mp4` — 342 KB, and the result half of two of the six pairs
   — was excluded by a `*.mp4` rule meant for 4K masters, so the checker
   reported `Missing or escaping source` and a reviewer could verify nothing.
   It is tracked now; the 33 MB frame sequence behind it still is not.

## Summary of my work

I wrote three shaders by hand, line by line, and Claude Code wrote the driver,
the tests and the audits. `git log --format='%h %an' -- godot/shaders/` returns
four commits and all four are mine, with no co-author trailer on any of them.

**The specification came first.** `CHANGE-BRIEF.md` was committed on
2026-10-23, before any shader existed and before the first agent prompt. It
names the colour line, the uniform table, six measurable rules and five
predicted failure cases, and it predicts the pixels two ways because
`source_color` was the thing in question. Four dated revisions record what
changed and why.

**Every prediction was written down before it could be measured, and every one
landed exactly.**

| Predicted, and when | Measured |
|---|---|
| Eight pixel values at `warn_amount` 0.0 / 0.5 / 1.0 (§6, 10-23) and 2.0 (rev 5.0.4, 10-24) | **All eight exact**, worst channel difference 0 |
| Six band values for the hint experiment (§7, 10-23) | **All six exact** |

Those settle two questions the brief left open: `source_color` does **not**
change the value a 2D `canvas_item` shader receives (H1 holds; H2 was out by
20–43 counts per channel), and `hint_range` does **not** clamp a value set
from code — 2.0 passed straight through and pixel B went pure `255, 0, 0`,
where a clamp would have given `214, 60, 47`.

**99 automated checks** across four suites, the trap suites at 30, 60 and 144
fps, all from a fresh cache with zero import errors.

**Four deliberate breakages**, each caught by a different net, which is the
point:

| Mutation | `SHADER ERROR` | What caught it |
|---|---|---|
| semicolon deleted | 2 lines | the wrapper's grep **and** an empty uniform list |
| uniform renamed | none | **only** the uniform-list assertion |
| `source_color` deleted from `bands_srgb` | none | **only** the source text — and the capture, where both quads became identical |
| `source_color` deleted from `stone_albedo` | none | **only** the source text |

No single check catches more than two of those. The third is invisible to
`get_shader_uniform_list()` because **the engine does not report
`source_color` on a sampler at all**, while reporting it plainly on a `vec3` —
which is the finding I am most glad this assignment forced out, and which
`test_materials.gd` now asserts directly so the source-text check cannot be
simplified away later.

**Human checks, done on real hardware.** I played the slice and judged 0.40 s
enough time to react. I took the in-engine captures at four controlled values
and compared one against an OS screenshot: on this machine they agreed
exactly, which was not expected, and `TEST-REPORT.md` says why the engine
capture is still the one to trust.

**The film** pairs each code excerpt with the thing it produces on screen,
**six times**, across 18 beats, and its evidence ledger passes the course
checker: 44 source files, 14 exclusions, 7 components, **6 exact excerpts, 6
code-result pairs**. The warning is shown as real motion from a 4K take whose
own driver counted **0 of 709 frames** with more than one trap lit. Five of
the six results are full-frame evidence cards that put an engine capture above
its own recorded report, every figure read out of that report at build time
and drawn verbatim — change a report and the card changes with it.

## Known limitations

1. **The slice has no audio and no art beyond code-drawn blocks.** The art
   and audio from `walker-ninja` were deliberately not carried across:
   Assignment 5's boundaries put the player, the HUD and the audio outside
   this change, and "boundaries kept" is a scored line. The port is
   Assignment 6's first work, dated 2026-10-24 in `FRICTIONAL.md`. The trap's
   sprite never comes across — §6 fixed its pixels before it was drawn.
2. **No normal map, so no curl check.** `CHANGE-BRIEF.md` §8 chose
   code-written textures, which forgoes the Poly Haven calibration pair the
   check needs. Said plainly there rather than discovered here.
3. ~~**One human judgement is still open.**~~ **Closed 2026-10-28.**
   Whether any setting in the interface sweep *breaks* the look rather than
   merely changing it, judged by looking at the twelve sweep captures in
   `captures/a5/materials/`: **`tint` at 0 breaks the look; the other three only change it.** Tint at zero is not a darker stone, it is no stone -- the albedo is multiplied to black and the texture goes with it, and the flooded slime reads as a silhouette. `roughness_dry` at 0 is the next most extreme (flooded mean 32, 43, 39, the lowest of the twelve) and it still reads as stone, just a very wet one. `water_darkening` and `water_roughness` move the surface across their whole range without ever leaving it.

   It is listed here rather than quietly deleted because it was a known
   limitation of this submission for four days, and the date it closed is
   part of the record.
4. **The retrigger exploit.** A player who steps off the detection zone and
   back on restarts the warning every time and is never hit. Accepted in
   revision 5.0.1 as the price of "every trigger gets its own full warning".
5. **Six claims in the film are reasoning, not measurement**, and
   `FACTCHECK.md` lists them in one place rather than leaving them mixed in.
   It was four until B03A and B11A were written on 2026-10-28, each of
   which added one. The easy move was to leave the list at four so the
   verdict panel stayed accurate; the panel was corrected instead.
6. **`CLAUDE.md` was drafted by the session that built the repository**, not
   by a cold agent, which makes it more accurate and therefore a weaker thing
   for my review to test. `tools/check_claude_refs.py` asserts all 50 claims
   in it by content; it has caught seventeen drifts, three of which a bare
   `:NN` reference had hidden from it entirely.

## Changed games since Assignment 2

**Yes.** On 2026-10-17, using the course's one permitted change of game, with
the written justification in `FRICTIONAL.md`. Assignments 1–3 were submitted
from `walker-ninja-TiantongZhang` under the tags `a2-submitted` and `a3`, and
that repository has not been modified since. Per the rule the tags continue
here, and `a5` is this repository's first tag.
