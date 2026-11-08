# COMPONENTS.md — what this film explains, and what it leaves out

Six components, 66 inventoried source files, 40 explicit exclusions. The
machine-checkable half of this is `gamedev-evidence.json`, written by
`scripts/build_particles_ledger.py` and verified by
`./art godot-gamedev --check`. That check decides whether every file is
accounted for and whether every excerpt matches its source. It cannot decide
whether a mechanism was explained clearly or whether an exclusion is honest.
That is what this file is for, and it is mine to defend.

Game-source revision `31fb5a7`.

---

## 1. `effect-a-grit-burst` — beats B02, B03, B03A, B04, B05

Nine files: the effect scene and its lifecycle script, the spawner, the spike
trap that owns the event, the preview scene, and the two test suites.

**Where it lives and what data enters.** `godot/effects/hit_burst.tscn` is
three `GPUParticles2D` under one `Node2D`. Nothing enters it but the position
it is placed at: `hit_burst_spawner.gd` connects to the trap's existing
`fired` signal, binds the trap that sent it, instances the scene, sets its
global position and calls `fire()`.

**The important lines.** `spike_trap.gd:98`, `fired.emit()`, inside the
`State.FIRING` branch — the event, which existed before this assignment and
was not touched. `hit_burst.tscn:106-116`, the `Flash` node, where all three
parts of a particle system are visible at once: emission on the node, process
behind `process_material`, draw in the `CanvasItemMaterial` and
`visibility_rect`.

**What changes, and what the player sees.** 32 particles over 0.60 s: four
large pale chunks at the lip, twenty specks thrown up and out, eight soft
puffs that outlast them. It tells the player that *this* trap has just fired
and is therefore safe for the next six tenths of a second, which is the one
piece of information the game has no other way to give.

**Why this design, and the trade-off.** The retrigger rule is **overlap** —
one instance per event — and the alternative was one reused `one_shot` node.
That alternative is the assignment's named failure: setting `emitting = true`
on a one-shot node that is still emitting does not restart it, so the second
of two close events is silently dropped. The cost of overlap is that the
effect allocates and frees a scene per event, and B11B shows that cost is the
only thing a headless run can weigh.

**What the film does not show about it.** The `Grit` and `Dust` emitters'
settings are named but not shown line by line; the config suite reads all 80
of them back and `CHANGE-BRIEF.md` §1.3 holds them.

## 2. `effect-b-dungeon-motes` — beats B06, B07, B07A, B07B

Six files: the effect scene and its condition script, the preview, and the two
suites.

**Where it lives and what data enters.** One `GPUParticles2D`. The only thing
that reaches it is the player's `died` signal; `dungeon_motes.gd` writes
exactly one property, `emitting`, and only ever to `false`.

**The important line.** `dungeon_motes.tscn:52`, `preprocess = 8.0`. One full
lifetime, simulated before the first frame is drawn.

**What changes, and what the player sees.** Sixty one-to-two-pixel motes
drifting down and slightly left, warm against a cold wall, at α 0.35. Its job
is place, not information. The one functional thing it does is keep the
picture from reading as frozen when the player stands still.

**Why this design, and the trade-off.** `preprocess` is the feature Effect A
does not use, and the trade-off is that it costs one whole simulated lifetime
at load. The alternative — starting empty — is F4: every scene load, every
death, every test run begins in a room that fills over eight seconds, and
nothing errors.

**What the film does not show about it.** B4 — that a hidden node keeps
emitting and simulating, so showing it again does not produce a refill — is
asserted by the state suite and is not in the film. The state test also prints
six `NOTE` lines that are deliberately not checks, because a headless run
cannot reach them.

## 3. `effect-c-step-dust` — beats B10, B11

Seven files: the effect scene, its lifecycle script, the driver, the preview
and the two suites.

**Where it lives and what data enters.** Two `GPUParticles2D` under one
`Node2D`. `step_dust_driver.gd` reads `global_position`, `is_on_floor()`,
`velocity` and `health` from the player and writes nothing back — the same
three things `pose_driver.gd` already read.

**The important lines.** `step_dust_driver.gd:112-115`: the accumulated
distance, the `while` that handles a frame covering more than one stride, and
the spawn stepped back by the overshoot.

**What changes, and what the player sees.** One puff per 24 px travelled on
the ground, plus one on every landing at `amount_ratio` 1.0 against a stride's
0.6. The trail runs two or three puffs deep because a puff outlives a stride.

**Why this design, and the trade-off.** The event does not exist in the game,
and §3 of the brief keeps `player.gd` and the input map out of scope, so the
driver derives one from measured position delta rather than asking for a new
signal. The trade-off is that a derived event can be subtly wrong in ways a
real signal cannot: the first version placed the puff at the player's current
position and the spacing came out frame-rate dependent, 3.2 px off at 30 fps
and correct at 60. The suite runs at 30, 60 and 144 for exactly that reason.

**What the film does not show about it.** Effect C is not required by the
assignment, which asks for two effects. It exists because the author's verdict
on Effect B named a gap ambience is the wrong tool for. Its tuning loop has an
r0 reading and **no author verdict yet**; the film says so rather than
implying a loop that did not close.

