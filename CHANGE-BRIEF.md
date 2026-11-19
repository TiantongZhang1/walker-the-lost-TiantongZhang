# CHANGE-BRIEF.md — Assignment 7 specification

**The Lost · walker-the-lost-TiantongZhang · Tiantong Zhang**

Drafted 2026-11-15. Committed before the first agent prompt of this
assignment. `CLAUDE.md` imports this file with `@CHANGE-BRIEF.md`, so it is
the contract the agent works to. Assignment 6's brief stays in history at tag
`a6.1`.

> **Tags.** **[decided]** — chosen by the author. **[proposal]** — derived by
> Claude and not yet confirmed. Anything the author adopts from a
> **[proposal]** is typed in by them and recorded in `SOURCES.md` and
> `FRICTIONAL.md`. Same convention as A5 and A6.

---

## 0. What this change is, in one paragraph

The player gets a **run cycle** played from a sprite sheet, and a **sword
swing** played on a 2D cutout rig. The run cycle loops. The swing is a
committing action: once it starts it finishes, which is a line out of this
game's own GDD rather than a rule invented for this assignment —
`the-lost-gdd/GDD.md:198`, *"The combo is committed: once a swing starts it
finishes, so holding attack is a real risk and letting go is a real choice."*
`GDD.md:393` lists the state machine this assignment finally builds: *idle /
run / jump / roll / combo-1,2,3 / cast.* A7 builds **idle, run, airborne,
swing and dead**; roll, cast and combo-2/3 stay unbuilt and are named as
limitations rather than left looking forgotten. **[decided]**

---

## 1. What exists now, and the authority problem this change inherits

Measured from the files, not remembered.

| | | Reference |
|---|---|---|
| Player | one `Sprite2D`, one `CollisionShape2D` (10 × 28), one `PoseDriver` | `godot/features/player/player.tscn` |
| Who writes the sprite | **`pose_driver.gd`**, every `_process`, writes `texture` and `flip_h` | `godot/features/player/pose_driver.gd:52` |
| Poses | five separate 32 × 32 PNGs, swapped by texture | `godot/assets/poses/` |
| AnimationPlayer | **none anywhere in the project** | `grep -rl AnimationPlayer godot/` is empty |
| Input actions | three: `move_left`, `move_right`, `jump` | `godot/project.godot` `[input]` |
| Physics tick | **60** (`physics_ticks_per_second` is unset, so the default) | `godot/project.godot` |
| Collision layer 6 | already named **`PlayerAttack`** | `godot/project.godot` `[layer_names]` |
| Player speed / step dust stride | `SPEED = 96.0`, `stride_px = 24.0` | `player.gd:19`, `game/main.tscn` |

**`pose_driver.gd` is the current authority over the player's `Sprite2D`**, and
the clip this assignment adds keys the same node. That is exactly the
collision Assignment 7 is about, and it is not hypothetical here: it is in the
repository today. The resolution is §5.

---

## 2. The two clips

### 2.1 Clip A — `run`, the cycle

| | |
|---|---|
| **What it communicates** | That the character is *moving under their own power*, not sliding. The game already has step dust kicked up every 24 px (Effect C, A6); until now the body above those puffs has been a single frozen pose, so the dust looked like it belonged to something else. |
| **Why the player needs it** | Speed is the only resource in this room — the traps are 1.17 s apart at walking speed and the warning window is 0.40 s. A run that reads as a run is how the player judges whether they will clear the next trap. |
| **Plays on** | `Player/Sprite2D` in `godot/features/player/player.tscn` |
| **Route** | **Sprite2D with `hframes`/`vframes` + an `AnimationPlayer` frame track** |
| **Why that route** | Chapter 10: *"Prefer it for anything gameplay reads. Then the hitbox, the sound and the frame live on one timeline."* The `AnimatedSprite2D` route would put the sprite outside the AnimationPlayer's read-back, give it no `callback_mode_process`, and hand the scene a second authority. |
| **Authority** | the `AnimationPlayer` named in §5 |
| **Reads** | `player.gd`'s `velocity`, `is_on_floor()`, `health`, and its new `action` — through `player_anim.gd`, which writes no game state |
| **Cycle or action** | **the cycle.** It loops. |

**[decided — that the run is the cycle and that it is a frame track]**

### 2.2 Clip B — `swing`, the committing action

| | |
|---|---|
| **What it communicates** | That the attack is a *commitment*. The startup is long enough to be read and punished; the active window is shorter than a spike trap's lethal window, so you cannot trade with a trap; the recovery is where you find out whether committing was right. |
| **Why the player needs it** | `GDD.md:196-198` makes the whole combat design rest on it: *"their attention is free for the two decisions that matter — when to stop attacking and roll."* Without visible phases there is no decision, only a button. |
| **Plays on** | a new `Player/SwordArm` cutout rig — a `Node2D` pivot carrying `Blade` (`Sprite2D`) and `Hitbox` (`Area2D`) |
| **Route** | **2D cutout rig, keyed as resource text.** Parts under a plain `Node2D` pivot, keyed on `rotation_degrees`. |
| **Why that route** | The three `.glb` models in `godot/assets/models/` were checked with a glTF JSON probe on 2026-11-15: **`skins: 0`, `animations: NONE`** on all three. There is no imported rig in this project to key, and building one is a different assignment. `Bone2D`/`Skeleton2D` with painted `Polygon2D` weights buys nothing for a two-part arm, and `SkeletonModificationStack2D` is marked **Experimental** in the class reference. |
| **Authority** | the same `AnimationPlayer`. Nothing else writes `SwordArm`. |
| **Reads** | `player.gd`'s `action` |
| **Cycle or action** | **the committing action.** `LOOP_NONE`. |

**[proposal — the cutout construction; [decided] that the swing is the
committing action and that it is a rig]**

---

## 3. The sheet

**Source: written by code, in this repository.** `tools/make_sprites.py`
already draws this game's sprites from the palette `CHANGE-BRIEF.md` fixed in
Assignment 5, and asserts two named prediction pixels so that a future edit
cannot move them silently. The run cycle is added to that file.

| | |
|---|---|
| Source | `tools/make_sprites.py`, this repository |
| Author | Tiantong Zhang, with Claude Code, 2026-11-15 |
| Licence | Mine. No external asset, no model, no downloaded art. |
| Date checked | n/a — nothing was fetched |
| **The editable source** | **the generator, not the PNG.** Assignment 7 asks for "the original file, as downloaded"; for a code-written sheet the code *is* that file, and it is committed. |
| Output | `godot/assets/sprites/player_sheet.png` |
| Cell size | **32 × 32** |
| Grid | **`hframes = 6`, `vframes = 2`** — 12 cells, 192 × 64 px |

**Why 32 × 32 and not the 16 × 28 the generator draws today.**
`pose_driver.gd:21-25` records the arithmetic that must survive: the figure's
feet sit on **row 30** of a 32 × 32 cell, the body box is 10 × 28 centred on
the origin, so its underside is at y = +14, and a centred 32 px sprite spans
y −16..+16 — which puts row 30 at exactly y = +14 with **no offset to
maintain**. Changing the cell size would mean re-deriving that. **[decided]**

**Frame order.**

| Cell | Clip | What it is |
|---|---|---|
| 0 | `run` | contact, right foot forward |
| 1 | `run` | down (weight low) |
| 2 | `run` | pass, right leg under the hip |
| 3 | `run` | contact, left foot forward |
| 4 | `run` | down |
| 5 | `run` | pass, left leg under the hip |
| 6 | `idle` | standing |
| 7 | `rising` | airborne, velocity.y < 0 |
| 8 | `falling` | airborne, velocity.y ≥ 0 |
| 9 | `dead` | collapsed |
| 10 | `swing` | braced stance, the body under the swinging arm |
| 11 | — | **deliberately blank** |

