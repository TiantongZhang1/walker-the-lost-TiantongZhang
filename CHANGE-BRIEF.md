# CHANGE-BRIEF.md — Assignment 6 specification

**The Lost · walker-the-lost-TiantongZhang · Tiantong Zhang**

Drafted 2026-11-05, reviewed and adopted by the author 2026-11-06.

Committed before the first agent prompt of this assignment. `CLAUDE.md`
imports this file with `@CHANGE-BRIEF.md`, so it is the contract the agent
works to. Assignment 5's brief stays in history at tag `a5`.

> **Tags.** **[decided]** — chosen by the author. **[proposal]** — derived by
> Claude and not yet confirmed. Anything the author adopts from a
> **[proposal]** is typed in by them and recorded in `SOURCES.md` and
> `FRICTIONAL.md`, as the assignment requires. Same convention as A5.

---

## 0. What was measured before anything was specified

Three findings, from probing the pinned engine rather than from the class
reference. They change what the rest of this brief can say.

### 0.1 Every feature this brief needs exists in 4.7.2

`ClassDB.class_get_property_list()` on this build reports all of:
`amount_ratio`, `use_fixed_seed`, `seed`, `trail_enabled`, `preprocess`,
`visibility_rect` on `GPUParticles2D`; `turbulence_enabled`,
`sub_emitter_mode`, `collision_mode`, `anim_speed_min`, `emission_shape`,
`damping_min/max`, `color_ramp`, `scale_curve` on `ParticleProcessMaterial`.
So the feedback loop can drive `amount_ratio` properly rather than falling
back to `speed_scale`, and the preview can pin a seed.

`ParticlesMaterial` and `Particles2D` — the Godot 3 class names — **do not
exist**, so a scene file naming either fails loudly. That is the easy half.

### 0.2 The Godot 3 *property* trap is worse than the assignment describes

The assignment warns that `initial_velocity` and `scale` are Godot 3 names.
On 4.7.2 `ParticleProcessMaterial` **has all three of**
`initial_velocity`, `scale` and `damping` — as `Vector2` properties with
usage flag **12** (`EDITOR | INTERNAL`), which means **they are not written
to scene files at all**:

```
initial_velocity      usage=12  type=Vector2   NOT stored
initial_velocity_min  usage=6   type=float     real
scale                 usage=12  type=Vector2   NOT stored
scale_min             usage=6   type=float     real
damping               usage=12  type=Vector2   NOT stored
scale_random                    does not exist at all
```

`material.set("initial_velocity", 7.0)` returns `(0.0, 0.0)` — it is
accepted and discarded. So there are **two different silent failures**, not
one:

| Mutation | What happens |
|---|---|
| `initial_velocity_min` → `initial_velocity` | the property exists, the parser is happy, the value is never stored, the effect runs at the default |
| `scale_min` → `scale_random` | the property does not exist; `set()` is a no-op and `get()` returns `<null>` |

Step 2's mutation must therefore be the **first** one to demonstrate what the
assignment is pointing at. **[decided — which mutation to run]**

### 0.3 A5's evidence check fails on `main` from the first file this adds

Verified by experiment: clone the `a5` tag into an empty directory, add one
file under `godot/`, run `./art godot-gamedev --check` → `Inventory coverage
mismatch`. A6 adds `godot/effects/`, `godot/previews/`,
`particles_generated.gdshader` and new tests, so this is certain, not a risk.

The `a5` **tag** is unaffected and a clone of it still passes; only `main`
changes. `TEST-REPORT.md` says so rather than leaving a reviewer to think
the previous assignment was broken. **[decided]**

---

## 1. Effect A — the grit burst

### 1.1 The job

**What it tells the player.** That *this* trap has just fired, and therefore
that it is now safe. The trap fires for `FIRE_SECONDS = 0.18`, retracts for
`0.22`, and then sits in `COOLDOWN` for `0.60` looking exactly like an armed
trap — the texture swaps back. For six tenths of a second the player has no
way to tell a harmless trap from a lethal one. The burst is that
information, and it is the only presentation this game has for it.
**[proposal — the reasoning; the author decides whether this is the job]**

