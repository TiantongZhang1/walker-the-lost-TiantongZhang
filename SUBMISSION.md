# SUBMISSION.md

**Assignment:** Assignment 7 - Doing Animation with Claude and Godot

**Student:** Tiantong Zhang · zhang.tiant@northeastern.edu · GitHub `TiantongZhang1`

**Project name:** The Lost

**GitHub repository URL:**
<https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang>

**Git tag and submitted commit SHA:** tag **`a7`**. A commit cannot carry its
own SHA; it is in the Canvas note and recoverable with
`git rev-list -n 1 a7`.

**Game-source revision shown in the film:** **`b33b06c`**. Every code panel,
every hash and every capture in the film is taken at it, and
**`git diff b33b06c..a7 -- godot/` prints nothing** — commits after it add
film documentation and film scripts only.

**Godot version, renderer, and operating system:** Godot
**4.7.2.stable.official** `ed1daf0bf`, **Forward+** (Vulkan 1.4.357),
Windows 11. Physics tick **60** — `physics_ticks_per_second` is unset, so the
engine default, and every frame count below is stated at that rate.

**Sprite clip: route, node, scene, frame rate:**
`swing` — **`Sprite2D` with an `AnimationPlayer` frame track**, the preferred
sprite route. Node `Rig/Body` in `godot/features/player/player.tscn`,
**30 fps**, `Animation.step` = 1/30, 18 frames, `LOOP_NONE`.
The sheet is `godot/assets/sprites/player_sheet.png`, 32 × 32 cells,
`hframes = 4`, `vframes = 2`.

**Rig clip: route, rig source, node, scene, frame rate:**
`legs_run` — **2D cutout rig keyed as resource text**. Plain `Node2D`
pivots, no `Bone2D`: `Rig/LegFront` and `Rig/LegBack` in the same scene,
keyed on `rotation_degrees`, plus `Rig:position:y`. **8 fps** — four keys
per 0.500 s — `Animation.step` = 0.125, `LOOP_LINEAR`.
The rig source is the committed GPT-6 pose `p2-run`, **cut** into a torso and
two legs by `tools/make_sprites.py`, which asserts the cut is lossless.

> **The imported-3D route was checked and rejected on evidence.** A glTF JSON
> probe on 2026-11-15 found **`skins: 0` and no animations** in all three
> `.glb` files in `godot/assets/models/`. There is no imported rig in this
> project to key, and the brief records the probe rather than the preference.

**Which clip loops and which commits:**
**`legs_run` loops** — `LOOP_LINEAR`, and the seam rule that applies to it is
the **continuous** one: every interpolated track's value at `t = 0` equals
its value at `t = length` (front 38 → 38, back −14 → −14, bob 0 → 0).
**`swing` commits** — `LOOP_NONE`, 18 frames at 30 fps, with the phase table
in `CHANGE-BRIEF.md` §6: startup 0–5, active 6–9, recovery 10–17, end at 18.

> **This is the opposite way round from the obvious split, and the reason is
> art rather than animation.** A frame cycle needs several drawings of a run
> and this project has one; a cutout rig needs no new drawing at all, because
> it cuts the legs off the pose that exists. The assignment allows either way
> round and `CHANGE-BRIEF.md` revision 7.0.1 argues this one.

**The one authority over each animated node:**

| Animated node | Its one authority | What it writes |
|---|---|---|
| `Rig`, `Rig/Body`, `Rig/SwordArm`, `…/Blade`, `Hitbox` | `Player/AnimationPlayer` | `position:y`, `frame`, `position`, `rotation_degrees`, `visible`, `monitoring` |
| `Rig/LegFront`, `Rig/LegBack` | `Player/LegAnim` | `rotation_degrees`, `visible` |

**Two `AnimationPlayer`s, and that is still one authority per node.** The
rule is *one authority per animated NODE*, not one player per scene — so a
second player over a **disjoint** set of nodes satisfies it exactly.
`test_player_clips.gd` asserts the partition **in both directions**: no node
is on both lists, every `LegAnim` path begins `Rig/Leg`, and **no**
`AnimationPlayer` path does. The third assertion is not redundant: *a
partition checked one way round is only a subset*, and putting one leg track
back on the body player fails two of the three.

`Rig/Body.texture` is set once in the scene and never written at runtime.
`player_anim.gd` plays both players and writes **no animated property**; the
one thing it writes is `Rig.scale.x`, the facing, which **no clip keys** —
`CHANGE-BRIEF.md` §5 states that wrinkle rather than hiding it. Both players
and `player_anim.gd` are on the **physics** tick.

