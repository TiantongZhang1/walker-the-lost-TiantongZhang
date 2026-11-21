# SHOTLIST.md — every shot, what it is, and how it was made

Eighteen beats. Three are engine footage, four are composed evidence cards,
ten are Remotion graphics and one is the locked outro. Durations are the
measured narration, which is the film's clock; nothing is cut to a target
length.

**Labels used here and on screen.** **PLAYED** — held keys through the real
input map, nothing teleported, no state written, no clip seeked.
**FIXTURE** — a capture of a preview scene, not of the game.
**RECONSTRUCTION** — a prompt card that was never sent.

**There is no SCRIPTED label in this film, and that is a fact about the
subject rather than a virtue.** Assignment 6 needed one: three particle
bursts alive at once cannot be produced by walking the room, so the take that
showed the ceiling emitted the signal directly and said so in its own title
card. Nothing in Assignment 7 is like that. A clip plays because a key was
pressed, so every take here is held keys and the question never came up.

---

| # | Act | Shot | Source | Label |
|---|---|---|---|---|
| B00 | ASK | `ClaudeComposerAsk` | Remotion | RECONSTRUCTION, said aloud |
| B01 | RESULT | `BrutalistHesitantWriter` | Remotion | — |
| B02 | BUILD | `GodotDevWorkbench`, `animations/legs.tres:24-38` | Remotion | Godot editor reconstruction |
| B03 | RESULT | take c, 0.60–7.70 s | engine | **PLAYED**, cropped + framed |
| B04 | BUILD | `GodotDevWorkbench`, `animations/player.tres:110-121` | Remotion | Godot editor reconstruction |
| B05 | RESULT | take s, 0.45–5.25 s | engine | **PLAYED**, cropped + framed |
| B06 | BUILD | `GodotDevWorkbench`, `tests/test_player_clips.gd:217-230` | Remotion | Godot editor reconstruction |
| B07 | RESULT | `media/B07.png` | composed card | **PLAYED** frames, cropped |
| B08 | BUILD | `GodotDevWorkbench`, `tests/measure_clocks.gd:131-138` | Remotion | Godot editor reconstruction |
| B09 | RESULT | `media/B09.png` | composed card | recorded tool output |
| B10 | BUILD | `GodotDevWorkbench`, `features/player/player.gd:111-118` | Remotion | Godot editor reconstruction |
| B11 | RESULT | take m, 0.50–7.60 s | engine | **PLAYED**, cropped + framed |
| B12 | BUILD | `GodotDevWorkbench`, `tests/test_swing_edges.gd:428-438` | Remotion | Godot editor reconstruction |
| B13 | RESULT | `media/B13.png` | composed card | **PLAYED** frames, cropped |
| B14 | TURN | `media/B14.png` | composed card | **FIXTURE** frames, cropped |
| B15 | VERDICT | `ClaudeVerdictArtifact` | Remotion | — |
| B16 | TURN | `ClaudeComposerAsk` | Remotion | — |
| B17 | OUTRO | `ClaudeTitleOutro` | Remotion | LOCKED, silent |

---

## The six code → result pairs

The teaching contract is `code-then-result-v1`: every beat that shows a source
excerpt is immediately followed by a narrated beat showing what those lines do
in this game, and the checker verifies the adjacency and the hash of the media
shown. **It does not verify that the result proves the claim.** That is this
document's job and `FACTCHECK.md`'s.

| Pair | Code | Result | What the result is actually evidence of |
|---|---|---|---|
| 1 | `legs.tres:24-38` | take c | that the cycle reads as a gait, in both facings, with the dust landing on the footfall. **Not** that 0.500 s is derived — that is arithmetic and the panel shows it. |
| 2 | `player.tres:110-121` | take s | that the three phases are distinguishable in play. **Not** that the window opens at 0.200 — a hitbox contributes no pixels and this footage cannot show it. That is pair 4's job. |
| 3 | `test_player_clips.gd:217-230` | `media/B07.png` | both players' track lists, read out of the resources as text, and two frames showing the two leg clips under one body clip. |
| 4 | `measure_clocks.gd:131-138` | `media/B09.png` | the recorded run, in both tick modes, including the line about what it cannot see. |
| 5 | `player.gd:111-118` | take m | that the jump happens mid-swing and the character keeps swinging. **Not** that the clip was untouched — that is pair 6. |
| 6 | `test_swing_edges.gd:428-438` | `media/B13.png` | two frames at the same playhead, one grounded and one airborne, beside the 0.000000 s the comparison reports. |

**Pairs 2 and 5 are deliberately weaker than they look, and the table says
so.** Footage of a swing cannot show when a hitbox opened, and footage of a
jump cannot show that a clock did not move. Both claims are carried by a
later pair. A film that let the footage stand for the claim would be doing
the thing this film is about.

---

## Framing decisions, per shot

**Every footage beat is cropped and nothing else.** No retiming, no speed
change, no colour correction, no compositing. The takes are 3840 × 2160 of a
640 × 360 game — an integer 6× of nearest-filtered pixel art — so a crop
moves the frame and changes no pixel value.

| Beat | Window | Why that window |
|---|---|---|
| B03 | take c, 0.60–7.70 | starts after the fall settles, ends before the last stop. Covers both facings and at least four full cycles. |
| B05 | take s, 0.45–5.25 | the whole take minus the settle. Four swings in five seconds is what a half-second gap between fresh presses gives. |
| B11 | take m, 0.50–7.60 | the two travelling swings and the first jumped one. The second jumped swing, the one taken while running, is past the end of the narration and is not shown. |

**B11 leaves footage unused on purpose.** The window ends where the narration
ends. `scripts/build_animation_beat_sheet.py` clamps every window to the
measured narration rather than padding the beat with a frozen frame, and the
first build of this sheet was caught doing the opposite: B05's narration ran
8.4 s past its take.

---

## The evidence cards

Each is 3840 × 2160, composed by `scripts/compose_animation_evidence.py`, and
**every figure on them is computed at build time** from the committed
resources, the committed take logs and the recorded evidence files. Delete a
frame or a resource and the script stops rather than drawing a stale number.
The same measurements are written to `evidence/a7/*.txt` so a reviewer can
read them as text.

- **B07** — the two players' track paths, parsed out of `player.tres` and
  `legs.tres` as resource text. The same fact is read through the engine by
  `test_player_clips.gd`; two routes to one fact, and they agree.
- **B09** — `evidence/a7/clocks.txt`, verbatim, beside the last frame with the
  hitbox off and the first with it live.
- **B13** — the two frames are **found by searching take m's own log** for a
  grounded frame and an airborne frame whose playheads agree to within a
  millisecond. If no such pair existed the script would stop; it did not pick
  a flattering frame.
- **B14** — r1's windmill and r4's shipped strike at the same table frame,
  from the frame strips the author judged, beside the ten-revision table.

---

## What is a reconstruction, and where it is said

**B00 and B16 are prompt cards that were never sent.** Both say so on screen
and B00 says it aloud in the first breath. The work in this repository was
done through many turns of conversation over six days; a single prompt card is
an illustration of the shape of the ask, not a transcript, and
`PROMPTS.md` holds what was actually said.

**The `GodotDevWorkbench` panels are a reconstruction of an editor, not a
screenshot of one.** The code in them is real and byte-exact — the ledger
re-reads every range from disk — but the surrounding chrome is drawn by
Remotion. No frame of the Godot editor appears in this film.
