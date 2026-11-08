# RIFF.md — the commentary, and what it is riffing on

The riff register for this film is Teardown: explain the mechanism while the
line that implements it is on screen, and never riff on imagined play. Every
aside below is anchored to something inspected — a file, a log row, a measured
frame — and the anchor is named.

---

## The through-line

**A green check is not a measurement, and a picture is not a proof.** Every
beat in this film is an instance of one of those two.

The assignment's own split says it first: a headless run proves the effects
are configured as the brief says and that they fire and stop on the right game
states, and proves nothing about what the screen shows. This project kept
finding the sharper version of that — a check that passed having measured
nothing, and a capture that showed something true about the wrong file.

## Where the riff lands, beat by beat

**B02, the event.** The riff is on what the spawner *does not* do. The obvious
build is one node and `emitting = true`, and it is wrong in a way that never
errors. Anchored on `hit_burst_spawner.gd`'s docstring, which says it in the
file rather than only in a document.

**B03A, the ceiling.** The riff is that the brief's own ceiling is a number
the game cannot reach, and that the honest response was to label the take
rather than to quietly show it as play. Anchored on revision 6.0.2 and on take
p's measured peak of 1. The brief got this wrong first — it reasoned from the
trap's state machine to "three traps, so three bursts" without ever dividing
112 by 96 — and the revision says so in those words.

**B04, the three parts.** The riff is that the three steps are not an
abstraction: one node shows emission on itself, process behind a reference,
and draw in a different material entirely. The file keeps them apart and the
Inspector does not.

**B05, the prediction.** The riff is on the miss, not the hits. Five of six is
a good score and the sixth is the interesting one, because the two frames came
back *bit-identical* — which is a stronger statement than "roughly the same"
and a weaker one than "the particle is dead". `TUNING.md` holds that
distinction open rather than closing it, because the capture that would close
it is a change to the effect scene and belongs to a revision of its own.

**B07, the mutation.** The riff is that F4's failure mode is invisible to
everything except a picture. Nothing errors. The configuration test passes.
The room just starts empty, every single load, forever.

**B07A/B07B, the condition.** The riff is on *stopping is not clearing* — the
one design decision in Effect B that a viewer can feel. An effect that cleared
on death would read as the renderer dying with the player.

**B08/B09, the shader.** The riff is that a curve in the Inspector is a
texture, and that the two lines which prove it only exist when the material
has one. The empty-material conversion is the anchor: Claude pronounced that
file fine on three true checks, and it was the wrong file.

**B10, the derived event.** The riff is on the `while` and the back-date —
two details that look like fussiness and are the difference between a cadence
and a frame rate. Anchored on the measured 3.2 px at 30 fps before the fix.

**B11A/B11B, the price.** The riff is the one this film would keep if it could
keep only one: *read the table the right way round.* The microseconds are
noise shaped like a measurement. The instances column is the measurement.

## Riffs that were cut

**"Three effects instead of two, so this is extra credit."** Cut. Effect C is
more surface than the assignment asked for and it is the least settled of the
three — no author verdict on its r0 reading. Presenting it as a bonus would
misreport it. The film shows it as what it is: a third scene that exists
because the author's verdict on Effect B named a gap.

**"The tests prove the effects work."** Cut, in every form. 301 check results
prove the configuration matches the brief and that the nodes fire and stop on
the right states. Not one of them has seen a pixel.

**Anything about how the effects look, in Claude's voice.** The tuning
verdicts are the author's and are quoted as theirs. Claude's strip readings
are in `TUNING.md` as claims, including the one the author's verdict
overruled — Claude read Effect B's dust-through-the-floor defect as the thing
to fix next, and the author, told to look for it, did not see it in play and
named a different gap entirely.

## One thing this film is riffing on that it cannot show

The GPU budgets. Every one of them — 0.30, 0.20 and 0.10 ms — is a prediction
with no measurement under it, and the Visual Profiler is the only instrument
that can settle them. The film says so three times, in three different voices,
because it is the largest open thing in the work and burying it in a footnote
would be the one dishonest move available.