**Sprite sheet source and licence (or model, version, and terms):**
**Written by code, in this repository.** `tools/make_sprites.py` cuts and
composes `godot/assets/sprites/player_sheet.png` from seven pose PNGs in
`godot/assets/poses/`, generated with **GPT-6** for
`walker-ninja-TiantongZhang` in 2026-10 and credited in `ATTRIBUTION.md`.
Licence: **mine**; no downloaded sheet, no asset library, no 3D generator.
**The editable source is the generator plus the poses as committed**, and
neither is modified by the other — `assert_lossless_cut()` recomposites every
cut and exits unless it equals the source pixel for pixel. No pose file is
ever edited. The blade `sword.png` is drawn by the same generator in two
greys that are already in every pose.

**Final film URL and filename:** `TheLostAnimation_TiantongZhang.mp4`
(`youtube/claude-liam-walker-the-lost-animation-gamedev/exports/landscape/claude-liam-walker-the-lost-animation-gamedev.mp4`),
`godot-gamedev` with the `walker` modifier, 3840 × 2160, 30 fps,
**9:30.57** (570.567 s), 34.3 MB, 18 beats, **six code → result pairs**.
URL: _PENDING — the upload is mine; the hash below is what the uploaded file
must match._

**Final film SHA-256:**

```
6eb488d454fc98899c4ed77445250247c80bd2b5883810db88469c39e8e5646f
```

**Summary of my work:** `CHANGE-BRIEF.md`'s original brief plus revisions
7.0.1 – 7.0.10. In order: the two clips swapped routes so the character's
existing art could be kept; the blade came back; it stopped spinning; the
pivot became part of the animation instead of a constant in the scene; the
blade got longer; the swing worked in the air; it stopped locking movement;
the run cycle was rebuilt on three measurements that were wrong; the clock
prediction was measured and found **wrong in sign**; the legs got their own
authority; and the jump left the lock.

**Nine of those ten revisions began with me playing the game and saying
something was wrong.** None began with a test that had been passing and
started failing. The tenth came from a measurement written to test a
prediction the brief had tagged `[proposal]`.

**Known limitations:**

- **The hitbox can hit nothing.** This room has no enemy. The window is real,
  measured and tested at both tick settings; what it would *do* is a later
  assignment. `CHANGE-BRIEF.md` §11.3 said so before it was built.
- **The run cycle alternates but does not stride.** The cut leg moves its
  foot about 10 px against a 24 px step. The only fix is drawing a longer
  leg, which changes the character's art — the thing revision 7.0.1 exists
  because I rejected.
- **The jitter half of §8's clock prediction is not established.**
  `--fixed-fps` locks the render tick to the physics tick, so every run of
  the measurement is identical. Running a deterministic measurement three
  times is one measurement printed three times, and the file says so in its
  own output.
- **Three HUMAN rows in `CHANGE-BRIEF.md` §9 are still open** and listed as
  open rather than covered by a general verdict: both clips over the darkest
  and lightest level art; whether a moving swing reads after revision 7.0.9
  changed the answer; and whether a braced stance hanging in mid-air reads.
- **The film's own fact-check is written by the party that wrote its
  narration**, and `FACTCHECK.md` says so in its closing section.

**Changed games since Assignment 2 (yes/no; if yes, FRICTIONAL.md entry):**
**No.** The game chosen in Assignment 2 is the one built here. The repository
lineage is `walker-jumpman` → `walker-ninja` → `walker-the-lost`, and
`FRICTIONAL.md` records it; the change of repository happened before
Assignment 4, which the course allows.

---

## The two clips

Assignment 7 says *"the natural split is a looping sprite cycle and a rig
action, but either way round works."* **This is the other way round**, and
the reason is art rather than animation — §3 below.

### `run` — the cycle, a 2D cutout rig

| | |
|---|---|
| What it communicates | that the character moves under their own power rather than sliding. The game already kicks up step dust every 24 px; until this clip existed the body above those puffs was one frozen pose, so the dust looked like it belonged to something else |
| Route | `Node2D` pivots keyed on `rotation_degrees` and `position`, as **resource text**, never built in code at runtime |
| Plays on | `Rig`, `Rig/LegFront`, `Rig/LegBack` |
| Length | **0.500 s**, `LOOP_LINEAR`, `step` 0.125 s |
| Keys | five — contact, pass, contact, pass, contact |

