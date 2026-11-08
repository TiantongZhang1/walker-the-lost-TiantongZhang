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

## Effect C — the step dust, and four defects the tests found in themselves

`CHANGE-BRIEF.md` revision 6.0.4. A third effect, added on the author's verdict
on Effect B: *dust falling from the sky, but none at the floor*. Ambience does
not react to the player, so this is an event effect and a separate scene rather
than a revision of Effect B.

**The event does not exist, so it is derived.** `player.gd` has no footstep
signal and §3 keeps it out of scope. `step_dust_driver.gd` accumulates measured
position delta while the player is on the floor and spawns one puff per 24 px —
a distance, not a timer and not a per-frame chance. `amount_ratio` scales a
landing's puff to 1.0 against a stride's 0.6; it is the feature §0.1 probed and
the first two effects did not need.

```bash
./scripts/run-test.sh test_step_dust_config.gd 60
./scripts/run-test.sh test_step_dust_state.gd 30
./scripts/run-test.sh test_step_dust_state.gd 60
./scripts/run-test.sh test_step_dust_state.gd 144
```

**63 checks, 0 failures** for the configuration. **26 checks, 0 failures at
each of 30, 60 and 144 fps** for the state.

| Rule | Result |
|---|---|
| C1 cadence | 8 puffs for 192.0 px at 30 fps, 8 for 193.6 px at 60 and 144 |
| C1 never otherwise | nothing standing still, nothing airborne, nothing once dead |
| C2a spacing | consecutive puffs **0.0000 px** from one stride apart, at all three rates |
| C2b position | within two physics steps of the player; **0.000 px** at the collision box's underside |
| C4 landing | exactly one puff per jump, at `amount_ratio` 1.0 |
| C5 | parented to the room; all gone within one lifetime of the key release |
| C6 | a puff's world position does not change while the player walks on |
| C7 | the same walk with the driver deleted ends at the same x and the same health |

### Four defects, and all four were in the tests

This is the part worth reading. The effect itself needed one real change; the
tests needed four.

**1. A check that could not fail.** C7 was written as
`_trap_states(main) == trap_states or true`. The `or true` makes it pass
whatever happens. It was put there because comparing trap states across half a
second is meaningless — they run their own machine — and then left in rather
than replaced. It is now a **differential**: the same walk run with the driver
present, with it deleted, and with it present again. Trajectory and health are
identical to the last float across all three.

**2. A second check that could not fail.** "The player left the floor" was
written as `_seen.size() >= 0`, which is true of every array that has ever
existed. A jump that never happened would have produced zero puffs and the
landing check would have failed for the wrong reason. It now records
`is_on_floor()` across the jump.

**3. A comparison that was not controlled.** The C7 differential first ran with
a room of its own already open, so three `Main`s were in the tree at once and
the key presses reached all of them. The traps came out in different states
between runs that were supposed to be identical, and the difference looked like
the driver writing game state. **A third run, with the driver present again,
is what showed it was not**: the two control runs disagreed with each other, so
the comparator was invalid. The scenario now loads nothing of its own and each
walk is alone in the tree. Where the controls still disagree the test prints
what it saw and makes no claim.

**4. Two windows that were not the same window.** The cadence check counted
puffs over one window and divided the distance measured over a longer one. At
60 and 144 fps the two happened to agree; at 30 fps it reported 7 puffs for 8
strides. The sampler now runs through the wind-down, which is the window the
distance is measured over.

### The one real defect, and the measurement that found it

At 30 fps the puff was **3.2 px** from the player instead of the brief's 2.
Not a tolerance problem: the spawn was at the player's *current* position when
the stride had finished part way through the frame, so the spacing between
puffs depended on the frame rate — which is what C3 exists to forbid, in the
dimension C3 did not mention. The driver now steps the spawn back by the
overshoot, and the measured spacing is **0.0000 px** from one stride at every
rate. Revision 6.0.5.

That revision also records the clock mistake behind it: the first corrected
bound was written in **rendered frames** and failed at 144 fps, because the
player moves in `_physics_process` at 60 Hz whatever the render rate is. Two
render frames at 144 fps is 1.33 px, tighter than anything that can happen.
Same mistake as revision 5.0.3, new place, caught the same way — by running at
three rates instead of one.

### Effect C — frame strip r0 (FIXTURE CAPTURE)

