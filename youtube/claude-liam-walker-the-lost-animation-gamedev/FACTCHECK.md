# FACTCHECK.md — every claim the narration makes, and what establishes it

One row per factual claim spoken in the film. **MEASURED** means a number this
repository produced from a run, a resource or a capture, with the file named.
**READ** means it is read out of a committed file and the film shows that
file. **REASONING** means it is an argument rather than a measurement, and
those rows are the ones to argue with.

Game-source revision `b33b06c`. Every line number cited here is at that
revision; the ledger re-reads every panel's range and refuses to write if a
line moved.

---

## B00 — the ask

| Claim | Status | Where |
|---|---|---|
| "The prompt on screen is a reconstruction... It was never sent." | **READ** | said aloud, on screen, and in `SHOTLIST.md`. The real prompts are in `PROMPTS.md`. |
| "a character who could walk and jump and nothing else" | **READ** | `CHANGE-BRIEF.md` §1: one `Sprite2D`, one `CollisionShape2D`, one `PoseDriver`; `grep -rl AnimationPlayer godot/` was empty. |

## B01 — what was built

| Claim | Status | Where |
|---|---|---|
| "Two hundred and eighty automated checks" | **MEASURED** | 82 + 79 + 26 + 60 + 15 + 13 + 5 = 280, `evidence/a7/suite.txt`. Step-dust's 26 × 3 rates are counted once, as 26, because it is one suite. |
| "seven deliberate breakages" | **MEASURED** | `evidence/a7/mutations.txt`, M1–M7. |
| "ten tuning revisions" | **READ** | `CHANGE-BRIEF.md` revisions 7.0.1 – 7.0.10. |
| "nine of them reported by the author, playing" | **MEASURED** | `evidence/a7/revisions.txt`, computed from the table in `scripts/compose_animation_evidence.py`. The tenth, 7.0.8, is Claude's. |
| "Not one of the ten started with a test that had been passing and started failing" | **REASONING** | Argued in `evidence/a7/revisions.txt`. 7.0.8 came from a measurement **written to test a prediction**, which is not the same as an existing test going red. The distinction is drawn explicitly rather than smoothed over. |
| "a cut-out rig, and a sword swing on a sprite sheet — the opposite way round" | **READ** | Assignment 7's own text says *"the natural split is a looping sprite cycle and a rig action, but either way round works."* `CHANGE-BRIEF.md` revision 7.0.1 §2. |

## B02 — the cycle

| Claim | Status | Where |
|---|---|---|
| "Length, nought point five seconds" | **READ** | on screen, `legs.tres:24`. |
| "a puff of dust every twenty four pixels... ninety six pixels a second" | **READ** | `stride_px = 24.0` in `game/main.tscn`; `SPEED = 96.0` in `player.gd:42`. |
| "a gait cycle is two strides. Half a second, exactly" | **REASONING** | 2 × 24 / 96 = 0.500. The *arithmetic* is exact; that a gait cycle is two strides is a definition this brief adopts and `CHANGE-BRIEF.md` revision 7.0.7 §5 argues for. |
| "Step is nought point one two five — a quarter cycle" | **READ** | `legs.tres:26`. |
| "thirty eight, twelve, minus fourteen, twelve, thirty eight" | **READ** | on screen, `legs.tres:37`. |
| "front plus back is twenty four on every single key" | **MEASURED** | `test_player_clips.gd` asserts it as arithmetic: measured `24.0, 24.0, 24.0, 24.0, 24.0`. |
| "the cycle this replaced had two legs that came within two degrees of each other" | **MEASURED** | `CHANGE-BRIEF.md` revision 7.0.7 §7. |
| "the facing mirrors the whole rig, so one set of keys is correct both ways round" | **READ** | `player_anim.gd` writes `Rig.scale.x`; no clip keys it. |

## B03 — the cycle in play

| Claim | Status | Where |
|---|---|---|
| "Both facings" | **MEASURED** | the take asserts it; the card prints the frame count facing left, read from `take-c-inputs.jsonl`. |
| "the dust lands under the planted foot" | **REASONING, and the author's** | The *arithmetic* says it must: the contacts fall 0.250 s apart, which at 96 px/s is 24 px, which is `stride_px` exactly. **Whether it reads is a HUMAN row** and the author answered it on 2026-11-20 — *灰尘也对得上*. The footage is offered as a look, not as the proof. |

## B04 — the committing action

