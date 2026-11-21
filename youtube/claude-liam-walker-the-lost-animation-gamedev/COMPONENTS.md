# COMPONENTS.md — what this film explains, and what it leaves out

Six components, 72 inventoried source files, 64 explicit exclusions. The
machine-checkable half of this is `gamedev-evidence.json`, written by
`scripts/build_animation_ledger.py` and verified by
`./art godot-gamedev --check`. That check decides whether every file is
accounted for and whether every excerpt matches its source. **It cannot decide
whether a mechanism was explained clearly or whether an exclusion is honest.**
That is what this file is for, and it is mine to defend.

Game-source revision `b33b06c`.

**64 exclusions against Assignment 6's 40.** The repository is cumulative —
three assignments of particle effects, shaders and 3D assets sit under
`godot/` and none of them is animation — so each film's honest scope is a
smaller slice of a larger project. A reviewer should read the exclusion list
as the more interesting half.

---

## 1. `the-sheet` — beats B02, B04

Twenty-two files: the sheet, the two leg textures, the blade, and the seven
pose PNGs they are all cut from, each with its `.import` sidecar.

**Where it lives and what data enters.** Nothing enters it at runtime.
`godot/assets/sprites/player_sheet.png` is a 128 × 64 grid of eight 32 × 32
cells, set once on `Rig/Body.texture` in the scene file and never written
again. The two leg `Sprite2D`s take `leg_front.png` — **both of them**, half a
cycle apart, with the back one darkened by `modulate`.

**The important fact.** The sheet is **cut**, not drawn.
`tools/make_sprites.py` loads the committed pose PNGs, slices three of them at
row 20, and `assert_lossless_cut()` recomposites torso plus legs and **exits
unless the result equals the source pixel for pixel**. So "the cut is lossless"
is proved on every run rather than claimed once. **No pose file is ever
edited.** The GPT-6 art generated for `walker-ninja-TiantongZhang` in 2026-10
is unchanged on disk and credited in `ATTRIBUTION.md`.

**Why that matters more than it sounds.** The first version of this
assignment's sheet was drawn by code, as a silhouette, and the author rejected
it on sight — *这个人物模型也太简陋了*. The rejected version is still in
history at `d303899`. Cutting a rig out of existing art rather than drawing
new art is what let this project keep its character, and it is the reason the
two clips take the opposite routes from the obvious ones.

**What the film does not show about it.** The generator's palette, its two
named prediction pixels, and the rotation-band scan are named but not shown
line by line. `tools/check_sword_reach.py` and `CHANGE-BRIEF.md` revision
7.0.1 hold them.

---

## 2. `clip-run-the-cycle` — beats B02, B03

Four files: the leg animation library, the preview fixture it is captured
from, and the 82-check read-back.

**Where it lives and what data enters.** `godot/animations/legs.tres` is an
`AnimationLibrary` with four clips, owned by a `LegAnim` `AnimationPlayer`.
Nothing enters it but a clip name: `player_anim.gd` reads the player's state
and calls `play()`.

**The important lines.** `legs.tres:24-26` — length `0.5`, `loop_mode = 1`,
`step = 0.125`. All three are derived rather than chosen. Two strides at
`stride_px = 24` against `SPEED = 96` is 0.500 s; a quarter cycle is the step
because a gait has four landmarks.

**What changes, and what the player sees.** Two legs alternating, 52° apart at
the contacts, with a one-pixel bob per footfall. Before this clip the body
above the step dust was one frozen pose, so the dust looked like it belonged
to something else.

**Why this design, and the trade-off.** A frame-by-frame run cycle needs
several drawings of a run and this project has one. A cutout rig needs no new
drawing at all. **The cost is stated in the film and measured in the brief:
this cycle alternates but it does not stride.** The cut leg is 8.6 px long
with its foot almost directly under the hip, so across 88° of rotation the
foot moves about 10 px against a 24 px step. Drawing a longer leg is the only
fix and it changes the character's art — which is the thing revision 7.0.1
exists because the author refused.

