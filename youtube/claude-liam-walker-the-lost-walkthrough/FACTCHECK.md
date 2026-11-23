# FACTCHECK.md — every claim the narration makes, and what establishes it

One row per factual claim spoken in the film. **MEASURED** — a number this
repository produced from a run, a resource or a capture, with the file named.
**READ** — read out of a committed file. **OBSERVED** — visible in the
footage the beat plays, and the evidence window in `coverage.json` says
where. **REASONING** — an argument rather than a measurement; those are the
rows to argue with.

Game source `5042a6b`, `build_id` `11af9145…`. Every time cited below was
read off a take's input log, not counted forward from the driver's sleeps.

---

## B00 — the ask

| Claim | Status | Where |
|---|---|---|
| "The prompt on screen is a reconstruction… It was never sent." | **READ** | said aloud, on screen, and in `SHOTLIST.md`. `PROMPTS.md` holds the real ones. |
| "a dungeon slice… where every hazard announces itself before it can hurt you" | **READ** | `spike_trap.gd`: 0.40 s warning before a 0.18 s strike. |

## B01 — what was built

| Claim | Status | Where |
|---|---|---|
| "five animation states" | **READ** | `player.gd`'s enum and `player_anim.gd`'s selector: idle, run, rising/falling, swing, dead. |
| "Three animations" | **READ** | `legs.tres` (cycle), `player.tres` (`swing`), `floating_key.tscn` (`hover`). |
| "The hitbox hits nothing" | **READ** | `Hitbox` masks layer 3, `Enemy`; the room has none. `CHANGE-BRIEF.md` §11.3. |
| "no respawn… no menu" | **READ** | `main.tscn` has neither; nothing handles death beyond the clip. |
| "Three hundred automated checks" | **MEASURED** | 82+79+26+60+15+13+5+20 = 300, `evidence/a7/suite.txt`. Step-dust's 26 is counted once though it runs at three rates. |
| "not one of them can tell you whether it reads" | **REASONING** | the evidence split in `CHANGE-BRIEF.md` §9, which keeps nine HUMAN rows for exactly this reason. |

## B02 — idle, the cycle, the facing, the dust

| Claim | Status | Where |
|---|---|---|
| "idle is a single held frame, not a clip" | **READ** | `player.tres`'s `idle` keys one frame value and holds. |
| "The cycle is half a second" | **READ** | `legs.tres:24`, `length = 0.5`. |
| "two strides at twenty-four pixels against ninety-six a second" | **MEASURED** | `stride_px = 24.0` in `main.tscn`, `SPEED = 96.0` in `player.gd`. 2 × 24 / 96 = 0.500 exactly. |
| "The dust spawns on the same twenty-four" | **READ** | `step_dust_driver.gd`, distance-driven, `stride_px`. |
| "On the turn, the whole rig mirrors" | **OBSERVED** | facing flips at 4.53 s in take a; `player_anim.gd` writes `Rig.scale.x` and no clip keys it. |

## B03 — the air states, and the simple animation

| Claim | Status | Where |
|---|---|---|
| "two states for one key, split on the sign of the vertical velocity" | **READ** | `player_anim.gd`: `rising` if `velocity.y < 0`, else `falling`. |
| "the horizontal velocity carries through" | **OBSERVED + READ** | take a 13.10–15.00 s: `run` → `rising` → `falling` → `run`; nothing in the jump branch writes `velocity.x`. |
| "No rig, no frames, two tracks" | **MEASURED** | `test_pickup_clip.gd` asserts exactly that, 20 checks. |
| "It autoplays" | **READ** | `floating_key.tscn`, `autoplay = "hover"`. |
| "nothing collects it" | **READ** | it has no `Area2D`, no collision shape and no script. `CHANGE-BRIEF.md` revision 8.0.1 §4. |

## B04 — the committing action

| Claim | Status | Where |
|---|---|---|
| "Eighteen frames at thirty" | **READ** | `player.tres`: `length = 0.6`, `step` 1/30, `LOOP_NONE`. |
| "ten degrees in two frames, then a hundred and fifty in four" | **MEASURED** | the rotation keys: −60° → −50° over 0.0667 s, then −50° → +100° over 0.1333 s. `CHANGE-BRIEF.md` revision 7.0.2 §4. |
| "The arm nearly stops before it goes" | **MEASURED** | 150 °/s against the strike's 1125 °/s — a factor of 7.5. |

> **The figure this row exists to protect.** An earlier cut of Assignment 7's
> other film said the strike was *"five times the speed of the wind-up"*. It
> is 2.25× the wind-up's average and 7.5× its slowest segment; "five" came
> from comparing against only the first segment and rounding. **It had been
> copied out of a design document instead of recomputed.** This film says
> only the 7.5× comparison and names what it is compared against.

## B05 — the edge

