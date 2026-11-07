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

---

## 2026-11-07 — Effect B, r0, the first look

**Strip:** `captures/dungeon_motes/r0/`, laid out in `captures/dungeon_motes/r0-strip.png`
**F4 control:** `captures/dungeon_motes/f4-no-preprocess/`, laid out in `captures/dungeon_motes/f4-no-preprocess-strip.png`
**Scene at this revision:** `godot/effects/dungeon_motes.tscn`
**Configuration test:** 39 checks, 0 failures · **State test:** 19 checks, 0 failures

Both strips use the **room** view — the whole 640 × 360 viewport. Effect A's
strips are cropped to the trap because a 24 px burst would vanish in a
whole-room panel; Effect B is the room, and cropping it would hide whether the
field is even.

### The mechanical reading, made before anyone looked at the picture

A third capture was taken with the field switched off entirely
(`emitting = false`), so "full" and "empty" are absolute counts rather than
impressions. Mote pixels = pixels differing from that field-off baseline, with
the player's column band excluded. `room_backdrop.gd:28` records that nothing
in this backdrop moves, so the only thing that can differ between two runs of
the same frame is the field.

| frame | shipped, `preprocess = 8.0` | mutated to `preprocess = 0.0` |
|---|---|---|
| 1 | **578 px** | **12 px** |
| 10 | 558 | 44 |
| 40 | 567 | 108 |

**B1 is settled, and F4 is demonstrated.** The shipped effect is at full
density on the **first drawn frame** and stays flat. The same effect with one
number changed starts at 2 % of that and climbs at the rate one lifetime over
eight seconds predicts: 17 % of the way through the fill at frame 40, measured
108 / 578 = 19 %. This is the failure `CHANGE-BRIEF.md` F4 names and the reason
§2.1 chose `preprocess` as the feature Effect A does not use. No headless test
sees any of it.

**B2's tail, measured.** After the player dies at frame 100, mote pixels fall
412 → 400 → 409 → 315 → 288 → 191 → 144 → 76 → 49 → 16 → **0** at frames 100,
110, 130, 160, 190, 220, 250, 280, 310, 330, 340. Empty at exactly 8.0 s after
the stop, with no cut. §2.5 predicted frame 130 would be "thinner, not empty";
at 1 s it is **not yet measurably thinner** (409 against 412) and the fall only
begins around 2 s. See revision 6.0.3.

### Claude's reading of r0

**One clear defect: the field drifts through the floor.** 14 % of the visible
motes on frame 1, and **22 % by frame 40**, are six or more logical pixels
*inside* the floor slab, and the lowest mote reaches y = 266 — sixty-six pixels,
four metres at this game's scale, under solid rock.

The arithmetic was in §2.3 and nobody did it. The emission box is centred at
(320, 100) with extents (320, 100), so motes are born anywhere from y = 0 down
to **y = 200, which is the floor line itself**. A mote then falls at 2–6 px/s
plus `gravity` 2 px/s² for its whole 8 s life: 6 × 8 + ½ × 2 × 64 = **112 px**
of travel. One born near the floor ends up a hundred pixels below it. Nothing
stops it, because `visibility_rect` culls the node and does not clip particles,
and there is no collision on an ambience effect.

Two candidate fixes, one setting each, for whichever the author wants first:
raise the box so it stops above the lip, or cut the downward drift so a mote
cannot cross 200 px in its lifetime. **Neither is in this revision.**

**What reads well.** At 1 logical pixel each and α 0.35, the motes are specks
and not snow — §2.2's size call looks right. 39 % of them fall inside a torch
pool, which is where they are easiest to see, and the brief predicted the
opposite ("nearly nothing against a torch pool"). On the evidence the warm
colour against the lit stone is *more* visible, not less, but the difference is
small and this is a judgement, not a measurement.

**What I cannot tell you**, and what the capture cannot: whether 60 motes over
a 640 × 200 room reads as air or as an empty room with a few dots in it. That is
ten seconds of standing still in the running game, and it is the verdict.

**My verdict (author, in the running game).** Said in the session on
2026-11-07; recorded verbatim, with the English in square brackets:

> 看起来像是天上有浮灰往下掉，但没看出地板灰尘
> [it looks like dust falling from the sky, but I don't see any dust at the
> floor]

**Kept, and the field is doing its job.** The first clause is §2.1's goal in
the author's own words: the room has air in it. Effect B is not revised.