```bash
godot --path godot res://previews/step_dust_preview.tscn \
    --write-movie "$PWD/captures/step_dust/r0/frame.png" \
    --fixed-fps 30 --quit-after 110
```

The preview runs right, turns, runs left and stops, with real key events, and
is bounded so the player never enters a trap's detection zone — a trap firing
mid-strip would put Effect A in the frame. Frames **20, 26, 32, 50, 70, 95**.
A control with `stride_px` set to 9999 gives a dust-free run of the same
movement, so the dust can be counted rather than estimated.

| frame | dust px | below the floor line | brightest delta |
|---|---|---|---|
| 20 | 82 | 14 (17 %) | 111 |
| 26 | 130 | 21 (16 %) | 145 |
| 32 | 74 | 8 (11 %) | 108 |
| 50 | 98 | 12 (12 %) | 111 |
| 70 | 87 | 25 (29 %) | 145 |
| 95 | **0** | 0 | 0 |

**G3 is answered and the answer is yes.** §C.2 refused to assume that
`scale.x = -1` mirrors the emission direction of a `local_coords = false`
emitter, and no test here can see it. Frame 32, running right, throws the dust
to the left of the character; frame 70, running left, throws it to the right.

**Two things the strip shows that no test does**, both in `TUNING.md` awaiting
the author's verdict: the puff is far quieter than "kicked up" implies — a 2–3
pixel smudge against Effect A's burst at four times the brightness — and
11–29 % of the dust ends up under the floor, because C2's spawn point is the
floor line itself and `Kick` carries `gravity` 900.

## Step 7 — the headless price, and the instrument's own resolution

```bash
./scripts/run-test.sh cost_effects.gd 60 300
```

`CHANGE-BRIEF.md` §5 and revision 6.0.4 §C.6 predict that all three effects
read **≈ 0 ms over the control** here, and predict it *by construction*: a
`GPUParticles2D`'s process step is a shader on the graphics card, a headless
run uses a dummy renderer, and a measurement that never reaches the card has
nothing of the card to measure. §5 also says that a clear difference would
mean the script is wrong or the prediction is.

| condition | median µs | mean µs | p90 µs | peak emitters | instances created |
|---|---|---|---|---|---|
| empty scene (control) | 3.0 | 2.6 | 3.0 | 0 | 0 |
| room, effects REMOVED (run 1) | 129.5 | 146.8 | 204.0 | 0 | 0 |
| room, all three live (run 1) | 135.0 | 156.7 | 209.0 | **8** | **25** |
| room, effects REMOVED (run 2) | 122.0 | 139.0 | 199.0 | 0 | 0 |
| room, all three live (run 2) | 128.0 | 147.2 | 209.0 | **8** | **25** |

**Effects on minus effects off: +5.8 µs per frame (+0.0057 ms). Prediction
holds.**

### Two things this script had to be fixed to earn

**1. The load has to be shown, not asserted.** The first version printed a
single snapshot of the emitter count and reported **1** — the ambience node,
and nothing else, at the instant it happened to look. A row labelled "all
three effects live" that never shows more than one emitter has measured a
label. It now reports the **peak** emitter count and the number of distinct
effect instances created across the run: **8** and **25**, which is Effect B's
one node plus a burst's three plus two step-dust puffs' two each, and
twenty-five scenes spawned and freed during a ten-second walk. That is the
heavy state §5 asks to be measured at, and now the table says so.

**2. The difference was smaller than the noise, and the first version did not
know it.** Four runs of the original gave +18.0, +10.0, +1.0 and +8.5 µs —
while the median of the *unchanged* "effects removed" condition wandered from
116 to 131 µs between runs. Reporting "+0.010 ms" off that is reporting the
weather.

The script now runs **each room condition twice, interleaved**, and computes
the spread between two runs of a condition that did not change. That spread is
this instrument's resolution. In the run above it is **7.5 µs against a 5.8 µs
difference**, so the script says what is true:

> The difference is SMALLER THAN THE NOISE. The honest reading is not
> "+0.0057 ms" but "below this instrument's resolution".

A measurement that cannot state its own resolution cannot distinguish a real
effect from a quiet machine, and this project has already shipped three checks
that passed while measuring nothing.

### What Step 7 does not establish

