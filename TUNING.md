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


---

# Assignment 7 — the clips, one change at a time

Same five parts as above, same rule: **my verdict in the running game
decides.** Assignment 7 adds one more, because this assignment's strips can
be measured as well as read — a pixel difference between consecutive captured
frames is a fact, and it goes beside the reading rather than instead of it.

---

## 2026-11-18 — the swing, r0 → r1. There is no sword in the art.

### 1. What I saw, in the running game, before Claude read anything

> 跑步还行，但挥刀的时候根本看不见刀
>
> [the run is okay, but when swinging you can't see the sword at all]

Played at the project's window size with the game launched from the editor
binary: A/D to walk, space to jump, J to swing.

### 2. What the capture measures

`captures/swing/r0-strip.png`, and the per-frame difference
`tools/build_anim_strips.py` prints:

| capture frame | table frame | pixels changed |
|---|---|---|
| 10 | 0 | 1524 |
| 16 | 6 | 1376 |
| 22 | 12 | 1376 |
| 28 | 18 | 1524 |
| every other frame | — | **0** |

Two things that are facts rather than opinions. `UPDATE_DISCRETE` holds in a
real render: nothing changes between keys. And **the active window closing
changes no pixel at all** — table frame 10 is identical to table frame 6,
because a hitbox is invisible. The strip cannot show that boundary, which is
why `test_swing_edges.gd` asserts it instead.

### 3. Claude's reading, and where it was wrong

`CHANGE-BRIEF.md` revision 7.0.1 §6 said, in Claude's words:

> the character's own art already carries a weapon in `p6-windup` and
> `p7-live`, and adding a second one on a pivot would have drawn two.

**That is false, and the author's playtest is what caught it.** Looking at
the two cells enlarged, with the light-grey pixels counted:

| cell | light-grey px | what it actually is |
|---|---|---|
| 1 idle | 78 | boots, forearm |
| 5 windup | 113 | a **raised arm** behind the head — no blade |
| 6 live | 98 | an extended arm, legs apart — **no blade** |

These are `walker-ninja`'s poses. That game's character fought **unarmed**;
windup and live are martial-arts poses. Nothing in them is a sword, and a
difference of 381 and 369 pixels against idle is a difference in *stance*,
not in weapon.

The `SwordArm` / `Blade` rig existed in the original §2.2 and revision 7.0.1
**deleted it on this false premise.** It comes back.

### 4. The change

One thing: **restore the blade as a cutout rig part under `Rig`.**

- `Rig/SwordArm`, a `Node2D` pivot at the shoulder, so `Rig.scale.x` flips it
  with the character.
- `Rig/SwordArm/Blade`, a `Sprite2D` whose hilt sits on the pivot.
- The blade is drawn by `tools/make_sprites.py` **in the character's own
  palette** — `#9AA7BD` and `#5E6472`, the two greys already in every pose —
  so it reads as the same character's steel and not as a pasted-on object.
- `swing` gains two tracks: `SwordArm:rotation_degrees`, continuous, sweeping
  the arc the original §6 table specified; and `SwordArm/Blade:visible`,
  discrete. Every other clip and `RESET` hide it.

**No pose is edited.** The art stays exactly what GPT-6 produced; the blade is
a separate sprite on a separate node, which is what a cutout rig is for.

### 5. Claude's prediction for r1, written before the recapture

- The per-frame difference at table frames 0, 6, 12 and 18 will **grow**,
  because the blade's rotation now changes the picture on those frames too.
- Frames that changed by **0** will stop being 0: the rotation track is
  continuous, so the blade moves on *every* frame between keys even though
  the body cell does not. That is the clearest single piece of evidence that
  a rig clip and a frame clip are different mechanisms.
- The active window closing will **still** change nothing attributable to the
  hitbox, because a hitbox is still invisible. If the strip starts showing
  that boundary, something other than the hitbox moved.

### 6. What r1 measured, against the prediction

`captures/swing/r1-strip.png`, same frames, same band, same tool.

| | r0 | r1 |
|---|---|---|
| frames identical to the one before | **19 of 24** | **4 of 24** |
| range of the non-zero changes | 1376 – 1524 px | **126 – 1568 px** |
| change at table 0 / 6 / 12 / 18 | 1524 / 1376 / 1376 / 1524 | **1562 / 1394 / 1451 / 1568** |

All three predictions held:

- the four named frames grew, because the blade now changes on them too;
- **the frames that changed by 0 stopped being 0.** The rotation track is
  continuous, so the blade moves on every frame between keys even though the
  body cell does not. That is the single clearest piece of evidence in this
  assignment that a rig clip and a frame clip are different mechanisms, and
  it came out of a measurement rather than a description;
- the active window closing still shows nothing attributable to the hitbox.
  Frame 20 does change in r1 — by 280 px — but that is the blade passing
  through, not the window shutting. A hitbox contributes zero pixels whether
  it is open or shut.

**Two pieces of stale text were caught by this revision**, both of the same
kind as the hard-coded check count in `test_input_map.gd`:

- the strip tool printed "every other frame is identical to the one before
  it", which was true of r0 and false of r1. It counts the frames now.
- the strip's own caption on table 10 said "SAME PIXELS as table 6", true of
  r0 and false of r1. The captions describe the **table**, not one capture.

### 7. My verdict in the running game

Played at the project's window size, 2026-11-18, J to swing. Recorded
verbatim, English in square brackets:

> 刀不太对，他不是挥出去的，而是在身子上面转圈
>
> [the sword isn't right — it isn't swinging out, it's spinning in circles
> above the body]

**Half kept.** The blade is there and it is visible, which is what r1 was for,
so the restoration stands. Where it goes is wrong, and that is r2 below.

---

## 2026-11-18 — the swing, r1 → r2. A swing goes one way. A windmill goes round.

### 1. What I saw, in the running game, before Claude read anything

> 刀不太对，他不是挥出去的，而是在身子上面转圈
>
> [the sword isn't right — it isn't swinging out, it's spinning in circles
> above the body]

### 2. Claude's reading — and this time the author was right before the capture was taken

**No strip was needed to confirm this one**, and that is the finding. The
original `CHANGE-BRIEF.md` §6 rotation table, written on 2026-11-16 and
restored verbatim by r1, says it outright once the arithmetic is done. The
pivot is at (3, −2) in rig coordinates; the blade is 16 px long; the figure is
32 px tall with its waist at y = 0 and its feet at y = +13.

| r1 frame | deg | blade tip | |
|---|---|---|---|
| 0 | +20 | (+8.5, **−17.0**) | above the top of the sprite |
| 6 | −80 | (−12.8, −4.8) | horizontal, behind |
| 10 | +85 | (+18.9, −3.4) | horizontal, in front |
| 12 | +75 | (+18.5, −6.1) | |
| 18 | +20 | (+8.5, **−17.0**) | back above the head |

1. **The tip never goes below y = −3.** All 18 frames are in the top half.
   "Above the body" is the *range of the function*, not an impression.
2. **The arc reverses direction twice**: +20 → −80 anticlockwise, −80 → +85
   clockwise, +85 → +20 anticlockwise. Total path **330° in 0.600 s = 550°/s**,
   every degree of it watched. Two reversals about an overhead pivot is a
   windmill. 转圈 is the correct word, not an exaggeration.

The r1 entry above congratulated itself on a measurement — *"the clearest
evidence in this assignment that a rig clip and a frame clip are different
mechanisms"* — and it was a true measurement of the wrong thing. It proved
the blade moved every frame. It never asked **where**.

### 3. The change

Two rules, and the keys that follow from them. `CHANGE-BRIEF.md` revision
7.0.2 §3–§4 is the table; this is the reasoning.

> **R1. While the blade is visible the arc travels one way.**
> **R2. It finishes below the hand** (past ±90°, out of the top half).

A swing is a commitment in one direction. Something that goes out and comes
back along its own path is a wave; if the pivot is overhead, it is a propeller.
The return to rest still has to happen — so it happens **sheathed**, which is
also what a person with a sword does.

| | r1 | r2 |
|---|---|---|
| rest | **+20** (blade above the head) | **−150** (point down, behind the heel) |
| cocked, frame 6 | −80 | **−50** |
| struck, frame 10 | +85 (horizontal) | **+100** (forward and **low**) |
| settle, frame 12 | +75 (rising again) | **+115** (lower still) |
| blade visible | frames **0–18**, all of it | frames **2–13** |
| visible travel | 330°, **2 reversals** | **223°, 0 reversals** |
| return to rest | watched | **sheathed**, 268° |
| tip's lowest y | **−3.4** | **+5.5**, below the waist |

The strike itself — frame 6 to frame 10 — is **150° in 0.133 s = 1127°/s**,
five times the wind-up's speed. The active window is now the fastest thing on
the timeline, which is what makes it read as a strike rather than a gesture.
No timing moved: the phase table, the hitbox keys and the clock argument are
untouched.

### 4. The part that is uncomfortable, and is recorded rather than smoothed over

Both rules are now **headless read-back assertions** in
`test_swing_clip.gd` — and both of them fail r1's angles. Pasting r1's values
back onto r2's key times:

```
FAIL  the VISIBLE arc never reverses direction   [legs: -60 -40 +165 -10 -15 ]
FAIL  the last visible angle is past horizontal  [60.0 deg]
```

**9 failures, 67 checks.** So the defect the author found by playing was
sitting in the key table the whole time, fully visible to a headless run, and
**no test was asking.** The lesson is not "write more tests". It is that a
read-back only ever sees the questions it was written to ask, and in this
project the questions keep coming from someone playing the game. That is the
same shape as A6's containment check and the same shape as r1 itself.

`test_player_clips.gd`'s blade check changed **shape**, not value: "swing's
first key is `true`" would now fail a correct clip, because r2's blade starts
sheathed. It asserts the invariant instead — no other clip ever shows the
blade, `swing` shows it at some point, `swing` ends hidden. A check written
against one revision's values is the same stale-summary failure as
`test_input_map.gd`'s hard-coded count.

### 5. Claude's prediction for r2, written before the recapture

- **Table frame 0 will change by LESS than r1's 1562 px.** At rest the blade
  is hidden, so capture frame 10 shows the body cell alone — closer to r0's
  1524 than to r1's 1562.
- **Frames 12 and 13 will differ from each other by a large amount** — the
  blade is sheathed between them, so a 16 px sprite disappears in one frame.
  Predicted: the largest single-frame change in the visible span.
- **Frames 14–18 will be identical to one another and to r0's** — the body
  cell holds and the blade is gone, so nothing is left to move. Predicted
  **0 px** on every one of them, where r1 had motion on all of them.
- The active window closing still shows nothing attributable to the hitbox.

### 6. What r2 measured, against the prediction

`captures/swing/r2-strip.png`, same frames, same band, same tool.

| | r0 | r1 | **r2** |
|---|---|---|---|
| frames identical to the one before | 19 of 24 | 4 of 24 | **9 of 24** |
| range of the non-zero changes | 1376–1524 | 126–1568 | **117–1524** |
| table 0 / 6 / 12 / 18 | 1524 / 1376 / 1376 / 1524 | 1562 / 1394 / 1451 / 1568 | **1524 / 1496 / 1424 / 1524** |

The middle row of the first column is derivable and holds: in r1 the blade
was visible for all 18 frames, so the continuous track moved the picture on
every one of them and only 4 frames held. In r2 it is visible for 11, so the
7 sheathed frames hold as well as the frame track's own. 19 → 4 → 9.

**Prediction 1 — table 0 changes by less than r1's 1562: ✅ 1524**, which is
r0's number exactly. At rest the blade is hidden, so capture frame 10 is the
body cell alone, which is the state r0 was in for the whole clip.

**Prediction 3 — table 14–17 are identical: ✅ 0 px on all four.** r1 had
motion on every one of them. **But the prediction said "14–18" and table 18
changed by 1524**, which it was always going to: `Rig/Body:frame` steps to
cell 1 at 0.600. Half right, and the wrong half was carelessness rather than
a wrong model — the body cell's own key was in the table being predicted
from. ❌

**Prediction 4 — the active window closing still shows nothing attributable
to the hitbox: ✅.** Table 10 changes by 280 px and all of it is the blade
mid-arc.

### Prediction 2 was wrong, and it is the useful one

> frames 12 and 13 will differ by a large amount — the blade is sheathed
> between them, so a 16 px sprite disappears in one frame. Predicted: the
> largest single-frame change in the visible span.

**Measured: 154 px, one of the smallest in the span.** And its mirror image,
the blade *appearing* at table 2, is **146 px**. Those two numbers are a
direct measurement of how much of the screen this blade occupies:

| Event | Captured pixels changed |
|---|---|
| the blade appears (table 2) | **146** |
| the blade vanishes (table 13) | **154** |
| the body cell steps (tables 0, 6, 12, 18) | **1424–1524** |
| the blade moving mid-arc (tables 7–11) | 165–295 |

**A 3 × 16 blade is about one tenth of the event that a 32 × 32 body cell
change is.** It is the right shape now and it is small, and those are
separate questions — exactly the split that A6's Effect A r1 ran into, where
`Flash` was the right idea at a size nobody could see. Whether 150 px is
enough to read at this window size is **not** something this table can
answer; §7 is where that is decided.

The prediction was wrong because it compared the blade to itself instead of
to what else is on screen. That is the same error as r1's: a measurement of
the right quantity, asked without reference to the rest of the picture.

### 7. My verdict in the running game

Played 2026-11-18. Recorded verbatim, English in square brackets:

> 刀没挥出区，已刀把为中心在旋转，而且旋转的中心点在人物背部，我觉得应该在前面
>
> [the sword isn't swinging out, it's rotating about the hilt, and the centre
> of rotation is at the character's **back** — I think it should be in front]

**Rejected, and the diagnosis is the author's, not Claude's.** r2 fixed which
way the arc travelled and left the pivot where r1 put it. The author did not
say "it still looks wrong"; they said **where** it was wrong and **where it
should be**, and a column profile of the sheet says they were right to the
pixel. r3 is below.

---

## 2026-11-18 — the swing, r2 → r3. The pivot was on the character's spine.

### 1. What I saw, in the running game, before Claude read anything

> 刀没挥出去，已刀把为中心在旋转，而且旋转的中心点在人物背部，我觉得应该在前面
>
> [the sword isn't swinging out, it's rotating about the hilt, and the centre
> of rotation is at the character's **back** — I think it should be in front]

**This is not "it still looks wrong".** It names the defect and it names the
fix, and both are correct. It is the third revision in a row where the author
playing the game found something no test in this repository was asking about,
and the first where the author supplied the diagnosis as well.

### 2. The measurement — and the number r2 used was the wrong number

`tools/check_sword_reach.py` was written for this revision. It takes a
**column profile** of sheet cell 6 (`p7-live`): solid pixels per column, with
the scarf's purple ramp excluded, over the committed sheet.

```
  columns with >= 20 solid px run +3 .. +13
  so the torso's BACK edge is x = +3 and its FRONT edge x = +13
```

**The pivot was at x = +3.** The back edge, to the pixel.

How it got there: r2 reasoned from the cells' **ink bounding box**, which
starts at x = −11 and gives a centre of about +2. But x = −11 is the
**scarf**, streaming out behind a figure that faces right. A bounding box
containing a trailing scarf has its centre dragged backwards, so +3 read as
"the middle of the torso" on paper and sat on the character's spine in the
game.

That is the same shape as r1's error and as r2's wrong prediction: **a
correctly computed measurement of the wrong quantity.** Three times now. The
pattern is not carelessness with arithmetic; it is choosing what to measure
without asking what the eye is actually looking at.

### 3. Why r2's fix could not have worked, as geometry

The blade is 16 px; the torso is 10 px wide. **With the hilt fixed anywhere
inside the silhouette, the blade's near end never moves** and the far end
traces a circle centred on the character. That is a clock hand. Changing
which *direction* it turns does not change what it is — which is exactly why
the author's second report sounded like the first. r2's two rules were
necessary and not sufficient, and the brief said they were sufficient.

### 4. The change

**`Rig/SwordArm:position` becomes a keyed track.** The pivot stops being a
constant in the scene and becomes part of the animation. Rotation keys,
phase boundaries, hitbox keys and clocks are all untouched.

| | r2 | r3 |
|---|---|---|
| pivot at full cock (frame 6) | (3, −2), fixed | **(3, −5)** — behind the shoulder |
| pivot at the blow (frame 10) | (3, −2), fixed | **(13, +1)** — at the front edge |
| pivot at rest | (3, −2) | **(0, +2)** — sheathed at the hip |
| hilt travel, active window | **0 px** | **10 px forward** |
| tip travel, active window | 28 px | **38 px**, across a 10 px figure |
| tip's final x | +18.8 | **+28.8**, clear of the front edge (+13) |

### 5. The rule, and the two things it makes checkable

> **R3. The hilt is behind the torso's back edge at full cock, out in front
> of it on the last active frame, and travels at least 8 px between them.**

`test_swing_clip.gd` asserts R3 and two consequences: the tip's horizontal
sweep must exceed the figure's own width, and the tip must finish **outside**
the front edge. **All three are computed from `position` and
`rotation_degrees` together** — neither track alone can answer any of them.
That is the sharpest thing this assignment has produced about what a cutout
rig is for: a frame track has one number per frame, and no pair of numbers to
reason about.

`TORSO_BACK` and `TORSO_FRONT` are no longer typed in. `check_sword_reach.py`
asserts them against the sheet on every run, and **it caught `TORSO_FRONT`
wrong the first time it was run** — 15 had been taken from the sparse ink
edge; the dense mass ends at 13.

### 6. What r3 measured

`captures/swing/r3-strip.png`, same frames, same band, same tool.

| | r1 | r2 | **r3** |
|---|---|---|---|
| frames identical to the one before | 4 of 24 | 9 of 24 | **9 of 24** |
| range of the non-zero changes | 126–1568 | 117–1524 | **147–1576** |
| mid-arc frames (tables 7–11) | 165–295 | 165–295 | **279–315** |

The held-frame count is unchanged at 9, as it had to be: `Blade:visible` did
not move, so the same seven frames are sheathed. **The mid-arc frames all
grew**, which is the position track showing up — the blade is now translating
as well as rotating, so more of the picture changes per frame even though the
angles are identical to r2's.

**The strip is not the evidence for this revision.** A pixel count cannot
distinguish "the blade swept past the body" from "the blade swept through
it"; both change the same number of pixels. The evidence that r3 fixes what
the author reported is the geometry in section 4, asserted in section 5, and
then the author's eye. That is section 9 of the brief working as intended
rather than as a formality.

### 7. My verdict in the running game

Played 2026-11-18. Recorded verbatim, English in square brackets:

> 挥出去了，现在可以了
>
> [it swings out now — this is fine]

**Kept.** The swing closes here: r0 → r1 → r2 → r3, every step of it
started by the author playing the game and none of it by a test going red.

### What the three revisions cost, and what they bought

| | what the author said | what was actually wrong | what no test was asking |
|---|---|---|---|
| r0 → r1 | can't see the sword | there was no sword — the poses are unarmed | whether the art contained what the brief claimed |
| r1 → r2 | it spins above the body | the arc reversed twice about an overhead pivot | which **way** the arc travelled, and how **low** it got |
| r2 → r3 | the centre of rotation is at the back | the pivot sat on the torso's back edge, x = +3 | **where the pivot was at all** |

Three revisions, three defects, **zero of them found by a read-back** — and
all three were fully visible to one, headlessly, in the key table and the
sheet, before the game was ever launched. They are all asserted now, and
every assertion was written **after** a person said what they saw.

That is the finding this assignment actually produced, and it is not "write
more tests". A read-back sees only the questions it was written to ask. The
questions came from playing.

---

## 2026-11-18 — the swing, r3 → r4. A longer blade, and one number with three homes.

### 1. What I asked for, in the running game

> 刀再长一点，然后把跳跃改成空格键
>
> [make the sword a bit longer, and change jump to the spacebar]

### 2. The change

`SWORD_LEN` 16 → **20**, cutting edge 11 → 15 px, `Blade.offset` (0, −8) →
(0, −10). Nothing else: no key, no timing, no phase boundary, no rule.

There is no measurement behind this one and there should not be. How long a
sword should look is a judgement, and `CHANGE-BRIEF.md` §9 puts judgements
about how a thing *reads* with the author. The arithmetic only says what the
judgement costs:

| Across the active window | r3 (16 px) | r4 (20 px) |
|---|---|---|
| hilt travels forward | 10 px | **10 px** — unchanged; it is the pivot |
| tip travels horizontally | 38 px | **45 px**, across a 10 px figure |
| tip finishes at x | +28.8 | **+32.7**, front edge is +13 |

**r4 cannot have fixed r3's defect and was not asked to.** The three rules
r2 and r3 shipped all still pass, by a wider margin, because a longer blade
reaches further from the same pivot. Saying so matters: a revision that
happens to widen a margin is not evidence that the margin was the problem.

### 3. What the recapture measured

`captures/swing/r4-strip.png`, same frames, same band, same tool.

| | r3 (16 px) | r4 (20 px) |
|---|---|---|
| frames identical to the one before | 9 of 24 | **9 of 24** |
| the blade appearing (table 2) | 147 | **195** |
| the blade vanishing (table 13) | 157 | **204** |
| mid-arc frames (tables 7–11) | 279–315 | **375–412** |
| the body cell stepping (tables 0, 6, 12, 18) | 1524 / 1672 / 1648 / 1524 | same ±0 at 0 and 18 |

The blade-only frames grew by about **30 %**, which is what a 25 % longer
sprite sweeping a wider arc should do, and the held-frame count did not move
at all, because `Blade:visible` did not. Tables 0 and 18 are **1524 in r1,
r2, r3 and r4** — the blade is sheathed on both, so its length cannot show
there. A number that refuses to move when an unrelated thing changes is worth
as much as one that moves.

### 4. One number had three homes, and nothing compared them

16 was written in `tools/make_sprites.py`, in `player.tscn`'s `Blade.offset`,
and in `test_swing_clip.gd`'s `BLADE_PX` — which every tip-reach assertion is
computed from. Change one and the other two go on being wrong quietly: the
test would compute the tip of a 16 px blade on a 20 px sprite and report
PASS.

`SWORD_LEN` is the source now, and `tools/check_sword_reach.py` asserts the
PNG's height, the scene's `offset` (which must be **−LEN / 2**, or the blade
pivots about its own middle — r1's failure arriving by another door), and
`BLADE_PX`, every run.

This is the fourth instance of the same fault in this assignment:
`test_input_map.gd`'s hard-coded count, the strip tool's fixed sentence, the
caption that described one capture, and now a length in three places.

### 5. The jump binding — not changed, because it was already right

Space already pressed jump, along with W and UP, and has since before this
assignment. Nothing moved.

**But `test_input_map.gd` only asserted that the action EXISTS.** An action
can exist carrying the wrong key, or no key, and all seven of its checks
would still be green — so "it already is" was a claim about a file, not a
measurement. The three keys are pressed and released now through
`Input.parse_input_event`. 7 checks → **13**.

Where the spacebar genuinely does nothing is the 0.600 s of a swing:
`player.gd:71` returns from `_physics_process` while `is_locked()`, before
the jump branch at `:83`. That is §7's interrupt table and `GDD.md:198` in
code, and `test_swing_edges.gd` asserts it. If space felt dead in play, that
is the likeliest reason and it is the design.

### 6. My verdict in the running game

Played 2026-11-18. Recorded verbatim, English in square brackets:

> 刀长度可以了
>
> [the blade's length is fine now]

**Kept.** `SWORD_LEN` stays at 20.

---

## 2026-11-18 — the swing, r4 → r5. In the air, and a gate nothing was guarding.

### 1. What I asked for, in the running game

> 刀长度可以了，让角色在空中也能挥刀
>
> [the blade's length is fine now — let the character swing in the air too]

The first clause closes r4. **Kept**: `SWORD_LEN` stays at 20.

### 2. The change

A design change, not a tuning one, so `CHANGE-BRIEF.md` revision 7.0.5 holds
the table and §7's `SWING` entry condition is superseded. `is_on_floor()` is
deleted from the attack gate and from the buffered restart; in exchange two
*new* `is_on_floor()` tests appear, around the planting:

> **A commitment locks out INPUT, not physics.**

On the ground the swing plants — `velocity.x` held at 0 every tick, so you
cannot slide into or out of your own attack. In the air there is nothing to
plant against, and zeroing `x` would stop the jump arc dead and drop the
character straight down. The jump's horizontal velocity is carried and no
key changes it. The guard is re-tested every tick rather than remembered, so
**landing mid-swing plants on the frame the floor is found**.

`player_anim.gd` did not change. `_clip_for_state()` already ranked
`is_locked()` above the airborne branch, so `swing` beat `rising`/`falling`
from the first air swing. That was written for the ground case and happens
to be right here — which is luck until a test says it, so a test says it.

### 3. The finding: nothing was guarding the gate

**No test in this repository ever pressed `attack` in the air.** Not the
nine interrupt cases, not the frame-by-frame trace of the whole window, not
the structure test, not the pin. `is_on_floor()` could have been deleted by
accident on any day of this assignment and all 23 checks would have stayed
green.

That is the same shape as everything else A7 has turned up, with one
difference worth naming: the earlier three were **wrong things that no test
asked about**. This one was a **right thing that no test held in place** — a
rule the brief stated, the code obeyed, and nothing defended. Both are the
same gap seen from opposite sides.

### 4. What is asserted now

Eleven new checks in `test_swing_edges.gd`, 23 → **34**, both sides of the
rule:

| | measured |
|---|---|
| attack in the air starts a swing | `swing_count` +1 while `is_on_floor()` is false |
| the lock is on in the air | yes |
| `swing` beats `rising`/`falling` | `current_animation == "swing"` |
| the jump's x velocity is carried | **96.0 px/s, unchanged for the whole lock** |
| holding the opposite direction | does **not** turn it around |
| gravity still runs | `velocity.y` rises every frame |
| jump during an air swing | ignored: y went 10.0 → 25.0, which is gravity, not −260 |
| the air swing ends on its own | 24 further physics frames |
| a ground swing still plants | `velocity.x` exactly 0.000 |

One check exists only to keep another honest — *"it was moving, so
'carried' is not trivially true"* — because an assertion that the velocity
is unchanged passes beautifully when the velocity is zero. That is the
fourth time in this assignment a check has needed a check.

### 5. Found, not fixed, not new

`test_swing_edges.gd` and `test_player_states.gd` both print `ObjectDB
instances were leaked` and `resources still in use at exit`. **Pre-existing**:
`test_swing_edges.gd` at the previous commit, before any of this, printed 4
and 2; it now prints 8 and 4, scaling with how much of the scene the run
exercises. `scripts/run-test.sh` deliberately does not fail on either line —
its rule 4b lists `SHADER ERROR`, `SCRIPT ERROR` and `Failed loading
resource`, and these are neither. Recorded rather than chased: it is a
`SceneTree` test tearing down a scene at `quit()`, it predates A7, and
fixing it is not this assignment.

### 6. My verdict in the running game

_To be written by the author after playing r5._
