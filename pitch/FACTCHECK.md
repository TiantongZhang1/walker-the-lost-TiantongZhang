<!-- GENERATED COPY. The original is
     youtube/claude-liam-walker-the-lost-pitch-gdd/FACTCHECK.md
     Rebuild with: python -X utf8 scripts/assemble_pitch_folder.py
     Do not edit this copy; edit the original. -->

# FACTCHECK.md — every narrated claim, traced to the file it came from

Assignment 8's honesty rule is the thing this film is graded on hardest, so
every number and every verb tense in the narration is listed here with where
it came from and what kind of statement it is.

| Kind | Means |
|---|---|
| **MEASURED** | a number read out of a committed file or computed from one at build time |
| **COUNTED** | counted from the repository at build time by a script, not typed |
| **DECIDED** | the author's design decision; true because they decided it |
| **REASONING** | an argument, not a measurement. It can be wrong and is flagged so |
| **PROPOSED** | a statement about something that does not exist. Every one is in the future tense in the narration |

---

## B00 — the ask

| Claim | Kind | Source |
|---|---|---|
| "most of what I describe does not exist" | MEASURED | `gdd-evidence.json`: 5 of 9 sections carry `proposed` or `pending` |
| "three assignments on one character in one room" | MEASURED | tags `a5`, `a6`, `a7`. **This said four in the first cut** — see Corrections |
| composer card: "9 sections found - 9 covered, 0 excluded" | MEASURED | the checker's own output |
| composer card: "7 exact excerpts · 4 evidence files · 2 real captures" | MEASURED | the checker's own output |

The composer panel is a **reconstruction** of the Claude interface, not a
screenshot, and the skill requires it to be labelled as one.

## B01 — BLUF

| Claim | Kind | Source |
|---|---|---|
| "one room exists, tested to an unusual depth" | MEASURED | `TEST-REPORT.md`: 280 checks, 0 failures |
| "the game around it is proposed" | DECIDED | `PROJECT-BRIEF.md` §B |

## B02 — §1 What is it

| Claim | Kind | Source |
|---|---|---|
| the one-sentence description | DECIDED | brief lines 20–21, on screen verbatim |
| "a Windows desktop export plus the tagged repository" | PROPOSED | brief §1. **No export exists**; `godot/export_presets.cfg` is absent |
| "under ten minutes, no reading" | PROPOSED | brief §3. A target, stated in the future tense |
| "the full design has four floors" | MEASURED | `GDD.md` §7.4 lists four, plus the Shrine |
| "that is the cut the design document already names" | MEASURED | `GDD.md:414`, quoted in brief §1 |

## B03 — §2 Why anyone would care

| Claim | Kind | Source |
|---|---|---|
| "two progress bars and only one is in the interface" | DECIDED | `GDD.md` §2 |
| "the comparable is Hollow Knight, which I have played" | **the author's** | Claude proposed candidates; the author named this one. Claude must not assert that someone played a game and did not |
| "Dirtmouth fills with people you rescued off the critical path" | REASONING | a statement about a published game, from the author's play. No source in this repository can verify it and none is claimed |
| "the bosses are the ones you killed" | REASONING | same |
| "in The Lost the boss IS the resident — one system" | DECIDED | `GDD.md` §5, "the four lost" |

**No market claim is made anywhere in this beat.** No sales figure, no
audience size, no "players want". The card's own status band reads
*"PROPOSED · comparison, not a market claim"*.

## B04 — §3 Who opens it (real captured play)

| Claim | Kind | Source |
|---|---|---|
| "target role is gameplay programmer" | DECIDED | the author, 2026-11-23 |
| "real captured play at revision b33b06c" | MEASURED | `gdd-evidence.json` evidence record, SHA-256 pinned |
| "held keys, real input map, nothing staged" | MEASURED | `capture/logs/take-c-inputs.jsonl`, one object per physics frame |
| card: frames 535, length 8.88 s, player x 19→184, 195 frames facing left | MEASURED | computed from that log at build time |
| **the last 1.55 s is a held final frame** | MEASURED | labelled on screen for exactly those seconds |

## B05 — §4 What it proves

| Claim | Kind | Source |
|---|---|---|
| "shaders at a5" — 3 shaders, 99 checks, 4 breakages | MEASURED | `TEST-REPORT.md`, tag `a5` |
| "particles at a6" — 249 checks / 301 results | MEASURED | `TEST-REPORT.md`, tag `a6` |
| "animation and state at a7" — two clips, one timeline | MEASURED | `godot/animations/`, `test_player_clips.gd` |
| "two animation players asserted as a partition in both directions" | MEASURED | `test_player_clips.gd`; `evidence/a7/partition.txt` |
| "two hundred and eighty checks" | MEASURED | `evidence/a7/suite.txt`: 82+79+26+60+15+13+5 = 280 |
| "seven mutations" | MEASURED | `evidence/a7/mutations.txt`, M1–M7 |
| "none of it says I can write an enemy or ship a build" | COUNTED | 0 enemy or boss scenes under `godot/`; no `export_presets.cfg` |

## B06 — §A the window that hits nothing (real captured play)

| Claim | Kind | Source |
|---|---|---|
| "the committing swing, played, four times" | MEASURED | take-s asserts exactly 4 swings and exits nonzero otherwise |
| "a hitbox window, open a hundred and thirty-three milliseconds" | MEASURED | `CHANGE-BRIEF.md` §6: active frames 6–9 at 30 fps = 0.200–0.333 s |
| card: 329 frames, 5.45 s, 4 swings, window opened 4 times, 32 live frames, clips 36–36 | MEASURED | computed from `take-s-inputs.jsonl` at build time |
| card: "enemy scenes in this project 0" | COUNTED | `godot/**/*.tscn` with *enemy* or *boss* in the stem, counted at build time |
| **the last 2.02 s is a held final frame** | MEASURED | labelled on screen for exactly those seconds |