**Cell 11 is blank on purpose.** The grid is rectangular and eleven cells are
used. A blank twelfth cell means a mis-slice shows *nothing* rather than
showing the wrong art, and nothing is easier to see than wrong. The read-back
asserts `frame < hframes * vframes`, so 11 is in range and 12 is not.
**[proposal]**

**Registration.** The generator draws every cell from one figure definition at
one origin, so drift within cells is impossible by construction rather than
unlikely by inspection. The frame strip still reads it (§9), because "by
construction" is an argument and the strip is the check.

**The five GPT-6 poses in `godot/assets/poses/` stay in the repository and
stay credited in `ATTRIBUTION.md`.** They are no longer loaded. Deleting the
art of a previous assignment to make this one tidier would delete the record
of where this game's look came from. **[decided]**

---

## 4. The cycle spec — `run`

| | |
|---|---|
| Frame count | **6** |
| Frame rate | **12 fps** |
| Length | **0.500 s** |
| `Animation.step` | **1/12 s = 0.0833333** |
| `loop_mode` | **`Animation.LOOP_LINEAR`** |
| Track | one value track, `Sprite2D:frame`, **`Animation.UPDATE_DISCRETE`** |
| Key times | 0, 1/12, 2/12, 3/12, 4/12, 5/12 → values 0, 1, 2, 3, 4, 5 |

**The frame rate is derived, not chosen.** **[decided]**

```
stride_px / SPEED      = 24 / 96   = 0.250 s per stride
one cycle = two strides            = 0.500 s
6 frames / 0.500 s                 = 12 fps exactly
```

`stride_px = 24.0` is set in `game/main.tscn` and `SPEED = 96.0` is
`player.gd:19`. A6's Effect C spawns one dust puff per stride, so **the cycle
and the dust share a clock**: the planted foot and the puff under it are the
same event. If the cycle is retimed, this arithmetic is what has to change
first — not the keys. The human check in §8 reads exactly this.

**The seam rule for a frame track.** Chapter 10 gives the general rule as
"values at time 0 and at `length` should match"; for a **discrete frame
track** that is wrong in the obvious reading, because repeating cell 0 at the
wrap shows cell 0 for two frame periods and the cycle limps. The rule this
clip is held to:

1. **No duplicate across the wrap** — the last key's value is 5, not 0.
2. **The gap from the last key to `length` equals the key interval** —
   0.500 − 5/12 = 1/12. ✔
3. `loop_mode` is `LOOP_LINEAR`.

All three are asserted headlessly. Whether the wrap *reads* as smooth is the
human check in §8. **[decided]**

---

## 5. One authority

**The problem.** `pose_driver.gd` writes `Sprite2D.texture` and
`Sprite2D.flip_h` every `_process`. The `run` clip writes `Sprite2D.frame`.
Two nodes writing one sprite is the failure Assignment 7 names, and whichever
runs last in the frame wins — which depends on node order, which is not a
design.

**The resolution.** **[decided]**

| Animated node | The one authority | What it writes |
|---|---|---|
| `Player/Sprite2D` | **`AnimationPlayer`** | `frame`, and nothing else |
| `Player/SwordArm` | **`AnimationPlayer`** | `rotation_degrees` |
| `Player/SwordArm/Blade` | **`AnimationPlayer`** | `visible` |
| `Player/SwordArm/Hitbox` | **`AnimationPlayer`** | `monitoring` |

- `Sprite2D.texture` is set **once, in the scene file**, to the sheet. Nothing
  writes it at runtime. The five `preload`ed pose textures and the texture
  swap go away with `pose_driver.gd`.
- `pose_driver.gd` is **replaced** by `player_anim.gd`, which **plays clips
  and does not write any animated property**. It calls `play()` on the
  AnimationPlayer and it writes `Sprite2D.flip_h`.
- **`flip_h` is the one honest wrinkle and the brief states it rather than
  hiding it.** No clip keys `flip_h`, so there is still exactly one writer per
  property and exactly one *animation* authority per node — but `Sprite2D` has
  two writers at the node level. The alternative, keying `flip_h` in every
  clip, doubles every clip and makes facing a property of the animation rather
  than of the character. This is a judgement, and §8 records it as one.

**What else in this project could write to these nodes, and does not:**
`room_backdrop.gd`, `room_audio.gd`, `trap_warning_driver.gd`,
`step_dust_driver.gd` and `hit_burst_spawner.gd` all read player state and
write only their own nodes. `capture_rig.gd` freezes a *trap* for A5's capture
and touches no player node. Checked 2026-11-15.

---

## 6. The phase table — `swing`

**In frames at 30 fps.** `Animation.step` = **1/30 s = 0.0333333**, one frame
period, so editor snapping agrees with this table. Length **0.600 s**,
**`loop_mode = Animation.LOOP_NONE`**.

| Phase | Frames | Begins on | Seconds | What the player may do | What the game reads |
|---|---|---|---|---|---|
| **Startup** | 0–5 (6 frames) | **frame 0** | 0.000–0.200 | **Nothing.** No move, no turn, no jump, no second attack. | `action == SWING` → movement locked, read every physics tick |
| **Active** | 6–9 (4 frames) | **frame 6** | 0.200–0.333 | Still nothing. | `Hitbox.monitoring == true`, read by the physics server |
| **Recovery** | 10–17 (8 frames) | **frame 10** | 0.333–0.600 | **Buffer** the next attack; it starts at frame 18. | `action == SWING` still → still locked |
| *(end)* | frame 18 | | 0.600 | Movement returns. | `action` returns to `NONE` |

**[proposal — the numbers. The author adopts or changes them, and a change
goes in §6 and flows down to the keys, never the other way round.]**

**Where the numbers come from.**

- **Active 0.133 s against the trap's `FIRE_SECONDS = 0.18 s`.** The swing's
  lethal window is *narrower* than the trap's, deliberately: you cannot trade
  with a trap, which is what `GDD.md:277` means by rolling on the attack
  rather than on the wind-up.
- **Total 0.600 s against the trap's 1.40 s cycle.** One swing fits inside one
  trap cycle with room to walk out, so attacking near a trap is a real choice
  and not an automatic death.
- **Startup 0.200 s** is half the trap's 0.40 s warning window — long enough to
  be read, short enough not to feel broken.

**Rotation keys** (`SwordArm:rotation_degrees`, linear interpolation).
**The convention: 0° is the blade pointing straight up out of the hand**, and
positive is clockwise, which for a figure facing right is forward. It is
stated because the numbers are meaningless without it — and because an
earlier draft of this table described 20° as "blade down and forward", which
is 160°, not 20°. Corrected 2026-11-16 before any key was written.

| Frame | Time | Degrees | Why |
|---|---|---|---|
| 0 | 0.000 | **20** | rest: blade up, shouldered, tipped slightly forward |
| 6 | 0.200 | **−80** | fully wound back, almost horizontal behind; end of startup |
| 10 | 0.333 | **85** | swept through to horizontal in front; end of active |
| 12 | 0.400 | **75** | the overshoot settles back |
| 18 | 0.600 | **20** | back to rest |

**Every transition is linear (1.0) in r0.** Easing the startup is the obvious
first tuning change and §9 leaves it somewhere to go; shipping r0 already
eased would mean the tuning loop had nothing to measure.

**Discrete tracks:**