| Claim | Status | Where |
|---|---|---|
| "a second attack a tenth of a second in, inside the startup — nothing" | **OBSERVED + MEASURED** | take b: swing starts 7.25 s, press at 7.35 s, next swing in the log is 9.82 s from a separate press. The startup is 0–0.200 s. |
| "one four and a half tenths in, inside recovery — buffered" | **OBSERVED + MEASURED** | take b: swing at 9.82 s, press at 10.27 s, next swing at **10.42 s** — 0.600 s after the first, which is the clip's own end. Recovery is 0.3333–0.600 s. |
| "the playhead decides" | **READ** | `player.gd` compares `current_animation_position` against `RECOVERY_START`. |
| "8 swings from 10 presses" (the take's own assertion) | **MEASURED** | the capture driver's verdict line, in the render log. |

## B06 — the two revisions

| Claim | Status | Where |
|---|---|---|
| "the gait keeps running underneath" | **OBSERVED** | take c 2.12–3.13 s: `swing` current, `legs_run` current, player x 174 → 232. |
| "the legs have their own animation player" | **READ** | `LegAnim` in `player.tscn`; `test_player_clips.gd` asserts the partition in both directions. |
| "the swing carries on from where it was" | **OBSERVED + MEASURED** | take c 7.15–9.00 s. Established properly by `test_swing_edges.gd` §E: the same swing run twice, jumped and not, agreeing to **0.000000 s** over 36 frames. |
| "that branch writes one field" | **READ** | `player.gd:115-116`, two lines. |
| "there is no path from it to the clip's clock" | **REASONING** | a claim about the whole function, of which the film shows two lines. Its *consequence* is the measurement above. |

## B07 — the hazard, damage, and death

| Claim | Status | Where |
|---|---|---|
| "waits four tenths of a second, and fires" | **READ** | `spike_trap.gd:39-40`: 0.40 warning, 0.18 fire. |
| "four tenths against a swing's two-tenth wind-up" | **READ** | 0.40 against the startup's 0.200. |
| "why you can read a trap and still attack near it" | **REASONING** | a design argument from those two numbers. `CHANGE-BRIEF.md` §6 makes it; nothing measures whether a player actually can. |
| "the hit does… nothing" to the animation | **OBSERVED** | take d: health drops at 2.83, 5.62, 8.40 s and no clip changes on any of them. |
| "Five hits kill" | **MEASURED** | `MAX_HEALTH = 5`; the log shows 5→4→3→2→1→0. |
| "the fifth state… a condition a player action caused" | **OBSERVED + READ** | `dead` becomes current at 17.90 s, 0.02 s after health reaches 0 at 17.88 s. |
| "no respawn, no retry" | **READ** | nothing in the project handles it. Listed `planned` in `coverage.json` with that reason. |

## B08 — cause and effect

| Claim | Status | Where |
|---|---|---|
| "the author played it and said: it is spinning in circles above the body" | **READ** | `TUNING.md`, 2026-11-18, quoted verbatim in the original Chinese with a translation. |
| "the tip is never below minus three pixels in any of the eighteen frames" | **MEASURED** | computed on the card itself from r1's key table: the lowest tip y is **−3.4**. `evidence/a7/before-after.txt`. |
| "the rotation keys stopped reversing direction and the pivot became part of the animation" | **READ** | revisions 7.0.2 and 7.0.3. |
| "no check was asking" | **READ** | revision 7.0.2 §5 records that both new rules fail r1's angles when pasted back in — nine failures — and that no test had been asking. |

## B09 — the verdict

| Claim | Status | Where |
|---|---|---|
| "five states each entered by its own input or by a condition an input caused" | **OBSERVED** | B02–B07; `coverage.json` names the window for each. |
| "a cycle that wraps without a seam" | **MEASURED** | `test_player_clips.gd`'s seam rule; 18 wraps observed in take a. **Whether it reads as seamless is the author's and is answered in `TUNING.md`, not here.** |
| "300 checks and seven deliberate breakages" | **MEASURED** | `evidence/a7/suite.txt`, `evidence/a7/mutations.txt`. |
| "agreeing to zero" | **MEASURED** | `evidence/a7/swing-edges-e.txt`, three phases, 0.000000 s each. |
| "whether a braced stance hanging in mid-air reads at all… nobody has judged that" | **READ** | `CHANGE-BRIEF.md` §9's ninth HUMAN row, still open. |

## B10 — your turn

No claim about the game. The claim about this project — *"the answer during
the startup was nothing at all, and nothing at all is also what a completely
unwired version would have done"* — is **READ**: Chapter 10 and
`CHANGE-BRIEF.md` H6 both state that `play()` with the name already playing
does not restart, and `test_swing_edges.gd` §B is what distinguishes the two.

---

## Said nowhere in this film, on purpose

- **Any performance or cost number.** Nothing here was priced; Movie Maker
  renders offline and a figure from it would be meaningless.
- **That the author enjoyed it, or that it feels good.** No scripted capture
  is a playtest. The author's verdicts are dated in `TUNING.md` and this film
  quotes one of them — the complaint — rather than the approvals.
- **That the walkthrough is complete.** It is complete against an inventory
  **this project wrote about itself**. A feature nobody thought of is not in
  `coverage.json` and no check can say so.

## Who audited this

Claude wrote the narration and Claude wrote this file. **That is the same
party checking its own work**, and it is worth knowing while reading it. The
one external check is the machine one — `./art godot-waikthrough --check` —
and it validates hashes, dimensions, time ranges and references, not truth.
