# TEST-REPORT.md — Assignment 5

**Source revision:** `051fd21`+ · **Godot** 4.7.2.stable.official `ed1daf0bf` ·
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

## The evidence table

| Check | Status |
|---|---|
| Baseline | **done** — above |
| Shaders parse | **partial** — `trap_warning.gdshader` parses, with uniform-list assertions, and no `SHADER ERROR` line in any run. The spatial shader does not exist yet. |
| Both shader mutations exit 1 (semicolon, rename) | **done** — above. The third mutation, `source_color` on the spatial shader's colour sampler, waits on that shader. |
| Driver sampled at 30/60/144 through a real event, incl. retrigger | **partial** — the uniform now is, at all three rates, through a walk-in trigger: 408 pairs, worst gap 0.000000000. **Retrigger is checked on the state only** (`test_trap_warning.gd` R3); no scenario yet samples the uniform across a restart. |
| Controlled values (HUMAN) | **done** — above, all eight exact. **The OS-screenshot comparison the assignment also asks for is still outstanding.** |
| In play (HUMAN) | **partial** — the red has now been seen on screen, but only as the rig's four-frame sweep. Nobody has walked into a trap and judged whether 0.40 s is enough warning. |
| Hint experiment (HUMAN) | **not yet** |
| Interface sweep (HUMAN) | **not yet** |
| One shader, two materials (HUMAN) | **not yet** |
| Material wiring after fresh import; `source_color` mutation exits 1 | **not yet** |
| Texture data — curl ratio | **not applicable as planned** — the brief's material plan uses code-written colour and data textures and no normal map. If that changes, the calibration pair comes with it. |
| Import settings — `.import` diffs the editor rewrote | **not yet** — the editor has not been opened on this project |

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
4. **No human check has been performed yet.** Every HUMAN row above is
   outstanding. A passing headless suite establishes that the state behaves;
   it establishes nothing about what the screen shows.