| Track | Keys |
|---|---|
| `SwordArm/Hitbox:monitoring` | 0.000 → `false`, **0.200 → `true`**, 0.333 → `false` |
| `SwordArm/Blade:visible` | 0.000 → `true`, 0.600 → `false` |
| `Sprite2D:frame` | 0.000 → `10` (braced), 0.600 → `6` (idle) |

**A `RESET` clip is added** holding the default pose — `rotation_degrees` 20,
`Blade.visible` false, `Hitbox.monitoring` false, `frame` 6. Chapter 10:
`RESET` "holds the 'default pose'". Without it, a scene saved mid-swing keeps
the swing. **[proposal]**

**No method tracks.** Chapter 10: `callback_mode_method` defaults to
**deferred**, so a method key at 0.1 s runs at the end of the frame that
crossed it, *after* that frame's scripts read the old value — the chapter
measured a nominal frame 12 landing on frame 14. The assignment says method
tracks are not a way to make the clocks agree, and this brief does not use
one. The active window is a **discrete value track on `monitoring`**, read by
the physics server on the tick it is written. **[decided]**

---

## 7. The state machine

Owned by **`player.gd`**, because locking movement is gameplay, not
presentation. `player_anim.gd` reads it and never writes it.

| State | Clip | Entered when | Leaves when |
|---|---|---|---|
| `IDLE` | `idle` (frame 6 held) | on floor, `|velocity.x| ≤ 1.0` | any row below |
| `RUN` | `run` (loops) | on floor, `|velocity.x| > 1.0` | stops, leaves the floor, swings or dies |
| `AIRBORNE` | `rising` / `falling` | `not is_on_floor()` | lands |
| `SWING` | `swing` | `attack` just pressed **and** on floor **and** `action == NONE` | the clip reaches frame 18 |
| `DEAD` | `dead` | `health == 0` | never |

**Transitions, and what causes each:**

| From | To | Condition |
|---|---|---|
| IDLE | RUN | `absf(velocity.x) > MOVING_EPS` |
| RUN | IDLE | `absf(velocity.x) ≤ MOVING_EPS` |
| IDLE / RUN | AIRBORNE | `not is_on_floor()` |
| AIRBORNE | IDLE / RUN | `is_on_floor()` |
| IDLE / RUN | SWING | `Input.is_action_just_pressed("attack")` and `is_on_floor()` |
| SWING | IDLE / RUN | `AnimationPlayer.animation_finished` for `swing` |
| any | DEAD | `health == 0` (the existing `died` signal) |

**Interrupts — what each phase does with an input.** These are what §8's edge
tests assert.

| Input, during | Startup | Active | Recovery |
|---|---|---|---|
| `attack` again | **ignored** (`GDD.md:198`) | ignored | **buffered**, plays at frame 18 |
| `move_left` / `move_right` | ignored; no turn | ignored | ignored |
| `jump` | ignored | ignored | ignored |
| taking damage | **does not interrupt** — committed means committed | does not interrupt | does not interrupt |
| `died` | **aborts immediately**, DEAD | aborts | aborts |

**No `AnimationTree`.** One clip plays at a time and nothing blends, so an
`AnimationTree` would add a second mixer with its own defaults
(force-continuous discrete handling, per Chapter 10) for no gain. Because
there is no `AnimationTree`, this brief names no `advance_expression_base_node`
and no `advance_mode`. **[decided]**

---

## 8. The two clocks

| Thing | Its clock | Set where |
|---|---|---|
| `Player/AnimationPlayer` | **`ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`** | set in the scene; **the engine default is idle** (Chapter 10 printed `callback_mode_process=1` from the 4.7.2 binary) |
| `AnimationTree` | none exists | — |
| `AnimatedSprite2D` | **none exists.** Noted because the assignment asks: an `AnimatedSprite2D` advances on the **process tick** and has **no** `callback_mode_process`. Choosing the frame-track route is what avoids that. | — |
| `player.gd` movement and the lock | **physics tick**, 60 Hz | `_physics_process` |
| `Hitbox.monitoring` | written by the clip, read by the physics server | — |

**The fact gameplay reads is `Hitbox.monitoring`, and it is read on the
physics tick.** Setting the AnimationPlayer to physics makes writer and reader
share a tick, so the designed disagreement is **0 s**.

**That is a claim, and A7 asks it to be measured.** The measurement runs the
same clip twice, once at the engine default (idle) and once at physics, and
records the frame on which `monitoring` first reads `true` from
`_physics_process`. **Predicted:** at physics, the physics frame
corresponding to 0.200 s; at idle, up to **one physics step late — 1/60 s ≈
0.0167 s** — and jittering between runs because the render tick is not locked
to the physics tick. The idle figure is the number reported as "the largest
disagreement in seconds". **[proposal — the prediction]**

---

## 9. The evidence split

| Rule | Checked by | How |
|---|---|---|
| Every track resolves to a real node and property | **read-back** | `track_problems()`, branched on track type |
| `run` key times, step, loop mode | **read-back** | compared with tolerance 0.5/12 s, never `==` |
| `run` frame keys are inside the sheet | **read-back** | `value < hframes * vframes` |
| `run` track is `UPDATE_DISCRETE` | **read-back** | only on `TYPE_VALUE` tracks |
| `run` seam: no duplicate at the wrap, last gap = interval | **read-back** | §4's three rules |
| `swing` key times match §6 | **read-back** | one assertion per phase boundary |
| `swing` is `LOOP_NONE`, step = 1/30 | **read-back** | |
| `monitoring` opens at 0.200 and closes at 0.333 | **read-back + edge test** | |
| The state machine plays the right clip in each state | **structure test** | states driven through real input via `Input.parse_input_event` |
| Movement is locked in startup, active and recovery | **edge test** | one frame before, on, and one frame after each boundary |
| A second `attack` is ignored in startup/active, buffered in recovery | **edge test** | |
| Nothing else writes the animated nodes | **pin + review** | the Step 2 pins, plus `grep` for writers |
| The two clocks agree | **measurement** | §8, both modes, reported in seconds |
| **Does the run read as a run?** | **HUMAN** | play at 1280 × 720, run the length of the room |
| **Does the cycle wrap without a seam?** | **HUMAN** | at least five wraps at normal speed |
| **Do the dust puffs land under the planted foot?** | **HUMAN** | §4's arithmetic says they must; the eye says whether they do |
| **Do startup, active and recovery read as distinct?** | **HUMAN** | swing many times in normal play |
| **Does the character drift within its cells?** | **HUMAN** | the cycle's frame strip |
| **Both clips over the darkest and lightest level art** | **HUMAN** | the unlit trap gap at x 208 and the torch pool at x 320 |

No headless run establishes any HUMAN row. That is the point of the split.

---

## 10. The frame strip

**Preview:** `godot/previews/swing_preview.tscn`, background **a real stretch
of this level** — the `room_backdrop.gd` wall, the floor lip, and a trap in
its unlit gap, at in-game camera scale.

**Captured at 30 fps**, which is the phase table's own rate, so one captured
frame is one table frame.

**Trigger on frame 10** of the capture, so there are ten frames of
pre-roll to see the resting pose against.

| Capture frame | Table frame | Time | Should show |
|---|---|---|---|
| 10 | 0 | 0.000 | Rest. Blade down and forward at 20°, hitbox off. |
| 16 | 6 | 0.200 | **Fully wound back, −80°.** The last frame before the hitbox opens. |
| 20 | 10 | 0.333 | **Swept through, 85°.** The last active frame. |
| 22 | 12 | 0.400 | Overshoot settling, 75°. |
| 28 | 18 | 0.600 | Back to rest, blade hidden, movement returned. |
| 40 | — | 1.000 | Unchanged from 28. If anything still moves, the clip is longer than it says. |

