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

---

## 2026-10-24 — Forward+ confirmed, and the check that nearly wasn't one

The open item from yesterday is closed. Forward+ initialises on this machine:
Vulkan 1.4.357, NVIDIA GeForce RTX 5080 Laptop GPU, window 1280 × 720, exit 0.
`CHANGE-BRIEF.md` §6 and §7 keep the Forward+/Mobile assumption their
predictions are written under, and no Compatibility caveat is needed.

**The part worth recording is how nearly this check proved nothing.** My first
instinct was to have Tiantong read the editor's Output panel and tell me what
it said. Two things were wrong with that:

1. They pressed F5 and looked at the **game** window, which has no panels. The
   Output panel is in the editor window. A check that depends on someone
   finding the right pane is a check that can quietly not happen.
2. More seriously — the headless runs had **already been reporting
   `forward_plus` and `vulkan`**. If I had asked for those two lines and got
   them back, I would have "confirmed" Forward+ from a dummy renderer that had
   initialised no device at all.

What distinguishes the two is the **adapter name**: headless leaves it empty
and the window 0 × 0. So `godot/game/main.gd` prints the adapter and the window
size as well as the method, and the real run is the one that names the GPU.
Running it windowed with `--quit-after` made the whole thing a single command
whose output is the evidence, instead of a question about what someone saw.

This is the same shape as the `CLAUDE.md` line numbers yesterday: the thing
that caught it was making the check mechanical, not looking harder.

**Still open after this:** whether 0.45 s is enough warning to react to. That
one genuinely cannot be mechanised — it needs Tiantong to play the slice.

---

## 2026-10-24 (later) — a green suite for a trap that could not hit anyone

Tiantong looked at the trap and said the spikes should come out as the player
approaches, not after they have walked past. That turned out not to be a
preference. **The trap could not hit a walking player at any speed**: the
trigger was 16 px, the player crossed it in 0.27 s, and the warning was
0.45 s. The spikes always arrived after the player had gone.

**Nineteen checks had been passing over this.** Worse, the suite had *printed*
the evidence and I had read past it. R3's scenario logs

```
PASS      player walked out of the trigger mid-window   [warn_amount was 0.630]
```

The player was gone at 63 % of the warning. I had written that line as a
precondition for testing the retrigger rule and never asked why it was
possible.

Every check in the suite measured the **timing of the warning**. Not one asked
whether the trap **worked**. That is the kind of hole a passing test suite
hides best, because the greenness is real — the rules it checks are all
correctly implemented. The specification simply did not contain the rule that
mattered, so nothing was there to fail.

### The fix, and the number that was not chosen

One area could not just be widened: the player would have taken damage from
three tiles away. So detection and damage are now separate — `DetectArea`
48 × 24 px notices the player, `HurtArea` 16 × 20 px is the only thing that
hurts.

The 48 px is derived from the warning length rather than picked:

```
detect half-width = SPEED × WARN_SECONDS − player half-width
                  = 96 × 0.30 − 5 = 23.8 px
```

Predicted offset when the spikes arrive: −0.2 px. Measured: +3.2 px. Both
inside the ±13 px hurt box.

Tiantong chose 0.30 s over 0.45 s. **I had given them the wrong numbers to
choose from** — I wrote `half-width = d + 5` instead of `d − 5` and quoted
48/96/125 px for the three options when the right answers were 48/76/105. The
direction of the choice was unaffected, but the table was wrong and I corrected
it before implementing rather than quietly building to the right number.

### What is now checked that was not

Scenario **F6** drives the player in with real input, does not react, and
asserts the player is short of the trap when it warns, over it when the spikes
arrive, and one life down afterwards. −25.6 px, +3.2 px, health 5 → 4,
identical at 30, 60 and 144 fps. 19 checks, 0 failures at each rate.

### And a check that could not fail

Fixing the scenes moved two lines that `CLAUDE.md` cites. Yesterday's reference
checker said both were fine, because all it verified was that the line number
*existed* — and it did, pointing at the wrong node. A reference check that
cannot fail when the target moves is not a check.

`tools/check_claude_refs.py` now pairs every reference with a substring the
target line must contain, and fails on drift, on a reference missing from its
table, and on the file going over 120 lines. It caught both drifted references
immediately. Same lesson as the renderer check this morning: the fix is to make
the check mechanical, not to look harder.

