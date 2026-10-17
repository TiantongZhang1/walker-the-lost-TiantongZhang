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