**A second strip for the cycle**, the same background, the player running:
capture frames **20, 21, 22, 23, 24, 25** — one full 6-frame cycle at 12 fps
sampled at 30 fps is not one capture frame per cell, so the strip is read for
*registration and drift*, not for cell order. Cell order is the read-back's
job. **[proposal]**

---

## 11. Boundaries

Unchanged by this work: collision layers and shapes **except the new
`Hitbox`**, player movement speed and jump velocity, the trap's state machine
and every one of its timings, every file in `godot/shaders/`, every A6 effect
scene, and every object that is not named here.

**Three changes this brief names, which the boundary otherwise forbids:**

1. **A new input action `attack`.** The input map goes from three actions to
   four, so `test_input_map.gd`'s count assertion **changes from 3 to 4**.
   That is a predicted change, recorded here before it happens.
2. **Movement is locked during the swing.** `player.gd` gains an `action`
   state and consults it in `_physics_process`. Speed, jump velocity, gravity
   and the input bindings are untouched.
3. **A new `Area2D` hitbox** on layer 6 (`PlayerAttack`, already named in
   `project.godot`), masking layer 3 (`Enemy`). **It can hit nothing today** —
   this room has no enemy, and adding one is not this assignment. The brief
   says so rather than letting a reviewer discover it. The window is still a
   real gameplay fact: it is read by the physics server, asserted at every
   phase boundary, and it is what §8 measures the clocks against.

Presentation code may **read** game state. It never writes it. The one place
that rule bends is the clip writing `Hitbox.monitoring`, which Chapter 10
asks for in those words — *"a gameplay fact like 'the hitbox is live' should
not depend on a tween that can be killed halfway"* — and §5 names the
AnimationPlayer as its authority.

---

## 12. Predicted failures

| # | What could go wrong | The check that catches it |
|---|---|---|
| **H1** | The frame track is left on **`UPDATE_CONTINUOUS`**, the Godot default. Between two keys the `frame` property is *interpolated*, so the sprite sweeps through every cell including the blank one, and nothing errors. | The read-back's `value_track_get_update_mode` assertion — called **only on `TYPE_VALUE` tracks**, because on a transform track it errors and answers `UPDATE_CONTINUOUS`. |
| **H2** | The clip is written with Godot 3's **`loop = true`** instead of `loop_mode`. It loads without complaint and the cycle plays once and stops. | The read-back's `loop_mode == Animation.LOOP_LINEAR`. |
| **H3** | A track names `SwordArm:rotation` (Godot 3) or a renamed node. The track is **silently inert**: no error, no motion. | `track_problems()` resolving every path to a real node and a real property. |
| **H4** | The key times are compared with `==` and pass in memory, then fail after a `.tres` round trip, because key times are **32-bit floats**. | Comparing with a tolerance of half a frame period. |
| **H5** | `Animation.step` is left at its default **1/30** while the cycle is authored at 12 fps, so every key snaps somewhere §4 does not name. | The key-time assertion, with a tolerance *narrower* than the snap. |
| **H6** | `play("swing")` is called again while `swing` is already playing. Chapter 10: nothing restarts a clip that is already playing — the second press is **silently swallowed**, which is correct here but would be a bug if the brief had wanted a restart. | The edge test for a second `attack` during each phase. |
| **H7** | The AnimationPlayer is left at the engine default **idle** tick, so the hitbox opens up to one physics step late and jitters between runs. | §8's measurement, run in both modes. |

---

## 13. The brief answers

**Which route does each clip use, and what does that route's read-back see
that the other route's does not?**
`run` is a `Sprite2D` frame track under an `AnimationPlayer`; `swing` is a
keyed 2D cutout under the same player. Both are read back through
`AnimationPlayer`, so the read-back sees **key times, `step`, `loop_mode`,
update mode, and every track's node-and-property path** — and it sees both
clips in one place. An `AnimatedSprite2D` sits outside the AnimationPlayer
entirely: its read-back can only ask a `SpriteFrames` resource for frame
count, speed, loop and autoplay, and it has no key times to pin, no `step`, no
update mode, and no path to resolve.

**If the frame track is left on continuous updates, what does the sprite show
between two keys, and why?**
It shows **interpolated cell numbers** — the `frame` property is an integer
but the track blends toward the next key, so between cell 2 and cell 3 the
sprite is briefly showing whatever `int()` of the interpolated value lands on,
and at the wrap it sweeps backwards through every cell from 5 to 0 instead of
cutting. `UPDATE_DISCRETE` "will update at the keyframes" only, which is the
behaviour a sheet needs.

**What will `Animation.step` be, and what happens if it is left at the
default?**
`run`: **1/12 s**. `swing`: **1/30 s**. The default is 1/30 s. Left at the
default, `run`'s keys at 1/12, 2/12, 4/12 and 5/12 — 0.0833, 0.1667, 0.3333,
0.4167 — do not land on a 1/30 grid, so editor snapping moves them to the
nearest 0.0333 and the cycle is no longer 12 fps. `swing` is authored at 30
fps and would survive the default by luck, which is not a reason to leave it.

**Which node is the one authority over each animated node, and what else could
write to it?**
§5's table: the `AnimationPlayer`, for all four. What else *could* write to
`Sprite2D` is `pose_driver.gd`, which writes `texture` and `flip_h` today —
and which this change deletes. `player_anim.gd` keeps `flip_h` and is named as
the wrinkle rather than hidden.

**Which tick does each clip advance on, and which tick does gameplay read the
active window on? If they differ, what is the largest disagreement?**
Both clips advance on the **physics** tick, because the AnimationPlayer's
`callback_mode_process` is set to physics rather than left at the engine's
idle default. Gameplay reads `Hitbox.monitoring` on the physics tick. So the
disagreement is **0 s by design**, and §8 measures the default to say what was
avoided: up to **one physics step, 1/60 s ≈ 0.0167 s**, varying between runs.

**For the cycle: what is the seam rule for its track type, and what would a
duplicated frame at the wrap look like in play?**
§4's three rules. A duplicated frame would hold cell 0 for **two frame
periods, 1/6 s**, once per 0.5 s cycle — a limp on every second stride, at the
same moment a dust puff spawns, so it would read as the character stumbling
rather than as an animation bug.

**If the rig is imported: where does loop mode have to live?**
It is not imported — the probe on 2026-11-15 found `skins: 0` and no
animations in all three `.glb` files. Recorded because Assignment 5's trap is
the same shape: a setting made in the scene rather than in the importer's
per-animation settings is lost on the next reimport, and the only way to prove
it survived is to delete `godot/.godot` and import again. Mutation 4 in Step 6
runs that deletion anyway, because **`.import` files for the sheet** are
subject to the same loss.

---

## 14. What this brief does not settle

- Whether 6 frames is enough for a run to read. Twelve-frame runs are
  conventional; six is what the stride arithmetic allows at 12 fps, and §4
  says the arithmetic changes first if the eye disagrees.
- The hitbox hits nothing, because this room has no enemy. The active window
  is real, measured and tested; what it would *do* is Assignment 8 or later.
- `roll`, `cast` and combo-2/3 from `GDD.md:393` are not built. One swing is
  one committing action, which is what A7 asks for.
- Whether the code-drawn figure reads as well as the GPT-6 poses it replaces.
  That is a look the author chose on 2026-11-15 to get one sheet, one
  authority and provable registration, and `FRICTIONAL.md` records the
  trade rather than presenting it as a free win.


---

# Revision 7.0.1 — 2026-11-18 — the two clips swap routes, and the art stays the author's