## 4. `process-shader` — beats B08, B09

Two files: the generated shader and the scratch scene the material was lifted
into.

**Where it lives and what data enters.** Nothing loads it. It is in the
project to be read. `godot/previews/step6_scratch.tscn` holds a verbatim copy
of Effect A's `PPM_dust`, lifted by script with its four sub-resources so that
nothing was retyped; a headless check compared twelve settings against the
real `Dust` emitter and found zero mismatches. The author converted that
material to a `ShaderMaterial` in the editor and saved it.

**The important lines.** 161 and 162, inside `process_display_param`: the
scale multiplied by a lookup into `scale_curve`, and the colour multiplied by
a lookup into `color_ramp`, both at the particle's own normalised lifetime.
That is what a curve in the Inspector actually is — a one-dimensional texture
sampled once per particle per frame, on the graphics card.

**Why Dust.** Three of the six emitters carry **both** a colour ramp and a
scale curve — `Flash`, `Dust` and Effect C's `Puff` — and the generated shader
only contains those two lines when the material has them. `Dust` is the one
whose curves a strip can read: its `scale_curve` rises 0.6 → 1.8 across a
0.45 s life, so the puff visibly grows while its alpha falls to zero. `Flash`
lives 0.12 s and is additive, which is exactly why revision 6.0.1's strip could
not see it on five of its six frames. Converting any other emitter — or, as
happened first, a default empty one — produces a file in which two of the
seven required line references do not exist. Line 160, `// Compile-time add
textures.`, is Godot's insertion point and in the empty version it has nothing
after it.

## 5. `the-room` — beats B03, B07A, B07B, B11

Thirty-four files: the room scene and its scripts, the player, the trap
warning driver and its shader, the sprites and poses and audio, and
`project.godot`.

**Why these are one component rather than background.** The contrast
decisions in the brief are made against *this* backdrop — the unlit gap in the
floor lip at each trap, the torch pools, the floor tile `#16242B` — and the
HUMAN checks are run at this window size. A film that explained the effects
without the surface they are judged against would be explaining them against
nothing. `game/debug_keys.gd` is here too: it is the F9 vsync toggle this
assignment added, and it is in the room because it is a property of the window
rather than of any effect.

## 6. `evidence-harness` — beats B11A, B11B

Three files: the cost script, the capture driver and the input-map check.

**What it is for.** Every price claim and every frame of footage in this film
rests on these. The cost script runs the assignment's four named conditions
with an empty-scene control and a twice-run baseline, so that it states its
own noise floor before reporting any difference. The capture driver asserts
its own outcome. The input-map check is how the F9 key is shown to have added
no action — three non-`ui_` actions before and after.

**What they cannot prove.** The cost script measures CPU wall clock in a run
that draws nothing. It cannot see a GPU particle process, because there isn't
one. Its windowed sibling `tests/gpu_cost_effects.gd` can, and is in this
component for that reason: it reads the same GPU timestamp query the editor's
Visual Profiler displays, and **refuses to run headless**, because a dummy
renderer would report `0.000` ms for every condition and look exactly like
three effects that cost nothing.

**What that one cannot prove either.** A per-effect price. Its own
containment check fails — "all three" measures cheaper than Effect B alone —
which puts the differences below the instrument's floor. What it establishes
is the ceiling: 0.022 ms for the whole frame against a 0.60 ms budget.

---

## The exclusions, and why they are honest

Forty files are excluded with reasons, in three groups.

**Assignment 5's shaders and materials** — `dungeon_surface.gdshader`,
`hint_bands.gdshader`, `standard_generated.gdshader`, the hint experiment and
showcase scenes, four `.tres` materials, three texture pairs, and four test
and tool files. They are the previous film's subject. Their suites still run
and still pass, and `git diff --stat godot/shaders/` is empty for every agent
commit of this assignment — but shaders and materials are not what this film
explains, and claiming them as components would make the ledger say otherwise.
`standard_generated.gdshader` is excluded with its own reason, because leaving
both generated shaders in scope would invite a reviewer to think the wrong one
was converted.

**Assignment 3's 3D assets** — three `.glb` files and their `.import`
sidecars, and `check_assets_3d.gd`. Carried across with the showcase scene; no
particle effect touches them.

**Carried-over and one-off tooling** — `route_driver.gd` and
`test_keyboard.gd` from walker-ninja, `setup_input_map.gd` which ran once on
2026-10-23, `write_textures.gd`, and `MATERIALS.md`, which is a document
inside the project rather than a file the game loads.

`write_textures.gd` is the one I would argue about with a reviewer, so it is
flagged here rather than buried: it is why this project has no downloaded or
generated art to license. It is excluded because **none of the six emitters in
this film has a texture at all**, so it is not a component of the particle
work — but if a reviewer thinks the texture question belongs in the film, that
file is where the answer lives, and `../../ATTRIBUTION.md` carries it.

Seven `.gitkeep` placeholders are listed rather than silently skipped, because
the reference asks for omissions to be explicit and arguable.
