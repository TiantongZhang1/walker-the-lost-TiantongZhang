# SHOTLIST.md — the visible sequence, written before the narration

What is on screen and when. The narration was written against this, not the
other way round, so a beat that has nothing to show does not exist.

15 beats, ~7 minutes estimated. Timings are fractions of each beat's own
measured length, replaced by the timing pass once Kokoro has spoken.

---

| # | act | surface | what you see |
|---|---|---|---|
| **B00** | ASK | `ClaudeComposerAsk` | Composer card fades in · greeting lands · the Walker prompt types on · `RECONSTRUCTION` label holds for the whole beat |
| **B01** | RESULT | `BrutalistHesitantWriter` | Four lines write on · "turns" is struck through and "ramps" written in its place · the four counts land |
| **B02** | BUILD | `GodotDevWorkbench` code | All 7 lines of `trap_warning.gdshader` at font 26 · line 2 highlights (the driven uniform) · line 3 (the warning red) · line 6 (the one line that changes a colour) |
| **B03** | RESULT | **FOOTAGE** take-w 1.40–2.45 s | The trap is flush and nearly invisible · red begins while the player is still short of it · full red with the player centred · the spikes arrive |
| **B04** | BUILD | `GodotDevWorkbench` code | `trap_warning_driver.gd` 62–76 · line 65 highlights (this trap's own parameter block) · line 68 (ask the shader what it declares) · line 76 (state in, uniform out) |
| **B05** | RESULT | **FOOTAGE** take-w 1.40–4.70 s | Trap one warns while two and three stay flush · trap one retracts · trap two takes the red · trap three, with the first two dark |
| **B06** | BUILD | `GodotDevWorkbench` code | `hint_bands.gdshader` 1–7 at font 26 · line 2 highlights (`unshaded`) · line 4 (this one decodes) · line 5 (this one does not) |
| **B07** | RESULT | `GodotDevWorkbench` asset | The two quads, one real frame · the measured table reveals beside the prediction · 64 → 137 marked as the largest error |
| **B08** | BUILD | `GodotDevWorkbench` code | `dungeon_surface.gdshader` 15–27 · line 17 highlights (how submerged) · line 23 (darkened where water pools) · line 26 (dry to wet, same mask) |
| **B09** | RESULT | `GodotDevWorkbench` asset | The two slimes side by side · the highlight on the flooded one is marked · the sweep numbers reveal, including the dry slime's twelve identical rows |
| **B10** | BUILD | `GodotDevWorkbench` code | Only lines 4–5 of `hint_bands.gdshader`, font 30 · `source_color` highlights on line 4 · the two lines are then shown as the engine sees them: identical |
| **B11** | RESULT | `GodotDevWorkbench` asset | The same scene with the hint deleted — both quads identical · the table reveals and the left column has moved · `SHADER ERROR: 0` is marked |
| **B12** | VERDICT | `ClaudeVerdictArtifact` | Four columns appear · the measured column fills · the open column holds to the end |
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

| pair | code | result | media |
|---|---|---|---|
| C1 | B02 | B03 | `capture/take-w.mp4` |
| C2 | B04 | B05 | `capture/take-w.mp4` |
| C3 | B06 | B07 | `media/B07-hint-experiment.png` |
| C4 | B08 | B09 | `media/B09-two-materials.png` |
| C5 | B10 | B11 | `media/B11-hint-mutated.png` |

## Labels that must stay on screen

- **B00** — `RECONSTRUCTION`. The prompt was never sent.
- **B02, B04, B06, B08, B10** — "Godot editor reconstruction" with the source
  path and line range. These are teaching views, not recordings of a live
  editing session.
- **B07, B09, B11** — "Engine capture — real windowed run, Forward+, RTX 5080".
  These are not reconstructions; they are the frames the GPU drew.
- **B11** additionally says, in narration, that the source was deliberately
  mutated for that capture and restored afterwards.

## Readability

Code beats run at font 23, and the two that carry the fewest lines run at 26
and 30. No beat shrinks the game to keep an editor chrome around it. The two
footage beats are the full 4K frame with no overlay, because the thing to
watch is three traps at once and cropping to one would destroy the point of
B05.