**What holds the event.**

| | |
|---|---|
| Script | `godot/features/traps/spike_trap.gd` |
| Signal | `fired`, emitted at `:98` on entering `State.FIRING` |
| Position | the emitting trap's own global position — `SpikeTrap1/2/3` at x 208, 320, 432, y 200 |

The trap sprite is 16 × 16 centred on y 200, so the spikes' tips are at
y ≈ 192 and the floor line is y = 200. **The burst originates at the floor
line**, which is where the spikes punch through.

### 1.2 The intent block

**Timing phases.** Total 0.60 s. **[proposal]**

| Phase | Duration | What happens |
|---|---|---|
| Impact | 0.00 – 0.12 s | A few large pale chunks at the lip, bright on the very first frame. If the player's eye is anywhere near the trap this is what catches it. |
| Spray | 0.12 – 0.35 s | Grit thrown up and outward in a cone, fastest here, already falling by the end. |
| Settle | 0.35 – 0.60 s | Grit falls under gravity and fades; the dust puff lingers longest and thins out. |

Gone at 0.60 s, which is **less than the 1.40 s a trap needs to come back
round to `FIRING`** (0.18 + 0.22 + 0.60 + 0.40). So one trap can never
overlap itself; overlap comes from different traps. §1.5 depends on this.

**Contrast against the real background.** The trap stands in one of the
**unlit gaps** in the floor lip — `room_backdrop.gd` breaks the lip at each
trap deliberately, so the background here is floor tile `#16242B` under wall
`#1b1620`, the darkest the room gets outside the alcoves. Pale grit is the
right answer: `#c8ccd6` against `#16242B` is roughly 9 : 1. Judge it at
**SpikeTrap2 (x 320), which stands under the middle torch**, and at
**SpikeTrap1 (x 208), which does not** — those are the lightest and dimmest
places this effect can appear. **[proposal — the colour; [decided] that it
is judged at both traps]**

**Scale against the character.** The character is 29 px tall and the trap is
16 px wide. The burst should read as **about half the character's height at
its widest** — roughly a 16 px radius at the spray's peak, reaching 24 px at
the outermost grit. Bigger than that and a 16 px trap looks like an
explosion; smaller and it is lost at the project's 1280 × 720 window.
**[proposal]**

**Change over life.** Alpha alone is not enough. Each emitter changes in at
least two of colour, alpha and scale: the flash shrinks and dims, the grit
holds its size and darkens toward the floor's own colour before fading, the
dust grows and thins. **[decided — that it must change in more than alpha]**

**Variation.** Velocity ± 55 %, scale ± 40 %, and a rotation offset per
particle. Effect A fires dozens of times in a play session and three times
in a single walk; stamped repeats would be obvious. **[proposal]**

**Layering — three emitters under one `Node2D` root.** **[proposal]**

| Emitter | Job |
|---|---|
| `Flash` | 4 large pale chunks. Owns frame one. |
| `Grit` | 20 small specks. Owns the shape of the thing. |
| `Dust` | 8 soft puffs. Owns the tail, and stops the burst ending abruptly. |

### 1.3 The settings

Node type: **`GPUParticles2D`**, three of them under one `Node2D`.
**[proposal]** — the process step belongs off the CPU, and the assignment's
point about a near-zero headless price is only demonstrable with a GPU node.
The cost of that choice is stated in §5: both effects are compared on GPU
time, and the headless number is a control rather than a budget.

`local_coords`: **off** on all three. The burst is spawned as its own
instance at the event position and never moves, so local coordinates would
buy nothing; off also means that if the root is ever moved mid-life the
particles stay where they were born, which is what grit does. **[proposal]**

`visibility_rect`: **`Rect2(-48, -64, 96, 96)`** on each emitter, **set and
checked, not generated** — generating it needs the editor and this value has
to survive a reimport. The widest grit reaches 24 px and the flash rises
about 20 px, so this is roughly double the real extent. **[proposal]**

`preprocess`: **0.0** on all three. A burst has no history. **[decided]**

