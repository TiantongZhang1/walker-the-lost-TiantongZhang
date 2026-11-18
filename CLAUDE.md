# CLAUDE.md

Godot 4 game repository, GDScript, project in `godot/`.

## Project context

Every fact carries the file it came from. Check them; do not trust them.

| Fact | Value | Reference |
|---|---|---|
| Engine, renderer | Godot **4.7.2.stable.official** `ed1daf0bf`, **Forward+** | the banner every `scripts/run-test.sh` run prints; `godot/project.godot:15` |
| Main scene, resolution | `res://game/main.tscn`; 640 × 360, nearest-neighbour | `godot/project.godot:14` `:19` `:65` |
| **Physics tick** | **60** — `physics_ticks_per_second` is unset, so the engine default | `godot/project.godot`, no `[physics]` section |
| Player | 16 px = 1 m; `SPEED = 96.0`, `JUMP_VELOCITY = -260.0`, `GRAVITY`, `health`, `signal died` | `godot/features/player/player.gd:26` `:36` `:37` `:38` `:45` `:29` |
| Step-dust stride | `stride_px = 24.0` — the cycle's frame rate is derived from it | `godot/game/main.tscn:78` |
| Trap timings | 0.40 + 0.18 + 0.22 + 0.60 = **1.40 s** | `godot/features/traps/spike_trap.gd:39` `:40` `:41` `:42` |

Scenes are referenced **by node name, never by line**; an editor save
renumbers nodes. `tools/check_claude_refs.py` asserts these both ways.

### The two clips, and the state machine that plays them

Both live in `godot/animations/player.tres`, on `player.tscn`; `CHANGE-BRIEF.md` §3–§7 and revision 7.0.1 hold the cells, cycle spec, phase table and transitions.

| | **`run` — the cycle** | **`swing` — the committing action** |
|---|---|---|
| Route | **2D cutout rig** — `Node2D` pivots, rotation and position | **`Sprite2D` + `hframes`/`vframes`, frame track** |
| Plays on | `Rig`, `Rig/LegFront`, `Rig/LegBack` | `Rig/Body`, `Hitbox` |
| Rate, length | **12 fps**, 0.250 s = one stride, `LOOP_LINEAR`, step **1/12** | **30 fps**, 18 frames, 0.600 s, `LOOP_NONE`, step **1/30** |
| Shape | seam: every interpolated track ends where it started | startup 0–5, active 6–9, recovery 10–17 |

Sheet `godot/assets/sprites/player_sheet.png`: **32 × 32 cells, 4 × 2**, CUT
from the committed GPT-6 poses by `tools/make_sprites.py`, which asserts the
cut is lossless; cell 7 is blank on purpose. `player.gd` owns the state
machine — locking movement is gameplay, not presentation — with states `IDLE`,
`RUN`, `AIRBORNE`, `SWING`, `DEAD`. `features/player/player_anim.gd` reads it,
plays the clips, writes no game state, and **replaces `pose_driver.gd`**,
which wrote `Sprite2D.texture` every `_process`.

**Test commands.** Always through the wrapper: it is the only thing that fails
on `SHADER ERROR`, `SCRIPT ERROR` or **`Failed loading resource`**, all of
which Godot prints while exiting 0.

```bash
godot --headless --path godot --import          # once after cloning
./scripts/run-test.sh <test>.gd <fps|realtime> [timeout-seconds]
```

At **60**: every `test_*_config.gd`, `test_input_map.gd`, `check_assets_3d.gd`,
`test_materials.gd`, the read-backs, the pins, the edge tests. At **30, 60 and
144**: `test_trap_warning.gd`, `test_trap_shader_driver.gd`,
`test_step_dust_state.gd`. `cost_effects.gd` as `60 300`; `realtime` for tests
that wait on audio. `gpu_cost_effects.gd` is **windowed**
(`scripts/run-gpu-cost.sh`), never headless. `godot` is not on PATH —
`scripts/run-test.sh:51` resolves it, `GODOT=` overrides.

### Headless facts

- A dummy renderer **draws nothing** but **advances clips and reads their
  structure** — whether the motion *reads* is not observable here.
- **Key times are 32-bit floats; compare with a tolerance**, never `==`.
- **Branch on track type.** `value_track_get_update_mode` is for value tracks
  only — on a 3D transform track it errors and answers `UPDATE_CONTINUOUS`;
  that track's subname is a **bone**, a blend-shape track's a **blend shape**.
- **Frame strips come from a windowed Movie Maker run the author starts**, and
  the verdict on one is theirs, never delegated. Uniform defaults are not
  reported headlessly; never add `--rendering-driver`.

## Current change

@CHANGE-BRIEF.md

## Ownership

**`godot/shaders/` is hand-written by the human, never edited by an agent;** if
one looks wrong, say so and stop. After any agent session
`git diff --stat godot/shaders/` must print nothing, and `scripts/run-test.sh`
is diffed too — A7 changed it once, in its own commit, for the
`Failed loading resource` rule; nothing else may. **Clips live as resources**
in `godot/animations/` or the scene that owns them, **never built in code at
runtime**; effect settings live in `godot/effects/`. Every prediction and
`TUNING.md` verdict is the human's.

## One authority

**Exactly one node writes to each animated node. Never add a second writer.**
`Player/AnimationPlayer` is that node for all of them: `Rig:position:y`,
`Rig/Body:frame`, both legs' `rotation_degrees` and `visible`, and
`Hitbox:monitoring`. `Rig/Body.texture` is set once in the scene, never at
runtime. `player_anim.gd` calls `play()` and writes `Rig.scale.x` (facing),
which **no clip keys**; it runs on the **physics** tick, like the mixer and
like `player.gd`. `CHANGE-BRIEF.md` §5 states that wrinkle, not hides it.

## Godot 4 names

Use Godot 4 names for **4.7.2**. Godot 3's boolean `loop`, `playback_speed` and
`AnimatedSprite` load without complaint and leave the setting at its default:
use **`loop_mode`**, **`speed_scale`**, `AnimatedSprite2D` + `sprite_frames`.
`ParticlesMaterial`/`Particles2D` fail loudly; the *property* names do not —
use `initial_velocity_min/_max`, `scale_min/_max`, `damping_min/_max`. **If
unsure a property exists here, say so instead of guessing**;
`ClassDB.class_get_property_list()` settles it.

## Out of scope

Do not touch: collision layers and existing shapes, `SPEED`, `JUMP_VELOCITY`,
`GRAVITY`, the existing input bindings, the trap's state machine or its timings,
any existing test's expectations except `test_input_map.gd`'s action count, the
`.glb` files, `godot/shaders/`, every A6 effect scene, and the five pose PNGs in
`godot/assets/poses/`, which stay committed and credited. Presentation reads
game state, never writes it — the one exception A7 names is the `swing` clip
writing `Hitbox.monitoring`, a gameplay fact on the timeline.

## Unconfirmed

- `CHANGE-BRIEF.md` §6's phase numbers are **[proposal]** until the author
  plays it. Keys come from the table; a change goes in the table.
- The three `.glb` files have **`skins: 0`, no animations** (glTF probe,
  2026-11-15): no imported rig to key. The hitbox **can hit nothing** — no enemy.
