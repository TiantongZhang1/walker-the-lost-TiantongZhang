# CHANGE-BRIEF.md — Assignment 5 specification

**The Lost · walker-the-lost-TiantongZhang · Tiantong Zhang · 2026-10-23**

Committed before any shader exists and before the first agent prompt of this
assignment. `CLAUDE.md` imports this file with `@CHANGE-BRIEF.md`, so it is the
contract the agent works to. The original is kept; revisions are appended below
it with dates.

> **Tags.** **[decided]** — chosen by the author. **[proposal]** — derived by
> Claude and not yet confirmed. Anything the author adopts from a **[proposal]**
> is typed in by them and recorded in `SOURCES.md` and `FRICTIONAL.md`, as the
> assignment requires.

> **Prerequisite, stated honestly.** This repository was created on 2026-10-17
> for the course's one permitted change of game, and contains no game yet.
> Assignment 5 assumes a game exists from Assignment 2. The 2D slice described
> here — player, floor, spike trap — and the copy of Assignment 3's 3D scene are
> prerequisite work that happens **after** this brief is committed and before
> Assignment 5's Step 1. `FRICTIONAL.md` records this. The shaders themselves
> are still specified before they are written, which is what the rule protects.

---

## 0. Renderer **[proposal]**

`godot/project.godot` currently names **GL Compatibility**, inherited from
`walker-ninja`. **Proposal: change it to Forward+ before any of this is built.**

Why: the assignment's prediction rules say *"These predictions assume Forward+
or Mobile. If you use Compatibility, say so and measure before you explain."*
Nothing in this repository depends on Compatibility — there is no game yet — so
taking the documented path costs nothing and removes a caveat from every
prediction in §6 and §7.

What it rules out either way is answered in §10.

**This must be confirmed by a real windowed run on the author's machine before
it is committed.** A headless run uses a dummy renderer and proves nothing about
whether Forward+ works on this hardware. If it does not, the renderer stays
Compatibility and §6 and §7 are measured first and explained second, as the
assignment allows.

---

## 1. The state

**What the effect communicates.** A spike trap is about to fire. The trap spends
most of its life flush with the floor and harmless; for a short window before the
spikes come up, it is lethal to stand on. The shader turns the trap red across
that window. **[decided]**

**Why the player needs it.** The Lost's design rule, from the GDD, is that
hazards announce themselves — floor 1's water level *is* the warning. A trap that
fires with no tell is not difficulty, it is a coin flip. The warning window is
the entire fairness of the trap, which is why its duration has to be the same at
30, 60 and 144 frames per second: a player on a 144 Hz monitor must not get a
shorter warning than a player on 30. **[decided]**

**The script and variable that hold it.**

| | |
|---|---|
| Script | `godot/features/traps/spike_trap.gd` |
| State enum | `State { ARMED, WARNING, FIRING, RETRACTING, COOLDOWN }` |
| The driving variable | `warn_amount: float`, `0.0` … `1.0` |
| What advances it | `_process(delta)` while `state == WARNING` |
| What begins the state | the player's body entering `TriggerArea` (an `Area2D`) |

`warn_amount` is presentation-facing state owned by the trap. It is **read** by
the material driver and never written by it. **[proposal — the file path, the
enum and the variable name are Claude's; the behaviour is the author's]**

---

## 2. The effect specification

### The shader

| | |
|---|---|
| Path | `godot/shaders/trap_warning.gdshader` |
| `shader_type` | `canvas_item` |
| `render_mode` | none |
| Sampler uniforms | **none** — the sprite's own texture arrives in `COLOR` |

### Uniforms

| Name | Type | Hint | Default | Set by |
|---|---|---|---|---|
| `warn_amount` | `float` | `hint_range(0.0, 1.0)` | `0.0` | **game code**, from `SpikeTrap.warn_amount` every frame |
| `warn_color` | `vec3` | `source_color` | `vec3(0.839216, 0.235294, 0.184314)` — `#D63C2F` | the material; not animated |

`warn_color` carries `source_color` deliberately: it is the one hint in this
assignment that is suspected of changing the value the shader receives, not just
the Inspector, and §6 predicts both outcomes so the measurement settles it.

### The colour line

Exactly one line inside `fragment()` changes the colour:

```glsl
COLOR.rgb = mix(COLOR.rgb, warn_color, warn_amount);
```