| | `Flash` | `Grit` | `Dust` |
|---|---|---|---|
| `amount` | 4 | 20 | 8 |
| `one_shot` | true | true | true |
| `explosiveness` | 1.0 | 0.85 | 0.4 |
| `lifetime` | 0.12 | 0.60 | 0.45 |
| `emission_shape` | Point | Sphere, radius 6 | Sphere, radius 4 |
| `initial_velocity_min/max` | 20 / 50 | 70 / 160 | 10 / 40 |
| `spread` | 55° | 70° | 35° |
| `gravity` | (0, 0) | (0, 900) | (0, −30) |
| `damping_min/max` | 0 / 0 | 40 / 90 | 10 / 20 |
| `scale_min/max` | 1.6 / 2.4 → **5.0 / 7.0**, Revision 6.0.1 | 0.8 / 1.4 | 2.0 / 3.5 |
| `scale_curve` | 1.0 → 0.2 | flat 1.0 | 0.6 → 1.8 |
| `color_ramp` | `#e8ecf4` → `#c8ccd6`, α 1 → 0 | `#c8ccd6` → `#5e6472`, α 1 → 1 → 0 | `#8a90a1` α 0.5 → 0 |
| draw texture | none (1 px white, point) | none | none |
| draw material | `CanvasItemMaterial`, blend **Add** | default (Mix) | default (Mix) |

`gravity` on `Grit` is **900**, the same number as `Player.GRAVITY`, so the
grit falls at the rate everything else in this game falls at. **[proposal]**

Blend **Add** on `Flash` only: the flash is light, the grit and dust are
matter. Additive dust over a dark floor would glow. **[proposal]**

### 1.4 Observable rules

| # | Rule |
|---|---|
| A1 | A burst appears on **every** `fired`, and never otherwise — in particular **not on scene load**, where three traps exist and none has fired. |
| A2 | The burst is at the emitting trap's x, at the floor line y = 200, within 1 px. |
| A3 | **Retrigger rule: overlap.** Every `fired` gets its own instance; nothing is cut off and nothing is dropped. |
| A4 | **At most 3 bursts alive at once**, so at most **96 particles**. Each trap's cycle is 1.40 s and a burst lives 0.60 s, so a trap cannot overlap itself; three traps is the hard ceiling. **Revision 6.0.2: correct, and unreachable by playing this room — the traps are 1.17 s apart at walking speed, so in play at most one burst is alive and the peak is 32.** |
| A5 | A burst does **not** die with the thing that caused it. It is parented to the room, not to the trap. |
| A6 | Each burst frees itself when its longest emitter has finished. No instance survives past 0.60 s. |

**Why overlap and not restart.** A single `one_shot` node would be the
obvious build, and it is the assignment's named failure: setting
`emitting = true` while a one-shot node is still emitting **does not restart
it**, so the second of two close events is silently dropped. With three traps
in one room and a player who walks past all three, that drop is ordinary
play. An instance per event cannot drop one. **[decided]**

**A5 is a rule about a failure this design avoids** rather than one it risks:
nothing frees a trap in this game. It is stated because the assignment asks
what would happen, and because parenting the burst to the trap would have
been the natural thing to write.

### 1.5 The frame strip

Preview: `godot/previews/hit_burst_preview.tscn`. Background is **a real
stretch of this level** — the `room_backdrop.gd` wall with a trap standing in
its unlit gap, at in-game camera scale, not the editor's grey.

Trigger at **frame 10**; second trigger at **frame 16** (0.20 s later, inside
the 0.60 s lifetime) when the preview's retrigger export is on.

Read frames **10, 12, 15, 20, 30, 50** at 30 fps. **[decided — the
assignment fixes these]**

| Frame | t after trigger | Should show |
|---|---|---|
| 10 | 0.00 s | The flash, at full brightness, at the trap's lip. Grit barely moved. |
| 12 | 0.07 s | Flash dimming, grit clearly a cone, widest acceleration. |
| 15 | 0.17 s | Flash gone. Grit at its widest spread, about 16 px. |
| 20 | 0.33 s | Grit falling, darkening. Dust at its largest. |
| 30 | 0.67 s | **Empty.** If anything remains, the lifetime is wrong. |
| 50 | 1.33 s | Empty, and the instance freed. |

