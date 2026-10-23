# FRICTIONAL — honest log of the design thinking

**walker-the-lost-TiantongZhang · Tiantong Zhang · started 2026-10-17**

A dated log of the design as it happens: what I was trying to make the player
see or hear, what I asked the model for, what came back, and what I decided.
Written the same day, not reconstructed at the end.

> **"I" is me. "Claude" is Claude. "the model" is whichever generative model
> produced the asset.** These three are scored apart, so they are never
> blended. Claude writes code, prompts and plans and organises these notes; it
> does not generate images or audio, and it does not write my judgement for me.

**This log continues from `walker-ninja-TiantongZhang/FRICTIONAL.md`**, which
covers Assignments 1–3 and stops at the `a3` tag. Nothing in that repository
has been edited since; the first entry below explains why the game changed and
why the old repository was left alone.

---

## 2026-10-17 — the one permitted change of game, used

**The rule, in the assignment's own words:**

> "The cumulative game. From Assignment 2 on, you build one game: the one you
> chose in Assignment 2, in a repository whose name begins `walker-`.
> Assignments 3–10 each add one layer to that same repository and are submitted
> as a git tag on it (`a3` here), so the final project is the sum of the
> semester rather than a restart. **You may change games once, before
> Assignment 4, with a short written justification in FRICTIONAL.md; the tags
> then continue on the new repository, and your submission note says so.**"

**What I am changing from and to.** From the cyber-ninja slice in
`walker-ninja-TiantongZhang` — a 2D side-scroller with a double jump, an air
dash and a sword, against spike traps, slimes and flying horses — to **The
Lost**, a 2D side-view dungeon crawler. Four themed floors, one boss each, and
the thing that makes it worth building: **you do not kill the bosses, you cure
them.** Each boss is an adventurer who went into the dungeon before you and was
corrupted by its miasma. Beating one purifies it; the monster collapses back
into a person, who walks out and takes a place in the hub. The design document
is `design/GDD.md`.

### Why, and I want to be exact about this rather than flattering

The honest reason is **not** that the ninja slice was failing. It passes 113
automated checks, it has tested movement, a level, enemies and a death/retry
loop, and Assignment 3's three assets sit in it correctly. It works.

The reason is that it has **nothing to say**. It is a competent collection of
verbs — jump, dash, hit — attached to no idea. Every assignment from here to
A10 adds a layer to one game, and seven more layers on top of "competent
collection of verbs" produces a bigger competent collection of verbs. When
Assignment 7 asks for something about the *experience*, I would have had
nothing to point at.

The Lost has one idea, and it is small enough to build and strong enough to
carry seven more assignments: **progress is the number of people standing in
the room you come home to.** Every other decision in the GDD is downstream of
that one — the ghosted placeholder figures visible from the first minute, the
hub music gaining a voice per rescue, the boss music cutting dead the instant
the boss is purified rather than playing a victory fanfare over a person waking
up. That is a design I can keep answering questions about for seven more
assignments.

### What it costs, said plainly

- **A working codebase.** The ninja slice's player controller, level and enemy
  code do not come across. I start A4 with an empty Godot project.
- **Assignment 3's three assets.** The spike trap, torch and slime were built
  in Blender for the ninja repository and stay tagged there under `a3`. They
  are dungeon props and would suit this game, but moving them would alter the
  `a3` submission's evidence, and that is not a trade I will make.
- **Time, during the semester's busiest stretch.** This is the real cost and I
  am choosing to pay it now precisely because the deadline for choosing is
  *before Assignment 4*. Making the same decision in November would not be
  allowed.

### What it does not cost

The build machinery carries over in full: the Brutalist film chain, the
headless check harness, the documentation skeleton. See `TOOLCHAIN.md`, which
classifies every copied file as generic, needing reshaping, or kept only as a
reference. That is most of what the last three assignments actually built, and
none of it was game-specific.

### Three decisions about the move itself

**1. The old repository is not touched.** Not one file. The temptation was to
add a pointer line to `walker-ninja-TiantongZhang/FRICTIONAL.md` saying where
the project went. I did not, because this exact move — adding a file to that
repository after a tag — is what silently broke Assignment 2's evidence ledger
when Assignment 3 added eight files under `godot/`. The ledger hashes an
inventory; anything new fails coverage. The pointer is not worth the risk, and
the Canvas submission note is where a reader is actually told.

**2. The tags continue here, they are not re-created.** The rule says "the tags
then continue on the new repository". So this repository's first tag will be
`a4`. There will be no `a2` or `a3` here, and `git tag` showing a sequence that
starts at `a4` is correct, not a mistake.