**The length is derived, not chosen.** A gait cycle is two steps, so it is
two strides: `2 × stride_px / SPEED = 48 / 96 = 0.500 s`. The two contacts
fall 0.250 s apart, which at 96 px/s is **24 px — `stride_px` exactly**, so
the step dust spawns on each footfall rather than on every other one. If the
cycle is retimed, that arithmetic is what changes first, not the keys.

**The seam rule for a continuous track** is the one the course notes state:
the value at `t = 0` and at `t = length` must match or the wrap jumps. Front
38 → 38, back −14 → −14, bob 0 → 0, asserted headlessly. Whether the wrap
*reads* smooth is a human check and it is mine.

### `swing` — the committing action, a sprite-sheet frame track

| | |
|---|---|
| What it communicates | that the attack is a commitment. The startup is long enough to be read; the active window is narrower than a spike trap's lethal window, so you cannot trade with a trap; the recovery is where you find out whether committing was right |
| Route | `Sprite2D` with `hframes`/`vframes` and a **discrete** `frame` track |
| Plays on | `Rig/Body`, `Hitbox`, and `Rig/SwordArm` (position **and** rotation) |
| Length | **0.600 s**, 18 frames at 30 fps, `LOOP_NONE`, `step` 1/30 |

| Phase | Frames | Seconds | What the game reads |
|---|---|---|---|
| Startup | 0–5 | 0.000–0.200 | the lock, every physics tick |
| **Active** | 6–9 | **0.200–0.333** | `Hitbox.monitoring == true`, read by the physics server |
| Recovery | 10–17 | 0.333–0.600 | still locked; a second attack is buffered |
| end | 18 | 0.600 | the lock releases |

**Both clips advance on the physics tick**, not the engine's idle default,
because the fact gameplay reads — `Hitbox.monitoring` — is read on the
physics tick.

---

## The one authority

This assignment's collision was not hypothetical here. It was in the
repository: `pose_driver.gd` wrote `Sprite2D.texture` and `flip_h` every
`_process`, and the new clips key the same node.

| Animated node | The one authority | What it writes |
|---|---|---|
| `Rig` | `AnimationPlayer` | `position:y` |
| `Rig/Body` | `AnimationPlayer` | `frame` |
| `Rig/LegFront`, `Rig/LegBack` | **`LegAnim`** | `rotation_degrees`, `visible` |
| `Rig/SwordArm` | `AnimationPlayer` | `position`, `rotation_degrees` |
| `Rig/SwordArm/Blade` | `AnimationPlayer` | `visible` |
| `Hitbox` | `AnimationPlayer` | `monitoring` |

**`pose_driver.gd` is deleted, not disabled.** Disabling it would leave a
second writer in the scene that happens to be asleep, and the next person to
wake it gets a bug with no error message. `player_anim.gd` replaces it: it
reads state, calls `play()`, and **writes no animated property at all.**

**The one honest wrinkle, stated rather than hidden.** `player_anim.gd`
writes `Rig.scale.x`, the facing, which **no clip keys** — so there is still
exactly one writer per property and one *animation* authority per node, but
`Rig` has two writers at the node level. The alternative, keying facing in
every clip, doubles every clip and makes facing a property of the animation
rather than of the character. `CHANGE-BRIEF.md` §5 records it as a
judgement.

---

## The two clocks, measured

`godot/tests/measure_clocks.gd`, `evidence/a7/clocks.txt`.

| mode | `swing` becomes current | playhead **on that frame** | window opens | playhead there |
|---|---|---|---|---|
| **PHYSICS** (ships) | f1 | **0.0000** | f13 | **0.2000** |
| **IDLE** (engine default) | f1 | **0.0167** | f12 | **0.2000** |

**The answer to the assignment's question:** both clips advance on the
physics tick; gameplay reads the active window on the physics tick; **the
disagreement between the clip's write and gameplay's read is zero seconds**,
and the measurement is what establishes it — the window opens on the frame
whose playhead reads 0.2000, in both modes.

**The brief's own prediction was wrong, and the file records it rather than
being rewritten to match.** §8 predicted idle would run *up to one physics
step late*. It runs one step **early**, because an idle-mode mixer takes an
extra advance during the idle step of the frame the clip starts — a step the
physics-mode mixer does not get until the next frame. The prediction was
tagged **[proposal]**, which in this brief means *derived by Claude and not
yet confirmed*. It was not confirmed. Revision 7.0.8.