The preview pins `use_fixed_seed` **on its own instance only** — never in the
effect scene, where repeats have to vary.

---

## 2. Effect B — the dungeon motes

### 2.1 The job

**Which job: ambience.** **[decided]**

**What it tells the player.** That the room is a sealed interior with air in
it, and — honestly — not much more. Ambience's job is place, not
information, and this brief is not going to pretend otherwise. The one
functional thing it does: when the player stands still, the motes are the
only moving thing on screen, so the picture never reads as frozen.
**[proposal]**

**The feature Effect A does not use: `preprocess`.** **[decided]** Secondary:
a **Box** emission shape against A's Point and Sphere.

**The condition.**

| | |
|---|---|
| Starts | the scene loads with the player alive — already running on frame 1, which is what `preprocess` is for |
| Stops | `player.gd`'s `died` signal, `:48` |
| Script that holds it | `godot/features/player/player.gd`, `var health` and `signal died` |

### 2.2 The intent block

**Timing phases.** There are none in the burst sense; a mote lives 8.0 s and
the field is in a steady state at all times. The phases that matter are the
*field's*: **full on the first frame** (preprocess), **steady** forever
after, and **thinning to nothing over one lifetime** once the player dies —
no hard cut. **[proposal]**

**Contrast against the real background.** Motes have to be visible over the
wall `#1b1620` and invisible enough not to compete with the trap warning.
Warm pale `#c89a5a` at α 0.35 is about 4 : 1 against the wall and nearly
nothing against a torch pool, which is correct — dust shows where it is lit.
**[proposal]**

**Scale against the character.** 1–2 px per mote against a 29 px character:
clearly air, never objects. **[proposal]**

**Change over life.** Alpha ramps 0 → 0.35 → 0 so motes fade in and out
rather than popping at the edges of the box — with a 60-particle field and
no `one_shot`, popping is the thing that would give it away. **[decided]**

**Variation.** Velocity ± 60 %, scale ± 50 %. **[proposal]**

**Layering: one emitter.** **[proposal]** A second would add nothing;
Assignment 6 asks each emitter to have a job and this effect has one.

### 2.3 The settings

Node type: **`GPUParticles2D`**, one. **[proposal]**

`local_coords`: **off**. The field belongs to the room, not to a node.
**[proposal]**

`preprocess`: **8.0** — one full lifetime, so the field is at steady state on
the first drawn frame. **This is the feature Effect A does not use** and it
is the assignment's named failure: without it the room starts empty and
fills in over eight seconds, on every single scene load. **[decided]**

`visibility_rect`: **`Rect2(0, 0, 640, 200)`** — the air volume, set and
checked. **[proposal]**

| | value |
|---|---|
| `amount` | 60 |
| `one_shot` | false |
| `explosiveness` | 0.0 |
| `lifetime` | 8.0 |
| `emission_shape` | **Box**, extents (320, 100), centred at (320, 100) |
| `initial_velocity_min/max` | 2 / 6 |
| `direction` | (−0.4, 1.0) normalised — drifting down and slightly left |
| `spread` | 25° |
| `gravity` | (0, 2) |
| `damping_min/max` | 0 / 0 |
| `scale_min/max` | 1.0 / 2.0 |
| `color_ramp` | `#c89a5a`, α 0 → 0.35 → 0.35 → 0 |
| draw material | default (Mix). **Not additive** — additive motes would bloom inside a torch pool. |

### 2.4 Observable rules

| # | Rule |
|---|---|
| B1 | The field is at steady state on the **first drawn frame** after the scene loads, not filling in. |
| B2 | `emitting` goes false when `died` fires, and existing motes finish their lives rather than vanishing. |
| B3 | **While the tree is paused**, the effect stops with it. `process_mode` is `inherit`, so a paused game is a frozen field — correct, because a frozen game with drifting dust reads as a bug. |
| B4 | **While the node is hidden**, it keeps emitting and keeps simulating. Showing it again must not produce a refill. |
| B5 | It never writes game state. It reads `health` and listens to `died`. |