**Supersedes §2's route rows, §3 entirely, §4 entirely, §5's node names, and
§6's rotation-key table. §1, the phase timings in §6, §7, §8, §9, §10, §11
and §12 stand.** No timing changes: the swing is still 18 frames at 30 fps
with the same phase boundaries, and the cycle is still locked to the stride.

## 1. Why

§3 said the sheet would be written by code, in the style of
`tools/make_sprites.py`'s existing 16 × 28 silhouette. It was, and the author
rejected it on sight:

> 这个人物模型也太简陋了，不能做到保持之间咱们用gpt做好的人物形象码
> [this character model is far too crude — can't we keep the character we
> already made with GPT?]

They are right, and the first version is in history at commit `d303899` so the
comparison is checkable rather than asserted. The game already had generated
pixel art for this character — hooded, cyan visor, purple scarf — carried from
`walker-ninja-TiantongZhang` and credited in `ATTRIBUTION.md`. Replacing it
with a silhouette to make this assignment's sheet easier was the wrong trade.

**Three poses had never been carried across.** `walker-ninja` holds eight;
this repository had five. The missing three are `p5-dash`, `p6-windup` and
`p7-live` — and **windup and live are a startup pose and an active pose for an
attack.** The committing action's art already existed. They are copied in;
`walker-ninja` itself is untouched, as `CLAUDE.md` requires.

## 2. The two clips swap routes

Assignment 7: *"The natural split is a looping sprite cycle and a rig action,
but either way round works."* This is the other way round.

| | **`run` — the cycle** | **`swing` — the committing action** |
|---|---|---|
| Route | **2D cutout rig**, plain `Node2D` pivots keyed on rotation and position | **`Sprite2D` + `hframes`/`vframes`, `AnimationPlayer` frame track** |
| Plays on | `Rig/LegFront`, `Rig/LegBack`, `Rig` | `Rig/Body`, `Hitbox` |
| Loops | yes, `LOOP_LINEAR` | no, `LOOP_NONE` |

**Why this way round is the one that keeps the art.** A frame cycle needs
several drawings of a run and the project has one. A cutout rig needs no new
drawing at all: it cuts the legs off the pose that exists and rotates them.
Cutting is not redrawing, and `tools/make_sprites.py` proves it rather than
claiming it — `assert_lossless_cut()` recomposites the three layers and fails
unless they equal `p2-run` **pixel for pixel**.

## 3. The sheet, revised

| | |
|---|---|
| Output | `godot/assets/sprites/player_sheet.png`, **128 × 64** |
| Cell size | 32 × 32 |
| Grid | **`hframes = 4`, `vframes = 2`** |
| Built by | `tools/make_sprites.py`, which **cuts and composes** the committed poses |
| Source art | `godot/assets/poses/p1,p2,p3,p4,p6,p7,p8`, generated with GPT-6 for `walker-ninja-TiantongZhang` in 2026-10 and credited in `ATTRIBUTION.md` |
| Editable source | the poses as committed, plus the generator. Neither is modified by the other. |

| Cell | Clip that shows it | What it is |
|---|---|---|
| 0 | `run` | `p2-run` **with the legs removed** — the only cell the rig uses |
| 1 | `idle`, end of `swing` | `p1-idle` |
| 2 | `rising` | `p3-rising` |
| 3 | `falling` | `p4-falling` |
| 4 | `dead` | `p8-death` |
| 5 | `swing` startup, and its settle | `p6-windup` |
| 6 | `swing` active | `p7-live` |
| 7 | — | **deliberately blank** |

Plus two textures that are not cells: `leg_front.png` and `leg_back.png`, the
planted and trailing legs cut off `p2-run` at row 20 and column 25, each kept
at 32 × 32 so that a `Sprite2D` at the hip lines up with the body with no
arithmetic.

**Registration** is no longer "by construction" — the poses are drawn art, so
it is **measured**: every pose cell's lowest inked row is **29**, asserted in
the generator. The run-torso cell is excluded by name, because its legs were
removed and it therefore ends higher on purpose.

## 4. The cycle spec, revised

| | |
|---|---|
| Length | **0.250 s** |
| `Animation.step` | **1/12 s** |
| `loop_mode` | **`Animation.LOOP_LINEAR`** |
| Tracks | `Rig/LegFront:rotation_degrees`, `Rig/LegBack:rotation_degrees` (both **continuous**), `Rig:position:y`, plus discrete holds for the body cell and the legs' visibility |

**One stride, not two, and the reason is the art.** §4 originally derived six
frames at 12 fps from *two* strides. `p2-run` has one planted foot and one
trailing leg held off the ground; there is no second planted foot to cut out,
so the honest cycle is **one stride**:

```
stride_px / SPEED = 24 / 96 = 0.250 s     <- the cycle's length
```

Effect C spawns one dust puff per stride, so the cycle and the dust still
share a clock and the planted foot and the puff under it are still the same
event. A two-stride cycle would need art this project does not have, and the
film says so rather than implying a full run cycle.

**Keys** (times 0, 1/12, 2/12, 3/12):

| Track | Values |
|---|---|
| `Rig/LegFront:rotation_degrees` | 0, +24, +12, 0 |
| `Rig/LegBack:rotation_degrees` | +22, −2, +10, +22 |
| `Rig:position:y` | 0, −1, −1, 0 |

**The rotation range is measured by rendering, not derived on paper.**
`tools/make_sprites.py` rotates each leg texture at every degree from −34 to
+34 and reports the band in which the foot never falls below row 29:

| Leg | Safe band | Why it is asymmetric |
|---|---|---|
| `leg_front` (planted) | **−2 .. +34** | its foot is already ON the floor at 0°, so one direction drives it through the floor and the other lifts it |
| `leg_back` (trailing) | **−34 .. +34** | it never touches the floor at all |

**The paper version of this had the sign backwards**, and a rendered
measurement caught it: the first preview put the foot two pixels under the
floor while the arithmetic said it was fine. The read-back asserts every key
against the measured band.

**The seam rule is the CONTINUOUS one**, which is the rule Chapter 10 actually
states: on every interpolated track the value at `t = 0` and at `t = length`
must match, or the wrap jumps. Front 0 → 0, back +22 → +22, bob 0 → 0. The
frame-track rule in the original §4 does not apply to this clip and is
superseded.

## 5. One authority, revised node names

| Animated node | The one authority | What it writes |
|---|---|---|
| `Rig` | `AnimationPlayer` | `position:y` |
| `Rig/Body` | `AnimationPlayer` | `frame` |
| `Rig/LegFront`, `Rig/LegBack` | `AnimationPlayer` | `rotation_degrees`, `visible` |
| `Hitbox` | `AnimationPlayer` | `monitoring` |

`Rig/Body.texture` is set once in the scene and never written at runtime.
**§5's `flip_h` wrinkle becomes `Rig.scale.x`.** Flipping only the body
would leave the cut-out legs swinging the wrong way, so facing is written
on the rig root instead. No clip keys it, so there is still one writer per
property; `player_anim.gd` is still the only node that touches it.

## 6. The swing's keys, revised

§6's phase table **stands unchanged** — startup frames 0–5, active 6–9,
recovery 10–17, end at 18, 30 fps, step 1/30, `LOOP_NONE`. What changes is
what the keys drive. There is no sword node and no rotation table:

| Track | Keys |
|---|---|
| `Rig/Body:frame` | 0.000 → **5** (windup), 0.200 → **6** (live), 0.400 → **5**, 0.600 → **1** (idle) |
| `Hitbox:monitoring` | 0.000 → `false`, **0.200 → `true`**, 0.333 → `false` |
| `Rig/LegFront:visible`, `Rig/LegBack:visible` | `false` |
| `Rig:position:y` | 0.0 |