| Claim | Status | Where |
|---|---|---|
| "Eighteen frames at thirty, nought point six seconds, and it does not loop" | **READ** | `player.tres`, `length = 0.6`, `loop_mode = 0`, `step` 1/30. Asserted by `test_swing_clip.gd`. |
| "Monitoring goes true at nought point two and false at nought point three three three" | **READ** | on screen, `player.tres:117`. |
| "dangerous for exactly four frames out of eighteen" | **MEASURED** | 0.3333 − 0.200 = 0.1333 s = 4 frames at 30 fps. Traced frame by frame in `test_swing_edges.gd` §A: opens on physics frame 12, closes on 20. |
| "Update equals one — discrete" | **READ** | on screen, `player.tres:119`. |
| "a hundred and fifty degrees in a hundred and thirty three milliseconds. Eleven hundred degrees a second" | **MEASURED** | −50° to +100° between frames 6 and 10 = 150° / 0.1333 s = 1125°/s, from `player.tres:155-158`. |
| "twice the average speed of the wind-up" | **MEASURED** | the wind-up is −150° to −50° over 0.200 s = 500°/s. 1125 / 500 = **2.25**. |
| "seven times the speed the arm has slowed to in the two frames just before it fires" | **MEASURED** | −60° to −50° over 0.0667 s = 150°/s. 1125 / 150 = **7.5**. |
| "narrower than the spike trap's own lethal window" | **READ** | `FIRE_SECONDS = 0.18` in `spike_trap.gd:40`, against 0.1333. |

> ### A correction this file caught before the film shipped
>
> **An earlier cut of the narration said "five times the speed of the
> wind-up".** Writing this row is what found it. The figure came from
> `CHANGE-BRIEF.md` revision 7.0.2 §4, which compared the strike against
> the wind-up's FIRST segment — −150° to −60° over 0.1333 s, 675°/s — and
> rounded up. Against the whole wind-up the ratio is 2.25.
>
> **It was repeated into the narration from a document instead of being
> recomputed**, which is the seventh time a figure in this assignment has
> travelled that way. The narration now says both true ratios, and the
> brief's §4 carries the correction at its source.
>
> The corrected sentence is also the better one: the arm nearly stops before
> it fires, and "seven times the speed it had two frames ago" says that.

## B05 — four swings

| Claim | Status | Where |
|---|---|---|
| "Four swings, four fresh presses — nothing buffered" | **MEASURED** | the driver taps with 1.1 s gaps, longer than the 0.3333 s recovery; the take asserts four distinct `swing_count` increments and the card prints them. |
| "the hitbox window is NOT visible in this footage" (on the card) | **READ** | a hitbox is an `Area2D` with no `CanvasItem`. It draws nothing. |

## B06 — one authority

| Claim | Status | Where |
|---|---|---|
| "a pose driver was writing the sprite's texture every frame and the new clip keyed the same node" | **READ** | `CHANGE-BRIEF.md` §1, `pose_driver.gd:52`. The file is deleted at this revision; it is in history. |
| "a design document in this repository said that would require an animation tree" | **READ** | `CHANGE-BRIEF.md` revision 7.0.6 §4, quoted verbatim in revision 7.0.9 §2. |
| "That sentence was wrong" | **MEASURED** | revision 7.0.9 built the alternative and it works: two players, disjoint node sets, no `AnimationTree`. |
| "the check asserts the partition in BOTH directions" | **READ** | on screen, `test_player_clips.gd:217-230`. |
| "a scene where both players write the legs satisfies the easy version perfectly" | **MEASURED** | the mutation does exactly that: two of three checks go red, and the one that would not have caught it is named. |

## B07 — the partition card

| Claim | Status | Where |
|---|---|---|
| "Six tracks on one player, six on the other" | **MEASURED** | parsed from `player.tres` and `legs.tres` by `compose_animation_evidence.py` at build time; printed to `evidence/a7/partition.txt`. |
| "the intersection is empty" | **MEASURED** | same. |
| "two of the three checks go red" | **MEASURED** | `evidence/a7/mutations.txt`. |

## B08 / B09 — two clocks

| Claim | Status | Where |
|---|---|---|
| "The brief predicted... up to one physics step LATE, and jitter" | **READ** | `CHANGE-BRIEF.md` §8, tagged `[proposal]`. |
| "It was wrong — wrong in sign. Idle is one step EARLY" | **MEASURED** | `evidence/a7/clocks.txt`: physics playhead 0.0000 on the starting frame, idle 0.0167. |
| "Both modes make the clip current on the same physics frame" | **MEASURED** | same file, f1 in both. |
| "the physics-mode mixer already took its step for that frame before anything called play" | **REASONING** | an explanation of the measurement in terms of tree order and callback mode. The *numbers* are measured; the *cause* is argued, and revision 7.0.8 §3 argues it. |
| "the window opens on the frame whose playhead reads nought point two exactly, so writer and reader disagree by zero seconds" | **MEASURED** | `evidence/a7/clocks.txt`, both modes. |
| "this cannot see the jitter" | **READ** | `measure_clocks.gd` prints it; `scripts/run-test.sh` passes `--fixed-fps`. |

