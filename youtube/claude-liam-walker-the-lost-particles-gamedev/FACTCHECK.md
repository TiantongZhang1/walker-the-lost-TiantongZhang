# FACTCHECK.md — every narrated claim, and what backs it

Verdicts: **MEASURED** — a number this repository produces and a reviewer can
reproduce. **SOURCE** — a fact about the files, checkable by reading them.
**REASONING** — an argument from measured facts, not itself a measurement.
**AUTHOR** — a human judgement, which is the only kind of evidence the
assignment accepts for how something looks.

A claim marked REASONING is not a weaker claim; it is a differently supported
one, and mixing the two silently is the failure this file exists to prevent.

---

## B00–B01, the bookends

| Claim | Verdict | Source |
|---|---|---|
| The prompt on screen is a reconstruction and was never sent | SOURCE | Said aloud in the narration and labelled on the card. `PROMPTS.md` carries the prompts that were actually used |
| Three effects, six emitters | SOURCE | `hit_burst.tscn` 3, `dungeon_motes.tscn` 1, `step_dust.tscn` 2 |
| 249 checks, 301 results | MEASURED | 80 + 22 + 39 + 19 + 63 + 26; the step-dust state suite's 26 run at 30, 60 and 144 fps. Run `./scripts/run-test.sh` on each |
| Two deliberate breakages | SOURCE | `CHANGE-BRIEF.md` §0.2's two mutations; `TEST-REPORT.md` records both exiting 1 |

## B02–B03, the event

| Claim | Verdict | Source |
|---|---|---|
| `fired` existed before this assignment and was not touched | SOURCE | `spike_trap.gd:24`, present at tag `a5`. `git log -- godot/features/traps/spike_trap.gd` |
| `emitting = true` on a busy `one_shot` node does not restart it | SOURCE | Godot's documented behaviour, and the assignment's named failure F3. **Not independently measured here** — the design avoids it rather than demonstrating it |
| The burst is parented to the room, not the trap | SOURCE | `hit_burst_spawner.gd`, `room_path` default `^".."`; asserted by rule A5 in the state suite |
| Three traps fire in one walk | MEASURED | take p asserted `fired` on all three before printing CAPTURE OK |

## B03A, rapid repeats

| Claim | Verdict | Source |
|---|---|---|
| This is not gameplay | SOURCE | take r calls `fired.emit()` directly; no input is parsed. Labelled on the card, in the title and in the narration |
| Three bursts alive at once | MEASURED | take r's own log; peak live-burst count 3, 60 instances in all |
| The played take peaked at one | MEASURED | take p's log, peak 1 |
| Traps 112 px apart, player 96 px/s, events 1.17 s apart, burst lives 0.60 s | SOURCE + REASONING | Positions from `main.tscn`, `SPEED` from `player.gd:19`, lifetime from `hit_burst.tscn`. The division is revision 6.0.2's |
| The ceiling of three is unreachable by playing this room | REASONING, corroborated | The arithmetic above, plus take p's measured peak of 1 |

## B04–B05, the three parts and the tuning loop

| Claim | Verdict | Source |
|---|---|---|
| Emission / process / draw split as narrated | SOURCE | `CHANGE-BRIEF.md` §7's table, and the excerpt itself |
| `visibility_rect` culls the node and never clips a particle | SOURCE | Godot's documented behaviour. **Not measured here.** `TUNING.md` notes the consequence: motes below the floor are not clipped by it |
| `Flash` at 1.6 / 2.4 was the same size on screen as the grit | AUTHOR + MEASURED | The author's reading of `r0-strip.png`; the scale values are in the scene file |
| The prediction was five of six, wrong on frame 12 | MEASURED | Recomputed by `scripts/compose_particles_evidence.py`; 52 px differ at frame 10 and 0 at 12 |
| The two frame-12 images are bit-identical | MEASURED | 0 pixels differ, no threshold, whole frame |
| If `Flash` contributed light at frame 12, tripling its scale would move a pixel | REASONING | `Flash` is the only thing that changed and it is drawn additively. The strip cannot separate "dead" from "below the quantization floor", and `TUNING.md` says so |
| The verdict was keep | AUTHOR | `TUNING.md`, 2026-11-07, 留下 |

## B06–B07B, Effect B

| Claim | Verdict | Source |
|---|---|---|
| `preprocess = 8.0` is one full lifetime | SOURCE | `lifetime = 8.0` on the same node |
| Full field on frame 1 with it, 2 % without | MEASURED | 518 px against 12 px, recomputed from the committed frames against an empty-room baseline |
| Climbing to 20 % by frame 40 | MEASURED | 99 px against 496 |
| Nothing errors without it, and the config test passes on both | MEASURED | The mutation was run; `TEST-REPORT.md` records it |
| No headless run in this repository can see it | SOURCE + REASONING | A headless run uses a dummy renderer and draws nothing. `CLAUDE.md` records the fact; F4 is the brief's own statement of the consequence |
| A paused tree freezes the field | MEASURED | take c, 78 consecutive frames with the player's x unmoved; also asserted by rule B3 in the state suite |
| `emitting` goes false on death and nothing is cut off | MEASURED | take c's log, and rule B2 |
| The field does not begin to thin for about two seconds | MEASURED | `TUNING.md`'s B2 tail: 412 → 409 mote px at 1 s. **Not re-measured for the film**; the film shows the tail rather than quoting the number |