**What the run cannot see, and does not claim.** `run-test.sh` passes
`--fixed-fps`, which locks the render tick to the physics tick, so every run
is identical and the *jitter* §8 also predicted is **not** established — that
needs a windowed run at a free frame rate. Running a deterministic
measurement three times is one measurement printed three times.

---

## The evidence

`TEST-REPORT.md`'s Assignment 7 section is the full report. In short:

| | |
|---|---|
| suites | 17, **0 failures**, `evidence/a7/suite.txt` |
| the two read-backs | 164 checks |
| structure test, edge tests, pin | 78 checks |
| the clocks | 5 checks, `evidence/a7/clocks.txt` |
| mutations | 5 that must fail (all exit 1) + the fresh-cache one (exits 0), `evidence/a7/mutations.txt` |
| frame strips | `captures/swing/r1–r4`, `captures/run/r1` — **fixture captures**, labelled as such wherever they appear |

**The mutation re-run was wrong the first time, and the evidence file keeps
that run instead of only the corrected one.** A fresh `git worktree` has no
import cache, so every mutation exited 1 on `FAIL the sheet is loaded`
whether or not its own assertion fired — one of them exited 1 on *that
alone*. A mutation that passes for a reason unrelated to the mutation proves
nothing, which is the exact thing mutations exist to detect. Each worktree is
imported first now and each run names the assertion that must fire and checks
that it did.

---

## Summary of my work

**The specification came first.** `CHANGE-BRIEF.md`'s A7 text was committed
before the first agent prompt and holds the routes, the cycle arithmetic, the
phase table, the authority table, the two-clock prediction, the evidence
split, the boundaries and seven predicted failures. **Eight dated revisions
are appended rather than edited in place**, so a reader can see what changed
and why, including the two places the brief turned out to be wrong about
itself.

**Eight revisions, seven of them started by me playing the game, none by a
test going red.**

| | what I said | what was actually wrong | **what no test was asking** |
|---|---|---|---|
| r1 | can't see the sword | there was no sword — the poses are unarmed | whether the art held what the brief claimed |
| r2 | it spins above the body | the arc reversed twice about an overhead pivot, 330° in 0.6 s | which **way** the arc went, and how **low** |
| r3 | the centre of rotation is at the back | the pivot sat on the torso's back edge, to the pixel | **where the pivot was at all** |
| r4 | make the blade longer | nothing — a judgement | its length lived in three files nothing compared |
| r5 | let me swing in the air | nothing — a design call | `is_on_floor()`: a **right** thing no test held in place |
| r6 | let me move while swinging | nothing — argued against first, then built | — |
| r7 | the legs waggle, they don't alternate | **three** defects at once | the band's sign, the back leg's length, the pivot |
| r8 | — | §8 predicted the wrong sign | the clocks had never been measured, only asserted |

**r1, r2, r3 and r7 were all fully visible to a headless run before the game
was ever launched** — in the key table, in the sheet, in the generator's own
output. They are asserted now, and every one of those assertions was written
**after** a person said what they saw.

**The worst finding, and it is about a measurement I was pleased with.**
Revision 7.0.1 §4 says *"the paper version of this had the sign backwards,
and a rendered measurement caught it."* The rendered measurement had it
backwards too: PIL's `rotate()` turns the opposite way from Godot's
`rotation_degrees`, so the generator's "safe band" was in the wrong sign, the
cycle drove the planted foot **3.3 px through the floor**, and the read-back
asserted every key was inside the band and passed. *Moving a calculation off
paper and into a renderer does not make it right; it makes it harder to
check.*

**What I rejected.** Claude built A7's first sheet by code, in the existing
silhouette style. I rejected it on sight — this game already has a face, and
replacing it to make one assignment easier would have spent the game's
identity to save a day. **The rejected version is still in history at
`d303899`**, because "I rejected it" is a claim and a commit is evidence. The
cost is recorded as a trade: the two clips had to swap routes, because a
frame cycle needs several drawings of a run and this project has one.

**What I asked for that the assignment argues against.** I asked to move
while swinging. Claude put the objection first — the movement lock *was*
`GDD.md:198`'s "real risk" — and then built it. I then asked to jump
mid-swing too. What survives is the commitment that matters: no cancel, no
restart, all 18 frames, and **no turn**, because `Rig.scale.x` mirrors the
whole sword arm and a turn mid-arc would teleport the blade across the body
in one frame. The jump is the narrowest of the three changes — it writes
`velocity.y` and touches nothing the swing reads — and that *"touches
nothing"* is measured rather than argued: the same swing is run with a jump
through it and without, and the two playheads agree on all 36 physics frames
to 0.000000 s.

