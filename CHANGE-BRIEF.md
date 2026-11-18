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
