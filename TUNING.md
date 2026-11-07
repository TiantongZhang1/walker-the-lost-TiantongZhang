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
**Scene at this revision:** `godot/effects/hit_burst.tscn`, commit `fb04465`
**Configuration test:** 80 checks, 0 failures

**Mechanical check, made before anyone looked at the picture** — pixels
differing from frame 8 inside a box around the trap: 48, 114, 130, 148, 182,
278 on frames 9, 10, 11, 12, 15, 20, then **0** on 30 and 50. The burst
fires, peaks near frame 20 and is gone by 30, as `CHANGE-BRIEF.md` §1.5
predicted. Particles appear on frame **9**, one ahead of the preview's own
counter; the strip is read from 10 as the brief says.

That is all a pixel count can say. It establishes that the effect *fires and
clears on time*, and nothing at all about whether it reads as grit.

**What I saw (running game, 1280 × 720).** Said in the session on 2026-11-07
rather than typed into this file; recorded here verbatim, with the English in
square brackets, because it is the author's line and not Claude's paraphrase:

> 扎出来的的时候我没看到碎石
> [when it stabs out I don't see any grit]

That was taken **before Effect A was wired into the game at all**. Step 2 built
the scene and the preview and deliberately stopped short of `main.tscn`, and
Claude told the author to look for the burst in play anyway — so the author was
sent to look for something that could not be there. Step 3 wired it. Looking
again, with the spawner in place:

> 效果没问题
> [the effect is fine]

So r0's verdict is **accepted as it stands**, and the revision below is a
deliberate push past "fine" rather than a repair.

**Claude's reading of r0.** The burst fires at the right place and clears on
time, and at frame 15 the grit does read as a cone. What it does **not** do is
own frame one. `CHANGE-BRIEF.md` §1.2 gives `Flash` the job of being "a few
large pale chunks at the lip, bright on the very first frame", and at
`scale_min/max` 1.6 / 2.4 the flash particles are the same size on screen as
the grit specks beside them. Frame 10 of `r0-strip.png` shows one
undifferentiated cluster of small pale dots; nothing in it is reading as a
chunk. The impact phase is present in the timing and absent in the picture.

---

## 2026-11-07 — Effect A, r1: `Flash.scale_min/scale_max` 1.6 / 2.4 → 5.0 / 7.0

**Strip:** `captures/hit_burst/r1/`, laid out in `captures/hit_burst/r1-strip.png`
**Side by side at the trigger frame:** `captures/hit_burst/r0-vs-r1-frame10.png`
**Scene at this revision:** `godot/effects/hit_burst.tscn`, `Flash` only
**Configuration test after the change:** 80 checks, 0 failures

Both strips are laid out by `scripts/build_effect_strip.py`, which was written
for this revision so that two revisions are cropped and scaled identically and
can be held against each other. `r0-strip.png` was regenerated with it from the
same committed frames in `captures/hit_burst/r0/`; the frames themselves are
untouched.

**The change.** One setting, on one emitter:

| | r0 | r1 |
|---|---|---|
| `Flash.scale_min` | 1.6 | **5.0** |
| `Flash.scale_max` | 2.4 | **7.0** |

Nothing else moved. `Grit` and `Dust` are byte-for-byte what they were, and
`Flash`'s `amount`, `lifetime`, `explosiveness`, velocities, `scale_curve`,
`color_ramp` and blend mode are unchanged. Approved by the author before it was
made ("批准，改吧" — go ahead and change it).

**Claude's prediction, written before the recapture:**

| Frame | Predicted |
|---|---|
| 10 | **Different** — visibly bigger chunks at the lip |
| 12 | **Different** — dimming and shrinking, but still the largest thing on screen |
| 15 | Identical — the flash is gone by here |
| 20 | Identical |
| 30 | Identical |
| 50 | Identical |

**What the recapture actually shows.** Pixels differing between the r0 and r1
frame of the same number, over the whole 1280 × 720 frame, no threshold:

| Frame | r0 vs r1 | Predicted | |
|---|---|---|---|
| 10 | **52 px differ**, largest channel delta 230 | different | ✅ |
| 12 | **0 px** — the two frames are identical | different | ❌ |
| 15 | 0 px | identical | ✅ |
| 20 | 0 px | identical | ✅ |
| 30 | 0 px | identical | ✅ |
| 50 | 0 px | identical | ✅ |

Five of six matched. **Frame 12 is where Claude was wrong**, and the miss is
not a rounding error: the prediction said the flash would still be the largest
thing on screen and the two frames are *bit-identical*.

**What explains it.** The deduction is tight, because `Flash` is the only thing
that changed and it is drawn **additively**: if a flash particle contributed any
light at frame 12, tripling its base scale would have to move at least one
pixel. Zero pixels moved, so **`Flash` contributes nothing at frame 12 in either
revision** — the whole visible difference lives on one frame.

The arithmetic says why its contribution is negligible by then. At 30 fps a
`lifetime` of 0.12 s is 3.6 frames, so by frame 12 a flash particle born at
frame 9 is about 83 % through its life, and §1.3 has two curves running at once
on it: `scale_curve` 1.0 → 0.2 puts it at ≈ 0.34 of its base, and the
`color_ramp`'s alpha 1 → 0 puts it at ≈ 0.17. 7.0 × 0.34 ≈ 2.4 px at alpha
0.17, additive, over a near-black floor — against r0's 2.4 × 0.34 ≈ 0.8 px at
the same alpha. Both round to nothing.

What the strip **cannot** settle is whether the particle is dead by frame 12 or
merely below the 1/255 quantization floor. Separating those needs a capture with
`Grit` and `Dust` silenced, which is a change to the effect scene and so belongs
to a revision of its own, not to this one.

**What this revision taught about the brief, not just the setting.** §1.5's six
frames — 10, 12, 15, 20, 30, 50 — were chosen to cover the burst's *phases*.
They turn out to be too sparse to see `Flash` at all: a 0.12 s emitter is alive
across roughly frames 9–12 and only **one** of the six lands inside that. Any
future revision that touches `Flash` should capture 9, 10, 11, 12 as well, or it
is tuning a thing it cannot see. This is a note about the evidence, not a
correction to the brief, so §1.5's frame list stands.

**Also seen, and deliberately not acted on.** In `r0-vs-r1-frame10.png` the
enlarged flash sits on the trap's **base**, not on the floor line at its lip.
§1.1 says the burst "originates at the floor line, which is where the spikes
punch through", and with `Flash` on a Point shape at `spread` 55° most of it
lands directly above the origin — on the trap body. That is a second candidate
change and it is not in this revision, because this loop moves one setting at a
time.

**My verdict (author, in the running game):**

> 留下
> [keep it]

**Kept.** `CHANGE-BRIEF.md` §1.3 is revised with a dated entry below the table
so the brief, the scene and `test_hit_burst_config.gd` all carry 5.0 / 7.0; the
test's expected value was updated in the same commit as the scene, which is what
keeps the read-back test honest in both directions.
