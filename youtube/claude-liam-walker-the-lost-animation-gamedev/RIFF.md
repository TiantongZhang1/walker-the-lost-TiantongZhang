# RIFF.md — the commentary, and what it is riffing on

The riff register for this film is Teardown: explain the mechanism while the
line that implements it is on screen, and never riff on imagined play. Every
aside below is anchored to something inspected — a file, a log row, a measured
frame, a dated entry in `TUNING.md` — and the anchor is named.

---

## The through-line

**A read-back only sees the questions it was written to ask.**

Assignment 6's film ended on *a green check is not a measurement*. This one is
the next sentence along, and it is less comfortable, because it is not about
checks being weak. The checks in this assignment are strong: 280 of them,
seven mutations, every mutation naming the assertion that has to fire. They
were strong and they were green and **the defects were in the data the whole
time.**

Three revisions in this assignment — 7.0.2, 7.0.3, 7.0.7 — fixed things that
a headless run could have printed before the game was ever launched. The
blade's tip is never below −3 px in any of the eighteen frames: that is the
range of a function over a key table, not an impression. The pivot was at
x +3 and the torso runs +3..+13: that is a column profile. The planted foot
was 3.3 px through the floor while the assertion about that foot was green,
because the band it was compared against had been measured with a library that
rotates the opposite way from the engine.

**None of those is a test being bad at its job. Each is a question nobody
asked.** And every one of the questions arrived the same way: the author
played the game and said something was wrong.

## Where the riff lands, beat by beat

**B01, the correction.** The hesitant writer strikes out one word and replaces
it. *Found* becomes *reported*. That is the whole film in one edit: nothing in
this assignment was *found* by the apparatus, it was **reported** by a person,
and the apparatus's job turned out to be turning a report into a rule that
cannot quietly come back. Anchored on `TUNING.md`'s ten dated entries, each
of which opens with the author's own words in their own language.

**B02, the derived number.** The riff is that `length = 0.5` is not a taste
decision and could not be. Two strides at 24 px against 96 px/s. The honest
consequence is stated in the same breath: if the cycle is ever retimed, *this
arithmetic* changes first and the keys follow — never the other way round.
Anchored on `legs.tres:24` and `main.tscn`'s `stride_px`.

**B03, the dust.** The riff is that the dust was not built for this film and
is the only thing on screen that can *show* an agreement which is arithmetic
everywhere else. Anchored on A6's `step_dust_driver.gd`, unchanged, and on
`COMPONENTS.md`'s argument for why it is a component here.

**B04, the window that is not a drawing.** The riff is that the one track in
this clip that gameplay actually reads is the one with no picture attached.
`Hitbox:monitoring`, discrete, on the clip's own timeline. Anchored on the
course notes' own sentence — *a gameplay fact like "the hitbox is live" should
not depend on a tween that can be killed halfway* — and on the trap's
`FIRE_SECONDS = 0.18` against the swing's 0.133.

**B05, what the footage cannot show.** The riff is said out loud on the card
rather than left as a gap: *the hitbox window is NOT visible in this footage.*
A hitbox contributes no pixels. The beat that follows a swing with four
visible phases has to admit that the thing it just claimed is not in the
picture. Anchored on `frame_animation_footage.py`'s own footer text.

**B06, the sentence that cost a day.** The riff is the shape of the mistake
rather than the mistake. Revision 7.0.6 §4 wrote down that fixing the sliding
swing *would mean an `AnimationTree`*, the author accepted it as a cost, and
it was quoted back for a day as settled. It was never measured. **A limitation
accepted on an unexamined claim looks exactly like a measurement once it is in
a table.** Anchored on revision 7.0.6 §4 and revision 7.0.9 §2, which quotes
its own earlier sentence before refuting it.

**B07, the third check.** The riff is on why three checks and not two. *LegAnim
writes the legs* is satisfied by a scene where **both** players write them,
which is precisely the failure the rule exists to stop. A partition checked
one way round is only a subset. Anchored on the mutation: put one leg track
back on the body player and two of the three go red.

**B08, a prediction that was wrong in sign.** The riff is on the tag. The
brief marked its own clock prediction `[proposal]` — *derived by Claude and
not yet confirmed* — and that tag is the reason a measurement got built
instead of a sentence getting believed. The prediction was wrong. The claim
underneath it survived. Both are in the file. Anchored on `CHANGE-BRIEF.md`
§8 and revision 7.0.8, which is a correction written as a correction.

**B09, what a deterministic run cannot replicate.** The riff is that
`--fixed-fps` makes every run of this measurement identical, so **running it
three times is one measurement printed three times.** The file prints that
sentence itself. Anchored on `measure_clocks.gd`'s own output and on
`scripts/run-test.sh`.

**B10, one sentence, two claims.** The riff is grammatical and it matters:
*jump while swinging, without interrupting the swing* contains a claim about
the jump and a claim about the swing, and they need different evidence. The
second one cannot be checked by looking at the jump at all. Anchored on the
author's message of 2026-11-20 and on `player.gd:111-118`.

**B12, proving a negative.** The riff is on mutation M7, and specifically on
what **stayed green** under it. A suite that only asserted "the jump works"
would be fully green on a build where every press restarted the swing.
Anchored on `evidence/a7/mutations.txt`, which also records the one blind spot
the new checks still have — a comparison that passed under the mutation
because the trace ran out of frames before the evidence would have appeared.

**B13, the picture as the argument.** The riff is that this is the rare beat
where a picture *is* proof: two frames at the same playhead, one grounded and
one airborne, found by searching the take's log rather than chosen by eye. If
the jump had touched the clip, the two poses would differ. Anchored on
`evidence/a7/same-swing-twice.txt`.

**B14, the honest version of the thesis.** The riff resists its own best line.
The tempting claim is *everything was missed*. The table refuses it: three of
the ten were design calls where the game was not wrong, two were judgements
about how a thing looks with no fact to check, one was found by an instrument.
**Three** say read-back, and those three are the subject. A film that counted
a design change as an instrument failure would be doing the thing it is
complaining about.

**B15, the limits.** The riff is that the hitbox can hit nothing — this room
has no enemy — and that this is stated as a limit rather than left for a
reviewer to discover. The window is real, measured and tested; what it would
*do* is a later assignment.

**B16, your turn.** The riff is the one transferable thing: go and check a
sentence in your own notes that says something is impossible. Not rewrite it.
Check it.

---

## Riffs that were cut, and why

**"The tests were useless."** Not true and not said. 280 checks caught real
things — a frame key outside the sheet, a track path that resolved to nothing,
a clip left on Godot 3's boolean `loop`, a second swing silently swallowed.
The claim is narrower and harder: the checks did not ask about the blade's
range, the pivot's column, or the band's sign.

**"Play-testing beats automated testing."** Also not said. Nine of ten
revisions came from play, and *none* of them would have survived contact with
the next change without a read-back written to hold it. The loop is the point,
not either half.

**"Claude got it wrong and the human fixed it."** Too flattering to both. The
windmill was built from a key table in the brief that the author approved; the
pivot was derived from a bounding box that was computed correctly; the band
was measured by a script, rendered, and believed. **Every one of those was a
true measurement of the wrong quantity**, which is a failure mode that does
not care who is making it.