**[proposal — Claude's; the author types it and must be able to explain it]**

`TIME` is not used. It is global engine time and cannot express time since the
trap armed.

---

## 3. Observable rules

Each rule is measurable, and §5 says what measures it.

| # | Rule | |
|---|---|---|
| R1 | `warn_amount == 0.0` while `ARMED`. At the instant `WARNING` begins it is still `0.0`; at the instant `FIRING` begins it is `1.0`. | **[decided]** |
| R2 | Across `WARNING`, `warn_amount` goes `0.0 → 1.0` **linearly** over `WARN_SECONDS = 0.45 s`, tolerance one frame period, and takes the same **game time** at 30, 60 and 144 fps. | **[proposal]** duration; **[decided]** that it must be frame-rate independent |
| R3 | **Retrigger mid-window: ignore.** A trap already in `WARNING` is unaffected by the player re-entering `TriggerArea`. The window neither restarts nor extends. | **[decided]** |
| R4 | The ramp uses **scaled** time — the `delta` from `_process` — so `Engine.time_scale = 0.5` makes the warning take 0.9 s of wall clock and still 0.45 s of game time. While the tree is paused the trap's process mode is `inherit`, so it stops and `warn_amount` holds its value. | **[proposal]** |
| R5 | If the state ends before the ramp finishes (the trap is disarmed, or the scene reloads), `warn_amount` snaps to `0.0` in the same frame. No fade out. | **[proposal]** |
| R6 | **Each trap instance gets its own value.** Every `SpikeTrap` duplicates the `ShaderMaterial` in `_ready()`, so three traps in one room warn independently. | **[decided]** |

R6 exists because it is the assignment's own named failure case — *"one enemy's
flash appearing on every enemy."* The scene will contain **three** traps
specifically so the rule can fail if it is wrong.

---

## 4. Boundaries

Unchanged by this work: collision layers and shapes, player movement, input
map, the trap's state machine timings once set here, every existing test and its
expectations, and every object that is not a `SpikeTrap`.

Presentation code may **read** game state. It never writes it. The driver reads
`SpikeTrap.warn_amount` and calls `set_shader_parameter`; it does not advance the
trap, time it, or decide when it fires.

---

## 5. The evidence split

| Rule | Checked by | How |
|---|---|---|
| R1 | **headless** | sample `warn_amount` from a high-`process_priority` node across a real trigger |
| R2 | **headless** | same sample at `--fixed-fps` 30, 60, 144; compare game-time duration |
| R3 | **headless** | trigger, wait 0.2 s, trigger again, assert the end time did not move |
| R4 | **headless** | run once at `time_scale = 1.0` and once at `0.5`; compare game time |
| R5 | **headless** | disarm mid-ramp, assert `0.0` on the next frame |
| R6 | **headless** | three traps, trigger one, assert the other two read `0.0` |
| Uniform names, types, defaults | **headless** | `get_shader_uniform_list()` plus defaults read from the shader source text |
| Does it read as a warning in play? | **HUMAN** | play the slice, trigger traps repeatedly, judge whether 0.45 s is enough time to react |
| Do the predicted pixels match? | **HUMAN** | in-engine capture at each controlled value, sample the two named pixels |
| Does the red read against floor 1's palette? | **HUMAN** | side-by-side with the floor tiles |

No headless run establishes any of the three human rows. That is the point of
the split.

---

## 6. Controlled inputs and predicted values

Computed by hand from the colour line, before the shader exists.

**The sprite is specified here and will be drawn to match**, so the predictions
drive the art rather than describing it.

| | Sprite-local pixel | Colour |
|---|---|---|
| Pixel **A** | `(8, 12)` — trap base plate | `#2A2A33` = `(42, 42, 51)` |
| Pixel **B** | `(8, 3)` — spike tip | `#8A90A1` = `(138, 144, 161)` |
| Background | floor tile behind the trap | `#16242B` = `(22, 36, 43)` |

Both named pixels are fully opaque, so the background does not enter the
arithmetic; it is recorded because the assignment asks for the real background
and because a capture will show it.

**Two hypotheses, because `source_color` is exactly what is in question.**

- **H1** — the shader receives `warn_color` as written: `(0.839216, 0.235294, 0.184314)`
- **H2** — `source_color` decodes sRGB → linear first: `(0.672443, 0.045186, 0.028426)`

Predicted 8-bit values of each pixel at three `warn_amount` values:

| Pixel | `warn_amount` | **H1** as written | **H2** linearised |
|---|---|---|---|
| A | 0.0 | 42, 42, 51 | 42, 42, 51 |
| A | 0.5 | **128, 51, 49** | 107, 27, 29 |
| A | 1.0 | **214, 60, 47** | 171, 12, 7 |
| B | 0.0 | 138, 144, 161 | 138, 144, 161 |
| B | 0.5 | **176, 102, 104** | 155, 78, 84 |
| B | 1.0 | **214, 60, 47** | 171, 12, 7 |

**Prediction: H1.** In a 2D canvas_item shader with HDR 2D off, `COLOR` carries
the texture's stored values and no linearisation happens, so a `source_color`
uniform that arrived linearised would be mixing in a different space from
`COLOR` and the result would be visibly darker than the picked colour. H1 says
`warn_amount = 1.0` reproduces `#D63C2F` exactly; H2 says it lands near
`#AB0C07`. These are far apart, so one capture settles it.

**If the measurement is H2, that is a finding, not an error** — it is recorded
with the capture and explained in `LANGUAGE-NOTES.md`, and it answers the
assignment's question about whether a hint changes the value the shader
receives.

Colours were chosen so that every H1 value at `warn_amount = 0.5` is an exact
integer; a prediction landing on `.5` cannot be checked against a rounded pixel.

**Contrast, computed.** Pixel A against the floor tile `#16242B`, as WCAG
relative-luminance ratios, under H1:

| `warn_amount` | Pixel A | Ratio against the floor |
|---|---|---|
| 0.0 | `#2A2A33` | **1.12 : 1** |
| 0.5 | `#803331` | **1.84 : 1** |
| 1.0 | `#D63C2F` | **3.44 : 1** |

The armed trap at 1.12 : 1 is very nearly invisible against the floor, which is
deliberate — an armed trap the player spots from across the room is not a trap.
The warning multiplies the ratio by **3.08×**. Whether that is enough to see in
0.45 s is a human check, not a computation.

---

## 7. The hint experiment

A committed GDScript writes a 3 × 1 PNG whose texels are the greys **64, 128,
192**. It is imported lossless, no mipmaps. One unshaded spatial shader binds
that same file to two samplers — one `source_color, filter_nearest`, one
`filter_nearest` only — and a `bool` uniform picks which writes `ALBEDO`. Two
materials, one per value, on two quads facing the camera, under a
`WorldEnvironment` with Linear tonemap at exposure 1.0, glow, fog and
adjustments off.

Using `encode(x) = 12.92x` for `x ≤ 0.0031308`, else `1.055·x^(1/2.4) − 0.055`:

| Stored | **With `source_color`** | **Without** |
|---|---|---|
| 64 | **64** | **137** |
| 128 | **128** | **188** |
| 192 | **192** | **225** |

**The `source_color` quad is the one that shows the file's values unchanged.**
Sampling decodes sRGB → linear, the shader passes the value straight to
`ALBEDO`, and the display encodes linear → sRGB. The two transforms are
inverses, so the number that comes out is the number that went in.

The other quad never decodes. It hands the stored value to `ALBEDO` as though it
were already linear, and the display encodes it anyway — one encode too many, so
every band is brighter. 64 → 137 is the largest error and is the band to look at
first.

Assumes Forward+ or Mobile per §0. If the renderer stays Compatibility, these
are measured before they are explained.

---

## 8. The material plan

**The object and the lighting.** The slime from Assignment 3, in the Assignment 3
showcase scene copied into this repository — one `DirectionalLight3D` at energy
1.0, ambient 0.25, judged under exactly that and nothing else. SSAO stays off
while judging, since it is the effect most easily confused with a data texture
doing its job. **[proposal]**

**The textures: written by code. [proposal]**

The assignment allows this explicitly — *"Textures written by code are fine; show
the code."* It gives exact provenance with no licence to track and no download,
and the generator script is committed. The trade-off, stated plainly: it forgoes
the Poly Haven `_nor_gl` / `_nor_dx` calibration pair, so **this plan uses no
normal map**, and the curl check in Step 3 does not apply. If the author would
rather do the normal-map work, say so now — it changes this section and adds the
calibration pair to §5.

| Texture | Role | Meaning of its numbers | Sampled as | Import settings, set explicitly |
|---|---|---|---|---|
| `stone_albedo.png` | the wet dungeon stone's colour | sRGB colour | **colour**, `source_color` | `compress/mode` = VRAM Compressed, `compress/normal_map` = Disabled, `mipmaps/generate` = On |
| `wetness_mask.png` | where water pools in the stone's low spots | a scalar 0–1 per texel; 0 dry, 1 submerged | **data**, no `source_color` | `compress/mode` = Lossless, `compress/normal_map` = Disabled, `mipmaps/generate` = On |

**The shader.** `godot/shaders/dungeon_surface.gdshader`, `shader_type spatial`,
two samplers as above, at least four non-texture uniforms in at least two
`group_uniforms` groups:

| Group | Uniform | Type | Hint | Default | What changes on screen |
|---|---|---|---|---|---|
| `surface` | `tint` | `vec3` | `source_color` | white | the stone's overall colour |
| `surface` | `roughness_dry` | `float` | `hint_range(0.0, 1.0)` | `0.85` | how matte the dry stone is |
| `water` | `water_darkening` | `float` | `hint_range(0.0, 1.0)` | `0.55` | how much the mask darkens albedo |
| `water` | `water_roughness` | `float` | `hint_range(0.0, 1.0)` | `0.08` | how sharp the reflection is where wet |

**The two materials. [proposal]**

| | `stone_dry.tres` | `stone_flooded.tres` |
|---|---|---|
| `water_darkening` | `0.00` | `0.55` |
| `water_roughness` | `0.85` | `0.08` |
| `tint` | neutral | slightly green-shifted |

They differ in three values, more than the required two, and the difference is
the one the game actually needs: the same stone above and below the waterline on
floor 1.

---

## 9. Predicted failure cases

| # | What could go wrong | The check that catches it |
|---|---|---|
| F1 | The `ShaderMaterial` is shared, so triggering one trap turns **all three** red. | R6's headless assertion: trigger trap 1, assert traps 2 and 3 read `0.0`. |
| F2 | The ramp advances per **frame** instead of per **second**, so the warning is 0.45 s at 60 fps, 0.9 s at 30 and 0.19 s at 144. | R2 run through `./scripts/run-test.sh` at all three pinned frame rates; the game-time durations must agree. |
| F3 | Re-entering the trigger **restarts** the window, so a player standing on the trap is never hit. | R3's headless assertion: the second trigger must not move the end time. |
| F4 | `wetness_mask.png` is sampled with `source_color`, so the mask is silently decoded and the waterline lands in the wrong place. | The material test asserts each sampler's hints read from the shader source; and the Step 3 mutation deletes `source_color` from the colour sampler and must make the test exit 1. |
| F5 | `warn_amount` is driven but the shader declares it under another name, so `set_shader_parameter` writes a value nothing reads — silently, with no error. | The uniform-list assertion, plus the Step 2 rename mutation. |

---

## 10. The brief answers

**Which renderer does `project.godot` name, and what does it rule out?**
Today: **GL Compatibility**, which rules out decals, compute shaders, VoxelGI,
SDFGI and SSIL. §0 proposes Forward+, which rules out none of them. Mobile would
allow decals and compute but still not VoxelGI, SDFGI or SSIL.

**What colour arrives in `fragment()` before I change it, and what would the
tempting alternative give?**
`COLOR` arrives holding the sprite's texture sampled at `UV`, already multiplied
by the node's modulate and by vertex colour. The tempting alternative is to
sample the texture again myself, which throws that multiplication away.

**For canvas_item: what would `texture(TEXTURE, UV)` give me instead of
`COLOR`?**
The raw texture sample only — no modulate, no vertex colour. A trap that the
game had faded out or tinted would ignore that fade entirely, so the warning
effect would fight the rest of the presentation instead of composing with it.
It is also redundant work: Godot already did that sample to fill `COLOR`.

**For spatial: what does `ALBEDO` hold if never written, and what does `COLOR`
hold?**
`ALBEDO` defaults to `vec3(1.0)` — white — not the mesh's material colour, since
a `ShaderMaterial` replaces that entirely. `COLOR` in a spatial shader is the
**vertex colour** interpolated across the face, which is unrelated to a 2D
shader's `COLOR` and is `vec4(1.0)` unless the mesh carries vertex colours.

**How long would a frame-counting version last at 30, 60 and 144 fps?**
If the ramp advanced `1.0 / 27` per frame — 27 being 0.45 s × 60 — then at 60 fps
it lasts 0.45 s, at 30 fps **0.90 s**, and at 144 fps **0.19 s**. The 144 Hz
player gets less than a quarter of the warning. This is F2, and it is why R2 is
measured at three pinned frame rates rather than one.

**Which resource holds the default, which holds the current value, and what if
two objects share the material?**
The **shader** holds the default, as written in its `uniform` line. The
**material** holds the current value. If two traps share one `ShaderMaterial`,
they share one `warn_amount` and both turn red together — which is F1, and why
R6 duplicates the material per instance.

**Does `hint_range` clamp a value set from code?**
**Prediction: no.** `hint_range` is expected to constrain the Inspector's slider
only, leaving `set_shader_parameter("warn_amount", 2.0)` to pass 2.0 straight
through to the shader, where `mix()` with `t = 2.0` extrapolates past
`warn_color` instead of stopping at it. Checked in Use It with a capture at 2.0.

---

## 11. What this brief does not yet settle

- §0's renderer change needs a real windowed run before it is committed.
- The three-trap room's layout, and whether 0.45 s is actually enough warning,
  are human judgements that cannot be made before the slice is playable. If
  0.45 s proves wrong in play, R2's duration is revised here with a date and the
  predictions in §6 are unaffected — they are parameterised by `warn_amount`,
  not by the clock.

---

# Revision 5.0.1 — 2026-10-23 — four decisions from the author

The original above is unchanged. These four supersede it where they conflict.

## §0 Renderer: **Forward+**, accepted **[decided]**

`godot/project.godot` changes to Forward+ before anything is built, so the
predictions in §6 and §7 follow the documented path instead of needing the
Compatibility caveat.

**Confirmed 2026-10-24 by a real windowed run.** Forward+ initialises on this
hardware; §6 and §7 keep the Forward+/Mobile assumption and need no
Compatibility caveat.

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

The headless runs had reported `forward_plus` and `vulkan` too, with an
**empty** adapter name and a 0 × 0 window — the dummy renderer naming a driver
it never initialised. The non-empty adapter is what makes this a real check.

## §3 R2 duration: **0.45 s stands, provisionally** **[decided]**

Kept as the starting value, to be judged once the slice is playable. If play
says otherwise it is revised here with a date; §6's predictions are unaffected,
because they are parameterised by `warn_amount`, not by the clock.

## §3 R3 retrigger: **restart**, not ignore **[decided]**

> R3 (superseded). Retrigger mid-window: **restart.** Every `body_entered` on
> `TriggerArea` sets `warn_amount` back to `0.0` and begins a fresh
> `WARN_SECONDS` window, whatever the trap was doing. The author's rule is that
> **every trigger gets its own full warning**.

What this changes elsewhere:

- **§5 evidence split, R3** now reads: trigger, wait 0.20 s, trigger again;
  assert `warn_amount` dropped to `0.0` on the retrigger frame and that the
  window ends 0.20 s later than it otherwise would have.
- **§9 F3 is inverted.** Restarting is no longer the failure; failing to restart
  is. See the revised table below.

**A consequence, recorded rather than discovered later.** `Area2D.body_entered`
fires on entry, not continuously, so a player standing still on a warning trap
does **not** reset it and will be hit. But a player who steps off and back on
repeatedly restarts the warning every time and is never hit. That is a real
exploit of the restart rule, it is the price of "every trigger gets its own
warning", and it is accepted deliberately rather than missed. It is listed as a
known limitation in `TEST-REPORT.md` and is a candidate for a later cooldown.

## §3 R4 time scale **[decided, with a reading flagged]**

The author answered "先不用" — *don't use it for now*. That is read as **the game
does not use `Engine.time_scale` anywhere**, not as a request to make the ramp
ignore it.

> R4 (superseded). The ramp uses Godot's ordinary scaled `delta` from
> `_process`, with no special handling. **The Lost sets `Engine.time_scale`
> nowhere**, so scaled and unscaled time coincide in play. The test sets
> `time_scale = 0.5` anyway and records what happens, so the behaviour is
> documented rather than assumed. While the tree is paused the trap's process
> mode is `inherit`, so it stops and `warn_amount` holds.

**If the intended meaning was "the warning must ignore `time_scale`", this is a
two-line change** — divide the accumulator by `Engine.time_scale`, or accumulate
from `Time.get_ticks_usec()` — plus one test expectation. Flagged for the author
rather than silently assumed either way.

## §9 revised failure cases

| # | What could go wrong | The check that catches it |
|---|---|---|
| F1 | The `ShaderMaterial` is shared, so triggering one trap turns **all three** red. | Trigger trap 1 headlessly; assert traps 2 and 3 read `0.0`. |
| F2 | The ramp advances per **frame**, so the warning is 0.45 s at 60 fps, 0.90 s at 30 and 0.19 s at 144. | R2 at all three pinned frame rates; game-time durations must agree. |
| **F3** | **The window fails to restart** — a second trigger is ignored or merely extends the first, so the second entry gets a partial warning or none. | Trigger, wait 0.20 s, trigger again; assert `warn_amount` returned to `0.0` and the end time moved out by 0.20 s. |
| F4 | `wetness_mask.png` is sampled with `source_color`, so the mask is decoded and the waterline lands in the wrong place. | The material test asserts each sampler's hints from the shader source; the Step 3 mutation deletes `source_color` and must exit 1. |
| F5 | `warn_amount` is driven under a name the shader does not declare, so the write goes nowhere, silently. | The uniform-list assertion, plus the Step 2 rename mutation. |

---

# Revision 5.0.2 — 2026-10-24 — the trap could not hit anyone

**The observation is the author's**, on seeing the trap behave: the spikes
should come out as the player *approaches*, not after they have walked past.

**It is not a matter of feel. The trap was unable to hit a walking player at
all**, and the arithmetic says so:

| | |
|---|---|
| Trigger width (revision 5.0.1) | 16 px — the trap's own tile |
| Player collider half-width | 5 px |
| Overlap the player crosses | 26 px |
| Player speed | 96 px/s |
| **Time inside the trigger** | **0.27 s** |
| **Warning window** | **0.45 s** |

The player left the trigger 0.18 s before the spikes arrived, by which point
they were 17 px clear. There was no value of anything that made this trap
dangerous.

**The suite had already measured it and not noticed.** R3's scenario printed
`player walked out of the trigger mid-window [warn_amount was 0.630]` — the
player gone at 63 % of the warning — and passed, because every check in it
asked whether the *timing* was right and none asked whether the trap *worked*.

## What changes

**R2 duration: 0.30 s** (was 0.45 s). **[decided]**

**The trap gets two Area2Ds instead of one.** A single area could not be
widened without the player taking damage from three tiles away.

| Node | Size | Job |
|---|---|---|
| `DetectArea` | **48 × 24 px** | notices the player; starts the warning |
| `HurtArea` | **16 × 20 px** | the trap's own tile; the only thing that damages |

**`DetectArea`'s width is derived, not chosen.** For a player who keeps walking
to be centred over the trap when the spikes arrive:

```
detect half-width = Player.SPEED × WARN_SECONDS − player half-width
                  = 96 × 0.30 − 5
                  = 23.8 px        →  48 px wide
```

Predicted offset at the moment of firing: **−0.2 px**. Measured: **+3.2 px**,
inside the ±13 px hurt box. Changing `WARN_SECONDS` without changing this shape
breaks the trap, which is said in a comment above the constant.

The three traps stay 80 px apart: detection zones are 216–264, 296–344 and
376–424, with 32 px gaps, so R6 is still demonstrable.

## A new rule, and the check it gets

> **R7.** A player who walks into the detection zone at full speed and does
> not react **is hit**. The warning exists to be reacted to; a warning that
> cannot be failed is decoration.

`test_trap_warning.gd` scenario F6 drives the player in with real input and
asserts three things at once: that the player is still short of the trap when
it warns, that they are over it when the spikes arrive, and that a life was
actually lost. Measured at 30, 60 and 144 fps: **−25.6 px**, **+3.2 px**,
**health 5 → 4**, identical at all three.

## What does not change

§6's pixel predictions. They are parameterised by `warn_amount`, not by the
clock, exactly as revision 5.0.1 said they would be. §7's hint experiment is
untouched.

---

# Revision 5.0.3 — 2026-10-24 — 0.40 s, and the test was lying about the frame rate

**R2 duration: 0.40 s** (was 0.30 s in 5.0.2, 0.45 s in 5.0.1). **[decided]**

`DetectArea` follows from it, as revision 5.0.2 established it must:

```
detect half-width = 96 × 0.40 − 5 = 33.4 px        →  66 px wide
```

Predicted offset when the spikes arrive: **+0.4 px**. Measured: **+6.4 px**,
inside the ±13 px hurt box.

**Trap spacing 80 px → 112 px** (now at x = 208, 320, 432). At 80 px the 66 px
detection zones left only 4 px of clear space between them once the player's
own width was counted; one more increase to `WARN_SECONDS` and they would have
overlapped, quietly making R6 untestable. The zones are now 175–241, 287–353,
399–465.

**Two new checks make the derivation self-enforcing**, so this cannot drift
again by hand:

- `DetectArea`'s half-width must equal `Player.SPEED × WARN_SECONDS − 5`.
- The three detection zones must not overlap.

## The test had been measuring against the wrong frame rate

Found while making this change, and it invalidates how the earlier R2 numbers
were judged.

The test read `Engine.max_fps` to learn its frame period. **`--fixed-fps` does
not set `Engine.max_fps`**, so every run computed its tolerance as if it were
at 60 fps:

| Run at | Tolerance used | Tolerance it should have used | |
|---|---|---|---|
| 30 fps | 0.0167 s | 0.0333 s | **2× too strict** — fails a correct result |
| 60 fps | 0.0167 s | 0.0167 s | correct by accident |
| 144 fps | 0.0167 s | 0.0069 s | **2.4× too loose** — passes a wrong one |

The measured durations in revisions 5.0.1 and 5.0.2 were real; the verdict
"within one frame" was not reliably earned at two of the three rates.

**Also: the frames at 144 fps are not uniform.** 1/144 s is 6944.44 µs and
Godot works in whole microseconds, so the delta alternates between 0.006944
(144 fps) and 0.006667 (150 fps), with the occasional 0.008. 30, 60 and 240
divide evenly and are perfectly uniform. A two-frame sample of the delta at
144 caught an outlier and reported 120 fps.

**The fix:** `scripts/run-test.sh` exports `TEST_FPS`, because `--fixed-fps` is
consumed by the engine and never reaches `OS.get_cmdline_args()`. The test
takes the **modal** delta over 40 frames and asserts the two agree within 1 %.

**R2's tolerance is now one frame period**, as this brief always said — not the
1.5× the test had been using — plus 1 ms for the 144 fps jitter.

| fps | Modal delta | Window | Tolerance | |
|---|---|---|---|---|
| 30 | 0.033333 (39/40 frames) | 0.433 s | ±0.0333 | pass |
| 60 | 0.016667 (40/40) | 0.417 s | ±0.0167 | pass |
| 144 | 0.006944 (35/40) | 0.403 s | ±0.0069 | pass |

**22 checks, 0 failures** at each rate.

---

# Revision 5.0.4 - 2026-10-24 - the warn_amount = 2.0 prediction, before the capture

§10 asks whether `hint_range` clamps a value set from code and answers
**"Prediction: no"**, to be settled by a capture at `warn_amount = 2.0`. It
never wrote down what that capture should show. This revision does, **before
the capture rig exists**, so the measurement can disagree with something.

`mix(c, w, t)` is `c + t*(w - c)`, which at `t = 2.0` is `2w - c` -
extrapolation past `warn_color`, not a stop at it. The result is written to
`COLOR.rgb` and clamped to [0, 1] there, which is where two channels die.

| Pixel | Channel | Raw float at t = 2.0 | 8-bit |
|---|---|---|---|
| **A** `(8, 12)` | R | 1.5137 | **255** (clamped) |
| | G | 0.3059 | **78** |
| | B | 0.1686 | **43** |
| **B** `(8, 3)` | R | 1.1373 | **255** (clamped) |
| | G | -0.0941 | **0** (clamped) |
| | B | -0.2627 | **0** (clamped) |

**Predicted: A becomes `255, 78, 43` and B becomes pure `255, 0, 0`.**

The same arithmetic reproduces §6's three existing rows exactly (42/42/51,
128/51/49, 214/60/47 for A), so this is the brief's own formula extended, not
a second method.

**What each outcome means.**

- Those values measured: `hint_range` constrains the Inspector only, the
  write passes straight through, and `mix()` extrapolates. §10's prediction
  holds.
- `214, 60, 47` measured instead: the value was clamped to 1.0 somewhere
  between `set_shader_parameter` and the shader. §10 is wrong, and the
  question becomes where - the material, the uniform upload, or the hint.
- Anything else: record it and find out why before explaining it.

B is the more useful pixel of the two. Two of its three channels go negative
before the clamp, so a correct extrapolation makes it **pure red** - a result
no other hypothesis produces by accident.