**No feedback loop here, so no `amount_ratio` mapping.** The assignment
requires `amount_ratio` *if* Effect B is a feedback loop; this one is
ambience. §0.1 records that `amount_ratio` exists on this build anyway, so
the choice was a design decision and not a version limitation. **[decided]**

### 2.5 The frame strip

Preview: `godot/previews/dungeon_motes_preview.tscn`, same real background.
The condition **starts at frame 10** (scene already loaded) and **ends at
frame 100** — the preview kills the player.

Read frames **10, 11, 40, 100, 130, 340**, and **frame 1** — revision 6.0.3, because B1 is a claim about the first drawn frame. **[proposal]**

| Frame | Should show |
|---|---|
| 10 | A **full** field. If it is empty, `preprocess` is not doing its job — this is the frame the whole feature exists for. |
| 11 | Indistinguishable from 10 at a glance; motes have moved 0.2 px. |
| 40 | Steady state, different motes, same density. |
| 100 | The last frame before the condition ends. Still full. |
| 130 | One second after. **Revision 6.0.3: still full** — 409 mote px against 412 at the stop. The fall begins around 2 s and the thinning is read at 160 and 220. |
| 340 | Empty. 8 s is one full lifetime after the stop. |

---

## 3. Boundaries

Unchanged by this work: collision layers and shapes, player movement, the
input map, the trap's state machine and every one of its timings, every
existing test and its expectations, **every file in `godot/shaders/`**, and
every object that is not an effect node.

Presentation code may **read** game state. It never writes it. The three
nodes the Assignment 6 port already added — `room_backdrop.gd`,
`room_audio.gd`, `pose_driver.gd` — keep that boundary and the effects keep
it too.

Effect settings live in **scene files** in `godot/effects/`, not in code.

---

## 4. The evidence split

| Rule | Checked by | How |
|---|---|---|
| A1 fires on every event | **headless** | drive the player through all three detection zones with real input; count bursts against `fired` emissions |
| A1 never otherwise | **headless** | assert zero burst instances exist on the frame after `_ready()` |
| A2 position | **headless** | compare each instance's global x with the emitting trap's, and y with 200.0 |
| A3 overlap | **headless** | fire two events 0.20 s apart; assert two live instances and that the first one's particles were not reset |
| A4 ceiling | **headless** | drive a full walk; assert the live-instance count never exceeds 3 |
| A6 frees itself | **headless** | assert instance count returns to 0 within 0.70 s of the last event |
| Every setting in §1.3 | **headless** | configuration test, reading each loaded resource back against this brief's value |
| B1 full on frame 1 | **frame strip** | frame 10 of the motes strip. A headless run draws nothing and cannot see a field. |
| B2 stop | **headless** | assert `emitting` false after `died`, and particles still alive |
| B3 paused | **headless** | set `get_tree().paused`, assert the field does not advance |
| B4 hidden | **headless** | hide, advance, show; assert `emitting` stayed true |
| Every setting in §2.3 | **headless** | configuration test |
| **Does the burst read as grit?** | **HUMAN** | play; watch a trap fire at x 320 (lit) and x 208 (dim) |
| **Is it the right size beside the character?** | **HUMAN** | play at 1280 × 720, stand the character next to a firing trap |
| **Do rapid repeats look stamped?** | **HUMAN** | walk the whole room, three traps in one pass, twice |
| **Do the motes read as air and not as snow?** | **HUMAN** | play; stand still for ten seconds |
| **Does the music mask the trap?** | **HUMAN** | play with sound on, then with `room_audio.gd`'s music muted. walker-ninja's CONCEPT 1.1 predicted a 124 bpm bed would drown a warning window, and this game's whole fairness argument is 0.40 s. |
| **Edge of screen** | **HUMAN** | fire the trap nearest a wall; the burst must not pop out |
| GPU price | **HUMAN** | Visual Profiler, effects off then on at the heaviest state |

No headless run establishes any HUMAN row. That is the point of the split.

---

## 5. Price predictions and budget