**3. The GDD stays where it was written, for now.** `the-lost-gdd\` outside
both repositories is where the design document and its two figures live,
because it was written as its own 5-point Canvas assignment before this
decision was made. It belongs in `design/` here and will move when A4 starts —
moving it now, before anything in this repository builds, would just be
shuffling files.

### What is not yet done

- No game code. The Godot project is an empty 640 × 360 shell with the layer
  names set up and no main scene. That is accurate: nothing is built.
- `CONCEPT.md`, `SOURCES.md`, `ASSET-LOG.md` and `PROMPTS.md` are skeletons
  with headings and no content. They are tracked from the start so that the
  commit history shows when each claim was first made, which is the same reason
  the ninja repository committed `CONCEPT.md` v1 before generating anything.
- The collision layer names in `project.godot` (layers 5 and 7, `Interactable`
  and `EnemyAttack`) are **Claude's**, derived from the GDD's chests, NPCs and
  the hitbox/hurtbox split. I have not tested that this is the right split and
  it may change once there is a player to test with.
- The submission note for Assignment 4 must answer "Changed games since
  Assignment 2" with **yes**, and point at this entry.

---

## 2026-10-23 — Assignment 5 begins, and the repository was empty

**The problem, found before any work:** Assignment 5 says to add shaders to
"the game you have been building since Assignment 2", and to do its parts 3 and
4 "in the 3D scene you added in Assignment 3 or 4". This repository had neither.
It was six days old and held documentation, a toolchain and an empty Godot
shell. The game change on 2026-10-17 was correct for the rule, and it left
Assignment 5 with nothing to attach to.

**Checked rather than assumed:** Assignment 4 is the Game Design Document, and
it describes The Lost. So the sequence is coherent — change the game, design it
in A4, build its first layer in A5 — and the "before Assignment 4" rule is
satisfied. The A5 submission note answers **yes** and points at the entry above.

**A mistake of mine, corrected.** The 2026-10-17 entry says Assignment 3's three
Blender assets could not come across because moving them "would alter the a3
submission's evidence". That is wrong: *copying* is not *moving*.
`walker-ninja-TiantongZhang` is untouched and the `a3` tag still hashes exactly
what it hashed. The three `.glb`, their `.import` files, `asset_showcase.tscn`
and `check_assets_3d.gd` were copied in today and credited in `SOURCES.md` §2.
I had been cautious in the wrong direction, and it had made me tell Tiantong the
work was about twice as large as it is.

### What was decided, and by whom

Claude proposed the spike trap's warning as the shader's subject over the
player's dodge-roll i-frames, on the grounds that a trap is multi-instance and
the roll is not — which makes the assignment's own named failure case ("one
enemy's flash appearing on every enemy") a rule that can actually fail. The
room holds **three** traps so that it can. Tiantong chose the trap.

Four decisions are Tiantong's, recorded as revision 5.0.1 of `CHANGE-BRIEF.md`:
Forward+, 0.45 s provisionally, **retrigger restarts** (rejecting Claude's
"ignore"), and `Engine.time_scale` unused.

The retrigger decision inverted one of the brief's own predicted failure cases.
F3 had said restarting was the bug; it now says *failing* to restart is. The
consequence was written down rather than discovered later: a player who steps
off and back on repeatedly restarts the warning and is never hit. That is a real
exploit of "every trigger gets its own warning", and it is accepted knowingly.

`Engine.time_scale` was answered "先不用". That is read as *the game does not use
time_scale*, not as *the warning must ignore it*. The reading is flagged in the
brief, and the test sets `time_scale = 0.5` anyway so the behaviour is recorded
instead of assumed. If the reading is wrong it is a two-line change.

### Three things the work turned up

**The sprite was drawn to the brief, not the brief to the sprite.**
`CHANGE-BRIEF.md` §6 named the trap's colours and two prediction pixels before
any art existed. `tools/make_sprites.py` then drew the trap to those values and
**asserts both pixels**, so a later edit that moves them fails the script rather
than silently invalidating the predictions.

**`ProjectSettings.save()` deleted the renderer line I had just written.**
Setting Forward+ by hand and then running a script that called
`ProjectSettings.save()` removed `renderer/rendering_method` entirely — Godot
omits any setting equal to its default, and Forward+ *is* the default. The
project still runs Forward+ and `config/features` still names it, but
`project.godot` no longer *said* it, and Assignment 5 asks which renderer
project.godot names. The lines were restored with a comment saying the editor
may drop them again. Worth knowing before the editor does it silently.

**The `CLAUDE.md` draft cited four wrong line numbers.** Assignment 5 warns that
this happened in Chapter 6's run, and it happened here too — `player.gd:14`
pointed at a blank line, `run-test.sh:22` at `set -o pipefail` instead of the
`GODOT=` override, `test_trap_warning.gd:28` at an array declaration instead of
`process_priority`, and one reference was written as a bare filename that
resolves to nothing. They were caught by a script that opens every `path:line`
in the file and prints what is actually on that line — not by reading, which is
what let them through in the first place. All ten references now resolve.

**One thing this draft cannot do for Tiantong.** The assignment's shape assumes
a cold agent drafts `CLAUDE.md` by reading an unfamiliar repository, and that
the human catches what it got wrong. This draft came from the session that
*built* the repository, so it is more accurate and the review step is
correspondingly weaker as a check. That is said at the bottom of `CLAUDE.md`
itself, and every line number still needs checking by hand.

### What the tests establish, and what they do not

`test_trap_warning.gd` drives the state with synthesized key events through the
real game loop — the player walks into the trap — and never calls the trap's
update directly. That matters because the assignment records an agent that,
after a 30 fps failure, rewrote its test to call the update function, at which
point the frame rate stopped mattering and the summary still claimed to have
tested 30 and 144.

Measured warning window, 16 checks passing at each rate:

| fps | window | one frame |
|---|---|---|
| 30 | 0.467 s | 0.0333 s |
| 60 | 0.467 s | 0.0167 s |
| 144 | 0.451 s | 0.0069 s |

All within one frame of the specified 0.450 s, which is R2.

None of this says anything about colour. There is no shader yet, and a headless
run draws nothing.

### Still unresolved

- **Forward+ has never run on real hardware here.** Set today; every run since
  has been headless, which uses a dummy renderer and proves nothing. The first
  windowed editor run confirms it or reverts it.
- Whether 0.45 s is enough warning to react to. Nobody has played the slice.
- Whether `source_color` changes the value the shader receives. Predicted both
  ways in the brief; one capture settles it.
- The player has move and jump only. The GDD's combo, magic and dodge roll are
  deliberately absent — Assignment 5 grades shaders, and the brief's boundaries
  say movement and input do not change, so building them now would only give
  that boundary more to not touch. This is a limitation, not an oversight.
