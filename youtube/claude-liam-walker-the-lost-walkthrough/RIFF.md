# RIFF.md — the commentary, and what it is riffing on

The register here is **walkthrough**, not teardown. The footage is the
argument; the voice is the caption. Every aside below is anchored to
something inspected — a file, a log row, a measured frame — and the anchor is
named. Nothing riffs on imagined play.

---

## The through-line

**Most of what this game does well is a number agreeing with another
number, and you cannot see agreement.**

The cycle is half a second because a stride is twenty-four pixels. The dust
spawns every twenty-four pixels. The swing's active window is narrower than
the trap's. The hitbox opens on the frame whose playhead reads exactly
0.2000. None of that is visible: what is visible is a character running, and
dust under its feet, and a trap you can walk away from.

So the riff's job in this film is to say, each time, **which invisible
agreement the visible thing is standing on** — and then to be honest that the
footage is not what establishes it.

## Where the riff lands, beat by beat

**B02, idle.** The riff is on what a held frame costs and what it cannot do.
It costs nothing and it cannot breathe. Saying that about your own game's
cheapest state is more useful than praising the expensive one.

**B02, the cycle.** The riff is that half a second is arithmetic, not taste —
and the consequence, which is the part worth keeping: *if the run is ever
retimed, the arithmetic changes first and the keys follow.* Anchored on
`legs.tres:24` and `main.tscn`'s `stride_px`.

**B02, the dust.** The riff is that two systems agree because they were
derived from the same number, and **nothing enforces it at runtime**. That is
a real fragility and it is said rather than admired.

**B03, the key.** The riff is on the word *decorative*. A key in a dungeon
implies a door. There is no door. The film says so in the same breath as
showing it, because a walkthrough that lets a prop imply a mechanic is
misreporting the game.

**B04, the wind-up.** The riff is that the arm nearly stops before it goes —
ten degrees in two frames against a hundred and fifty in four. The pause is
the thing that makes a strike read, and it is the sort of detail that only
shows up when you look at a key table rather than at the animation.

**B05, the edge.** The riff is the uncomfortable one and it is the best thing
in the film: **the ignored attack would pass by accident.** `play()` with the
name already playing does nothing at all, so a build that had never wired the
rule would look identical. The code reads the playhead instead — which makes
it a decision rather than a side effect, and makes the check that
distinguishes them worth having.

**B06, the two revisions.** The riff is that both of these exist because a
person played the game and said it was wrong, and neither was found by a
test. The legs keeping their gait is the one that needed a second
`AnimationPlayer`; the jump not interrupting is the one that needed nothing
at all, because the branch already wrote only one field.

**B07, the trap.** The riff is the ratio: four tenths of warning against two
tenths of wind-up. That is the whole reason attacking near a trap is a choice
and not a mistake.

**B07, damage.** The riff is on an absence. The hit does nothing to the
animation, and the film names that as a *limit* rather than letting silence
read as restraint.

**B07, death.** The riff is that this is the only state no key can reach, and
that nothing follows it. The beat holds on the corpse for four and a half
seconds rather than cutting, because cutting away would be answering the
question "what happens next?" by not asking it.

**B08, before and after.** The riff is that the defect was in the numbers the
whole time: the tip never gets below −3.4 px in any of the eighteen frames of
the first version. That is a range over a function, not an impression — and
no check was asking.

---

## Riffs that were cut, and why

**"This is a complete little game."** It is not. No enemy, no respawn, no
menu, five of the GDD's states built out of eight. `coverage.json` lists five
planned features with reasons and the verdict says them out loud.

**"The tests prove it works."** Three hundred checks establish that the
animation state follows the player under the inputs that were scripted. They
establish nothing about whether any of it reads, and the assignment's own
summary says so in those words.

**"Claude built it and the human reviewed it."** Too flattering to both. Nine
of the ten tuning revisions started with the author playing and saying
something was wrong; the tenth started with a measurement contradicting a
prediction Claude had written. The interesting failures were not anyone's
carelessness — they were true measurements of the wrong quantity.

**Any joke about the character dying.** Take d ends with five trap hits and a
corpse. It is the only failure state the game has, and treating it as a
punchline would undercut the one beat that is about the game's limits.