**Two things the verdict settles that the pixel count could not.**

1. **The motes inside the floor slab are not visible to a player.** 22 % of the
   field is under the rock and the author, told to look for it, did not see it.
   The defect is real and stays recorded here; it is **not** worth a revision,
   because the only instrument that can see it is a difference image. If a
   later change makes the field denser or brighter, this is the first thing to
   re-check.
2. **The gap the author did see is a different one.** Falling dust, no dust at
   ground level — nothing in this game is disturbed by the player moving
   through it. That is not a tuning change to Effect B; §2.1 chose ambience and
   ambience does not react. It is a third effect, and the author asked for it
   in the same breath: grit kicked up where the feet land.

**No r1 for Effect B.** The loop's output here is a verdict of *keep*, a
recorded defect that the verdict demotes, and a new piece of work.

---

## 2026-11-07 — Effect C, r0, the first look

**Strip:** `captures/step_dust/r0/`, laid out in `captures/step_dust/r0-strip.png`
**Scene at this revision:** `godot/effects/step_dust.tscn`
**Configuration test:** 63 checks, 0 failures
**State test:** 26 checks, 0 failures at **30, 60 and 144 fps**

The strip uses a third view, **feet** — 240 × 180 logical pixels around the
left of the room. The room view would hide a puff that is a few pixels tall,
and the trap view is looking at the wrong place.

### The mechanical reading, made before anyone looked at the picture

A control was captured with `stride_px` set to 9999 in the preview, so the
same run produces no strides at all and the difference is the dust and
nothing else.

| frame | dust pixels | of which **below the floor line** | brightest delta |
|---|---|---|---|
| 20 | 82 | 14 (17 %) | 111 |
| 26 | 130 | 21 (16 %) | 145 |
| 32 | 74 | 8 (11 %) | 108 |
| 50 | 98 | 12 (12 %) | 111 |
| 70 | 87 | 25 (29 %) | 145 |
| 95 | **0** | 0 | 0 |

Frame 95 at zero is C5 seen rather than asserted: thirteen frames after the
key is released, nothing is left.

### G3 is answered, and the answer is yes

§C.2 refused to assume that `scale.x = -1` mirrors the emission direction of a
`local_coords = false` emitter, and no test in this repository can see it.
Frame 32 (running right) throws the dust to the **left** of the character;
frame 70 (running left) throws it to the **right**. The mirror works on
4.7.2, and that is now a measured fact rather than a hope.

### Claude's reading of r0

**It is there, and it is too quiet to be the thing that was asked for.** The
author's words were 脚踩过的地方溅起来点灰尘 — dust *kicked up* where the feet
land. What the strip shows is a 2–3 pixel smudge at ankle height, at a
brightest delta of about 110–145 out of a possible 765. Beside Effect A's
burst, which peaks near 278 changed pixels in a much smaller box, this is a
quarter of the event and reads as a scuff rather than a kick.

The single setting with the most leverage is `Puff.scale_min/max`, currently
**1.6 / 2.8**. That is the same lever and the same diagnosis as Effect A's r1,
where `Flash` was the right idea at a size nobody could see.

**The second defect is the one Effect B already has: dust sinks into the
floor.** 11–29 % of the visible dust is under the lip. The cause here is
sharper than Effect B's and is in `step_dust_driver.gd` rather than in a
setting: C2 puts the spawn at the underside of the collision box, which is
**exactly** the floor line at y = 200, and `Kick` carries `gravity` 900. Any
speck whose initial velocity has a downward component is inside the rock on
the next frame.

**Two candidate changes, one setting each, for whichever the author wants
first:**

| | change | what it should do |
|---|---|---|
| r1a | `Puff.scale_min/max` 1.6 / 2.8 → **3.2 / 5.0** | the cloud becomes visible as a cloud; the trail reads at a glance |
| r1b | the spawn raised ~3 px above the floor line | the specks arc instead of sinking |

**Claude recommends r1a first**, because it is the thing the author actually
asked for and because r1b changes a derived number in a driver rather than a
setting in a scene, which is a bigger decision than a tuning step.

**My verdict (author, in the running game):**

> _TO FILL IN — run the game, hold D and run across the room, then jump.
> Is the dust something you notice without looking for it? Is the landing
> puff bigger than a stride's? r1a, r1b, both, or neither?_
