# SHOTLIST.md — every shot, what it is, and how it was made

Twenty beats. Five are engine footage, four are composed evidence cards, ten
are Remotion graphics and one is the locked outro. Durations are the measured
narration, which is the film's clock; nothing is cut to a target length.

**Labels used here and on screen.** **PLAYED** — held keys through the real
input map, nothing teleported, no state written. **SCRIPTED** — a signal
emitted directly, which is not gameplay and is labelled as such in the beat's
own title. **FIXTURE** — a capture of a preview scene, not of the game.
**RECONSTRUCTION** — a prompt card that was never sent.

---

| # | Act | Shot | Source | Label |
|---|---|---|---|---|
| B00 | ASK | `ClaudeComposerAsk` | Remotion | RECONSTRUCTION, said aloud |
| B01 | RESULT | `BrutalistHesitantWriter` | Remotion | — |
| B02 | BUILD | `GodotDevWorkbench`, `spike_trap.gd:95-102` | Remotion | Godot editor reconstruction |
| B03 | RESULT | take p, 0.40–9.06 s | engine | **PLAYED**, cropped + framed |
| B03A | RESULT | take r, 0.90–16.00 s | engine | **SCRIPTED**, cropped + framed |
| B04 | BUILD | `GodotDevWorkbench`, `hit_burst.tscn:106-116` | Remotion | Godot editor reconstruction |
| B05 | RESULT | `media/B05.png` | composed card | **FIXTURE** |
| B06 | BUILD | `GodotDevWorkbench`, `dungeon_motes.tscn:45-55` | Remotion | Godot editor reconstruction |
| B07 | RESULT | `media/B07.png` | composed card | **FIXTURE**, one panel mutated |
| B07A | RESULT | take c, 0.30–9.64 s | engine | **PLAYED**, framed, uncropped |
| B07B | RESULT | take c, 10.30–20.13 s | engine | **PLAYED**, framed, uncropped |
| B08 | BUILD | `GodotDevWorkbench`, `particles_generated.gdshader:159-164` | Remotion | Godot editor reconstruction |
| B09 | RESULT | `media/B09.png` | composed card | **FIXTURE**, cropped |
| B10 | BUILD | `GodotDevWorkbench`, `step_dust_driver.gd:112-115` | Remotion | Godot editor reconstruction |
| B11 | RESULT | take p, 1.90–10.58 s | engine | **PLAYED**, cropped + framed |
| B11A | BUILD | `GodotDevWorkbench`, `cost_effects.gd:97-104` | Remotion | Godot editor reconstruction |
| B11B | RESULT | `media/B11B.png` | composed card | recorded tool output |
| B12 | VERDICT | `ClaudeVerdictArtifact` | Remotion | — |
| B13 | TURN | `ClaudeComposerAsk` | Remotion | — |
| B14 | OUTRO | `ClaudeTitleOutro` | Remotion | LOCKED, silent |

---

## The six code → result pairs

The teaching contract is `code-then-result-v1`: every beat that shows a source
excerpt is immediately followed by a narrated beat showing what those lines do
in this game, and the checker verifies the adjacency and the hash of the media
shown. It does not verify that the footage proves the claim; that needs
watching it.

| Code | Result | What the result is |
|---|---|---|
| B02 `spike_trap.gd` | B03 | the burst, on the game's own event, three traps in one walk |
| B04 `hit_burst.tscn` | B05 | the tuning revision, before and after, with the prediction |
| B06 `dungeon_motes.tscn` | B07 | frame one with `preprocess` and frame one without |
| B08 `particles_generated.gdshader` | B09 | the burst growing and dimming, measured |
| B10 `step_dust_driver.gd` | B11 | the trail, and the mirror on the turn |
| B11A `cost_effects.gd` | B11B | the recorded cost table, two runs |

## Framing decisions, stated

**Three beats are cropped.** B03, B03A and B11 take logical x 107–533,
y 80–320 of the 640 × 360 room and rescale it to 3840 × 2160 with
nearest-neighbour. The window is derived from the room — traps at x 208, 320,
432, detect zones spanning x 175–465, the player 16 × 28 on a floor whose top
edge is y 200 — and not eyeballed. A 24-pixel burst in an uncropped 4K frame
of this game is four pixels of a slide.

**Two beats are not cropped.** B07A and B07B are the mote field, which is the
whole room; cropping it would hide whether the field is even, which is the one
thing those shots exist to show.

**All five are framed**, inset on the brand ground with the numbers their own
take log recorded. The reason is measured and is A5's finding, repeated here:
the visual-QC gate counts a pixel as content when it differs from the
background by more than 28 in some channel, and this game's floor is `#16242B`
against a `#17141B` sky — a largest channel difference of 16. The floor is not
content as far as the checker is concerned, so a full frame of this room
measures underfilled however it is cropped. The two honest options were to
brighten the capture, which would misreport what the engine drew, or to frame
it. The low contrast is a design requirement, not an accident: the armed trap
is deliberately hard to see from across the room.

**Nothing is brightened, retimed, composited or re-ordered.** The pixels that
remain in every shot are the pixels the engine drew, at their own values.

**Two beats share take p and two share take c**, at overlapping windows. That
is deliberate: the burst and the step dust happen in the same unbroken walk,
and showing them as one take rather than two is the honest version. Every
window is in `beat_sheet.json`.

**Holds.** `scripts/build_media_clips.py` cuts each clip to the frame and pads
any remainder with a cloned final frame rather than slowing the action. One
beat has a hold worth mentioning: B03A holds its last frame for 1.13 s of a
16.23 s beat, because take r is 16.05 s long and the narration over it is
16.23. The other four hold for under a fiftieth of a second.

## What is not in this film

- No Short, no vertical companion, no publication.
- No paid media generation. Narration is local Kokoro, $0.00.
- No game change made to film better. The one game-source file this film
  added is the capture driver, and it reads state and writes none.
- No on-screen captions; none were requested.