## B10 / B11 — the jump

| Claim | Status | Where |
|---|---|---|
| "this branch writes one field — vertical velocity — and nothing else" | **READ** | on screen, `player.gd:115-116`. |
| "It does not touch the action state, the swing counter, the buffered attack, or any animation player" | **READ** | the two lines are on screen in full. |
| "There is no code path from a jump to the clip's clock" | **REASONING** | a claim about the whole function, of which the film shows eight lines. The *consequence* is measured in B12/B13. |
| "a swing that travels with its gait still under it" | **MEASURED** | 108 frames of `locked` with `legs_run` current, asserted by the take and printed on the card. |

## B12 / B13 — the comparison

| Claim | Status | Where |
|---|---|---|
| "run the same swing twice... and compare the two clocks frame by frame" | **READ** | on screen, `test_swing_edges.gd:428-438`. |
| "Playhead, hitbox window, lock, clip name, on all thirty six physics frames, in all three phases" | **READ** | the loop is on screen; the three phases are the enclosing `for`. |
| "Nought point zero zero zero zero zero zero seconds, in all three phases" | **MEASURED** | `evidence/a7/swing-edges-e.txt`. |
| "Every single check that the jump WORKS stays green under it. All three of them. Eight others go red" | **MEASURED** | `evidence/a7/mutations.txt`, M7. |
| "in the recovery case, one of the comparison checks passed under the mutation too" | **MEASURED** | same file, recorded as a named blind spot rather than omitted. |

## B14 — the ten revisions

| Claim | Status | Where |
|---|---|---|
| "Nine of them started with the author playing the game" | **MEASURED** | `evidence/a7/revisions.txt`, computed. |
| "Three of the ten were design calls... Two were judgements... three of them say read-back" | **MEASURED** | same, computed from one table. The **classification itself is REASONING** and the reason for each row is written out in that file so it can be argued with. |
| "the tip is never below minus three pixels in any of the eighteen frames" | **MEASURED** | `CHANGE-BRIEF.md` revision 7.0.2 §2, computed from the r1 key table. |
| "a correctly computed bounding box of the wrong quantity, because it included a trailing scarf" | **MEASURED** | revision 7.0.3 §2; `tools/check_sword_reach.py` measures the dense run at +3..+13 against the ink box starting at −11. |
| "a planted foot three pixels through the floor while the assertion about that foot was green" | **MEASURED** | revision 7.0.7 §2: 3.3 px, and the band assertion passed. |

## B15 — the verdict

| Claim | Status | Where |
|---|---|---|
| "Two hundred and eighty checks and seven mutations" | **MEASURED** | as B01. |
| "the hitbox can hit nothing, because this room has no enemy" | **READ** | `CHANGE-BRIEF.md` §11.3 and `CLAUDE.md`'s Unconfirmed section. The hitbox masks layer 3, `Enemy`; the room has none. |
| "the cut-out leg moves its foot about ten pixels against a twenty four pixel step" | **MEASURED** | revision 7.0.7 §6: across 88° the foot moves ~10 px. |
| "three questions in the evidence table are still open" | **READ** | `CHANGE-BRIEF.md` §9: both clips over the darkest and lightest level art; whether a moving swing reads, which 7.0.9 changed the answer to and which has not been re-judged; whether a jumped swing reads in mid-air. |

## B16 — your turn

No factual claims about the game. The one claim about this project —
*"the sentence that cost this project a day"* — is **MEASURED** in the sense
that the dates are in the files: revision 7.0.6 is dated 2026-11-19 and
revision 7.0.9, which refuted its §4, is dated 2026-11-20.

---

## Numbers deliberately NOT said in the film

- **The GPU cost of any of this.** Nothing here was priced. Assignment 6
  priced its effects and said what the instrument could not resolve; this
  assignment did not measure frame cost at all, and saying nothing is the
  honest version of that.
- **How many of the 280 checks are "about animation".** The suites overlap —
  the input-map check is in the harness, the step-dust suite is A6's — and any
  split would be a judgement dressed as a count.
- **Whether the film's own figures were checked by anyone but their author.**
  They were not. This file is the audit and it is written by the same person
  who wrote the narration, which is worth knowing while reading it.