**The hitbox is not visible in this footage and the film says so.** An
`Area2D` contributes no pixels. That is why the window is measured rather
than shown, and the card states it.

## B07 — §A and §B, the two lists

| Claim | Kind | Source |
|---|---|---|
| "ten things can be cloned at a tag and run" | MEASURED | brief §A: 11 rows, 10 of which name a tag. **This said eleven in the first cut** — see Corrections |
| "the eleventh, the design document itself, is in no repository at all" | MEASURED | `the-lost-gdd/` is not a git work tree; `git rev-parse` fails in it |
| "not the enemy, not the boss, not the shrine, not a title screen, no export of any kind" | COUNTED | none of these exists under `godot/` |
| "the game has never left the editor" | COUNTED | no `godot/export_presets.cfg` |

## B08 — §5 In, out, first

| Claim | Kind | Source |
|---|---|---|
| "one level only, no save system" | DECIDED | brief §5 |
| "an enemy the existing hitbox can hit" | PROPOSED | brief §5. Future tense throughout |
| "measure clocks already pins the frame that window opens on" | MEASURED | `evidence/a7/clocks.txt` |
| "the one whose playhead reads nought point two thousand" | MEASURED | `evidence/a7/clocks.txt`, both callback modes |
| "the first test asserts the enemy's area entered signal fires on that frame" | PROPOSED | that test does not exist. Stated as what will be written |

## B09 — §6 What could sink it

| Claim | Kind | Source |
|---|---|---|
| "thirty-six physics frames, no cancel, no restart, no turn" | MEASURED | 0.600 s × 60 Hz; `player.gd`, `player_anim.gd` |
| "every piece of evidence that this feels acceptable was gathered in a room with nothing in it" | COUNTED | 0 enemies, every run of every suite |
| "the lock has narrowed three times" | MEASURED | `CHANGE-BRIEF.md` revisions 7.0.6, 7.0.9, 7.0.10 |
| "each time because I played it and said it felt bad" | MEASURED | `TUNING.md` carries each report in the author's own words, dated |
| "either the best thing in the game or the reason nobody finishes the fight" | **REASONING** | this is the risk. It is explicitly a thing nobody knows, and the card's status band reads `PENDING` |
| "the sixty-check suite that is my best evidence has that rule written through it" | MEASURED | `test_swing_edges.gd` is 60 checks; the facing assertions and sections C, D and E all depend on the no-turn rule. **This said "sixty checks are written around cannot turn" in the first cut, which overstated it** — see Corrections |

## B10 — §7 Why this project

| Claim | Kind | Source |
|---|---|---|
| "shaders, particles, a state machine, a headless harness — all at a tag" | MEASURED | tags `a5`, `a6`, `a7` |
| "every new thing involves a second thing being in the room" | REASONING | an observation about the §B list, and the film presents it as one |
| "I do not know whether the purification beat reads as a reward or an anticlimax" | **the honest row** | nothing measures this and the film says nothing measures it |

## B11 — Verdict

**Recapitulation only.** Every line restates a claim already made and already
labelled above. The one new statement is about authorship —

| Claim | Kind | Source |
|---|---|---|
| "Claude mapped the sections and ran the checks" | MEASURED | `scripts/build_pitch_*.py`, and the checker's output |
| "the scope, and whether it is worth playing, stayed mine" | **the author's** | `SOURCES.md` §6 splits it line by line |

## B12 — Your turn · B13 — Outro

B12 asks a question; it asserts nothing about this project except the card's
line *"every check ran in a room with no opponent"*, which is **COUNTED**.
B13 carries no narration.

---

## Corrections this fact-check caused

Three, all made before the master was rendered, and all recorded rather than
quietly fixed — the same convention `CHANGE-BRIEF.md` revision 7.0.8 used for
a prediction that came out wrong in sign.

1. **"four assignments" → "three assignments"** (B00 narration, and brief
   line 255, which B10 displays). Four assignments have been *about* The
   Lost — the GDD was Assignment 4 — but only `a5`, `a6` and `a7` built
   anything in the room. The sentence is about the room.
2. **"eleven things can be cloned at a tag" → "ten … and the eleventh is in
   no repository at all"** (B07). §A has eleven rows, and the first of them
   is the design document, which the same table already flags as having no
   tag. The narration had quietly counted it as evidence while the table
   beside it called it a gap.
3. **"sixty checks are written around cannot turn" → "the sixty-check suite
   … has that rule written through it"** (B09 narration and card, brief
   §6). `test_swing_edges.gd` is 60 checks and *several of its sections*
   depend on the no-turn rule; the suite as a whole also covers the lock, the
   air swing, movement, the jump and the two clocks. The first phrasing read
   as *all sixty are about turning*, which is not true.

**All three are the same mistake**: a true number attached to the wrong
quantity. That is the failure `CHANGE-BRIEF.md` revision 7.0.3 §2 named —
*"a true measurement of the wrong quantity"* — arriving for the fourth time
in this repository, and this time in the film about honesty.

## What this fact-check cannot do

It is written by the party that wrote the narration. It can catch a number
that disagrees with a file, and it caught three. It cannot tell you whether
the argument in B09 is a good one, whether the comparison in B03 is fair to
Hollow Knight, or whether the project is worth building. Those are the
reviewer's and the author's.