| | Effect A | Effect B |
|---|---|---|
| Peak particle count | **96** (3 × 32) — a design ceiling, not a measured peak; Revision 6.0.2 | **60** |
| Predicted headless CPU price | **≈ 0 ms over the control**, by construction | **≈ 0 ms over the control** |
| Predicted GPU time | **≤ 0.30 ms** | **≤ 0.20 ms** |
| Budget, and the price it is compared on | **0.30 ms GPU** | **0.20 ms GPU** |

**Both effects are GPU nodes, so both are compared on GPU time.** The
headless CPU measurement is still run and still reported, with an
empty-scene control, because the prediction that it reads ≈ 0 is itself a
claim this assignment asks to be tested. If the cost script reports a
*difference* for a GPU effect, something is wrong with the script or with
the prediction, and the brief would rather be caught than vague.
**[proposal — the numbers; [decided] that the comparison is on GPU time]**

---

## 6. Predicted failures

| # | What could go wrong | The check that catches it |
|---|---|---|
| F1 | A scene file written with `initial_velocity` instead of `initial_velocity_min`. §0.2 measured that this is **accepted and discarded** on 4.7.2, so the effect runs at defaults and nothing errors. | The configuration test, which reads the real property back. Step 2 runs this mutation deliberately and it must exit 1. |
| F2 | A scene file written with `scale_random`, which does not exist at all. | Same test; `get()` returns `<null>` and the comparison fails. |
| F3 | Effect A built as **one** `one_shot` node reused per event, so the second of two close events is silently dropped. | A3's assertion: two events 0.20 s apart must produce two live instances. |
| F4 | Effect B shipped **without `preprocess`**, so every scene load starts with an empty room that fills over 8 s. | Frame 10 of the motes strip. No headless test can see this. |
| F5 | `visibility_rect` left at the default and too small, so a burst near a wall is culled and pops out. | The configuration test asserts the value; the HUMAN edge-of-screen check sees the symptom. |
| F6 | The burst parented to the trap. Nothing frees traps in this game, so **this would never fail here** — and would fail silently in the next game that reuses the code. | A5's assertion that the instance's parent is the room. |
| F7 | A colour ramp with no visible effect because the draw material ignores vertex colour. 2D `CanvasItemMaterial` has no such switch, so this is a 3D failure that does **not** apply to these effects. | Stated so a reviewer knows it was considered and ruled out, not missed. |

---

## 7. The brief answers

**Which node type does each effect use, and which features does it lack?**
Both are `GPUParticles2D`. §0.1 probed the build: it lacks none of the
features this brief names. A `CPUParticles2D` would lack turbulence,
attractors, collision, sub-emitters and trails, and would also lack
`amount_ratio` — none of which either effect uses, so the choice was made on
where the process step runs, not on a missing feature.

**With `local_coords` as set, what does Effect A do if its parent moves after
the event?** Nothing. `local_coords` is off, so particles are simulated in
world space and stay where they were born. Moving the root mid-life moves
nothing that is already alive. In this game nothing moves the root, and the
burst is parented to the room rather than to the trap, so the question is
answered twice over.

**Under the retrigger rule, how many Effect A bursts can be alive at once?
What peak particle count does that give?** Three, and 96. A trap's full cycle
from `FIRING` back to `FIRING` is 0.18 + 0.22 + 0.60 + 0.40 = 1.40 s, and a
burst lives 0.60 s, so no trap can overlap itself. Three traps exist. Each
burst is 4 + 20 + 8 = 32 particles.

**What will a headless run report as the cost of a GPU effect, and why?**
Approximately the control, because a headless run uses a dummy renderer: it
draws nothing and runs no GPU particle process. The process step of a
`GPUParticles2D` *is* a shader on the graphics card, so a measurement that
never reaches the card has nothing of it to measure. What is left is the
node's own bookkeeping, which is near zero.
**With vsync on, FPS would read the display's refresh rate with the effects
off and the same with them on**, because vsync holds the frame rate there
until a frame actually misses. 96 particles will not make a 5080 miss. FPS
is the wrong instrument twice over, and GPU time from the Visual Profiler is
the right one.