**Every budget in §5 and §C.6 is a GPU budget and none of them is settled
here.** 0.30 ms for Effect A, 0.20 ms for B, 0.10 ms for C — all GPU time, all
to be read from the **Visual Profiler on hardware, by the author**, at the
heaviest state the game reaches. §4's evidence split puts that row under HUMAN
and nothing headless can move it.

**FPS is not used as an instrument either**, and §7 says why: with vsync on,
the frame rate reads the display's refresh rate with the effects off and the
same with them on, because vsync holds it there until a frame actually misses.
96 particles will not make a 5080 miss.

**~~No vsync toggle was added to demonstrate that in play.~~** ~~It would need
a new action in the input map, and §3 keeps the input map out of scope.~~
**Corrected 2026-11-08: that reasoning was wrong and the key has been added**
— see "The vsync debug key" below. Reading a raw keycode off the event needs
no action in the input map, which is what the assignment's own example does.

## The process shader

`godot/shaders/particles_generated.gdshader` — 384 lines, 41 uniforms.

**How it was produced.** `godot/previews/step6_scratch.tscn` holds one
`GPUParticles2D` whose process material is a verbatim copy of
`hit_burst.tscn`'s `PPM_dust`, lifted by script with its four sub-resources so
that nothing was retyped. A headless check compared twelve settings against the
real `Dust` emitter and found zero mismatches. The author converted that
material to a `ShaderMaterial` in the Godot editor, saved it, and Claude
extracted the generated code from the saved resource.

**`Dust` is the emitter this step needs.** The generated shader includes the
ramp and curve sampling only when the material actually has them, so
converting an emitter without both would have produced a file with two of the
required line references missing — which is exactly what the first attempt
did (see below).

> **Correction, 2026-11-08.** This paragraph originally said `Dust` was *the
> only one of the three* carrying both a `color_ramp` and a `scale_curve`.
> **That is wrong.** Reading the scene files back:
>
> | emitter | `color_ramp` | `scale_curve` |
> |---|---|---|
> | `Flash` | yes, `hit_burst.tscn:45` | yes, `:44` |
> | `Grit` | yes, `:70` | **no** |
> | `Dust` | yes, `:101` | yes, `:100` |
> | `Kick` | yes, `step_dust.tscn:42` | **no** |
> | `Puff` | yes, `:73` | yes, `:72` |
> | `DungeonMotes` | yes, `dungeon_motes.tscn:43` | **no** |
>
> Three of the six emitters carry both, not one. The real reason `Dust` is
> the right emitter to convert is that its curves are the ones a strip can
> read: `scale_curve` rises 0.6 → 1.8 across a 0.45 s life, so the puff
> visibly grows while its alpha falls to zero. `Flash` carries both too and
> lives **0.12 s** — 3.6 frames at 30 fps — with an additive blend and a
> `scale_curve` that falls 1.0 → 0.2, which is why revision 6.0.1's strip
> could not see it on five of its six frames. `Puff` is Effect C's and was
> not built when Step 6 was done.
>
> Found on 2026-11-08 while fact-checking the film's narration, which
> repeated the same claim. `FACTCHECK.md` in the reel records it too. The
> original sentence is replaced rather than struck through because it was a
> statement of fact with no reasoning attached to it; what the correction
> replaces it with is the reasoning that was actually doing the work.

### The line references

Located by the author in the first generated file and carried across to this
one when it was regenerated; every line below was then read back out of the
committed file rather than calculated.

| What | Line | The line itself |
|---|---|---|
| `shader_type` | **3** | `shader_type particles;` |
| `start()` | **230** | `void start() {` |
| `process()` | **282** | `void process() {` |
| Initial velocity from its min and max | **140** | `params.initial_velocity_multiplier = mix(initial_linear_velocity_min, initial_linear_velocity_max, rand_from_seed(alt_seed));` |
| …and where that reaches the particle | **269** | `USERDATA1.xyz = get_random_direction_from_spread(alt_seed, spread) * dynamic_params.initial_velocity_multiplier;` |
| Gravity becomes a force | **316** | `force = gravity;` |
| …and changes velocity | **329** | `USERDATA1.xyz += force * DELTA;` |
| **Colour over life is sampled** | **162** | `parameters.color *= texture(color_ramp, vec2(lifetime));` |
| **Scale over life is applied** | **161** | `parameters.scale *= texture(scale_curve, vec2(lifetime)).rgb;` |
| Per-particle random scale, from min and max | **150** | `params.scale = vec3(mix(scale_min, scale_max, rand_from_seed(alt_seed)));` |
| …and where that reaches the transform | **364–377** | `if (first_frame) { … TRANSFORM[0..2].xyz *= … }` |
| `color_ramp` / `scale_curve` declarations | **45–46** | `uniform sampler2D color_ramp : repeat_disable;` |
| `gravity` declaration | **44** | `uniform vec3 gravity;` |
| `scale_min` / `scale_max` declarations | **30–31** | `uniform float scale_min;` |

