# CLAUDE.md

Godot 4 game repository, GDScript, project in `godot/`.

## Project context

Every fact carries the file it came from. Check them; do not trust them.

| Fact | Value | Reference |
|---|---|---|
| Engine, renderer | Godot **4.7.2.stable.official** `ed1daf0bf`, **Forward+** | the banner every `scripts/run-test.sh` run prints; `godot/project.godot:15` |
| Main scene, resolution | `res://game/main.tscn`; 640 × 360, nearest-neighbour | `godot/project.godot:14` `:19` `:65` |
| **Physics tick** | **60** — `physics_ticks_per_second` is unset, so the engine default | `godot/project.godot`, no `[physics]` section |
| Player | 16 px = 1 m; `SPEED = 96.0`, `JUMP_VELOCITY = -260.0`, `GRAVITY`, `health`, `signal died` | `godot/features/player/player.gd:32` `:42` `:43` `:44` `:51` `:35` |
| Step-dust stride | `stride_px = 24.0` — the cycle's frame rate is derived from it | `godot/game/main.tscn:78` |
| Trap timings | 0.40 + 0.18 + 0.22 + 0.60 = **1.40 s** | `godot/features/traps/spike_trap.gd:39` `:40` `:41` `:42` |

Scenes are referenced **by node name, never by line**; an editor save
renumbers nodes. `tools/check_claude_refs.py` asserts these both ways.

### The two clips, and the state machine that plays them

`godot/animations/player.tres` (body, arm, hitbox) and `legs.tres` (the legs), on `player.tscn`. `CHANGE-BRIEF.md` §3–§7 plus revisions 7.0.1–7.0.10 hold the cells, cycle spec, phase table and transitions.

| | **`run` — the cycle** | **`swing` — the committing action** |
|---|---|---|
| Route | **2D cutout rig** — `Node2D` pivots, rotation and position | **`Sprite2D` + `hframes`/`vframes`, frame track** |
| Plays on | **`LegAnim`**: both legs | `Rig/Body`, `Hitbox`, `Rig/SwordArm` (pos + rot) |
| Rate, length | 0.500 s = **two steps**, `LOOP_LINEAR`, step **0.125** (rev 7.0.7) | **30 fps**, 18 frames, 0.600 s, `LOOP_NONE`, step **1/30** |
| Shape | seam: every interpolated track ends where it started | startup 0–5, active 6–9, recovery 10–17 |

Sheet `godot/assets/sprites/player_sheet.png`: **32 × 32 cells, 4 × 2**, CUT
from the committed GPT-6 poses by `tools/make_sprites.py`, which asserts the
cut is lossless; cell 7 is blank on purpose. `player.gd` owns the state
machine (`IDLE`, `RUN`, `AIRBORNE`, `SWING`, `DEAD`) because committing is
gameplay. **The lock narrowed three times (7.0.6 movement, 7.0.9 legs, 7.0.10
jump); a swing still cannot be cancelled, restarted or TURNED.**
`player_anim.gd` reads it, plays the clips, writes no game state, and
**replaces `pose_driver.gd`**, which wrote `Sprite2D.texture` each `_process`.

**Test commands.** Always through the wrapper: it is the only thing that fails
on `SHADER ERROR`, `SCRIPT ERROR` or **`Failed loading resource`**, all of
which Godot prints while exiting 0.

```bash
godot --headless --path godot --import          # once after cloning
./scripts/run-test.sh <test>.gd <fps|realtime> [timeout-seconds]
```

At **60**: every `test_*_config.gd`, `test_input_map.gd`, `check_assets_3d.gd`,
`test_materials.gd`, the read-backs, the pins, the edge tests, `measure_clocks.gd`.
At **30, 60 and 144**: `test_trap_warning.gd`, `test_trap_shader_driver.gd`,
`test_step_dust_state.gd`. `cost_effects.gd` as `60 300`; `realtime` for audio.
`gpu_cost_effects.gd` is **windowed** (`scripts/run-gpu-cost.sh`), never
headless. `godot` is not on PATH — `scripts/run-test.sh:51` resolves it.

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

**Exactly one node writes to each animated node.** **TWO** `AnimationPlayer`s,
partitioned BY NODE (revision 7.0.9): `LegAnim` owns `Rig/LegFront` and
`Rig/LegBack`; `AnimationPlayer` owns `Rig:position:y`, `Rig/Body:frame`,
`Rig/SwordArm`'s `position` AND `rotation_degrees`, `Blade:visible`,
`Hitbox:monitoring`. No node is on both lists and `test_player_clips.gd`
asserts the partition **both ways**. `Rig/Body.texture` is set once in the
scene. `player_anim.gd` plays both and writes `Rig.scale.x` (facing), which
**no clip keys**; both players and it are on the **physics** tick.

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
`.glb` files, `godot/shaders/`, every A6 effect scene, and `godot/assets/poses/`.
Presentation reads game state, never writes it — the one exception A7 names is
the `swing` clip writing `Hitbox.monitoring`, a gameplay fact on the timeline.

## Unconfirmed

- `CHANGE-BRIEF.md` §6's phase numbers are **[proposal]** until the author
  plays it. Keys come from the table; a change goes in the table.
- The three `.glb` files have **`skins: 0`, no animations** (glTF probe,
  2026-11-15): no imported rig to key. The hitbox **can hit nothing** — no enemy.
