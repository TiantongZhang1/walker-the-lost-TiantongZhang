# PROJECT-BRIEF.md — the final project, in seven answers

**Assignment 8 · The Lost · Tiantong Zhang · `zhang.tiant@northeastern.edu`**

Drafted 2026-11-23. **This is a pitch. Most of it does not exist.** The two
lists at the end are the honesty mechanism of this document: §A is what can be
opened and run today at a named tag, §B is everything else, and no sentence
above those lists uses the past tense for anything in §B.

> **Tags, as in every brief in this repository.** **[decided]** — chosen by
> the author. **[proposal]** — derived by Claude and not yet confirmed.
> Every **[proposal]** that was open in this file's first draft has since been
> settled by the author; they are marked **[decided]** below and the draft is
> in git history.

---

## 1. What is it?

The Lost: Floor One — a playable vertical slice of a 2D side-view dungeon
crawler in which you do not kill the boss, you cure them.

**The artifact is a Windows desktop export plus the tagged repository it was
built from.** A stranger downloads one `.exe`, double-clicks it, and plays from
a title screen to an end screen in under ten minutes without reading anything.
The same tag holds the test report they can rerun headlessly.

**No web build.** **[decided]** That is a scope decision and it is also a risk
decision, and §6 says what it costs and what it buys.

The full design is `../the-lost-gdd/GDD.md` — four themed floors, four bosses,
a hub that fills with the people you rescue. **This project is floor one and
one boss**, which is the cut the GDD itself names: *"the correct cut is floor
count, not floor quality"* (`GDD.md:414`). **[decided]**

---

## 2. Why would anyone care?

**What it gives the player.** A boss fight whose reward is a person. You fight
a corrupted adventurer who went down before you; beating them purifies them
back into a human, who walks out of the arena. When you return to the shrine
they are standing in it, and one of the four grey outlines on the wall is no
longer grey.

**The difference, stated as a mechanic rather than as a feeling.** The game has
two progress bars and only one of them is in the UI. The visible one is floors
cleared. The invisible one is **how many people are standing in the room you
come home to** — and it is the same number, because the four people you are
rescuing *are* the four bosses.

### The comparable: Hollow Knight

**Hollow Knight is the game this one is measured against, and it is a game I
have played.** **[decided — the author's, not Claude's]** It is the right
comparable because it already does both halves of what The Lost is built on,
separately:

- **A corrupting force.** Hallownest's infection is the same idea as the
  miasma: it takes creatures rather than killing them.
- **A hub that fills up.** Dirtmouth starts almost empty and gains residents —
  Bretta, Zote, Cloth, Quirrel — as the game goes on, and walking back into a
  fuller town is a real feeling the game earns.

What The Lost does that Hollow Knight does not: it makes those the same
act. In Hollow Knight the people who turn up in Dirtmouth are the ones you
rescued off the critical path, and the bosses are the ones you killed.
The two systems never touch. A player who runs the main line and nothing else
comes home to a town that is still empty, and the infection is only ever cured
once, globally, in an ending.

In The Lost there is one system. **The boss is the resident.** The only way to
add a person to that room is to clear a floor, and the only way to clear a
floor is to add a person to that room — so you cannot play the main line and
miss it, you cannot grind it out early, and the cure is something you watch
happen four times to four named people rather than once to a world.

**What the slice can and cannot show.** One boss means the mechanic is
demonstrated **once**. "Four outlines become four people" is the full game;
"one outline becomes one person, and you can see the other three still grey" is
what a reviewer will be able to play. **[decided — say this in the film rather
than let a reviewer find it]**

---

## 3. Who opens it, and what do they do in the first sixty seconds?

| | |
|---|---|
| **Target role** | **Gameplay programmer.** **[decided]** The built evidence is a character controller, a state machine, two animation clips on one timeline and an edge-test suite; the shader and particle work supports that rather than leading it |
| **Reader** | a lead engineer or hiring manager, and a player |

**A player** downloads the `.exe`, runs it, sees a title screen, presses any
key. They are moving within about ten seconds and swinging within twenty. A/D
or arrows to move, Space to jump, J to swing — the same bindings the game has
today. **No reading, no menu, no tutorial text.**

**A lead engineer** who wants the other thing clones the tag and runs
`./scripts/run-test.sh`, then reads `TEST-REPORT.md` and `TUNING.md`. Those two
files are the reason this repository is worth more than the `.exe`.

---

## 4. What does it prove about me?

Course skills, each with the evidence that already exists for it.