---

## 2026-10-24 (later still) — 0.40 s, and a test that did not know what speed it was running at

Tiantong moved the warning from 0.30 s to 0.40 s. `DetectArea` follows by the
derivation set up in the last entry — 66 px — and that is now **asserted** by
the suite rather than maintained by hand: one check that the shape equals
`SPEED × WARN_SECONDS − 5`, another that the three detection zones do not
overlap. The second one earned itself immediately: at the old 80 px spacing the
wider zones left 4 px of clearance, so the traps moved to 112 px apart.

### The frame rate the test believed in was wrong

Making that change turned up something worse than the trap bug.

The test read `Engine.max_fps` to work out its frame period. **`--fixed-fps`
does not set `Engine.max_fps`.** It was zero on every run, so the test fell
back to 60 and judged all three rates against a 60 fps tolerance:

| Run at | Tolerance used | Should have been | |
|---|---|---|---|
| 30 | 0.0167 | 0.0333 | 2× too strict |
| 60 | 0.0167 | 0.0167 | right by accident |
| 144 | 0.0167 | 0.0069 | 2.4× too loose |

Everything had passed, so nothing drew attention to it. It surfaced only
because 0.40 s at 30 fps finally overshot the bogus tolerance and failed — a
**correct** result failing a **wrong** check. If the duration had stayed at
0.30 I would still not know.

The measured durations in the last two entries were real. The verdict "within
one frame of specification" was not reliably earned at 30 or 144.

### Then the fix was wrong too

First attempt: read `--fixed-fps` from `OS.get_cmdline_args()`. It is not there
— the engine consumes it. Second attempt: measure the delta from the engine
over two frames. That reported **120 fps** on a `--fixed-fps 144` run.

Not a cap. 1/144 s is 6944.44 µs and Godot works in whole microseconds, so at
144 the frames are **not uniform**: 0.006944 (144 fps) 35 times in 40,
0.006667 (150 fps) four times, 0.008 once. 30, 60 and 240 divide evenly into a
second and are perfectly uniform. My two-frame sample had landed on an outlier.

So: `run-test.sh` exports `TEST_FPS`, the test takes the **modal** delta over
40 frames, and the two are cross-checked within 1 %. A tolerance derived from
the wrong number is worse than no tolerance at all, so the test now fails if
they disagree.

With the real frame periods, R2's tolerance went back to **one frame period**,
which is what this brief said all along — the 1.5× was slack I had added to
make a wrong number work.

### What I keep relearning

Three times in two days: the renderer check that would have passed on a dummy
device, the reference checker that only verified a line number existed, and now
a frame-rate tolerance computed from a constant nobody set. Each one looked
green. Each was caught by making the check compute something it could be wrong
about, not by reading more carefully.

---

## 2026-10-24 — I wrote the shader, and the tooling fought me before the language did

Four lines. The language was the easy part; getting the file to exist was not.

My first draft had six errors and Claude listed all six: `shader_typt` for
`shader_type`; `shader_test_1` where the **mode** goes, because I had read that
keyword as a name field when it only takes one of five fixed values; a stray
backtick I had copied along with the Markdown; `==` for `=`; and `warm_` for
`warn_` in both uniform names while `fragment()` still said `warn_`.

That last one is **F5 from my own §9**, and I wrote it by accident on the first
try. This time the compiler would have caught it, because `fragment()`
referenced an undeclared name. The dangerous direction is the other one — had
the *driver* been the file with the typo, nothing would have reported anything.

Then two dead ends in the editor, both from advice that was wrong about this
version of Godot:

- FileSystem → right-click → **新建** has only 文件夹 / 场景 / 脚本 / 资源 /
  文本文件. There is no Shader entry.
- 文本文件 refuses `.gdshader`: its filter is `*.txt, *.md, *.cfg, *.ini,
  *.log`, so the dialog answered "扩展名无效".

I made the file outside Godot in the end. Worth writing down because the
correct in-editor route is not where you would look for it: it is on the
**node**, not in the file browser — Sprite2D → Inspector → Material → New
ShaderMaterial → its Shader property → New Shader, and the "Built-in" box must
stay unchecked or the shader goes inside the `.tscn` and
`git diff --stat godot/shaders/` can never see it again.