**The `SwordArm` / `Blade` rig of §2.2 is dropped.** It was invented to give
the swing something to move; the character's own art already carries a weapon
in `p6-windup` and `p7-live`, and adding a second one on a pivot would have
drawn two. The `Hitbox` survives as a direct child of the player — still on
layer 6 `PlayerAttack`, still masking layer 3 `Enemy`, still switched by a
discrete track on the clip's own timeline, which is the only part of it that
the assignment cares about.

## 7. What this revision does not change

The deadline arithmetic, the phase timings, the one-authority rule, the two
clocks, the evidence split, the boundaries and the predicted failures. H1
(a frame track left continuous) and H2 (Godot 3's boolean `loop`) now apply
to `swing` rather than to `run`; H3 (an inert track path) applies to the rig.

---

# Revision 7.0.2 — 2026-11-18 — the blade comes back, and then it stops spinning

**Supersedes revision 7.0.1 §6's deletion of the `SwordArm` rig, and the
original §6's rotation-key table and §10's capture-frame rotations.** It
carries two tuning revisions, r1 and r2, both driven by the author playing the
game. Everything else stands: the phase boundaries, the clocks, the authority
table, the evidence split, the boundaries.

## 1. r1 — the premise of 7.0.1 §6 was false

7.0.1 §6 dropped `SwordArm` on this sentence:

> the character's own art already carries a weapon in `p6-windup` and
> `p7-live`, and adding a second one on a pivot would have drawn two.

It does not. `walker-ninja`'s character fights **unarmed**; those two cells
are a raised arm and an extended arm. The author found it in play —
*跑步还行，但挥刀的时候根本看不见刀* — and counting the light-grey pixels
confirmed it afterwards (113 and 98 against idle's 78: a difference of
**stance**, not of weapon). `TUNING.md` holds the measurement.

The rig is restored exactly as the original §2.2 specified: `Rig/SwordArm`, a
`Node2D` pivot at (3, −2) under `Rig` so `Rig.scale.x` mirrors it, carrying
`Blade`, a 3 × 16 `Sprite2D` drawn by `tools/make_sprites.py` in the
character's own two greys. **No pose file is edited.**

## 2. r2 — the restored arc was a windmill, and the numbers said so first

The author played r1:

> 刀不太对，他不是挥出去的，而是在身子上面转圈
>
> [the sword isn't right — it isn't swinging out, it's spinning in circles
> above the body]

**That is literally what the original §6 key table describes**, and nobody had
done the arithmetic. 0° is the blade straight up out of a hand at (3, −2);
the blade is 16 px long on a 32 px figure whose waist is y = 0 and whose feet
are y = +13.

| r1 frame | deg | blade tip | |
|---|---|---|---|
| 0 | +20 | (+8.5, **−17.0**) | **above the top of the sprite** |
| 6 | −80 | (−12.8, −4.8) | horizontal, behind |
| 10 | +85 | (+18.9, −3.4) | horizontal, in front |
| 12 | +75 | (+18.5, −6.1) | |
| 18 | +20 | (+8.5, **−17.0**) | back above the head |

**Two facts, both derivable from that table without opening the game.**

1. **The tip is never below y = −3.** Every one of the 18 frames puts the
   blade in the top half of the frame. "Above the body" is not an impression;
   it is the range of the function.
2. **The arc reverses direction twice** — `+20 → −80` anticlockwise,
   `−80 → +85` clockwise, `+85 → +20` anticlockwise — for a total path of
   **330° in 0.600 s, 550°/s**, all of it watched. Two reversals about an
   overhead pivot is the definition of a windmill, and 转圈 is the right word.

## 3. The two rules r2 ships

> **R1. While the blade is visible the arc travels one way.**
> **R2. It finishes below the hand** — past ±90°, out of the top half.

A swing is a *commitment in one direction*; a thing that goes out and comes
straight back along its own path is a wave, and if the pivot is overhead it is
a propeller. The return to rest still has to happen, so it happens **with the
blade sheathed** — which is also what a character with a sword actually does.

## 4. The revised rotation table

`Rig/SwordArm:rotation_degrees`, continuous, linear. **0° is the blade
straight up out of the hand; positive is clockwise, which for a figure facing
right is forward.** `Rig.scale.x` mirrors the whole arm, so one set of keys is
correct in both facings.

| Frame | Time | Deg | Blade tip, rig coords | What it is |
|---|---|---|---|---|
| 0 | 0.0000 | **−150** | (−5.0, +11.9) | rest: point down, behind the heel. **Hidden.** |
| 2 | 0.0667 | *(−105)* | (−12.5, +2.1) | **drawn** — the blade appears, pointing back |
| 4 | 0.1333 | **−60** | (−10.9, −10.0) | lifting into the cock |
| 6 | 0.2000 | **−50** | (−9.3, −12.3) | fully cocked. Last frame before the hitbox opens |
| 10 | 0.3333 | **+100** | (+18.8, +0.8) | **struck** — forward and low. Last active frame |
| 12 | 0.4000 | **+115** | (+17.5, +4.8) | the overshoot settles lower |
| 13 | 0.4333 | **+118** | (+17.1, +5.5) | last visible frame. **Sheathed** from here |
| 18 | 0.6000 | **−150** | (−5.0, +11.9) | back to rest, travelled unseen |

*(−105 at frame 2 is interpolated, not keyed — it is the angle the blade is at
when it becomes visible.)*

**Visible travel 223°, all clockwise, no reversal. The 268° return is
sheathed.** The strike itself — frame 6 to frame 10, −50° to +100° — is
**150° in 0.133 s, 1127°/s**, five times the speed of the wind-up. The active
window is the fastest thing on the timeline, which is what makes it read as a
strike rather than as a gesture.

`Rig/SwordArm/Blade:visible`, discrete: `0.0000 → false`, **`0.0667 → true`**,
**`0.4333 → false`**. `RESET` and every held clip key it `false`.
The scene's own `SwordArm.rotation` is **−2.6179939 rad = −150°**, so a scene
opened cold shows the resting pose and not a mid-swing one.

**No timing moved.** Startup 0–5, active 6–9, recovery 10–17, end 18, 30 fps,
step 1/30, `LOOP_NONE`. `Hitbox:monitoring` is untouched: `false` / **`true`
at 0.200** / `false` at 0.3333. §6's phase table and §8's clock argument stand
exactly as written — this revision changed where the blade goes, not when
anything happens.

## 5. What this revision adds to §9's evidence split

Both rules in §3 are now **read-back assertions**, and both of them fail r1's
angles when they are pasted back in (9 failures, `TUNING.md` records the run).
That is the uncomfortable part and it is recorded rather than smoothed over:
**the defect the author found by playing was visible in the key table the
whole time, and no test was asking.** The lesson is not "test more"; it is
that a read-back only sees the questions it was written to ask, and the
questions came from someone playing the game.

`test_player_clips.gd`'s blade check also changed **shape**, not just value:
"swing's first key is `true`" would now fail a correct clip, because the blade
starts sheathed. It asserts the invariant instead — every other clip keys it
false throughout, `swing` shows it at some point, `swing` ends hidden.

---

# Revision 7.0.3 — 2026-11-18 — the hand travels, because the pivot was on the character's back

**Supersedes revision 7.0.2 §4's single fixed pivot.** The rotation keys,
the phase boundaries, the clocks, the hitbox keys and the authority rule are
unchanged. What changes is that **`Rig/SwordArm:position` is now keyed**, so
the pivot is part of the animation instead of a constant in the scene.

## 1. Why — the author, twice, before any test

> 刀没挥出去，以刀把为中心在旋转，而且旋转的中心点在人物背部，我觉得应该在前面
>
> [the sword isn't swinging out, it's rotating about the hilt, and the centre
> of rotation is at the character's **back** — I think it should be in front]

**They are right, and `tools/check_sword_reach.py` was written to prove it
from the committed art rather than from an opinion.** It takes a *column
profile* of sheet cell 6 (`p7-live`) — solid pixels per column, with the
scarf's purple ramp excluded — and reports the dense run:

```
  columns with >= 20 solid px run +3 .. +13
  so the torso's BACK edge is x = +3 and its FRONT edge x = +13
```

**The pivot was at x = +3. That is the back edge, to the pixel.**

## 2. The mistake underneath it, which is worth more than the fix

r2's own working note put the pivot "in the middle of the torso", and it was
derived from the cells' **ink bounding box**, which starts at x = −11. But
x = −11 is the **scarf**, streaming out behind a figure that faces right. A
bounding box that includes a trailing scarf has its centre dragged backwards,
so +3 looked central on paper while sitting on the character's spine in play.

That is the same failure as revision 7.0.2 §2 and as r1's: **a true
measurement of the wrong quantity.** The bounding box was computed correctly.
It was not the number the question needed. `check_sword_reach.py` exists so
the next person gets the right quantity by default, and it asserts
`test_swing_clip.gd`'s `TORSO_BACK` and `TORSO_FRONT` against the sheet on
every run — it caught `TORSO_FRONT` wrong (15, the sparse ink edge) the first
time it was run.

## 3. A rotating pivot inside the silhouette cannot read as a swing

This is geometry, not taste. The blade is 16 px; the torso is 10 px wide.
With the hilt fixed anywhere inside the body, **the blade's near end never
moves** and the far end traces a circle centred on the character. That is a
clock hand. Correcting the *direction* of travel (r2) does not change it,
which is exactly why the author's second report sounded like the first.

A real strike moves the hand: back behind the shoulder on the wind-up,
forward past the chest on the blow. So the pivot is **keyed**.

## 4. The position table

`Rig/SwordArm:position`, continuous, linear. Under the same `Rig.scale.x`
that mirrors everything else, so one set of keys is correct in both facings.
Times are the rotation track's own, so the two never disagree.

| Frame | Time | Position | Rotation | Hilt vs the torso (+3 .. +13) |
|---|---|---|---|---|
| 0 | 0.0000 | **(0, +2)** | −150 | sheathed at the hip. Hidden |
| 4 | 0.1333 | **(2, −4)** | −60 | drawing back and up |
| 6 | 0.2000 | **(3, −5)** | −50 | **behind the shoulder** — full cock |
| 10 | 0.3333 | **(13, +1)** | +100 | **out at the front edge** — the blow |
| 12 | 0.4000 | **(12, +3)** | +115 | the overshoot drops |
| 13 | 0.4333 | (12, +3) | +118 | sheathed |
| 18 | 0.6000 | **(0, +2)** | −150 | back to the hip, unseen |

| Measured across the active window (frames 6 → 10, 0.133 s) | |
|---|---|
| the **hilt** travels forward | **10 px** |
| the **tip** travels horizontally | **38 px**, across a **10 px** figure |
| the tip finishes at x | **+28.8**, clear of the front edge at +13 |

The scene's own `SwordArm.position` becomes **(0, 2)** and `RESET` holds it,
so a scene opened cold has the sword at the hip rather than mid-swing.

## 5. Three read-back rules now, not two

7.0.2 §3's two rules stand. r3 adds the one the author's second report names:

> **R3. The hilt is behind the torso's back edge at full cock, out in front
> of it on the last active frame, and travels at least 8 px between them.**

And two consequences of it, asserted from the keys rather than described:
the tip's horizontal sweep across the active window must exceed the figure's
own width, and the tip must finish **outside** the front edge. All of it is
computed from `position` and `rotation_degrees` together — neither track
alone can answer it, which is the clearest thing in this assignment about
what a rig clip is for.

**`swing` now has eight tracks**, `RESET` ten.

---

# Revision 7.0.4 — 2026-11-18 — the blade is 20 px, and the length now lives in one place

**Supersedes revision 7.0.3 §4's tip-reach numbers and revision 7.0.2 §1's
"3 × 16".** One number changed. No key, no timing, no phase boundary and no
rule moved.

## 1. Why

The author played r3 and asked for a longer blade. That is the whole reason
and it does not need a measurement behind it: how long a sword should look is
a judgement, and §9 puts judgements about how a thing reads with the author.

## 2. What changed

| | r3 | r4 |
|---|---|---|
| `sword.png` | 3 × 16 | **3 × 20** |
| of which cutting edge | 11 px | **15 px** |
| `Blade.offset` | (0, −8) | **(0, −10)** |

`offset` is **−LEN / 2** so that the hilt lands exactly on the pivot. It is
not a free parameter: get it wrong and the blade pivots about its own middle,
which is the clock-hand failure of r1 and r2 arriving by a different door.

## 3. What it does to r3's geometry

| Across the active window (frames 6 → 10) | r3 (16 px) | r4 (20 px) |
|---|---|---|
| the hilt travels forward | 10 px | **10 px** (unchanged — it is the pivot) |
| the tip travels horizontally | 38 px | **45 px**, across a 10 px figure |
| the tip finishes at x | +28.8 | **+32.7**, clear of the front edge at +13 |

All three of revision 7.0.3 §5's rules still pass, and they pass by a wider
margin than before, because a longer blade reaches further from the same
pivot. That is worth stating plainly: **r4 cannot have fixed r3's defect and
was not asked to.** It made a correct swing bigger.

## 4. The length now has one home, and two checks

Before this revision the number 16 was written in three places that nothing
compared: the generator, the sprite's `offset` in the scene, and
`BLADE_PX` in `test_swing_clip.gd`, which the tip-reach assertions are
computed from. Three copies of one number is this project's recurring fault —
the same shape as `test_input_map.gd`'s hard-coded count and the strip tool's
fixed sentence.

`tools/make_sprites.py`'s **`SWORD_LEN`** is the source now, and
`tools/check_sword_reach.py` asserts, on every run:

- the generated PNG is `SWORD_LEN` tall;
- `player.tscn`'s `Blade.offset.y` is exactly `−SWORD_LEN / 2`;
- `test_swing_clip.gd`'s `BLADE_PX` equals `SWORD_LEN`.

## 5. Not changed, and checked rather than assumed: the jump binding

The author asked in the same breath for jump to be on the spacebar. **It
already was** — `project.godot`'s `jump` action carries physical SPACE, W and
UP, and has since before this assignment. `CLAUDE.md` and §11 both put the
existing input bindings out of scope, and nothing needed to move.

But "it already is" was a claim about a file, and `test_input_map.gd` only
ever asserted that the **action exists**. An action can exist with the wrong
key on it, or with no key at all, and every check in that test would still be
green. So the keys are pressed now, through `Input.parse_input_event`, and
released again: six new checks, 7 → **13**.

**Where jump genuinely does nothing is §7's interrupt table, by design.**
`player.gd:71` returns from `_physics_process` while `is_locked()`, before
the jump branch at `:83`, so for the 0.600 s of a swing no jump is read. That
is *"the combo is committed"* in code and `test_swing_edges.gd` asserts it.
If the spacebar felt dead, this is the likeliest reason, and it is the
feature rather than a fault.

---

# Revision 7.0.5 — 2026-11-18 — the swing works in the air

**Supersedes §7's `SWING` entry condition and its transition row.** One
condition is deleted. No clip, no key, no timing, no phase boundary, no
authority and no hitbox behaviour changes.

## 1. Why

> 让角色在空中也能挥刀
>
> [let the character swing in the air too]

§7 required `is_on_floor()` to enter `SWING`, which came from the GDD's
ground combat and was never argued for in this brief. The author wants an
air attack. That is a design call and it is theirs.

## 2. What changes, in one line of code each

| | before | after |
|---|---|---|
| entering `SWING` | `attack` pressed **and `is_on_floor()`** and `action == NONE` | `attack` pressed and `health > 0` and `action == NONE` |
| the buffered second swing | restarts only if `is_on_floor()` | restarts regardless |
| `_start_swing()` | `velocity.x = 0.0` | `velocity.x = 0.0` **only on the floor** |
| the lock, every tick | `velocity.x = 0.0` | `velocity.x = 0.0` **only on the floor** |

**`player_anim.gd` does not change at all.** `_clip_for_state()` already
tests `is_locked()` *above* the airborne branch, so `swing` outranks
`rising`/`falling` the moment an air swing starts. That ordering was written
for the ground case and happens to be right for this one; the test now says
so out loud rather than leaving it to luck.

## 3. The rule the two `is_on_floor()` guards encode

> **A commitment locks out INPUT, not physics.**

On the ground the swing **plants**: `velocity.x` is held at 0 every tick, so
you cannot slide into or out of your own attack. In the air there is nothing
to plant against — zeroing `x` would stop the jump arc dead and drop the
character straight down, which is a different game's air attack. So the
horizontal velocity the jump already had is **carried**, and no key changes
it. Gravity runs exactly as before.

The guard is re-tested **every tick, not remembered at the start**, so
landing mid-swing plants on the frame the floor is found.

## 4. What stays locked

Everything §7's interrupt table already said, now true in the air as well:
no turn, no steering, **no jump**, a second attack ignored in startup and
active and buffered in recovery, damage does not interrupt, death aborts.
The clip is still `LOOP_NONE`, still 0.600 s, and `Hitbox:monitoring` still
opens at 0.200 and closes at 0.3333 — the window is on the clip's timeline
and knows nothing about the floor.

## 5. The part worth recording

**The `is_on_floor()` gate was never asserted by any test.** Nine interrupt
cases, a frame-by-frame trace of the whole window, a state-machine structure
test, a pin — and not one of them pressed `attack` in the air. The gate
could have been deleted by accident at any point in Assignment 7 and every
suite would have stayed green.

So this revision's own rule is asserted on both sides, in
`test_swing_edges.gd`: the swing starts in the air, the lock is on, `swing`
beats `rising`/`falling`, the horizontal velocity is carried, **holding the
opposite direction does not turn it around**, gravity still runs, jump is
still refused, the clip still ends on its own — and a ground swing still
plants at exactly 0. Eleven new checks, 23 → **34**.

One of them exists only to keep another honest: *"it was moving, so
'carried' is not trivially true"*. A test that the velocity is unchanged
passes beautifully when the velocity is zero.

---

# Revision 7.0.6 — 2026-11-19 — a swing no longer locks movement, and what "committing" still means

**Supersedes §7's interrupt row for `move_left` / `move_right`, §2.2's
"what it communicates", revision 7.0.5 §3 entirely, and §11's boundary 2.**
It also changes two existing tests' expectations, which `CLAUDE.md` puts out
of scope — named here, before the fact, as boundary crossings the author
authorised.

## 1. Why

> 人挥刀的时候也要可以移动
>
> [the character should be able to move while swinging too]

## 2. The objection, stated before the change rather than after

This is the one revision in Assignment 7 that touches the assignment's own
vocabulary. A7 asks for **one looping cycle and one committing action**, and
§0 of this brief grounded "committing" in the game's own GDD:

> `GDD.md:198` — *"The combo is committed: once a swing starts it finishes,
> so holding attack is a real risk and letting go is a real choice."*

**The movement lock was that risk.** Removing it removes the cost of
attacking, and §2.2's claim that the swing "communicates that the attack is
a commitment" is weaker for it. The author was told this and asked for the
change anyway, which is their call to make; it is recorded here so a
reviewer weighs the same trade rather than discovering it.

## 3. What makes it still a committing action

A movement lock is **one way** to make a commitment read. It is not what
makes a clip a committing action. All of this is unchanged:

| | |
|---|---|
| **cannot be cancelled** | no input sets `action` back to `NONE`. Only `animation_finished` and death |
| **cannot be restarted** | a second attack is ignored in startup and active, buffered in recovery — the phase read from the clip's own playhead |
| **always 18 frames** | `LOOP_NONE`, 0.600 s, every time |
| **no jump** | still gated by `is_locked()` |
| **damage does not interrupt** | unchanged |
| **no TURN** | `player_anim.gd` freezes `Rig.scale.x` while locked |

**The last row is the commitment that survives, and it is the right one.**
`Rig.scale.x` mirrors the entire sword arm, so a turn mid-arc would teleport
the blade from one side of the body to the other in a single frame. You may
now walk backwards out of your own swing; you may not change which way the
blade is going. Direction is what the arc depends on, so direction is what
the swing commits you to.

## 4. The cost, which is visual and is the author's to judge

`swing` hides the cut-out legs (`Rig/LegFront:visible` and
`Rig/LegBack:visible` are keyed `false`) and holds one static body cell. So
**a moving swing slides**: the character travels with no leg motion under
them. Effect C still spawns a dust puff every 24 px, because it is driven by
distance travelled — so there will be dust under a figure whose legs are not
moving, which is the exact complaint revision 7.0.1 §2 built the leg rig to
answer, arriving from the other direction.

Showing the legs during a moving swing would mean two clips at once, which
means an `AnimationTree`, which §7 declined with reasons that still hold.
**Not done, and named rather than left to be found.**

## 5. What the code became

The lock block no longer touches `velocity` at all — the movement block runs
on every tick whether or not a swing owns the player, and `_start_swing()`
no longer plants. Revision 7.0.5's ground-plant / air-carry split is gone
with it: there is nothing to plant or carry once the axis is read either
way.

## 6. Two existing tests changed their expectations, and both were inverted rather than deleted

`CLAUDE.md` forbids changing an existing test's expectations except
`test_input_map.gd`'s count. Two were changed:

- `test_player_states.gd`: *"holding right during the swing moves the player
  0 px"* → *"…DOES move the player now"*, plus a new check that it is still
  playing `swing` and not `run`.
- `test_swing_edges.gd` §A: *"the player moves 0 px for the whole lock"* →
  *"with no direction held, the swing moves the player 0 px"*. Section A
  holds no direction key, so the number is the same and the **claim** is
  different: it is now about drift, not about a lock.

Both were **inverted, not removed**, so the file still states the rule. A
test left asserting a superseded rule is the loudest available way to find
out the design moved; a test deleted for failing is the quietest.

`test_swing_edges.gd` gains section **D**, which asserts the new rule and
everything §3 says survives: full `SPEED` on the swing's first frame, 51.2 px
travelled across the lock, the facing unflipped through a mid-swing reversal,
and the clip still running to its own end rather than to a key release.
23 → 34 → **37** checks.

**One of those checks failed first, and the test was wrong, not the game.**
The facing was sampled after `await process_frame` without re-testing the
lock, so on the loop's final turn the swing had already ended and
`player_anim.gd` had correctly flipped the facing on that same physics tick.
A flip one frame *after* a commitment ends is the commitment ending.