## B08–B09, the process shader

| Claim | Verdict | Source |
|---|---|---|
| 384 lines, generated by converting Dust's material in the editor | SOURCE | The file, and `CLAUDE.md`'s dated ownership exception |
| Lines 161 and 162 sample `scale_curve` and `color_ramp` | SOURCE | Read back out of the committed file |
| A curve in the Inspector is a 1-D texture sampled per particle per frame | SOURCE | What those two lines do; the uniforms are declared `sampler2D` at 45–46 |
| Line 160 is Godot's insertion point and is empty for a material with no ramp or curve | MEASURED, the hard way | The first conversion was of a default empty material and had no `texture()` call anywhere. That file is not in the repository; the failure is recorded in `TEST-REPORT.md` |
| Dust is the only emitter with both a ramp and a curve | SOURCE | `hit_burst.tscn`: Flash has both, **so this is wrong as stated if read as "only"** — see the correction below |
| The burst gets wider and dimmer across its life | MEASURED | extent 10 × 12 → 69 × 69 logical px, brightest channel 230 → 92, frames 10 to 20 |

> **Correction, recorded rather than quietly fixed.** `Flash` also carries both
> a `scale_curve` and a `color_ramp`. The narration's reason for choosing Dust
> is therefore imprecise: Dust was chosen because it is the emitter whose
> curves are the *subject* — a growing, fading puff — and because `Flash` lives
> for 0.12 s and is additive, which makes its curves nearly impossible to read
> in a strip. `Grit` has a ramp and no curve. The on-screen note says "the only
> emitter carrying BOTH", which is accurate of Grit and Dust and not of Flash.
> The claim as narrated overstates it. Left in the film and corrected here,
> because re-rendering the beat to hide it would be the wrong lesson.

## B10–B11, Effect C

| Claim | Verdict | Source |
|---|---|---|
| There is no footstep signal in this game | SOURCE | `player.gd` has `health_changed` and `died` and nothing else |
| One puff per 24 px travelled | SOURCE | `stride_px` is an `@export` set to 24.0 in `main.tscn` |
| The spacing is the same at any frame rate | MEASURED | 0.0000 px deviation over seven gaps at 30, 60 and 144 fps, `test_step_dust_state.gd` |
| Without the back-date it was 3.2 px out at 30 fps | MEASURED | Recorded in revision 6.0.5 before the fix |
| 25 puffs in take p | MEASURED | take p's assertion, 25 distinct instances |
| The mirror works | MEASURED | `captures/step_dust/r0-strip.png` frames 32 and 70, and visible in take p |

## B11A–B11B, the price

| Claim | Verdict | Source |
|---|---|---|
| A headless run draws nothing and runs no particle process | SOURCE | Dummy renderer; stated in `CLAUDE.md` and in the cost script's own header |
| The ordering is stable; B smallest, A and C larger | MEASURED | Two recorded runs, `evidence/a6/cost-effects-run{1,2}.txt` |
| The microsecond figures are not stable | MEASURED | B moves +1.3 → +4.3 between runs while each run's own baseline spread reads 0.5 |
| The instances column is identical across runs | MEASURED | 30 / 0 / 22 / 55 in both |
| What is being weighed is instancing, not the particle process | REASONING | The process never ran; the only effect-specific CPU work left is spawning and freeing a scene. The instances column is consistent with it and does not prove it alone |
| With vsync on, FPS reads the refresh rate with the effects off and on | REASONING | `CHANGE-BRIEF.md` §7. **Not measured.** The F9 key exists so it can be, and that measurement has not been made |
| No budget here is settled | SOURCE | Every budget in §5 and §C.6 is GPU time. None has been read |

## B12, the verdict

| Claim | Verdict | Source |
|---|---|---|
| Who wrote what | SOURCE | `git log`, `FRICTIONAL.md`, and `CLAUDE.md`'s ownership section |
| Four checks that could not fail shipped green | SOURCE | `TEST-REPORT.md` names all four, including the one written as `x or true` |
| A capture helper threw once an instance freed itself | SOURCE | `hit_burst_spawner.gd`'s `live_count()` docstring, and the commit that fixed it |
| The first generated shader was converted from an empty material | SOURCE | `TEST-REPORT.md`, and the author found it by counting lines |
| No emitter has a texture | SOURCE | All six draw Godot's default point; `TEST-REPORT.md` and the config suites |
| GPU times are not read, so every budget is a prediction | SOURCE | `CHANGE-BRIEF.md` §5, and `SUBMISSION.md`'s known limitations |
| Effect B's loop produced a verdict of keep with no setting changed | SOURCE | `TUNING.md`, 2026-11-07. **This is a gap, not a finding**, and the film says so in the author's voice rather than in Claude's |
| 11–29 % of the dust drifts below the floor line | MEASURED | `TUNING.md`'s Effect C r0 table; Effect B's figure is 14–22 % |

---

## What this film does not claim

- That any effect meets its GPU budget. No GPU time has been read.
- That Effect B or Effect C has completed its tuning loop. B has a verdict and
  no revision; C has a reading and no verdict.
- That the headless cost figures are a price. They are a control on a
  prediction, and the prediction was that they would be approximately zero.
- That the author's verdicts are reproducible. They are judgements, recorded
  verbatim in `TUNING.md` with the strips that produced them, so a reviewer
  can see what was seen and disagree.