**What the film does not show about it.** The seam rule's three checks, the
measured safe bands, and the hip joints the generator measures. The read-back
asserts all of them and `CHANGE-BRIEF.md` revision 7.0.7 holds the numbers.

---

## 3. `clip-swing-the-committing-action` — beats B04, B05, B12, B13

Seven files: the body animation library, three preview fixtures, and the two
suites that read the clip back and drive it through its phase boundaries.

**Where it lives and what data enters.** `godot/animations/player.tres` holds
seven clips. `swing` has six tracks: the body's frame, the hitbox's
`monitoring`, the rig's bob, and the sword arm's **position and rotation
together**, plus the blade's visibility.

**The important lines.** `player.tres:110-121`, the `Hitbox:monitoring` track.
It is `update = 1` — discrete — and its keys are `false` at 0, `true` at
0.200, `false` at 0.3333. A gameplay fact, on the clip's own timeline, which
is the one place this assignment asks presentation to carry something the game
reads.

**Why position AND rotation.** This is the part the author found by playing,
twice. A blade rotating about a hilt fixed anywhere inside a 10 px torso has a
near end that never moves and a far end that traces a circle — a clock hand.
Correcting the *direction* of travel does not change that, which is why the
second report sounded like the first. The pivot is keyed, so the hand travels
10 px forward across the active window and the tip travels 45 px across a
10 px figure.

**What the film does not show about it.** The three rules the author's reports
produced — the arc travels one way while the blade is visible, it finishes
below the hand, the hilt crosses the torso — are stated but their assertions
are not shown. `test_swing_clip.gd` computes all three from `position` and
`rotation_degrees` **together**, which neither track alone can answer, and
that is the clearest thing in this assignment about what a rig clip is for.

---

## 4. `one-authority` — beats B06, B07, B10, B11

Five files: the state machine, the scene, the clip driver, and two suites.

**Where it lives and what data enters.** `player.gd` owns an `action` enum and
a `swing_count`, because locking an action is gameplay. `player_anim.gd` reads
`velocity`, `is_on_floor()`, `health` and `action`, picks a clip for each of
the two players, and **writes no animated property at all**.

**The important lines.** `test_player_clips.gd:217-230`, the partition
asserted in both directions.

**Why a second AnimationPlayer is not a second authority.** The rule is
*exactly one node writes to each animated node*. Two players whose track paths
do not intersect satisfy it exactly. The film spends a beat on this because
**a sentence in this repository's own design document said otherwise** — that
showing the legs during a moving swing would require an `AnimationTree` — and
that sentence was accepted as a cost for a day before anyone checked it.

**The one honest wrinkle, stated rather than hidden.** `player_anim.gd` writes
`Rig.scale.x`, the facing. No clip keys it, so there is still exactly one
writer per property — but `Rig` has two writers at the node level. The
alternative, keying the facing in every clip, doubles every clip and makes
facing a property of the animation rather than of the character.
`CHANGE-BRIEF.md` §5 and revision 7.0.1 §5 both name it as a judgement.

**What the film does not show about it.** The five states and their
transitions, the attack buffer, and the pin that proves the states this
assignment did not touch did not move.

---

## 5. `two-clocks` — beats B08, B09

Two files: the measurement, and `project.godot`.

**Where it lives and what data enters.** `measure_clocks.gd` loads the main
scene twice, sets the `AnimationPlayer`'s `callback_mode_process` to physics
and then to idle, presses the real attack key both times, and records the
physics frame on which `Hitbox.monitoring` first reads `true` from
`_physics_process` — together with the clip's playhead on that frame.

**Why `project.godot` is here.** Because the physics tick is **60 by being
unset**. There is no `[physics]` section; the value is the engine default. A
tick that is a default is still the tick every frame count in this film is
stated at, and a reviewer who greps for `physics_ticks_per_second` and finds
nothing deserves to be told why.