**One line tied to a setting in the brief, with its value.** Line **316**,
`force = gravity;`, together with its declaration at **44** and its effect at
**329**, is `CHANGE-BRIEF.md` §1.3's `Dust` column, **`gravity = (0, −30)`**.
That one setting is visible at three separate places in the shader — declared,
read, and applied to the velocity — which is the clearest thing in the file
about how a process setting actually becomes motion.

Two of the brief's settings are *not* separate lines here and that is worth
saying: `scale_min` and `scale_max` (§1.3, `Dust`, **2.0 / 3.5**) are one
`mix()` at line 150, and the curve that reshapes that scale over the
particle's life is a different line entirely, 161. The brief lists them in
adjacent rows; the shader treats them as unrelated steps.

### The first attempt, and what it got wrong

The first conversion took a **default, empty `ParticleProcessMaterial`** — the
one a freshly added `GPUParticles2D` arrives with — rather than one of this
game's. The resulting file had **no `sampler2D` and no `texture()` call at
all**, so "where colour over life is sampled" and "where scale over life is
applied" did not exist in it. Line 157 read:

```glsl
// Compile-time add textures.
```

with nothing after it. That comment is Godot's insertion point, filled in only
when the material carries a ramp or a curve.

**The author found it while counting lines**, reporting that the file had no
`texture()` sampling for the colour curve. Claude had already checked that
file — it loaded, reported `MODE_PARTICLES`, declared 38 uniforms and produced
no `SHADER ERROR` — and all three of those were true while the file was the
wrong one. It is the same failure this report keeps recording: a set of green
checks that measured something other than the thing in question.

The thirteen line references the author produced from that file were all
correct, and all had to be relocated when it was regenerated.

### Which of the brief's settings live in this shader, and which belong to draw

> **Written by Claude at the author's instruction on 2026-11-08.** Assignment 6
> Step 6 asks for the author's own words here and says the agent does not write
> the answers. It is recorded as Claude's so that nothing in this file
> misrepresents who wrote what.

Everything in `CHANGE-BRIEF.md` §7's **process** row is in this file, and
nothing from its **draw** row is.

`direction`, `spread`, `initial_velocity_min/max`, `gravity`, `damping_min/max`,
`scale_min/max`, `scale_curve` and `color_ramp` are all uniforms here, and each
one is read inside `start()` or `process()`. The split §7 drew on paper turns
out to be a split between two different programs: the process settings are
inputs to a shader that runs on the graphics card once per particle per frame,
and that is the whole content of this file.

The draw settings are not here and could not be. The `CanvasItemMaterial` and
its **Add** blend mode on `Flash`, the particle texture, `visibility_rect` and
`local_coords` never appear, because they are not decisions about how a
particle moves — they are decisions about how the result is rasterised, which
happens in a separate `canvas_item` shader, and in the case of
`visibility_rect` and `local_coords`, on the node before any shader runs.

The boundary is visible in one place: `COLOR` at line 357 and `TRANSFORM` at
364–377 are **written** by this shader and **consumed** by the draw step. They
are where the process step hands its result over. That is also why §1.3's
`color_ramp` can be correct while the burst still looks wrong — this shader
would do its job perfectly and an additive blend mode on the wrong emitter
would still ruin the picture, which is a draw decision no line in this file can
reach.

### What this step does not establish

Nothing about the running game. This shader is not used by anything: it is a
copy, converted for reading. `godot/effects/hit_burst.tscn` still carries a
`ParticleProcessMaterial` on all three emitters and its configuration test is
80 checks, 0 failures.

### Step 7, revised to the assignment's four cases

