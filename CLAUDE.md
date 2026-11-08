# CLAUDE.md

Godot 4 game repository, GDScript, project in `godot/`.

## Project context

Every fact carries the file it came from. Check them; do not trust them.

| Fact | Value | Reference |
|---|---|---|
| Engine | Godot **4.7.2.stable.official** `ed1daf0bf` | banner printed by every `scripts/run-test.sh` run |
| Renderer | **Forward+** | `godot/project.godot:15`. Not `rendering_method`: it equals the default, so editor saves delete it |
| Main scene | `res://game/main.tscn` | `godot/project.godot:14` |
| Logical resolution | 640 × 360, nearest-neighbour | `godot/project.godot:19`, `:59` |
| Scale | 16 px = 1 m | `godot/features/player/player.gd:13` |
| The floor line | **y = 200** — `Floor` at y 280 with a 640 × 160 shape | `godot/game/main.tscn`, node `Floor` |

**Scenes are referenced by node name, never by line:** an editor save
renumbers nodes and drops defaults. `tools/check_claude_refs.py` asserts them.

### The three particle effects

| | **A — grit burst** | **B — dungeon motes** | **C — step dust** |
|---|---|---|---|
| Job | one-shot, on a repeating event | ambience | one-shot, on a derived event |
| Node type | **`GPUParticles2D` × 3** under one `Node2D` | **× 1** | **× 2** under one `Node2D` |
| Scene | `godot/effects/hit_burst.tscn` | `godot/effects/dungeon_motes.tscn` | `godot/effects/step_dust.tscn` |
| Owns the event | `signal fired` — `godot/features/traps/spike_trap.gd:24`, emitted `:98` entering `State.FIRING` | `signal died` — `godot/features/player/player.gd:16`, emitted `:48` | **no signal exists**: `step_dust_driver.gd` derives it from distance travelled, one puff per `stride_px` |
| Appears in | `godot/game/main.tscn` — one instance per event, at the firing trap | `godot/game/main.tscn` — one node for the room | `godot/game/main.tscn` — `StepDustDriver`, `stride_px = 24` |
| Preview | `godot/previews/hit_burst_preview.tscn` | `godot/previews/dungeon_motes_preview.tscn` | `godot/previews/step_dust_preview.tscn` |
| Retrigger | **overlap**, at most 3 alive — a ceiling the room cannot reach, `CHANGE-BRIEF.md` revision 6.0.2 | n/a | overlap; the trail is 2–3 puffs |
| Feature the others lack | — | **`preprocess`**, Box emission | **`amount_ratio`** — 0.6 a stride, 1.0 a landing |
| State test rates | 60 | 60 | **30, 60 and 144** — the cadence is a distance |

### The state they read and never write

| | |
|---|---|
| Trap | `godot/features/traps/spike_trap.gd` — enum `:27`, `var state` `:51`, signals `:23` `:24` `:25` |
| Trap timings | `:39` `:40` `:41` `:42` — 0.40 + 0.18 + 0.22 + 0.60, a full cycle of **1.40 s** |
| Player | `godot/features/player/player.gd` — `var health` `:23`, `GRAVITY` `:21` |
| Nodes already keeping this boundary | `trap_warning_driver.gd`, `game/room_backdrop.gd`, `game/room_audio.gd`, `features/player/pose_driver.gd` |

**Test commands.** Always through the wrapper: it is the only thing that fails on a `SHADER ERROR` or `SCRIPT ERROR`, which Godot prints while exiting 0.

```bash
godot --headless --path godot --import          # once after cloning
./scripts/run-test.sh <test>.gd <fps|realtime> [timeout-seconds]
```

`test_*_config.gd`, `test_input_map.gd`, `check_assets_3d.gd` and
`test_materials.gd` run at **60**; `cost_effects.gd` as `60 300`.
`test_trap_warning.gd`, `test_trap_shader_driver.gd` and
`test_step_dust_state.gd` run at **30, 60 and 144** — a duration or a cadence
measured at one rate has not been measured. Other `test_*_state.gd` run at 60.

`godot` is not on PATH; the wrapper resolves it and `GODOT=` overrides — `scripts/run-test.sh:42`.

### Headless facts

- A headless run uses a **dummy renderer and draws nothing**: it can show a
  shader parses, what it declares and a float on a given frame, never colour.
  It **draws no particles and runs no GPU particle process** — node state
  (`emitting`, `amount_ratio`, visibility, instance counts) is observable, the
  look is not, and **a GPU effect's headless CPU price is ~0 by construction.**
- **Frame strips come from a windowed Movie Maker run, never a headless
  one.** An agent may take one when the author asks (they did, 2026-11-07);
  the verdict on a strip is the author's and is never delegated.
- It does **not** report uniform defaults; assert them with `get_shader_uniform_list()`. Never add `--rendering-driver` to a test.

## Current change

@CHANGE-BRIEF.md

## Godot 4 names

Use Godot 4 names for **4.7.2**. `ParticlesMaterial` and `Particles2D` do not
exist and fail loudly; the *property* names do not. `CHANGE-BRIEF.md` §0.2
measured that `ParticleProcessMaterial` here **has** `initial_velocity`,
`scale` and `damping` as `Vector2` properties with usage 12 that are **never
written to a scene file** — writing one is accepted and silently discarded.
Use `initial_velocity_min/_max`, `scale_min/_max`, `damping_min/_max`;
`scale_random` does not exist. **If you are unsure a property exists here,
say so instead of guessing** — `ClassDB.class_get_property_list()` settles
it in one run.

## Ownership

**`godot/shaders/` is hand-written by the human, never edited by an agent;**
if one looks wrong, say so and stop. **Dated exception, 2026-11-08, that
commit only:** Claude extracted `particles_generated.gdshader` from a `.tres`
the author converted in the editor.

**Effect settings live in scene files in `godot/effects/`, not in code.** A
driver may read state and set one value; it never holds the design.
`LANGUAGE-NOTES.md`, every prediction and every `TUNING.md` verdict are the
human's; an agent may check that line references point where they say. After
any agent session `git diff --stat godot/shaders/` must print nothing, and
`scripts/run-test.sh` is diffed too, since an agent can edit the wrapper.

## Out of scope

Do not touch: collision layers or shapes, player movement or the input map,
the trap's state machine or any of its timings, any existing test or its
expectations, the `.glb` files, the ported `room_backdrop.gd`,
`room_audio.gd`, `pose_driver.gd`, or anything that is not an effect node.

Presentation reads game state, never writes it, and an effect is not wired
into gameplay in the same step that builds it.

## Unconfirmed

- ~~Forward+ on real hardware; whether `source_color` changes the value the
  shader receives.~~ **Both settled 2026-10-24** — Vulkan 1.4.357, RTX 5080
  Laptop; it does not, and `hint_range` does not clamp. `TEST-REPORT.md`.
- ~~Every A6 budget in `CHANGE-BRIEF.md` §5 is a prediction — no GPU time read yet.~~ **Measured 2026-11-08, revision 6.0.6**: whole frame 0.022 ms at the design ceiling against a 0.60 ms combined budget, every budget met. The per-effect figures are below the instrument's floor and are not prices. `scripts/run-gpu-cost.sh`; it must not be run headless.
- **All three have an r0 strip** (`captures/`, `TUNING.md`). A has a kept
  revision; **B and C have no author verdict yet**, and both drift dust below
  the floor line (14-22 % and 11-29 %).
