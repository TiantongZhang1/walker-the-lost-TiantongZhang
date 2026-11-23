# SHOTLIST.md — every shot, what it is, and how it was made

Twelve beats, **4:15**. Six are engine footage, one is a composed still,
four are Remotion bookends and one is the locked outro.

**81.5 seconds of the film — a third of it — is moving gameplay at normal
speed**, plus 17.8 s of labelled final-frame hold. That ratio is the number
to argue with, and it is printed by the builder on every run.

**Labels used here and on screen.** **SCRIPTED INPUT** — held keys and taps
through the real input map, nothing teleported, no clip seeked, no
test-only shortcut called. **It is not a human playtest**, and the author's
own play verdicts are in `TUNING.md` rather than in this film's footage.
**RECONSTRUCTION** — a prompt card that was never sent.

---

| # | Act | Shot | Source | Label |
|---|---|---|---|---|
| B00 | ASK | `ClaudeComposerAsk` | Remotion | RECONSTRUCTION, said aloud |
| B01 | RESULT | `BrutalistHesitantWriter` | Remotion | — |
| B02 | BUILD | take a, 0.30–11.00 s | engine | **SCRIPTED INPUT**, left half, 1:1 |
| B03 | BUILD | take a, 11.00–26.10 s | engine | **SCRIPTED INPUT**, left half, 1:1 |
| B04 | BUILD | take b, 1.00–7.25 s | engine | **SCRIPTED INPUT**, left half, 1:1 |
| B05 | BUILD | take b, 7.25–16.20 s | engine | **SCRIPTED INPUT**, left half, 1:1 |
| B06 | BUILD | take c, 1.32–18.20 s | engine | **SCRIPTED INPUT**, whole room, 3× |
| B07 | RESULT | take d, 1.63–25.20 s | engine | **SCRIPTED INPUT**, whole room, 3× |
| B08 | RESULT | `media/B08.png` | composed still | fixture captures, cropped |
| B09 | VERDICT | `ClaudeVerdictArtifact` | Remotion | — |
| B10 | TURN | `ClaudeComposerAsk` | Remotion | — |
| B11 | OUTRO | `ClaudeTitleOutro` | Remotion | LOCKED, silent |

## Framing, and the two shapes it takes

Every gameplay beat is **inset in a card**, not shown full-bleed. Gate V
refused the first compile with fourteen BLOCKERs and thirteen MAJORs, all on
the gameplay, and both reasons were true of the footage rather than faults in
it: full-bleed gameplay touches the title-safe edge by definition, and this
room is `#16242B` floor against a `#17141B` sky — a largest channel
difference of 16 against the gate's threshold of 28, so a dungeon measures as
having almost no content ink. The two honest options were to brighten the
capture, which would misreport what the engine drew, or to frame it.

**Then the framing changed shape once more, and the reason is worth keeping.**
The first framed cut put the whole 640 × 360 room at 3× inside the inset, and
the character came out **84 pixels tall in a 2160-pixel frame — four per cent
of the height — in a film whose subject is whether you can see its legs
alternate.** So:

| beats | framing | why |
|---|---|---|
| B02–B05 | the room's **left half**, 320 × 180 logical, at the capture's own 6×, **pasted 1:1** | take a runs x 5…174 and take b stands at 96. The player never leaves that half, and the character is twice the size |
| B06–B07 | the **whole room** at 3× | take c reaches x 357 and take d reaches x 491. The crossing *is* what those beats show |

**Which beats crop is decided by measurement, not taste** — the player's x
range is read out of each take's log, and `frame_walkthrough_footage.py`
refuses a crop whose size does not land on the inset at an integer scale.
There is no third option: 320 × 180 at 6× and 640 × 360 at 3× are the only
sizes that give the inset exactly, and anything between them produces a
2-1-2-1 pixel pattern that is visible on a 28-pixel figure.

**Nothing is retimed, brightened, retinted or composited.** The full-bleed
originals are kept beside each beat as `media/<BID>-fullbleed.mp4`.

---

## The six gameplay beats, and what each one is evidence of

| Beat | Action | Hold | Features it carries |
|---|---|---|---|
| B02 | 10.70 s | 2.70 s | idle at rest; the run cycle looping; the facing mirroring the rig; step dust on the footfall |
| B03 | 15.10 s | 2.68 s | rising and falling; a jump taken at speed; **the floating key** — the simple animation |
| B04 | 6.25 s | 2.83 s | the swing's three phases; that it commits |
| B05 | 8.95 s | 3.15 s | **the edge**: an attack during a startup (ignored) and during a recovery (buffered) |
| B06 | 16.88 s | 1.80 s | a swing that travels; a swing jumped out of |
| B07 | 23.57 s | 4.60 s | the trap's warning and strike; damage not interrupting; **death**, the fifth state |

**Every one of those sixteen features has an evidence window in
`coverage.json`, and every window's times were read off the take's own log**
— the frame a clip became current, the frame a facing flipped, the frame
health dropped — rather than counted forward from the driver's sleeps. The
builder refuses to write if an evidence window falls outside the beat that
is supposed to play it.

---

## Where the holds are, and why they are allowed

The skill's rule is that extra narration time becomes **a labelled
final-frame hold**, never a slowed or re-cut action. Every hold in this film
is one, and `build_media_clips.py` writes it as `shot.hold_s` so it is in the
sheet rather than invisible.

**The rule bounding them took three attempts, and the first two were the
wrong shape:**

1. *Narration ≤ 1.15 × action.* Wrong shape: 1.15× of a sixty-second beat is
   a nine-second still, while 1.3× of a six-second beat is under two.
2. *…and ≤ 30 % of the action.* Flagged two beats whose holds were 2.8 and
   3.2 seconds — short enough that nobody would notice, on actions short
   enough that the percentage looked bad.
3. **A hold is never longer than five seconds, and never longer than the
   action it follows.** Both halves are needed: the first alone would allow
   four seconds of still after four seconds of play.

The longest hold in the film is **4.60 s**, at the end of B07, over the held
death pose — which is a frame that is *supposed* to sit still.

---

## What is a reconstruction, and where it is said

**B00 and B10 are prompt cards that were never sent.** B00 says so on screen
and aloud in its first breath. The work was done across many turns over eight
days; `PROMPTS.md` holds what was actually asked, including the ten tuning
requests in the author's own words.

**There is no footage of the Godot editor in this film**, and no rebuilt or
re-drawn version of the game. Every pixel of gameplay is what the engine
drew.