**Eleven sentences in this repository outlived the facts they stated**, each
true when written: a hard-coded check count, two strip captions, the blade's
length in three files, the cycle's length in a caption, a patch script that
counted text it had just written, a limitation I accepted on an unexamined
claim about the engine, a note inside a test file that was a revision out of
date, the list of open questions which went on listing one I had already
answered, a second hard-coded list that silently skipped two of the film's
three takes, and a figure in the film's own narration that was copied out of a
design document instead of being recomputed.

**The last two were found while building the film**, and the eleventh was
found by the act of writing `FACTCHECK.md` — which is what that file is for.
Each is recorded in `TEST-REPORT.md` with how it was found, and **not one of
the eleven was found by a test.** Each is recorded in `TEST-REPORT.md` with how it was found, and
**not one of them was found by a test.** The last two were found by reading
the file while changing something else, which is luck.

**Authorship.** `godot/shaders/` is untouched by Assignment 7 and
`git diff --stat godot/shaders/` prints nothing across every A7 commit.
`scripts/run-test.sh` changed **once**, in a commit of its own, to fail on
`Failed loading resource`. `SOURCES.md` §7b lists every A7 file and who wrote
it; `FRICTIONAL.md` has the dated log; **every `TUNING.md` verdict and every
prediction in it is mine**, quoted verbatim in the Chinese it was said in.

---

## Known limitations

- **The run cycle alternates; it does not stride.** Measured: across 88° of
  rotation the foot moves about **10 px** against a **24 px** step, because
  the cut leg is 8.6 px long with its foot almost directly under the hip. No
  key value fixes it. Drawing a longer leg would, and that is a change to the
  character's art — the thing I rejected a whole sheet over — so it stays a
  HUMAN row in `CHANGE-BRIEF.md` §9 and my decision.
- ~~A swing with a direction held slides.~~ **Fixed in revision 7.0.9, and
  the sentence that called it unfixable was the defect.** 7.0.6 §4 said
  showing the legs during a moving swing "means two clips at once, which
  means an `AnimationTree`". That is only true if the legs and the body come
  from the same player, and nothing ever said they did. They have their own
  `AnimationPlayer` now; the rule was always *one authority per node*.
- **The hitbox can hit nothing** — this room has no enemy. The window is
  real, switched by a discrete track on the clip's own timeline, and asserted
  at every boundary; what it would *do* is a later assignment. §11 said so
  before it was built.
- **The idle-mode clock's jitter is not measured**, only its one-step offset.
- **`roll`, `cast` and combo-2/3** from `GDD.md:393` are not built.
- **`godot/tests/test_keyboard.gd` does not load.** It preloads
  `res://game/session.gd`, a `walker-ninja` file that has never existed here;
  unloadable since the game changed on 2026-10-17, and unloadable at `a6.1`.
  Nothing in A7 touched it and it is not in the suite `CLAUDE.md` names.
  Recorded rather than deleted.
- **Two `SceneTree` tests leak at exit** (`ObjectDB instances were leaked`,
  `resources still in use`). Pre-existing and scaling with how much of the
  scene a run exercises; the wrapper deliberately does not fail on either.
- **Two existing tests changed their expectations**, which `CLAUDE.md`
  otherwise forbids. Both are named in revision 7.0.6 as crossings I
  authorised, and both were **inverted rather than deleted**, so the file
  still states the rule. A test left asserting a superseded rule is the
  loudest way to learn the design moved; a test deleted for failing is the
  quietest.

**Changed games since Assignment 2:** **Yes.** On 2026-10-17, using the
course's one permitted change of game, with the written justification in
`FRICTIONAL.md`. Assignments 1–3 were submitted from
`walker-ninja-TiantongZhang` under the tags `a2-submitted` and `a3`, and that
repository has not been modified since. Per the rule the tags continue here;
`a5` is this repository's first tag and `a7` is this submission's.

Assignment 7 itself changed nothing: same game and same repository as
Assignments 4, 5 and 6. This field answered "No" once during Assignment 6,
which was wrong — it answered *"did Assignment 6 change games"*, which is not
the question asked. It is answered correctly here, and the drift is recorded
in A6's note rather than quietly fixed.