**What does Effect B show on the first frame after its scene loads, with
`preprocess` and without it?** With `preprocess = 8.0`, a full field at
steady state — the engine simulates one whole lifetime before the first
frame is drawn. Without it, an **empty room** that fills in over eight
seconds, on every scene load, including every test run and every death.
**While the tree is paused**, the field freezes, because `process_mode` is
`inherit`. **While the node is hidden**, it keeps emitting and simulating, so
showing it again does not produce a refill.

**Which settings belong to emission, which to process, and which to draw?**

| Step | Settings |
|---|---|
| **Emission** | `amount`, `one_shot`, `explosiveness`, `lifetime`, `emission_shape` and its extents, `preprocess`, `amount_ratio` |
| **Process** | `initial_velocity_min/max`, `direction`, `spread`, `gravity`, `damping_min/max`, `scale_min/max`, `scale_curve`, `color_ramp` — everything a `ParticleProcessMaterial` holds |
| **Draw** | the texture, the `CanvasItemMaterial` and its blend mode, `visibility_rect`, `local_coords` |

`local_coords` and `visibility_rect` sit on the node rather than in either
material, and both decide what is drawn and where rather than how a particle
moves, so they are listed under draw.

---

## 8. What this brief does not yet settle

- Whether 0.60 s is the right burst length is a judgement that needs the
  running game; §1.2's phases are a starting point and the tuning loop may
  move them. Any change is appended here with a date, as A5's revisions were.
- Whether the music masks the trap warning (§4) is an open perceptual check
  carried over from walker-ninja's CONCEPT 1.1. It has never been run in
  *this* game.
- The mote colour is specified against the wall. It has not been judged
  inside a torch pool, which is the one place it might be too visible.

---

# Revision 6.0.1 — 2026-11-07 — `Flash.scale_min/max` 1.6 / 2.4 → 5.0 / 7.0

**Supersedes the `scale_min/max` cell of §1.3's `Flash` column.** Everything
else in that table stands.

| | before | after |
|---|---|---|
| `Flash.scale_min` | 1.6 | **5.0** |
| `Flash.scale_max` | 2.4 | **7.0** |

**Why.** §1.2 gives `Flash` the job of owning frame one — "a few large pale
chunks at the lip, bright on the very first frame". At 1.6 / 2.4 the flash
particles came out the same size on screen as the `Grit` specks beside them, so
frame 10 of `captures/hit_burst/r0-strip.png` reads as one undifferentiated
cluster of small dots and the impact phase exists in the timing but not in the
picture. This is the first revision of Assignment 6's tuning loop and the full
record of it — the author's reading of the running game, Claude's prediction
written before the recapture, where that prediction was wrong, and the author's
verdict — is in `TUNING.md` under **2026-11-07 — Effect A, r1**.

**Kept** on the author's verdict in the running game after the recapture.

**What changed with it, in the same commit:** `godot/effects/hit_burst.tscn`
and the expected value in `godot/tests/test_hit_burst_config.gd`. That test
reads §1.3's numbers back off the loaded resource, so a revision that moved only
two of the three would have failed it — which is the loop working as designed
rather than a near miss. 80 checks, 0 failures after the change.

**Still open, and deliberately not in this revision.** With `Flash` now visible,
`captures/hit_burst/r0-vs-r1-frame10.png` shows it sitting on the trap's **base**
rather than at the floor line at its lip, which is where §1.1 puts the origin of
the burst. `Flash` emits from a Point at `spread` 55°, so most of it goes
straight up from the origin and lands on the trap body. That is a candidate for a
later revision; this loop moves one setting at a time.

---

# Revision 6.0.2 — 2026-11-07 — A4's ceiling of 3 is correct and unreachable

**Amends §1.4 rule A4 and the "Peak particle count" row of §5. The numbers do
not change; what they are a claim *about* does.**

A4 says "at most 3 bursts alive at once, so at most 96 particles", and §7
repeats the reasoning: a trap's cycle is 1.40 s, a burst lives 0.60 s, so no
trap overlaps itself, and three traps is the ceiling. All of that is true. It is
also **not reachable by playing this room**, and the brief should have said so:

| | |
|---|---|
| Trap spacing | `SpikeTrap1/2/3` at x **208, 320, 432** → **112 px** apart |
| Player speed | `Player.SPEED = 96.0` — `godot/features/player/player.gd:19` |
| Time between two traps firing | 112 ÷ 96 = **1.17 s** |
| Burst lifetime | **0.60 s** |

Each trap's detect zone is offset ahead of it by the same `SPEED × WARN_SECONDS`
(`godot/features/traps/spike_trap.gd:33`), so the offset cancels and consecutive
`fired` events are 1.17 s apart at full speed. Crossing 112 px inside a 0.60 s
burst lifetime would need 187 px/s, and the player cannot move that fast.
**In real play at most one burst is alive at any moment, and the peak particle
count in play is 32, not 96.**

**What this changes:**

- **A4 stands as a ceiling**, and §5's 96 stays the number the GPU budget is set
  against — a ceiling the design permits is the right thing to budget for. It is
  a **design ceiling, not a measured peak**, and §5's row is relabelled as such.
- **§4's A4 row was close to vacuous.** "Drive a full walk; assert the live
  instance count never exceeds 3" passes whether the ceiling works or not,
  because the count never exceeds 1. The state test must therefore **report the
  maximum it actually observed** alongside the assertion, so a reader can see
  that the walk reached 1 and not 3.
- **§4's A3 row is synthetic, and must be labelled.** Two events 0.20 s apart
  cannot be produced by walking; the test emits them directly, and the preview's
  `retrigger` export does the same for the strip. A3 is still a real rule — it is
  what stops the design from being the single reused `one_shot` node of F3 — but
  the evidence for it is a constructed case, not play.

**Why it was wrong in the brief.** The 1.40 s figure was taken from the trap's
own state machine, which is the right source for "can a trap overlap *itself*",
and then the step to "three traps, so three bursts" was made without ever asking
how long it takes a player to walk between two of them. The arithmetic that was
missing is one division.

---

# Revision 6.0.3 — 2026-11-07 — Effect B's strip: frame 1, a control, and one prediction that did not hold

**Amends §2.5. The effect itself is unchanged**; this is about the evidence.

### 1. Frame **1** is added to the frames the strip reads

§2.4 B1 is a claim about the **first drawn frame**. §2.5's list started at
frame 10, which is a third of a second later and is not it. Frame 1 is now
kept and is the first panel of `captures/dungeon_motes/r0-strip.png`. The read
list is **1, 10, 11, 40, 100, 130, 340**.

### 2. A control strip, because one strip cannot show `preprocess` working

A full field and a field that filled quickly look identical in a single
capture. F4 is a claim about the *difference*, so the difference is captured:
the same preview, with `preprocess` mutated to **0.0** in the scene file and
reverted immediately afterwards, is `captures/dungeon_motes/f4-no-preprocess/`.
A third capture with the field switched off entirely gives an absolute zero to
count against. Mote pixels, against that baseline:

| frame | `preprocess = 8.0` | `preprocess = 0.0` |
|---|---|---|
| 1 | **578** | **12** |
| 10 | 558 | 44 |
| 40 | 567 | 108 |

This is the same mutation discipline §0.2 and Step 2 used for Effect A, applied
to the one rule a headless run cannot reach.

### 3. §2.5's frame-130 expectation was wrong

The table said frame 130 — one second after the condition ends — should be
"thinner, not empty". Measured, it is **not yet thinner**: 409 mote pixels
against 412 at the death. The field holds for about two seconds and then falls
away, reaching 0 at exactly 8.0 s.

The reason is in §2.2's own ramp and was not carried through to §2.5. Alpha is
`0 → 0.35 → 0.35 → 0` at offsets 0, 0.15, 0.85, 1.0, so a mote is at full alpha
for 70 % of its life and only fades over its last 1.2 s. One second after the
births stop, the oldest motes are the only ones dimming and they were already
dimming. Frame 130's row is corrected to **"still full; the fall begins around
2 s"**, and the thinning is read at 160 and 220 instead.