The first version of `cost_effects.gd` measured three conditions: empty, the
room with the effects off, and the room with all three on. The assignment
names four, and the two it named that were missing are the ones that carry the
information — **Effect A at the most bursts the brief says can be alive at
once**, and **Effect B in its heaviest state**. Measuring the three effects as
one lump hid what separates them.

| condition | median µs | mean µs | p90 µs | peak emitters | instances created |
|---|---|---|---|---|---|
| empty scene (control) | 3.0 | 2.8 | 3.0 | 0 | 0 |
| room, all effects REMOVED (1) | 127.0 | 136.8 | 183.0 | 0 | 0 |
| **A only, held at its ceiling of 3** | 136.5 | 155.5 | 240.0 | **9** | **30** |
| **B only, steady state** | 123.5 | 137.8 | 188.0 | **1** | **0** |
| **C only, player running** | 131.5 | 160.6 | 271.0 | **4** | **22** |
| all three, heaviest | 142.5 | 164.5 | 239.0 | 17 | 55 |
| room, all effects REMOVED (2) | 119.0 | 136.5 | 205.0 | 0 | 0 |

Baseline, the mean of the two runs with the effects removed: **123.0 µs**.
Spread between those two runs, which is this instrument's resolution:
**8.0 µs**.

| effect | over baseline | against the noise |
|---|---|---|
| A at its ceiling | **+13.5 µs** | above |
| B at steady state | **+0.5 µs** | below |
| C while running | **+8.5 µs** | above |
| all three | **+19.5 µs** | above |

**Effect A's peak emitter count is 9**, which is three bursts of three
emitters: the ceiling the brief sets the budget against was actually reached,
not assumed. The earlier three-case version reported a peak of 1 at one point
and 8 at another, and neither number told a reader which effect was doing
what.

### What the split between B and the other two is, and is not

**It is not the particle process.** That never runs here; a headless run uses
a dummy renderer. §5 predicted ≈ 0 ms over the control for all three by
construction, and at 13.5 µs — 0.0135 ms against Effect A's 0.30 ms GPU budget
— the prediction holds for every one of them.

**It is node bookkeeping, and the instances column is the evidence.** Effect B
is one persistent node that creates nothing: **0 instances, +0.5 µs, below the
noise floor.** Effects A and C spawn and free a scene per event — **30 and 22
instances** across 400 frames — and that instantiation is ordinary CPU work
that a headless run executes in full. It is the only part of these effects a
headless run can price, and it is what shows above the noise.

That is the sharper form of §7's answer. A GPU effect's headless price is near
zero *because the process step is on the card*; what remains is whatever the
effect does on the CPU, and for a one-shot effect that is the instancing. An
ambience node that allocates once shows nothing at all.

### Still not a budget

Every number in §5 and §C.6 is **GPU time** — 0.30 ms for A, 0.20 for B, 0.10
for C — and none of them is settled by this script. That is the Visual
Profiler, on hardware, read by the author, with each effect off and then on at
its heaviest. §4's evidence split puts that row under HUMAN.

**Effect A's row here is synthetic and the script says so in its own output.**
Revision 6.0.2 measured that three bursts cannot be alive at once by playing
this room: the traps are 1.17 s apart at walking speed and a burst lives
0.60 s, so play reaches one. Holding three alive means emitting `fired`
directly on a 0.20 s rotation. That is the brief's ceiling, which is the right
thing to budget against, and it is not a load a player produces.

### The vsync debug key

`godot/game/debug_keys.gd`, on the `DebugKeys` node in `main.tscn`. **F9**
toggles the window's vsync mode and prints the mode and the current FPS.

The assignment asks for the FPS comparison to be made with a debug key rather
than a project-setting change, so the shipped game is never running under
different settings than the one that was measured. §7 argues that with vsync
on the frame rate reads the display's refresh rate with the effects off and
the same with them on; the key is what lets that be shown rather than
asserted.

An earlier section of this report said no vsync key had been added because it
would need a new action in the input map, which §3 keeps out of scope. **That
was wrong.** The assignment's own example reads `event.keycode` straight off
the event and adds no action, and so does this. A headless check confirms the
input map still holds exactly three non-`ui_` actions — `move_left`,
`move_right`, `jump` — with `DebugKeys` in the tree.


## The film's own evidence, and the three things it caught

