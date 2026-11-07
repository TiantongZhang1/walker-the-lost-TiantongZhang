# TUNING.md — Effect A and Effect B, one change at a time

Assignment 6's tuning loop. Every revision below has the same five parts, and
none of them is optional:

1. **What I saw** in the running game, at the project's window size, in
   visual terms — written *before* Claude reads anything.
2. **Claude's reading** of the current strip.
3. **The change**, one setting, approved by me before it was made.
4. **Claude's prediction** for what the next strip should show, written
   before the recapture.
5. **My verdict** in the running game: kept or reverted, and why.

**Claude's reading of a strip is a claim, not a check.** Where we disagree,
my verdict in the running game decides and the disagreement is recorded here
rather than quietly resolved. The strips are what make that reviewable: a TA
can see what I saw.

All preview captures are **fixture captures** and are labelled as such
wherever they appear.

---

## 2026-11-06 — Effect A, r0, the first look

**Strip:** `captures/hit_burst/r0/`, laid out in `captures/hit_burst/r0-strip.png`
**Scene at this revision:** `godot/effects/hit_burst.tscn`, commit TBD
**Configuration test:** 80 checks, 0 failures

**Mechanical check, made before anyone looked at the picture** — pixels
differing from frame 8 inside a box around the trap: 48, 114, 130, 148, 182,
278 on frames 9, 10, 11, 12, 15, 20, then **0** on 30 and 50. The burst
fires, peaks near frame 20 and is gone by 30, as `CHANGE-BRIEF.md` §1.5
predicted. Particles appear on frame **9**, one ahead of the preview's own
counter; the strip is read from 10 as the brief says.

That is all a pixel count can say. It establishes that the effect *fires and
clears on time*, and nothing at all about whether it reads as grit.

**What I saw (running game, 1280 × 720):**

> _TO FILL IN — this is the first verdict and it comes before Claude reads
> the strip. Run the game, walk into a trap, watch it fire several times.
> Write it in visual terms: is it grit or is it a puff of nothing? Is it the
> right size beside the character? Can you see it at all at x 208, where
> there is no torch?_

**Claude's reading of r0:** _held until the line above is written._
