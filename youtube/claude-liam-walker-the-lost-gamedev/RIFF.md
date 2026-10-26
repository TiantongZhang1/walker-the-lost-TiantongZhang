# RIFF.md — the commentary, and what it is allowed to be about

Riff on what was inspected, never on imagined play. Every line below points at
a file, a log or a capture. Where a riff is an opinion it says so.

---

## The spine

Three shaders, four mutations, and one question that turns out to have two
different answers depending on where you ask it.

## What earns a riff

**The hint that is invisible to the engine.** Ask Godot to describe
`stone_albedo` and `wetness_mask` and it returns the same answer for both —
type 24, hint 17, `"Texture2D"`. One of them declares `source_color` and the
other does not. On a `vec3` the same keyword *is* visible, which is exactly
what makes the sampler case easy to assume away. A test written on the
uniform list would pass with the hint deleted. That asymmetry is the best
thing this assignment turned up, and `test_materials.gd` asserts the
blindness itself so nobody simplifies the source-text check away later.

**The state suite that passed 22 of 22 against a shader that did not parse.**
It exited 1 only because the wrapper greps the log for `SHADER ERROR`, which
Godot prints while still exiting 0. The wrapper was copied out of the
assignment without really believing it was load-bearing. It is.

**Four mutations, three nets, no overlap.** The semicolon needs the wrapper.
The rename needs the uniform list. `source_color` needs the source text. No
one of those catches the other two, and each was found by breaking the thing
on purpose rather than by reasoning about it.

**Roughness zero makes stone darker.** Measured, not guessed: `32, 43, 39`
against a baseline of `53, 62, 58`. At roughness 0 the surface is a mirror
and the background is nearly black, so the diffuse response is replaced by a
reflection of nothing. The sweep was built to find out which setting changes
the look most; it found one that changes it in the opposite direction from
the obvious guess.

**The capture rig that read empty air.** Its first run reported `23, 20, 27`
four times — the clear colour. `get_viewport().get_texture()` returns the
window, 1280 × 720, not the 640 × 360 logical surface. A wrong sample point
does not throw, does not warn and does not look empty: it returns a plausible
colour, four consistent rows and a confident conclusion about someone's
shader. It was caught only because the rig printed predictions beside
measurements instead of saving four PNGs for a human eye.

**A threshold that got stricter when the room got darker.** During the
shader-edit demonstration the same material change moved the mean 2 instead
of 3, and a check written as "must move more than 2 counts" reported
`UNEXPECTED` about a demonstration that had worked. A threshold in absolute
counts tightens every time a scene dims, and says nothing when it does.

## Opinions, labelled

- The armed trap at 1.12 : 1 against the floor is *almost too* invisible. It
  is defensible — an armed trap you spot from across the room is not a trap —
  but it leans on the warning doing all the work.
- Putting a dungeon-stone material on a slime is incongruous. It is what the
  brief chose, because the slime is the only 3D object Assignment 3 left, and
  the film says so rather than pretending it is a design decision.

## What the riff must not do

- Claim the film proves anything about colour from a headless run. It cannot;
  the dummy renderer draws nothing.
- Present any reconstruction as a recording. B00's prompt was never sent and
  the code panels are teaching views, both labelled.
- Round up the human checks. One is still outstanding: whether any setting in
  the interface sweep *breaks* the look rather than merely changing it. B12
  says so.
- Imply the slice is more game than it is. It has no audio and no art beyond
  code-drawn blocks, by a decision dated in `FRICTIONAL.md`.
