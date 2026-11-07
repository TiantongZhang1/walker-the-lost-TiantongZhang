# TEST-REPORT.md — Assignment 5

**Source revision:** `e8aee89`+ · **Godot** 4.7.2.stable.official `ed1daf0bf` ·
**Renderer** Forward+ *(confirmed on hardware 2026-10-24)* · **OS** Windows 11

Every row below is either a recorded result or an explicit **not yet**. Nothing
is marked done that has not been run.

---

## Baseline

Assignment 5 asks for "every earlier test, before and after, with pinned frame
rate and counts". **This repository had no earlier suite.** It was created on
2026-10-17 for the course's one permitted change of game and held no game until
today. The baseline is therefore the suite as it stands at the start of the
shader work, run from a **fresh clone** of `732b5aa` with one `--import`:

| Test | fps | Exit | Result | `SHADER ERROR` lines |
|---|---|---|---|---|
| `test_input_map.gd` | 60 | 0 | 5 checks, 0 failures | 0 |
| `check_assets_3d.gd` | 60 | 0 | ALL CHECKS PASSED (12 measurements) | 0 |
| `test_trap_warning.gd` | 30 | 0 | 22 checks, 0 failures | 0 |
| `test_trap_warning.gd` | 60 | 0 | 22 checks, 0 failures | 0 |
| `test_trap_warning.gd` | 144 | 0 | 22 checks, 0 failures | 0 |

Added after the baseline, with the driver (`480aa8b`):

| Test | fps | Exit | Result | `SHADER ERROR` lines |
|---|---|---|---|---|
| `test_trap_shader_driver.gd` | 30 | 0 | 24 checks, 0 failures | 0 |
| `test_trap_shader_driver.gd` | 60 | 0 | 24 checks, 0 failures | 0 |
| `test_trap_shader_driver.gd` | 144 | 0 | 24 checks, 0 failures | 0 |

Import errors from a clean clone: **0**.

`check_assets_3d.gd` is Assignment 3's own geometry check, copied with the 3D
scene; it passes here unchanged, which is the evidence that the copy arrived
intact.

## R2 — frame-rate independence

Specified: **0.40 s** (revision 5.0.3), tolerance **one frame period**.

| fps | Modal delta (of 40 frames) | Window | Tolerance | |
|---|---|---|---|---|
| 30 | 0.033333 — 39/40 | **0.433 s** | ±0.0333 | pass |
| 60 | 0.016667 — 40/40 | **0.417 s** | ±0.0167 | pass |
| 144 | 0.006944 — 35/40 | **0.403 s** | ±0.0069 | pass |

The overshoot is bounded by one frame because the ramp is checked once per
`_process`, so the window ends on the first frame at or past `WARN_SECONDS`.
It shrinks as the frame rate rises, which is what it should do.

**The frames at 144 fps are not uniform.** 1/144 s is 6944.44 µs and Godot
works in whole microseconds, so the delta alternates between 0.006944 (144 fps)
and 0.006667 (150 fps) with the occasional 0.008. 30, 60 and 240 divide evenly
and are uniform. The test takes the modal delta over 40 frames for this reason.

**The frame period itself was wrong until 2026-10-24.** The test read
`Engine.max_fps`, which `--fixed-fps` does not set, so every run judged itself
against a 60 fps tolerance — 2× too strict at 30, 2.4× too loose at 144. The
durations recorded in earlier revisions were real; the verdict "within one
frame" was not reliably earned. `scripts/run-test.sh` now exports `TEST_FPS`
and the test cross-checks it against the engine's modal delta within 1 %.

Under `Engine.time_scale = 0.5` the window is unchanged in game time, as R4
says.

## F6 — the trap can actually hit someone

Added 2026-10-24 after the author noticed the trap was firing once the player
had already walked past.

| | |
|---|---|
| Player offset when the trap warns | **−33.6 px** (short of the trap) |
| Player offset when the spikes arrive | **+6.4 px** (hurt box is ±13) |
| Health | **5 → 4** |

Identical at 30, 60 and 144 fps.

## Geometry — the derivation is asserted, not maintained

| | |
|---|---|
| `DetectArea` half-width | 33 px; `SPEED × WARN_SECONDS − 5` = 33.4 px |
| Detection zones | 175–241, 287–353, 399–465 — no overlap |

Changing `WARN_SECONDS` without changing the shape now fails the suite.
**22 checks, 0 failures** at each rate.

## The driver, and the shader's declared interface

`test_trap_shader_driver.gd`, added 2026-10-24 with the driver. **24 checks,
0 failures** at 30, 60 and 144 fps.