**What it found.** The brief predicted that idle mode would open the window up
to one physics step **late** and jitter. It is one step **early**, and the
cause is where the mixer's advance falls inside the frame, not read latency.
The brief's prediction was tagged `[proposal]`, which in this project means
*derived by Claude and not yet confirmed* — and the tag is why a measurement
was built to test it instead of a sentence being believed.

**What the film does not show, and says so.** The run **cannot** see the
jitter half of the prediction. `scripts/run-test.sh` passes `--fixed-fps`,
which locks the render tick to the physics tick on purpose, so every run of
the file is identical. Running a deterministic measurement three times is one
measurement printed three times, and `measure_clocks.gd` prints that sentence
in its own output rather than letting a reader assume otherwise.

---

## 6. `the-room-and-the-harness` — beats B03, B05, B11

Thirty-two files: the room, the traps, Assignment 6's step dust, the room's
art and audio, the capture driver and the input-map check.

**Why the step dust is a component here and not an exclusion.** This is the
judgement call in this ledger and it deserves the space. The dust was built
for Assignment 6 and nothing about it changed. But **the run cycle's length is
derived from the dust's stride** — `2 × stride_px / SPEED` — so the two share
a clock by construction, and the footfall and the puff under it are the same
event. It is also the only way a viewer can *see* that the cycle and the game
agree, because the agreement is arithmetic everywhere else. Excluding it would
make the film's own B03 narration unsupported by its own ledger.
`test_step_dust_state.gd` comes with it, because this assignment re-ran it at
30, 60 and 144 to show the agreement survives the frame rate. Its **config**
suite does not: those settings were not touched and are not explained.

**Why the trap is here.** The swing's active window is sized against the
trap's own `FIRE_SECONDS`: 0.133 s against 0.18 s, deliberately narrower, so
you cannot trade with a trap. A film that quoted that comparison while
excluding the trap would be citing a file it had declared out of scope.

**Why the capture driver is here.** A render is evidence only if it printed
`CAPTURE OK`. Each take asserts its own outcome — wraps, facings, puff count,
swing lengths, travelling-swing frames, jumped swings — and exits nonzero
otherwise, so a completed render is not by itself the claim.

**What the film does not show about it.** The room's backdrop shader, its
audio, and the trap's five-state machine. All three are previous assignments'
subjects and all three are excluded from *those* parts of the ledger by name.

---

## The exclusions, grouped

**Assignment 6, particle work (19 files).** Two of the three effects have
nothing to do with an animation clip. The third is claimed, above, with its
reason.

**Assignment 5, shaders and materials (15 files).** Untouched by this
assignment, and `git diff --stat godot/shaders/` prints nothing after every
agent commit. `trap_warning.gdshader` is excluded even though the trap it
draws for is a component, because the shader is hand-written by the author and
an agent does not edit it.

**Assignment 3, 3D assets (9 files).** The glTF probe on 2026-11-15 found
`skins: 0` and no animations in all three `.glb` files. **That is why this
assignment's rig is cut out of 2D art** — there was no imported rig in this
project to key, and building one is a different assignment. The exclusion
reason says so, because "excluded, irrelevant" would hide the fact that the
3D files are the reason the 2D route was taken.

**Carried across and superseded (4 files).** `route_driver.gd` and
`test_keyboard.gd` came from `walker-ninja-TiantongZhang`.
**`test_keyboard.gd` does not even load** — it preloads
`res://game/session.gd`, a file that has never existed in this repository, so
it has been broken since 2026-10-17. It is recorded in `TEST-REPORT.md` and
excluded here rather than quietly deleted, because deleting a broken carried
file removes the evidence that it was carried.

**Art nothing loads (2 files).** `p5-dash.png` was copied across in revision
7.0.1 with `p6-windup` and `p7-live` because all three were missing. Only two
of the three are cut into the sheet. It stays committed and credited, and the
exclusion says plainly that nothing loads it rather than leaving a reviewer to
find that by grepping.

**`.gitkeep` placeholders (6 files)** and `MATERIALS.md`, a document that
lives inside the project directory because an earlier assignment named that
path.