`youtube/claude-liam-walker-the-lost-particles-gamedev/`. Twenty beats, six
code-then-result pairs, game-source revision `31fb5a7`. The course checker
passes:

```json
{"status": "PASS", "source_files": 66, "exclusions": 40, "components": 6,
 "exact_excerpts": 6, "teaching_contract": "code-then-result-v1",
 "code_result_pairs": 6}
```

That check verifies hashes, inventory, source lines and associations. It does
not verify that a claim is true or that a frame shows what the narration says
it shows. Three things got through it and were caught by looking.

### 1. A take that came back wrong, and said so

`godot/tests/capture_particles.gd` take **p** asserts three traps fired, ≥ 3
distinct bursts, ≥ 12 distinct step-dust instances and both facings. During
one 4K render the author switched to another application. Godot releases every
pressed key when its window loses focus, so the held `D` was released, the
player stopped, and the take recorded **1 burst and 9 puffs** instead of 4 and
25. Every frame written looked perfectly normal. The take failed its own
assertion, which is the only reason it was noticed.

Fixed by re-pressing the held key every frame — safe for `move_left` and
`move_right`, which `player.gd` reads through `Input.get_axis()`, and
deliberately **not** done for `jump`, which is read with
`is_action_just_pressed`.

### 2. A card that captioned an empty room "three bursts alive"

`scripts/compose_particles_evidence.py` extracts a frame of take r for the
cost card. The first version hardcoded **3.0 s**. When take r was re-recorded
longer so the narration would have footage to play over, 3.0 s no longer had a
burst in it, and the card drew a picture of an empty room under the caption
*three bursts alive*. Nothing in the pipeline noticed; the hash matched, the
checker passed.

The timestamp is now read out of `capture/logs/take-r-inputs.jsonl` — the
first frame whose recorded live-burst count is ≥ 3 — and the count is read
back onto the card. A card that cannot find three bursts stops the build.

### 3. Two note panels that clipped mid-sentence

The `GodotDevWorkbench` notes column holds about **165 characters** of value
text across its two cards. Nothing enforces it and overflowing it clips
silently. B04's two notes totalled 207 characters and B10's 174; both second
cards were cut off mid-word in the rendered frame. B06 at 152 and B11A at 167
were fine. Found by extracting one frame per code beat and reading them side
by side, which is the only method that has ever found this class of fault in
this project.

### 4. A QC script that destroyed the other QC script's report

`scripts/qc_particles_master.py` pulls one frame per beat out of the master
so that the film can be read rather than trusted. Its first version wrote
`_qc/REPORT.md` — which is **Gate V's** filename. Gate V is the toolkit's own
visual check, `art final` runs it, and it had already written its result
there: frames sampled, BLOCKER count, MAJOR count. Running my script
afterwards silently replaced it.

Nothing errored and nothing warned. It was noticed only because `git status`
listed both `_qc/contact-sheet.png` (mine) and `_qc/contact_sheet.png`
(Gate V's) and the near-identical names did not look deliberate.

Recovered by re-running `runtime/qc/final_frame_check.py` against the
committed master, which produced the same kind of report over 40 sampled
frames: **BLOCKER 0, MAJOR 0**. My script now writes `_qc/BEAT-FRAMES.md`
and `_qc/beat-contact-sheet.png`, and **asserts at startup that it is not
about to write either of Gate V's two filenames**, so the collision cannot
come back.

This is the same shape as `scripts/finalise_beat_timing.py` rewriting
walker-ninja's beat sheet, recorded in `TOOLCHAIN.md`: a script that is
correct about its own job and destructive about somebody else's output.

### And one wrong claim, corrected rather than hidden

B08's note said `Dust` was the only emitter carrying both a `color_ramp` and a
`scale_curve`. **Three of the six do** — `Flash`, `Dust` and `Puff`. The
narration and the note were corrected before the master was rendered, the
process-shader section above carries a dated correction, and the reel's
`FACTCHECK.md` records it as well. The real reason `Dust` is the right emitter
to convert is in that correction.

### What the film does not claim

No GPU time. Every budget in `CHANGE-BRIEF.md` §5 and §C.6 is still a
prediction, the film says so three times, and `FACTCHECK.md` marks every
narrated claim as MEASURED, SOURCE, REASONING or AUTHOR so that the three
kinds are not mixed silently.