The shader itself is hand-written (commit `f28d2de`, author's own). Everything
below is what a headless engine will say about it.

| Asked of the engine | Answer |
|---|---|
| `shader_type` | `canvas_item` (`get_mode()` = 1) |
| `warn_amount` | `TYPE_FLOAT`, `PROPERTY_HINT_RANGE`, hint string `0.0,1.0,0.001` |
| `warn_color` | `TYPE_COLOR`, `PROPERTY_HINT_COLOR_NO_ALPHA` |
| Sampler uniforms | 0, as §2 specifies |

**`source_color` is visible to a headless run**, which was not assumed. A
`vec3` carrying it is reported as `TYPE_COLOR` with `COLOR_NO_ALPHA`; a plain
`vec3` comes back as `TYPE_VECTOR3`. Both hints are therefore asserted from
the engine rather than only from the source text. Defaults still are not
reported, so those two checks read the `.gdshader` file and say so.

| In motion, at each frame rate | |
|---|---|
| Uniform reached 1.0 in | **0.417 s** at 60 fps (want 0.400 ± one frame) |
| State/uniform pairs compared | **408** over 136 frames |
| Worst gap between state and uniform, any frame | **0.000000000** |
| Traps 2 and 3 peak uniform while trap 1 warned | **0.000000** |
| `warn_color` after a full cycle | unchanged — the driver animates one uniform |

**F1 is a real trap that was avoided, not a hypothetical.** A sub-resource
inside a `PackedScene` is shared by every instance of that scene, so without
`duplicate()` in `_ready()` the three traps held one `ShaderMaterial`. The
test asserts three distinct instance ids.

**F5 cannot be caught by a round trip.** `set_shader_parameter` on an
undeclared name writes nowhere and reports nothing, and reading it back
returns the stored value, so set-then-get passes on a broken contract. The
driver asks `get_shader_uniform_list()` at startup and the test asserts the
answer.

## The two shader mutations

Assignment 5 Step 2: break the shader twice, confirm the test exits 1, restore
it. The author made both edits; no agent touched `godot/shaders/`. Logs are in
`evidence/a5-mutations/`, and after the restore
`git diff HEAD -- godot/shaders/` printed nothing — the file is byte-for-byte
`f28d2de` again.

| | **1. semicolon deleted** | **2. uniform renamed** |
|---|---|---|
| Edit | `shader_type canvas_item` loses its `;` | `warn_amount` → `warn_level`, both occurrences, so it still compiles |
| `SHADER ERROR` lines | **2** | **0** |
| `test_trap_shader_driver.gd` | 17 checks, **4 failures**, exit **1** | 17 checks, **2 failures**, exit **1** |
| `test_trap_warning.gd` | 22 checks, 0 failures, exit **1** | 22 checks, 0 failures, exit **0** |

```
SHADER ERROR: Expected a ';' after 'shader_type canvas_item'.
```

**Mutation 1 is caught twice over.** A shader that fails to parse returns an
empty uniform list, so `declares warn_amount`, `declares warn_color` and F5 all
fail. But note the second row: **the state suite passed all 22 of its own
checks with a completely broken shader.** It exited 1 only because
`scripts/run-test.sh` greps for `SHADER ERROR` — Godot prints that line and
still exits 0. Without the wrapper this mutation goes by in silence.

**Mutation 2 is the one that matters, because nothing reports it.** The shader
compiles. There is no error line, the wrapper has nothing to grep, and the
state suite exits **0**. The driver writes `warn_amount` into a material whose
shader declares no such uniform; `set_shader_parameter` accepts it and says
nothing. Two assertions catch it:

```
FAIL      declares warn_amount
FAIL  F5  every driver found its uniform declared
```

**And this is why a set-then-get round trip is worth nothing here.** Under
mutation 2, with the trap unable to turn red at all, these still passed:

```
PASS  R2  the uniform took 0.417 s to reach 1.0 (want 0.400 +- 0.0167)
PASS      the uniform never differed from the state in any frame   [worst gap 0.000000000]
PASS      the uniform is back at 0.0 once the trap re-arms
```

`get_shader_parameter` returns what the material stored. It never asks the
shader whether anything reads it. Assignment 5 lists this exact failure under
"What the agent is likely to get wrong"; mutation 2 reproduces it deliberately,
in its quieter form.

**After the restore:** `test_trap_shader_driver.gd` 24 checks / 0 failures and
`test_trap_warning.gd` 22 / 0, both at 30, 60 and 144 fps, all exit 0.

## Controlled values — measured, and what they settle

**Author's run, 2026-10-24 19:56:26**, real windowed run, Forward+ on an
NVIDIA GeForce RTX 5080 Laptop GPU, window 1280 × 720, logical 640 × 360.
Captured in-engine with `godot/tools/capture_rig.gd` (F5), not with a
screenshot tool. Files and the raw report: `captures/a5/`.

| `warn_amount` | Pixel | Measured | H1 predicted | Δ | H2 predicted |
|---|---|---|---|---|---|
| 0.0 | A | `42, 42, 51` | `42, 42, 51` | **0, 0, 0** | — |
| 0.0 | B | `138, 144, 161` | `138, 144, 161` | **0, 0, 0** | — |
| 0.5 | A | `128, 51, 49` | `128, 51, 49` | **0, 0, 0** | `107, 27, 29` |
| 0.5 | B | `176, 102, 104` | `176, 102, 104` | **0, 0, 0** | — |
| 1.0 | A | `214, 60, 47` | `214, 60, 47` | **0, 0, 0** | `171, 12, 7` |
| 1.0 | B | `214, 60, 47` | `214, 60, 47` | **0, 0, 0** | — |
| 2.0 | A | `255, 78, 43` | `255, 78, 43` | **0, 0, 0** | — |
| 2.0 | B | `255, 0, 0` | `255, 0, 0` | **0, 0, 0** | — |

**Worst channel difference across all eight: 0.** Nothing to explain, which
is only worth saying because the predictions were committed first — §6 on
2026-10-23, the 2.0 row as revision 5.0.4 earlier on 2026-10-24, both before
the rig existed.

Two open questions close here.

**§6 — does `source_color` change the value the shader receives?** No, not in
a 2D `canvas_item` shader with HDR 2D off. **H1 holds; H2 is refuted by 20 to
43 counts per channel**, far outside any rounding. `COLOR` carries the
texture's stored values, the uniform arrives as written, and the mix happens
in one space. Note that this is a statement about the *value*, not about the
hint being inert: the engine still reports the uniform as `TYPE_COLOR` with
`PROPERTY_HINT_COLOR_NO_ALPHA` rather than `TYPE_VECTOR3`.

**§10 — does `hint_range` clamp a value set from code?** No. `2.0` passed
through `set_shader_parameter` untouched and `mix()` extrapolated past
`warn_color` instead of stopping at it. Pixel B is the decisive one: two of
its three channels go negative before the write to `COLOR.rgb` clamps them,
so a real extrapolation produces pure `255, 0, 0` — which is what was
measured. A clamp at 1.0 would have produced `214, 60, 47`.

## In play, and the OS-screenshot comparison

**The author played the slice on 2026-10-24** — walked into all three traps
with A/D and jump, repeatedly, and judged the warning:

> **0.40 s is enough time to react.**

So revision 5.0.3's duration stands, and §11's open question ("whether 0.40 s
is actually enough warning … cannot be made before the slice is playable")
closes. It was unanswerable until today, because the red did not exist.

`captures/a5/os-screenshot_in-play.png` is an OS screenshot of one live frame
during that session, taken by hand with Snipping Tool. It was not posed: it
caught trap 1 mid-strike with the player already past it.

### R6, proved again without any instrument

Three traps in one real frame, sampled out of that screenshot:

| Trap | Measured | |
|---|---|---|
| 1 | `214, 60, 47` — all 28 sampled pixels, one value | `warn_amount` = 1.0 |
| 2 | `138, 144, 161` and `42, 42, 51` | `warn_amount` = 0.0 |
| 3 | `138, 144, 161` and `42, 42, 51` | `warn_amount` = 0.0 |

Traps 2 and 3 are reading §6's `warn_amount = 0.0` row exactly. This is F1
failing to happen in ordinary play, with no capture rig, no headless run and
no synthesized input — the strongest form of that evidence in this report.

### Engine capture against OS screenshot

| | Pixel colour |
|---|---|
| In-engine capture at `warn_amount` = 1.0 | `214, 60, 47` |
| OS screenshot, live frame | **`214, 60, 47`** — 728 pixels, a single value |

**They agree exactly, which was not expected** — the assignment warns that an
OS screenshot goes through the display colour profile and desktop scaling.
Here it did not: 100 % scaling, an sRGB profile with no transform, no HDR, and
nearest filtering at an integer 2× means the tool copied framebuffer values
through unchanged. There is no anti-aliasing in the sample either; 728 pixels
share one value.

**Which is trusted: the engine capture.** Not because the screenshot was
wrong this time, but because its being right depended on four conditions that
are properties of this desktop rather than of the game. Change the scaling,
enable HDR, attach a wide-gamut display or switch capture tools and the same
pixel moves, with nothing announcing it. `get_viewport().get_texture()` reads
the rendered frame before any of that applies. One agreeing sample is not
evidence that a method is sound; it is evidence that it was sound once.

## Part 3 - the textured shader, the materials, the hint experiment

`test_materials.gd`: **48 checks, 0 failures**, run from a **fresh cache** -
`godot/.godot` deleted, reimported, **0 import errors**. `.import` files are
parsed with `ConfigFile`, and an *absent* key fails as well as a wrong one,
because absent means the importer used its own default and the file never
said so.

The full audit - every material's uniform values, every sampler's hints, six
findings - is `godot/MATERIALS.md`.

### The hint experiment, measured

Real windowed run, Forward+ on an RTX 5080, 2026-10-25. Scene:
`godot/scenes/hint_experiment.tscn`; capture and report in `captures/a5/`.

| Stored in the file | With `source_color` | Predicted | Without | Predicted |
|---|---|---|---|---|
| 64 | **64** | 64 | **137** | 137 |
| 128 | **128** | 128 | **188** | 188 |
| 192 | **192** | 192 | **225** | 225 |

**All six exact.** §7's reasoning holds: the decoding sampler and the display
encode are inverses, so the number that comes out is the number that went in;
the other sampler never decodes, the display encodes anyway, and every band
is one sRGB encode too bright.

`capture_hint.gd` asserts the pipeline rather than reading the `.tscn` for it
- Linear tonemap, exposure 1.0, glow / fog / volumetric fog / adjustments /
SSAO / SSR / SDFGI off, no light, `render_mode unshaded`. Every one of those
is a default value, so none is written to the scene file and reading it would
prove nothing.

### The third mutation, done twice

§7 and §8 each have a colour sampler, so both were mutated.

| | **3a** `bands_srgb` | **3b** `stone_albedo` |
|---|---|---|
| Edit | `source_color` deleted from the hint shader's colour sampler | deleted from the textured shader's |
| `SHADER ERROR` | **0** | **0** |
| `get_shader_uniform_list()` | **unchanged** | **unchanged** |
| `test_materials.gd` | 48 checks, **1 failure**, exit **1** | 48 checks, **1 failure**, exit **1** |
| The failing check | `bands_srgb declares source_color` | `F4  the COLOUR sampler declares source_color` |

**3a also broke the measurement, visibly.** With the hint deleted the capture
read **137, 188, 225 on both quads**: the two sides of the experiment became
identical and its entire result disappeared. That capture is
`evidence/a5-mutations/mutation3a-hint-sampler_capture.png`.

Both restored afterwards; `git diff HEAD -- godot/shaders/` prints nothing.

### Why three different checks, not one

| Mutation | `SHADER ERROR` | Caught by |
|---|---|---|
| 1 - semicolon deleted | 2 lines | the wrapper's grep, **and** an empty uniform list |
| 2 - uniform renamed | none | **only** the uniform-list assertion |
| 3 - `source_color` deleted from a sampler | none | **only** the shader source text |

No one of those three catches the other two. Mutation 3 is invisible to the
uniform list because **the engine does not report `source_color` on a sampler
at all** - `stone_albedo` and `wetness_mask` both come back as type 24, hint
17, `"Texture2D"`, identical. On a `vec3` the same keyword *is* visible,
which is what makes the sampler case easy to assume away. `test_materials.gd`
asserts that blindness directly, so a later rewrite that replaces the
source-text check with a uniform-list one fails loudly.

### Import settings

**The editor rewrote none of them.** It has now been opened on this project
several times, including sessions that drew the 3D scene. The only `.import`
change in the whole assignment is the `use_external` block this work added to
`slime.glb.import` by hand.

That is not luck: every texture carries `detect_3d/compress_to=0`, set when
the textures were written, which is the setting that otherwise makes the
editor rewrite `compress/mode` the first time a texture is drawn in 3D. There
is no editor-written diff to explain.

### The interface sweep

`capture_materials.gd`, real windowed run 2026-10-25, under §8's lighting:
one `DirectionalLight3D` at energy 1.0, ambient 0.25, SSAO off. Each of the
four uniforms set to minimum, shipped value and maximum **on
`stone_flooded.tres` only**, one PNG per step in `captures/a5/materials/`.
The number is the mean colour of that slime's middle region.

| Uniform | min | shipped | max |
|---|---|---|---|
| `tint` | `43, 46, 42` at black | `53, 62, 58` at `(0.85, 1, 0.9)` | `57, 62, 61` at white |
| `roughness_dry` | **`32, 43, 39`** at 0.00 | `53, 62, 58` at 0.85 | `52, 60, 56` at 1.00 |
| `water_darkening` | `56, 65, 61` at 0.00 | `53, 62, 58` at 0.55 | `51, 59, 55` at 1.00 |
| `water_roughness` | `53, 61, 57` at 0.00 | `53, 62, 58` at 0.08 | **`41, 50, 46`** at 1.00 |

**The dry slime read `50, 56, 55` in all twelve rows, unchanged to the
count.** One material was being driven and only its object moved — twelve
independent demonstrations of it, not one.

**The setting that changes the look most is `roughness_dry = 0.0`**, and it
changes it in the direction that surprises: the stone gets *darker*, not
shinier. At roughness 0 the surface is a mirror, and what it has to reflect
is a near-black background, so the diffuse response it had is replaced by a
reflection of nothing. `water_roughness = 1.0` darkens for the mirror-image
reason: the sharp highlight that made wet stone read as wet is gone.

**What this measure cannot show.** It is a mean over a region, so it
flattens local contrast — `water_darkening` at 1.00 moves the mean by only 5
counts even though the mortar channels darken a great deal, because the
channels are a small fraction of the visible area. Whether any of these
*breaks* the look rather than merely changing it is a judgement from the
PNGs, and it is the author's.

### One shader, two materials

| | |
|---|---|
| Edit | `stone_flooded.water_darkening` 0.55 → 0.00, at run time, nothing else touched |
| Flooded slime | `53, 62, 58` → `56, 65, 61` — **moved 3** |
| Dry slime | `50, 56, 55` → `50, 56, 55` — **moved 0** |

One material changed; only its object moved. Both materials still reference
the same `Shader` resource, which `test_materials.gd` asserts by object
identity, not by path string.

Then the other half. The author added one line to `dungeon_surface.gdshader`
— `ALBEDO *= 0.5;` at the end of `fragment()` — and nothing else:

| | Before | After | Moved |
|---|---|---|---|
| Dry slime | `50, 56, 55` | `42, 47, 45` | **8** |
| Flooded slime | `53, 62, 58` | `49, 55, 51` | **7** |

**Both moved.** One value in one material moves one object; one line in the
shader moves both. The material holds the parameters, the shader holds the
code, and the two materials hold the same `Shader` object between them.
Capture: `evidence/a5-mutations/shader-edit_both-objects-darken.png`. The
line was removed afterwards and the shader is byte-for-byte its commit.

**That run also found a bug in the measuring tool, not in the thing
measured.** With the scene darkened, the material-edit step moved the mean
3 → 2 and `capture_materials.gd` reported `UNEXPECTED`, because its check
was written as "flooded must move more than 2 counts". Halving the
brightness halved the dynamic range and so tightened a threshold that had
nothing to do with what was being tested. It is now relative — the flooded
slime must move while the dry one does not — which is the comparison the
check was always about. A threshold in absolute counts gets stricter every
time a scene gets darker, and says nothing when it does.

## The film, and the take behind it

`youtube/claude-liam-walker-the-lost-gamedev/`. The evidence ledger passes
the course checker:

```
status PASS · 44 source files · 14 exclusions · 7 components
              5 exact excerpts · 5 code_result_pairs · code-then-result-v1
```

### The take — the warning as real motion

`godot/tests/capture_shader.gd` walks the player east through all three traps
with a held key through the real input map, pausing between them. Nothing is
teleported, no state is written, and nothing is slowed or retimed — the
pauses are the key being released.

| | |
|---|---|
| Rendered | 3840 × 2160, 60 fps, **710 frames**, 11.83 s |
| Traps that fired | **all three** |
| Health | 5 → 2 |
| **Frames with more than one trap lit** | **0 of 709 sampled** |
| Warning onsets | t 1.82 at x 174.4 · t 4.90 at x 286.4 · t 7.98 at x 398.4 |

**That first onset is the geometry, observed.** `DetectArea`'s zone begins at
175 and the warning starts at 174.4 — the derivation in revision 5.0.3 was
computed before the trap existed and is now watched happening.

**R6 in motion.** The headless suite asserts the rule once per scenario;
this take checks every frame of a real run and the red never appears on two
traps at once. `captures/a5/warning-ramp-contact-sheet.png` holds five frames
of one window — armed, 0.23, 0.49, 1.00, firing — with traps 2 and 3 grey in
every one.

### Two mistakes the film work found, both in the measuring, not the measured

**A beat with twenty seconds of narration over one second of footage.** The
first take ran 6.03 s and the result beats were written as essays. A result
beat's job is "watch this". The take now pauses between traps and the two
footage beats were cut to one or two sentences each, so the picture outlasts
the voice: B03 4.54 s of narration against a 4.55 s window, B05 10.73 s
against 10.80 s.

**Props the component does not have.** The scene listing advertises
`treeLabel`, `inspectorLabel`, `notes` and `cues`; the component's actual
schema also has `image` and `tree` but no `lines`, and in `asset` mode it
lays out `{code}{image}` — so the measured tables would have rendered
nowhere. The fix is the previous film's: `code` stays empty on result beats,
because the checker rejects displayed code with no excerpt record, and the
numbers are composed into the picture instead, read verbatim from the
recorded reports and hashed.

The first composite then overflowed its own footer. `compose_lost_evidence.py`
now computes whether the rows fit, shrinks the type, and raises rather than
drawing over the bottom of the card.

### What the film cannot establish

Everything it says about colour came from a windowed capture on this
hardware. The checker verifies hashes, inventory, source lines, excerpt
adjacency and hash-bound media. It does not verify that any explanation is
true, and `FACTCHECK.md` separates the six claims that are reasoning from
the ones that are measurement.

## The evidence table

| Check | Status |
|---|---|
| Baseline | **done** — above |
| Shaders parse | **done** — all three parse, with uniform-list assertions for each and no `SHADER ERROR` line in any passing run. |
| All shader mutations exit 1 | **done** — four: semicolon, rename, and `source_color` deleted from each of the two colour samplers. |
| Driver sampled at 30/60/144 through a real event, incl. retrigger | **partial** — the uniform now is, at all three rates, through a walk-in trigger: 408 pairs, worst gap 0.000000000. **Retrigger is checked on the state only** (`test_trap_warning.gd` R3); no scenario yet samples the uniform across a restart. |
| Controlled values (HUMAN) | **done** — all eight exact, and the OS-screenshot comparison is recorded above with which one is trusted and why. |
| In play (HUMAN) | **done** — played 2026-10-24; 0.40 s judged enough to react; R6 holds in a live frame. |
| Hint experiment (HUMAN) | **done** — all six bands exact, above; capture in `captures/a5/`. |
| Interface sweep (HUMAN) | **measured** — all four uniforms at min/default/max, above, with a PNG each. The judgement of what breaks the look is the author's and is still outstanding. |
| One shader, two materials (HUMAN) | **done** — one material value moved only its own object (3 against 0); one shader line moved both (8 and 7). Both measured above. |
| Material wiring after fresh import; `source_color` mutation exits 1 | **done** — 48 checks from an empty cache, and both colour-sampler mutations exit 1. |
| Texture data — curl ratio | **not applicable as planned** — the brief's material plan uses code-written colour and data textures and no normal map. If that changes, the calibration pair comes with it. |
| Import settings | **done** — the editor rewrote **none**; `detect_3d/compress_to=0` is why. Explained above. |

## Renderer, confirmed

A real windowed run, 2026-10-24. Not a headless run: headless reports
`forward_plus` and `vulkan` while leaving the adapter name empty and the window
0 × 0, because it initialises no device. The adapter name is the evidence.

```
Vulkan 1.4.357 - Forward+ - Using Device #0: NVIDIA - NVIDIA GeForce RTX 5080 Laptop GPU
--- renderer check ---
  project.godot asks for : forward_plus
  actually running       : forward_plus
  driver                 : vulkan
  adapter                : NVIDIA GeForce RTX 5080 Laptop GPU
  adapter vendor         : NVIDIA
  window size            : (1280, 720)
----------------------
```

Exit code 0, no errors. §6 and §7 of `CHANGE-BRIEF.md` therefore keep the
Forward+/Mobile assumption their predictions are written under.

## Known limitations

1. ~~Forward+ has never run on real hardware here.~~ **Resolved 2026-10-24** —
   see "Renderer, confirmed" below.
2. **The restart exploit.** R3 restarts the warning on every entry, so a player
   who backs out of the detection zone and re-enters repeatedly is never hit. This is the
   accepted price of "every trigger gets its own warning" and is recorded in
   `CHANGE-BRIEF.md` revision 5.0.1 rather than discovered later. A cooldown on
   re-entry would fix it and is not in scope here.
3. **The player has move and jump only, and the slice has no audio.** No
   combat, no magic, no dodge roll; the sprites are code-drawn blocks. The
   art and audio from `walker-ninja` — eight character poses, four sound
   effects, a music loop, all with provenance already recorded there — are
   **not** carried across in this revision. Deliberate, and dated 2026-10-24
   in `FRICTIONAL.md`: the player, the HUD and the audio are outside this
   change's boundaries, and the port happens after `a5` is tagged, as the
   first work of Assignment 6. The trap's sprite stays code-drawn
   permanently, because §6's predictions were computed before it was drawn.
4. **The human checks are all done.** All five HUMAN rows are measured or
   judged and recorded above. The last one was not a measurement: whether
   any setting in the interface sweep *breaks* the look rather than merely
   changing it, over the twelve sweep captures in `captures/a5/materials/`.

   **Author's verdict, 2026-10-28.** **`tint` at 0 breaks the look; the other three only change it.** Tint at zero is not a darker stone, it is no stone -- the albedo is multiplied to black and the texture goes with it, and the flooded slime reads as a silhouette. `roughness_dry` at 0 is the next most extreme (flooded mean 32, 43, 39, the lowest of the twelve) and it still reads as stone, just a very wet one. `water_darkening` and `water_roughness` move the surface across their whole range without ever leaving it.

   Nothing headless could have produced that line. A passing suite
   establishes that the state behaves; it establishes nothing about what
   the screen shows, which is why this row was carried as open for four
   days rather than filled in from the means.

---

# Assignment 6

Source revision: this commit. Godot **4.7.2.stable.official** `ed1daf0bf`,
**Forward+**, Vulkan 1.4.357, NVIDIA GeForce RTX 5080 Laptop GPU, Windows 11.

## A5's evidence check fails on `main`, by construction

`CHANGE-BRIEF.md` §0.3, verified rather than assumed: clone the `a5` tag into
an empty directory, add **one** file under `godot/`, and the course checker
answers `Inventory coverage mismatch`. A6 adds `godot/effects/`,
`godot/previews/`, `particles_generated.gdshader` and four tests, so this is
certain.

**The `a5` tag is unaffected.** A clone of it still returns
`{"status": "PASS", … "exact_excerpts": 6, "code_result_pairs": 6}`, which was
run from GitHub on 2026-10-28 and is recorded in `SUBMISSION.md`. Only `main`
changes, and that is what a cumulative repository does. Nothing about
Assignment 5's submission was broken to do this.

## Baseline, through Assignment 6's wrapper

Every suite at its pinned mode, before any effect existed — commit `866bd5a`.

| Test | Mode | Result | `SHADER ERROR` |
|---|---|---|---|
| `test_materials.gd` | 60 | 48 checks, 0 failures | 0 |
| `test_trap_shader_driver.gd` | 30 / 60 / 144 | 24 checks, 0 failures each | 0 |
| `test_trap_warning.gd` | 30 / 60 / 144 | 22 checks, 0 failures each | 0 |
| `test_input_map.gd` | 60 | 5 checks, 0 failures | 0 |
| `check_assets_3d.gd` | 60 | ALL CHECKS PASSED | 0 |
| `test_input_map.gd` | **realtime** | 5 checks, 0 failures | 0 |

**99 checks, 0 failures**, and the new `realtime` path exercised rather than
assumed.

## Effect A — configuration

`./scripts/run-test.sh test_hit_burst_config.gd 60` → **80 checks, 0
failures**. It reads every value in `CHANGE-BRIEF.md` §1.3 back out of the
loaded resources, so it fails in both directions: scene drifting from the
brief, and brief revised without the scene.

### The two mutations

Both run against `godot/effects/hit_burst.tscn` and both restored afterwards;
`diff` against the pre-mutation copy is empty.

| # | Mutation | Config test | What it proves |
|---|---|---|---|
| 1 | `initial_velocity_min = 70.0` → **`initial_velocity = 70.0`** on `Grit` | **exit 1** — `FAIL Grit.initial_velocity_min == 70.0 [0.0]` | The Godot 3 name. §0.2 measured that this property **exists** on 4.7.2 as a `Vector2` with usage 12 and is never stored, so the scene loads silently, stores nothing, and the emitter runs at `0.0`. Nothing errors. Only a read-back of the real property can tell. |
| 2 | `lifetime = 0.6` → **`0.9`** on `Grit`, brief untouched | **exit 1** — `FAIL Grit.lifetime == 0.6 [0.9]` | Drift between the brief and the scene, in the direction the brief did not move. |

Mutation 1 is the one the assignment is pointing at, and it is worse than the
assignment describes: the chapter warns the Godot 3 names are wrong, and on
this build one of them is *accepted*. `scale_random` is the other kind — it
does not exist at all, `set()` is a no-op and `get()` returns `<null>`.

## Effect A — frame strip r0 (FIXTURE CAPTURE)

`godot/previews/hit_burst_preview.tscn`, a real stretch of this level: the
same `room_backdrop.gd` the game draws, the same floor tile, and a real
`spike_trap.tscn` standing where the backdrop breaks the lit lip.
`use_fixed_seed` is pinned on the preview's own instance only — the effect
scene does not pin it, and the configuration test asserts that.

```bash
godot --path godot res://previews/hit_burst_preview.tscn \
    --write-movie "$PWD/captures/hit_burst/r0/frame.png" \
    --fixed-fps 30 --quit-after 60
```

Frames 10, 12, 15, 20, 30 and 50 are kept in `captures/hit_burst/r0/`; the
rest of the sequence is deleted. `captures/hit_burst/r0-strip.png` is the
same six laid out.

**One mechanical observation, made before anyone looked at the picture.**
Counting pixels that differ from frame 8 inside a box around the trap:

| frame | 9 | 10 | 11 | 12 | 15 | 20 | 30 | 50 |
|---|---|---|---|---|---|---|---|---|
| changed px | 48 | 114 | 130 | 148 | 182 | 278 | **0** | **0** |

So the burst fires, peaks around frame 20 and is **gone by frame 30**, which
is what §1.5 predicted. It also appears on **frame 9, not 10** — the
preview's `_process` counter runs one frame ahead of the file numbering, and
the strip is read from 10 as the brief says.

This says the effect *fires and clears on time*. It says nothing whatever
about whether it reads as grit, which is `TUNING.md`'s first entry and the
author's verdict.

## Effect A — wired into the game, and A1–A6 as state (Step 3)

`godot/effects/hit_burst_spawner.gd` is a node in `main.tscn`. It connects to
each trap's existing `fired` signal and instances one burst per event, parented
to the room. **No game script was changed**: `spike_trap.gd` already emitted
`fired` at `:98` for Assignment 5's warning driver.

```bash
./scripts/run-test.sh test_hit_burst_state.gd 60
```

**22 checks, 0 failures.** What each scenario establishes:

| Rule | Result |
|---|---|
| A1 nothing on scene load | 0 live bursts on the frame after `_ready()`, and none anywhere in the tree, with all three traps present and ARMED |
| A1 one per event | one walk left to right with synthesized key input → 3 `fired`, 3 instances |
| A2 position | worst error 0.000 px in x against the firing trap, 0.000 px in y against the floor line |
| A5 parent | all three parented to the room |
| A4 ceiling | never exceeded 3 — **observed maximum 1** |
| A3 overlap | two instances alive, the older one's clock at 0.250 s against the younger's 0.017 s |
| A6 frees itself | alive at half life, gone after **0.583 s**, and out of the tree |

### A4's green line was nearly worthless, and the test now says so

`CHANGE-BRIEF.md` revision 6.0.2. The brief's ceiling of 3 bursts is
arithmetically right and **unreachable by playing this room**: the traps are
112 px apart, the player walks at 96 px/s, so two `fired` events are 1.17 s
apart and a burst lives 0.60 s. "Assert the count never exceeds 3" therefore
passes whether the design works or not. The test now prints the **observed
maximum** next to that assertion and separately asserts it is 1, so a reader
sees what the walk actually exercised. A3's overlap is produced by emitting
`fired` directly and is **labelled SYNTHETIC in the test's own output**.

### Two defects this test found, neither of which any other check could

**1. `live_count()` threw on every call once a burst had died.** It was
written as

```gdscript
_live = _live.filter(func(b: Node2D) -> bool: return is_instance_valid(b))
```

A freed object cannot be passed to a parameter typed `Node2D`, and `filter()`
returns an untyped `Array` that will not assign back to `Array[Node2D]`. Both
errors print and Godot carries on. The configuration test never calls it, and
nothing in the game reads it, so **the only thing in the repository that could
have found this is a state test that runs past a burst's lifetime.** Replaced
with an explicit loop.

**2. The state test's own A2 and A5 checks passed having measured nothing.**
The first version stored the burst node in a list and measured its position
after the walk finished. By then all three had freed themselves, and in GDScript
a freed object reference compares equal to `null` — so the loop's
`if row["burst"] == null: continue` skipped every row and both checks reported
`worst 0.000 px` and passed. Three green lines, zero evidence, and 0.000 px is
exactly what a correct result looks like.

What caught it was a check written for a different purpose: "every event
produced an instance", which counted the same `null`s and went red. The fix
records position and parent **at the event**, as plain numbers, and the
scenario now also asserts that three bursts were actually measured rather than
none. This is the same failure shape as Assignment 5's frozen film and the
`const SFX_TRAP` parse error: a suite reporting success about work it never
did.

### What this step does not establish

Nothing about appearance. A headless run draws no particles. The look is
`captures/hit_burst/` and the verdict on it is the author's, in `TUNING.md`.

## Effect A — frame strip r1 (FIXTURE CAPTURE)

`TUNING.md`'s first tuning revision: `Flash.scale_min/scale_max` 1.6 / 2.4 →
5.0 / 7.0, approved before the change and kept after it. Recaptured from the
same preview with the same pinned seed, the same command, the same six frames.

Pixels differing between the r0 and r1 frame of the same number, whole frame,
no threshold:

| frame | 10 | 12 | 15 | 20 | 30 | 50 |
|---|---|---|---|---|---|---|
| differing px | **52** | 0 | 0 | 0 | 0 | 0 |

Claude's prediction, written before the recapture, called frames 10 and 12
different and the rest identical. **Five of six matched; frame 12 was wrong** —
the two frames are bit-identical there. Since `Flash` is additive and is the
only thing that changed, tripling its base scale would have to move at least one
pixel if it contributed any light, so `Flash` contributes nothing at frame 12 in
either revision. The full write-up, including what the strip cannot settle, is
in `TUNING.md`.

`captures/hit_burst/r0-strip.png` and `r1-strip.png` are both laid out by
`scripts/build_effect_strip.py`, written for this revision so that two strips
of the same effect are cropped and scaled identically. r0's strip was
regenerated with it from the same committed frames; the frames are untouched.

## Effect B — configuration, and a third variant of the section 0.2 trap

```bash
./scripts/run-test.sh test_dungeon_motes_config.gd 60
```

**39 checks, 0 failures.** Every value is `CHANGE-BRIEF.md` §2.3's, read back
off the loaded resource. Three checks are about the pair of effects rather than
about Effect B alone, because §2.1's claim — that `preprocess` is the feature
Effect A does not use — is a claim about two scenes: B's `preprocess` is 8.0
and equals its lifetime, all three of A's emitters are at 0.0, and none of A's
emitters uses a Box emission shape.

**The new trap variant, found while building the scene.** §0.2 recorded two
ways a property name can fail silently on 4.7.2. Effect B turned up a third:
on a **live** `ParticleProcessMaterial` whose `emission_shape` is still Point,
`get_property_list()` reports `emission_box_extents` with usage **0** — Godot
hides the shape-specific properties of every inactive shape. So the answer to
"is this property real?" depends on the value of an unrelated property.
`ClassDB.class_get_property_list()` reports usage 6 either way, and reading the
value with `get()` is immune to both. `emission_shape_offset`, which this scene
uses to place the box without moving the node, was checked the same way: usage
6, and it survives a save/load round trip into the resource file.

## Effect B — frame strip r0, and the F4 control (FIXTURE CAPTURES)

```bash
godot --path godot res://previews/dungeon_motes_preview.tscn \
    --write-movie "$PWD/captures/dungeon_motes/r0/frame.png" \
    --fixed-fps 30 --quit-after 350
```

Frames **1, 10, 11, 40, 100, 130, 340** are kept — revision 6.0.3 adds frame 1,
because B1 is a claim about the first drawn frame and frame 10 is not it. The
preview uses the real player and ends the condition by dealing it its whole
health through `take_damage()`, so the `died` signal on the other end is the
real one.

**Why three captures and not one.** A full field and a field that filled
quickly look the same in a single strip, so F4 cannot be shown by one. Taken:
the shipped effect; the same scene with `preprocess` mutated to **0.0** and
reverted straight afterwards; and a third with the field switched off, which
gives an absolute zero to count against. `room_backdrop.gd:28` records that
nothing in this backdrop moves, so the only thing that can differ between two
runs of the same frame is the field.

Mote pixels, against the field-off baseline, player column excluded:

| frame | shipped, `preprocess = 8.0` | mutated, `preprocess = 0.0` |
|---|---|---|
| 1 | **578** | **12** |
| 10 | 558 | 44 |
| 40 | 567 | 108 |

**B1 holds and F4 is demonstrated.** Full density on frame one, flat
afterwards; the mutated scene starts at 2 % and climbs at the rate one lifetime
over eight seconds predicts — 19 % of the way at frame 40, against 17 %
expected. The configuration test and the state test are both green for the
mutated scene too. Nothing but a drawn frame catches it.

**B2's tail, measured.** Mote pixels after the death at frame 100: 412, 400,
409, 315, 288, 191, 144, 76, 49, 16, **0** at frames 100, 110, 130, 160, 190,
220, 250, 280, 310, 330, 340. Empty at exactly 8.0 s, no cut. §2.5 predicted
frame 130 would be thinner; it is not yet — revision 6.0.3 corrects that row
and explains why from §2.2's own alpha ramp.

**One defect the strip found, and no test could.** 14 % of the visible motes on
frame 1, and **22 % by frame 40**, are six or more logical pixels *inside* the
floor slab; the lowest reaches y = 266, sixty-six pixels under the floor line.
The emission box runs down to y = 200, which is the floor line, and a mote
falls up to 112 px in its 8 s life. `visibility_rect` culls the node, it does
not clip particles. Recorded in `TUNING.md` with two candidate one-setting
fixes; the verdict and the choice are the author's.

## Effect B — wired into the game, and B2–B5 as state

```bash
./scripts/run-test.sh test_dungeon_motes_state.gd 60
```

**19 checks, 0 failures**, plus six printed `NOTE` lines that are deliberately
not checks.

| Rule | Result |
|---|---|
| B2 stop | `emitting` false on `died`, node not freed, not hidden, still false half a second later |
| B3 paused | `can_process()` true, false while the tree is paused, true again after — which is what `process_mode = INHERIT` produces |
| B4 hidden | `emitting` stayed true across hide and show; `preprocess` still equals `lifetime`, so nothing called `restart()` |
| B5 no writes | a second of ambience changed no player health, no player position and no trap state or `warn_amount`; the effect is connected to `died` and writes one property |

**What the NOTE lines say, and why they are not checks.** B1 is not checked at
all — a headless run draws no field — and the note points at the two strips
instead. B2's "existing motes finish their lives" is a drawn frame; the state
test can only show that the node was not freed, hidden or restarted, and the
note carries the strip's 412 → 0 measurement. B4's "it keeps simulating while
hidden" has no exposed particle clock to read, so it stays a human check.

Counting those as passes would have put six more green lines under claims
nothing in the run had tested. That is the same failure this assignment has now
produced three times in different shapes, and the cheapest defence against it
is a printed line that says *not checked here*.
