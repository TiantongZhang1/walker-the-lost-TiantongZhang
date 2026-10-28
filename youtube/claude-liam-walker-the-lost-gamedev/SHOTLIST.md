# SHOTLIST.md — the visible sequence, written before the narration

What is on screen and when. The narration was written against this, not the
other way round, so a beat that has nothing to show does not exist.

**18 beats, 7:58 of measured narration.** Timings inside a beat are fractions
of that beat's own measured length; the cue times in the beat sheet are those
fractions multiplied by the narration Kokoro actually produced.

---

| # | act | surface | what you see |
|---|---|---|---|
| **B00** | ASK | `ClaudeComposerAsk` | Composer card fades in · greeting lands · the Walker prompt types on · `RECONSTRUCTION` label holds for the whole beat |
| **B01** | RESULT | `BrutalistHesitantWriter` | Four lines write on · "turns" is struck through and "ramps" written in its place · the four counts land |
| **B02** | BUILD | `GodotDevWorkbench` code | All 7 lines of `trap_warning.gdshader` at font 26 · line 2 highlights (the driven uniform) · line 3 (the warning red) · line 6 (the one line that changes a colour) |
| **B03** | RESULT | **FOOTAGE** take-w 1.40–2.45 s | The trap is flush and nearly invisible · red begins while the player is still short of it · full red with the player centred · the spikes arrive |
| **B03A** | RESULT | **CARD** `media/B03A.png` | The four controlled captures — `warn_amount` 0.0, 0.5, 1.0, 2.0 — in a 2×2 grid, with `REPORT.txt`'s predicted-against-measured table verbatim beneath them · the 2.0 row is marked: pixel B goes pure red, where a clamp would have given `214, 60, 47` |
| **B04** | BUILD | `GodotDevWorkbench` code | `trap_warning_driver.gd` 62–76 · line 65 highlights (this trap's own parameter block) · line 68 (ask the shader what it declares) · line 76 (state in, uniform out) |
| **B05** | RESULT | **FOOTAGE** take-w 1.40–4.70 s | Trap one warns while two and three stay flush · trap one retracts · trap two takes the red · trap three, with the first two dark |
| **B06** | BUILD | `GodotDevWorkbench` code | `hint_bands.gdshader` 1–7 at font 26 · line 2 highlights (`unshaded`) · line 4 (this one decodes) · line 5 (this one does not) |
| **B07** | RESULT | **CARD** `media/B07.png` | The two quads, one real frame · `HINT-REPORT.txt` verbatim below it · 64 → 137 marked as the largest error |
| **B08** | BUILD | `GodotDevWorkbench` code | `dungeon_surface.gdshader` 15–27 · line 17 highlights (how submerged) · line 23 (darkened where water pools) · line 26 (dry to wet, same mask) |
| **B09** | RESULT | **CARD** `media/B09.png` | The two slimes side by side · `SWEEP-REPORT.txt`'s baseline row and two of the four swept uniforms, verbatim · the dry slime's identical readings |
| **B10** | BUILD | `GodotDevWorkbench` code | Only lines 4–5 of `hint_bands.gdshader`, font 30 · `source_color` highlights on line 4 · the two lines are then shown as the engine sees them: identical |
| **B11** | RESULT | **CARD** `media/B11.png` | The same scene with the hint deleted — both quads identical · the mutated run's table, verbatim, with the left column moved · `SHADER ERROR: 0` |
| **B11A** | BUILD | `GodotDevWorkbench` code | `standard_generated.gdshader` 3–15 — the only shader here nobody wrote by hand · line 3 highlights (`shader_type`, and there is no `main()`) · line 7 (colour sampler, `source_color`) · line 14 (data sampler, a channel hint and no `source_color`) · two notes put each beside its equivalent in the hand-written `dungeon_surface.gdshader` |
| **B11B** | RESULT | **CARD** `media/B11B.png` | All four non-texture uniforms at both ends of their range, eight frames · each uniform's min and max rows from `SWEEP-REPORT.txt`, verbatim · the dry slime holding at 50, 56, 55 throughout |
| **B12** | VERDICT | `ClaudeVerdictArtifact` | Twelve lines fill in: what was measured, what is reasoning, the texture sources, the revision the film was shot from, the two mistakes caught in Claude's own work, and the one next step |
| **B13** | TURN | `ClaudeComposerAsk` | The composer card returns · the prompt types on · the bounded exercise holds while Liam signs off |
| **B14** | OUTRO | `ClaudeTitleOutro` | Locked card: exact title, `@NikBearBrown`, one slug-seeded mascot, no subline, stock jingle. No narration, no game SFX. |

---

## Read-the-code, then watch-the-result

Every `BUILD` beat is a code panel and the beat immediately after it is the
thing those lines produce. No beat shows code and its result at the same
time, and no two code beats sit next to each other. The ledger enforces both:
`build_lost_ledger.py` refuses to write if a code beat's successor is another
code beat or has no narration, and the official checker verifies adjacency
and hash-bound result media.

| pair | code | result | the result's media |
|---|---|---|---|
| C1 | B02 | B03 | `capture/take-w.mp4` |
| C2 | B04 | B05 | `capture/take-w.mp4` |
| C3 | B06 | B07 | `media/B07.png` |
| C4 | B08 | B09 | `media/B09.png` |
| C5 | B10 | B11 | `media/B11.png` |
| C6 | B11A | B11B | `media/B11B.png` |

**B03A is a result beat without a code beat of its own**, deliberately. It is
B03's evidence, in numbers, and B03 already has B02 in front of it; adding a
seventh code panel to introduce a table would have put two code beats three
apart with nothing between them. The ledger counts six pairs, not seven.

## The five evidence cards are not workbench beats, and here is why

B03A, B07, B09, B11 and B11B are full-frame 3840 × 2160 PNGs composed by
`scripts/compose_lost_evidence.py` and rendered by the compiler's STILL path
with `motion: "hold"` — no Ken Burns, because a table of measured numbers must
not drift. Two reasons they are not `GodotDevWorkbench` asset beats, both found
by rendering a beat and looking at it:

1. The workbench's `asset` mode lays out `{code}{image}`, so putting a measured
   table beside the capture means a non-empty `code` prop — and
   `verify_gamedev.py:68` requires every workbench beat with a non-empty `code`
   to carry a source-excerpt record *and* to be the code half of a
   code-then-result pair. A table of measurements is neither, so the official
   check failed with `Displayed code lacks an excerpt record`. Leaving `code`
   empty passes the check and renders half a frame of empty dark panel with a
   stray line number in it.
2. The workbench's chrome reads "Godot editor reconstruction · source-backed
   teaching view". That is the right label for the code beats. It is the wrong
   label for these: they are frames a real GPU drew in a windowed run, and the
   section below has always said so.

Every figure on those five cards is read out of the recorded report at build
time and drawn verbatim. None of it is typed into the compositor. Change a
report and the card changes with it, and the ledger's hash changes too.

## Labels that must stay on screen

- **B00** — `RECONSTRUCTION`. The prompt was never sent.
- **B02, B04, B06, B08, B10, B11A** — "Godot editor reconstruction" with the
  source path and line range. These are teaching views, not recordings of a
  live editing session.
- **B11A** additionally says, in narration, that this one file is Godot's own
  output from *Convert to ShaderMaterial* and was saved unedited — it is the
  only shader in the film nobody wrote by hand.
- **B03A, B07, B09, B11, B11B** — each card's own footer names the capture
  file, the date, the renderer and the GPU. These are not reconstructions;
  they are the frames the GPU drew.
- **B11** additionally says, in narration, that the source was deliberately
  mutated for that capture and restored afterwards.

## The two gameplay beats are cropped and framed, and here is exactly how

Gate V measured B03 and B05 at **47 % of the title-safe area** and **0.11
contrast**, and both numbers are properties of the game rather than of the
framing. The checker counts a pixel as content when it differs from the
background by more than 28 in some channel; this room's floor is `#16242B`
against a `#17141B` sky, a largest-channel difference of **16**, so the floor
does not count. Only the player, the traps and the grid lines do.

Two changes, neither of which alters a pixel value:

1. **Cropped** to the band the action happens in — logical `x 107..533`,
   `y 80..320`, derived from the detection zones (`x 175..465`) and the
   player's walking height, opened out to 16:9 and rescaled with nearest
   neighbour because the game is nearest-filtered pixel art.
   `scripts/crop_footage_beats.py`; the uncropped trims are kept beside the
   clips as `B03-uncropped.mp4` and `B05-uncropped.mp4`.
2. **Framed** on the brand ground with the beat's title and the take's own
   recorded numbers beside it — `scripts/frame_footage_beats.py`. The numbers
   are computed from `capture/logs/take-w-inputs.jsonl` at build time.

Cropping alone moved neither measurement. The frame is what fixed them, and
it fixed them by adding the film's own chrome rather than by touching the
capture. **The low contrast inside the inset is still there, and should be**:
`CHANGE-BRIEF.md` §6 puts the armed trap at 1.12 : 1 against the floor on
purpose, because a trap visible from across the room is not a trap.

## Readability

Code beats run at the component's minimum font of 23, and the two that carry
the fewest lines run at 26 and 30. Four capacities govern this film, and every
one was measured off a rendered frame rather than guessed:

- the code panel holds about **13 wrapped rows** at font 23 - rows, not source
  lines, because a long `uniform` declaration wraps to two;
- the notes column holds **2** cards and about **8 wrapped rows of value text
  between them**, roughly 160 characters;
- the verdict card holds about **8** lines before it outgrows the frame;
- a hesitant-writer context card holds **2** rows of detail.

Each was found by overflowing it. B11A was first written as eighteen lines at
font 20 - below the schema's own minimum, which Remotion accepted without
complaint - and the render clipped at line 17, throwing away the half of the
comparison the beat exists for and two of its three notes. B08's second note
was cut off mid-word. B12's twelve-line card grew past the frame and covered
the `@NikBearBrown` handle; that one Gate V did catch, as `edge-bleed`. B01's
three context cards each clipped their third row. The content came down to the
panel, never the other way round.

No beat shrinks the game to keep an editor chrome around it. The two footage
beats are the full 4K frame with no overlay, because the thing to watch is
three traps at once and cropping to one would destroy the point of B05.