| Skill | Evidence that exists today | Where |
|---|---|---|
| **Shaders and materials** | three hand-written shaders, 99 checks, four deliberate breakages, two findings about what the engine does *not* report | tag **`a5`** |
| **Particle effects** | three effects, 249 checks / 301 results, a measured cost table with an empty-scene control | tag **`a6`** |
| **Animation and state** | two clips on one timeline, two `AnimationPlayer`s asserted as a **partition in both directions**, the two clocks measured | tag **`a7`** |
| **Measured cost** | `cost_effects.gd` (headless, four named conditions) and `gpu_cost_effects.gd` (windowed) | tags **`a6`**, **`a7`** |
| **Verification habits** | 280 checks 0 failures, **7 mutations** each caught by a different net, and a HUMAN-check split that names what no headless run can establish | tag **`a7`**, `TEST-REPORT.md` |
| **Directing an agent with scoped tools** | `CLAUDE.md`'s *Out of scope* list, and the rule that the brief is committed before the first prompt of each assignment | every tag |

What the final project adds to that list: it is the first time any of it
has to survive a second character being in the room, and the first time any of
it leaves the editor as a build.

**What a reviewer could fairly conclude, and the evidence that backs it.** That
this person can take a written specification, build it, and then tell you which
parts of it are tested and which are only believed. The backing is not the
passing suites — it is `TEST-REPORT.md`'s list of **eleven sentences in this
repository that outlived the facts they stated**, none of which a test found,
and `CHANGE-BRIEF.md`'s ten revisions, **nine of which began with the author
playing the game**, not with a suite going red.

**What a reviewer could NOT conclude from what exists today**, and should not be
invited to: that the author can write enemy behaviour, build a boss, make a
hitbox connect with anything, or ship an export. `CHANGE-BRIEF.md` §11.3 says it
plainly about the hitbox — *"It can hit nothing today."*

---

## 5. What is in, what is out, what comes first?

### In

Title screen · one flooded-dungeon floor of hand-built rooms · one enemy type ·
the **roll with i-frames**, which the GDD calls the one defensive verb · a chest
that ejects its contents as physical objects · **one boss in two forms**,
corrupted and human · purification · the floor key · a minimal shrine holding
the goddess and the four outlines · an end screen · a Windows desktop export · a
rerunnable test report.

### Out, deliberately

**One level only, and no save system.** The slice is one sitting: close it and
it is gone. Also out, and each is in the GDD: floors 2–4, the other three
bosses, the gold economy, the blacksmith and the merchant, magic and MP, the
3-hit hold-to-combo — **one committing swing already exists and a combo is three
of them**, which is a different assignment's worth of state machine — and
**any web export**.

### First

**An enemy the existing hitbox can hit.**

It is first because it is the smallest change that is not cosmetic, because
everything else in §5 depends on knowing it works, and because it is the only
way to find out whether §6's risk is real while it is still cheap.

The hitbox is already built, already on layer 6 PlayerAttack masking layer 3
Enemy, already opens for a measured 0.133 s, and has never touched anything
in its life.

**How anyone would know it ran.** Not by watching. By the measurement that
already exists: `measure_clocks.gd` pins the physics frame on which the window
opens as the frame whose playhead reads **0.2000**, in both callback modes. The
first test of the first piece asserts that the enemy's `area_entered` fires on
**that** frame — the same number, out of the same file, now with something on
the other side of it. **[decided]**

---

## 6. What could sink it?

The swing commits, and it has never committed against anything that moves.

`swing` is 18 frames at 30 fps — **0.600 s, 36 physics frames** — and it cannot
be cancelled, cannot be restarted, and **cannot turn**. The no-turn rule is not
a preference: `Rig.scale.x` mirrors the whole sword arm, so a turn mid-arc would
teleport the blade across the body in one frame, and `player_anim.gd` freezes
the facing for the whole clip to stop it.

**Every bit of evidence that this feels acceptable was gathered in a room with
nothing in it.** That is the problem. The lock has already narrowed three times
— movement in revision 7.0.6, the legs in 7.0.9, the jump in 7.0.10 — and each
time because the author played it and said it felt bad **with no opponent
present**. Put something in the room that walks behind you, and a 36-frame
commitment to a direction is either the best thing in the game or the reason
nobody finishes the fight. There is no way to know which from here.

**If it is the second, the fix is not a tuning value.** It is a change to the
state machine, and `test_swing_edges.gd` — **60 checks**, this project's best
evidence — has *cannot turn* written through it: the facing assertions, section
C, section D's mid-swing reversal, section E's two-clock comparison. Changing
the rule invalidates all four.

