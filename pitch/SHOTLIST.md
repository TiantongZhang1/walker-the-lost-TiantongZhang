<!-- GENERATED COPY. The original is
     youtube/claude-liam-walker-the-lost-pitch-gdd/SHOTLIST.md
     Rebuild with: python -X utf8 scripts/assemble_pitch_folder.py
     Do not edit this copy; edit the original. -->

# SHOTLIST.md — every beat, what is on screen, and where it came from

**The Lost: Floor One** · `claude-liam-walker-the-lost-pitch-gdd` ·
14 beats · 13 narrated · **3:54** at 3840 × 2160, 30 fps.

Two of the fourteen are real captured play. Seven are document boards that
carry an exact excerpt of `pitch/PROJECT-BRIEF.md`. Five are the Walker
bookends. **No beat is a mock-up of an unbuilt game**: the unbuilt parts of
this project appear as lists and labels, never as pictures.

---

| # | Act | Pattern / source | Status | On screen | Length |
|---|---|---|---|---|---|
| **B00** | ASK | `ClaudeComposerAsk` | — | Reconstructed Claude composer. The real ask: turn the brief into a pitch film. Output lines are the checker's own figures | 11.88 s |
| **B01** | BLUF | `BrutalistHesitantWriter` | — | The misconception, typed and corrected live: **finished → proposed** | 12.01 s |
| **B02** | MECHANISM | `GodotDesignBoard`, layout `flow` | `proposed` | Brief lines 20–21 left; four flow cards right — one executable, title to end screen, one floor, plus the repo | 18.07 s |
| **B03** | MECHANISM | `GodotDesignBoard`, layout `cards` | `comparison` | Brief lines 65–67 left; four cards contrasting Hollow Knight's two systems with The Lost's one | 20.35 s |
| **B04** | EVIDENCE | **capture `take-c`** | `implemented` | **Real played capture at `b33b06c`**, cropped to the action band, pasted 1:1. Column: 535 frames, 8.88 s, player x 19→184, 195 frames facing left — all read from the take's log. **Last 1.55 s is a held final frame and says so on screen** | 10.48 s |
| **B05** | MECHANISM | `GodotDesignBoard`, layout `cards` | `observed` | Brief lines 117–119 left; a5 / a6 / a7 and a fourth card for what the evidence does **not** prove | 20.48 s |
| **B06** | EVIDENCE | **capture `take-s`** | `implemented` | **Real played capture at `b33b06c`**, cropped tight and doubled with a nearest filter. Column: 4 swings, window opened 4×, 32 live frames, clips 36–36, **enemy scenes 0** — counted at build time. **Last 2.02 s is a held final frame and says so on screen** | 7.52 s |
| **B07** | DESIGN-TELL | `GodotDesignBoard`, layout `zones` | `proposed` | Brief line 288 left; the §B list as four zones — combat that connects, the floor, the frame around it, and a build | 22.06 s |
| **B08** | DESIGN-TELL | `GodotDesignBoard`, layout `flow` | `proposed` | Brief lines 164–166 left; IN → OUT → FIRST → how you know it ran, as a flow | 21.89 s |
| **B09** | DESIGN-TELL | `GodotDesignBoard`, layout `cards` | `pending` | Brief line 179 left; the rule, why it is untested, what it costs if wrong, the mitigation | 33.12 s |
| **B10** | MECHANISM | `GodotDesignBoard`, layout `cards` | `proposed` | Brief lines 255–256 left; have / learning / do-not-know-yet / how I will find out | 20.10 s |
| **B11** | VERDICT | `ClaudeVerdictArtifact` | — | Five lines, all recapitulation. The last names what stayed the author's | 14.44 s |
| **B12** | YOUR-TURN | `ClaudeComposerAsk` | — | A bounded, paste-ready prompt: find the rule you have most evidence for, and name a condition it has never been tested in | 13.57 s |
| **B13** | OUTRO | `ClaudeTitleOutro` | — | The locked card. **No narration**, `audio_policy: "silence"` | 8.00 s |

**Total 234.07 s = 3:54.07.** Assignment 8 asks for 2–4 minutes.

---

## Highlight cues

Every board's card highlights are timed as **fractions of the beat** in
`scripts/build_pitch_beat_sheet.py` and converted to seconds against the
measured narration on the sheet builder's second pass. Nothing is hand-timed,
so a re-recorded line moves its own highlights with it.

## What is reconstructed, and labelled as such

| | |
|---|---|
| B00, B12 | the Claude composer. A reconstruction of the interface, not a screenshot |
| B02–B03, B05, B07–B10 | the document panel. The component prints *"Reconstructed reading view. Exact excerpt; interpretation at right."* on every frame |
| the right-hand diagrams | explanatory cards, never a picture of an unbuilt level |

## What is real engine output

B04 and B06 only — two captures, both PLAYED, both at game-source revision
`b33b06c`, both hashed in `gdd-evidence.json`. **No frame of the Godot editor
appears in this film.**

## What is held rather than played

3.57 s of the 234.07 s: 1.55 s at the end of B04 and 2.02 s at the end of
B06, each a cloned final frame carrying a burned-in label for exactly the
seconds it is frozen.