Committed on its own as `f28d2de`, before the driver existed.

### Opening the editor cost two things

`project.godot` lost `renderer/rendering_method` — `ProjectSettings.save()`
drops every line equal to the engine default, and Forward+ **is** the default.
The comment above those lines had predicted exactly this. Restored.

And the editor rewrote `spike_trap.tscn` with `uid=` and `unique_id=`
attributes, moving three nodes down the file. `CLAUDE.md` cited their old line
numbers. `tools/check_claude_refs.py` caught all three by content — then caught
them again when adding the driver node shifted them a second time. Five and six
on its tally. I have still never caught one by reading.

### The two mutations, and which one frightened me

| | semicolon deleted | uniform renamed |
|---|---|---|
| `SHADER ERROR` | 2 lines | **none** |
| `test_trap_warning.gd` | 22/0, exit **1** | 22/0, exit **0** |
| `test_trap_shader_driver.gd` | 4 failures, exit 1 | 2 failures, exit 1 |

The first one is the textbook case and the suite handled it. But look at the
second row: **the state suite passed all 22 of its own checks against a shader
that did not parse.** It only failed because `run-test.sh` greps for
`SHADER ERROR`, which Godot prints while exiting 0. I had copied that grep out
of the assignment without really believing it was load-bearing.

Mutation 2 is worse and quieter. The shader compiles, nothing is printed, the
state suite exits 0, and the trap simply never turns red. What still passed:

```
PASS  the uniform never differed from the state in any frame  [worst gap 0.000000000]
```

Perfect agreement, on a trap that cannot light up. `get_shader_parameter`
returns what the *material* stored; it never asks the shader whether anything
reads it. A set-then-get test would have called this healthy — which is the
failure the assignment lists under "What the agent is likely to get wrong",
reproduced here on purpose.

### A decision about scope, mine

I asked whether this repository should be carrying across the art and audio
from `walker-ninja` — eight character poses, four sound effects, a music loop —
instead of the code-drawn blocks it uses now. It should: the assignment says
"you build one game" and that Assignments 3–10 each add a layer, so whatever is
missing now stays missing through A10.

**But not during Assignment 5.** The brief's own boundaries put the player,
the HUD and the audio outside this change, and "boundaries kept" is a scored
line. Porting them now would buy a prettier film at the cost of the thing the
film is about. So: finish A5, tag it, submit it, and port the art and audio
immediately afterwards as the first work of Assignment 6.

One thing does **not** come across even then. The trap's sprite stays
code-drawn, because §6 fixed its two pixels before anything was drawn and the
predictions describe the sprite rather than the reverse. Swapping it would
void the measurement this assignment is built on.

---

## 2026-10-24 — the capture rig, and a bug that looked like a working shader

**Claude's work, verified before handing it over.** On its first real windowed
run the rig reported this, four times identically:

```
  0.0 | A |  23,  20,  27        2.0 | B |  23,  20,  27
```

`23, 20, 27` is `Color(0.09, 0.08, 0.105)` — `default_clear_color` from
`project.godot`. It was sampling empty background, so every value came back
the same, and the first reading of that table was "the shader does nothing".

The cause: `get_viewport().get_texture()` returns the **window**, 1280 × 720,
not the 640 × 360 logical surface. `canvas_items` stretch scales on the way
out, so logical pixel `(208, 204)` is image pixel `(416, 408)`. The rig now
derives the factor from the image rather than assuming it, and prints both
coordinates so the mapping is visible in the report.

Worth recording because of how it failed. A wrong sample point does not throw,
does not warn, and does not look empty — it returns a plausible colour, four
consistent rows, and a confident conclusion about someone's shader. The only
reason it was caught is that the rig printed predictions beside measurements
instead of just saving PNGs. Had it saved four files and left the comparison
to a human eye, "the trap looks the same in all four" is exactly what a broken
sample point and a broken shader have in common.

Second, smaller: `simplify_path()` strips a trailing slash, so the first run
wrote `captures/a5warn_0_0.png` in the parent directory rather than
`captures/a5/warn_0_0.png`.

After the fix, from a real run on the RTX 5080 with Forward+: **all eight
predicted values exact, worst channel difference 0.** The author's own run is
what gets recorded in `TEST-REPORT.md`; this one existed to find the bug.