**What I will do about it.** Build the enemy **first** — §5 already says so, and
this is the other reason. Judge the swing against a moving target in the first
week, while exactly one suite depends on the current rule, instead of after the
boss, the shrine and the floor have all been built on top of it. The verdict
goes in `TUNING.md` in my own words, as every verdict in this repository has.

### The risk I am retiring, and what retiring it costs

My own two documents disagree about the renderer: `GDD.md:369` says **GL
Compatibility**, `godot/project.godot:15` says **`Forward Plus`**. Everything in
`TEST-REPORT.md` was measured on Forward+, Vulkan 1.4.357, an RTX 5080 Laptop
GPU. A **web** export runs on Compatibility only, so a web build would put three
hand-written shaders and three `GPUParticles2D` effects somewhere nothing has
ever tested them, and every number in my test report would stop describing the
thing the reviewer is playing.

**Shipping desktop-only is what retires that**, and the cost is stated rather
than hidden: a reviewer downloads and runs an `.exe` instead of clicking a link,
which is slower and asks more trust. **The GDD's renderer row is wrong and will
be corrected** rather than left as a contradiction someone else has to find.

**Still open and not pretended away:** I have never exported this game at all.
There is no `export_presets.cfg`. "Desktop export" is a `[will exist]` row like
every other one in §B.

---

## 7. Why this project?

**A mix, and the two halves are not close.**

**Showing off — skills I have, with something real to point at.** Hand-written
shaders (`a5`). Particle effects and their measured cost (`a6`). An animation
state machine with two clips, one authority per node, and the clock measurement
that found my own prediction was wrong in sign (`a7`). A headless test harness,
and the discipline of writing the brief before the first prompt. All of that is
in this repository at a tag, and all of it is me repeating something I can
already do.

**Learning — skills I do not have, with nothing to point at.** Every one of them
involves a second thing being in the room:

- enemy behaviour of any kind. There is no enemy in this project and never has
  been;
- a boss — a scripted fight with phases, which is a state machine an order of
  magnitude past the player's five states;
- **combat that connects.** The hitbox has been built, measured, pinned at three
  frame rates and filmed, and it has hit nothing;
- scene transitions, and state that survives them — shrine to floor to boss
  arena and back;
- a title screen and an end screen;
- **an export.** There is no `export_presets.cfg` in this repository. The game
  has never left the editor.

The honest sentence. I have spent three assignments making one character look
and behave correctly in one room, and I have never made it meet anything.

**Where I genuinely do not know yet, and how I will find out.** Whether the
purification beat reads as a *reward* rather than as an anticlimax — you win the
fight, and then the music stops and someone walks away. No test can tell me
that. I will find out the way every HUMAN row in `CHANGE-BRIEF.md` §9 was
answered: by building the beat early, playing it, and writing down what I said
in my own words before Claude reads anything.

---

## §A. Exists today

Every row can be opened and run at the tag named. Nothing in this list is
planned.

| Thing | Tag / where |
|---|---|
| The design document — four floors, four bosses, the hub | `../the-lost-gdd/GDD.md` — **no tag, and that is a gap**: it is in no git repository. `README.md` already promises it moves into `design/` |
| One room: floor, backdrop, three spike traps with a 1.40 s state machine | `a5` · `godot/game/main.tscn` |
| A player who walks, jumps, takes damage and dies | `a5` · `godot/features/player/player.gd` |
| Three hand-written shaders, plus the engine's own converted output | `a5` · `godot/shaders/` |
| Three particle effects, a cost table, a vsync debug key | `a6` · `godot/effects/` |
| A run cycle and a committing swing, two authorities partitioned by node | `a7` · `godot/animations/` |
| A hitbox with a measured 0.133 s window **that hits nothing** | `a7` · `godot/features/player/player.tscn` |
| 280 checks, 0 failures, at 30 / 60 / 144 fps where cadence matters | `a7` · `TEST-REPORT.md` |
| 7 mutations, each caught by a different net | `a7` · `evidence/a7/mutations.txt` |
| Three explainer films | `a5`, `a6`, `a7` · `youtube/` |
| A tuning log in the author's own words, dated | `a7` · `TUNING.md` |

## §B. Will exist

Nothing in this list has been started.

Enemy · enemy behaviour · the roll and its i-frame window · a boss in two forms
· the purification beat · the floor key and a door that checks for it · a chest
that ejects · the shrine, the goddess and the four outlines · the outline that
becomes a person · a title screen · an end screen · scene transitions · state
that survives them · **any export at all** · the corrected GDD renderer row ·
the flooded-dungeon tileset and its cold-from-above light.
