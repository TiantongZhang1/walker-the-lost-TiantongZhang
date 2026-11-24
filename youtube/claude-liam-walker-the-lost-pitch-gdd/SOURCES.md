# SOURCES.md — what is in this film, where it came from, and who made it

**Assignment 8 · The Lost: Floor One · Tiantong Zhang**

Game-source revision **`b33b06c`**. Both captures in this film were recorded
at that revision; `git diff b33b06c..a8 -- godot/` is the check that nothing
under `godot/` moved afterwards. **Assignment 8 changed no game code at all** —
it adds a pitch folder, a reel and three build scripts, and nothing else.

---

## 1. The document this film walks through

**`pitch/PROJECT-BRIEF.md`, not `../the-lost-gdd/GDD.md`.**

The `godot-gdd` workflow walks through a design document. This project has
two, and they are not interchangeable:

| | |
|---|---|
| `../the-lost-gdd/GDD.md` | the whole four-floor game. Assignment 4's deliverable. **In no git repository** — `PROJECT-BRIEF.md` §A lists that as a gap rather than hiding it |
| `pitch/PROJECT-BRIEF.md` | **the project being pitched**: floor one, one boss, a desktop export |

A pitch film is a walk through the pitch. The GDD is quoted inside the brief
where it is used — for the cut rule at `GDD.md:414` and for the renderer row
at `GDD.md:369` that contradicts `project.godot` — and `gdd-evidence.json`
hashes the brief, because the brief is the document on screen.

**Every excerpt is read out of the brief by line number at build time**, by
`scripts/build_pitch_beat_sheet.py`, and `scripts/build_pitch_ledger.py`
re-reads the same lines and refuses to write a ledger if what a beat displays
and what the brief says have drifted apart. The checker then compares all
three a third time. There is no copy of any quotation typed into this film.

## 2. The two engine captures

**Both are re-used from Assignment 7's reel, with their input logs**, rather
than re-recorded. They are the same game at the same revision; recording them
again would have produced different frames of identical evidence and cost an
hour this assignment did not have. The re-use is why they are listed here
with the driver that made them.

| Take | Frames | Length | What it asserts before a frame of it counts |
|---|---|---|---|
| `take-c` | 535 | 8.88 s | ≥ 5 cycle wraps, both facings, ≥ 12 distinct dust puffs, **and zero swings** |
| `take-s` | 329 | 5.45 s | exactly 4 swings, the window opening exactly 4 times, every clip 34–38 physics frames |

**Both are PLAYED.** Held keys, parsed through the real input map by
`godot/tests/capture_animation.gd`. Nothing is teleported, no state is
written, no clip is seeked. **A render is evidence only if it printed
`CAPTURE OK`**: each take asserts its own outcome and exits nonzero otherwise,
so a completed render is not by itself the claim.

`take-c` never crosses a trap, deliberately — the driver paces the clear
stretch west of the first one, so the figure ends the take undamaged. A take
about the game's feel that ends in the death pose is a take about two things.

### What was done to the footage, and what was not

| | |
|---|---|
| **Cropped** | yes. The room is 640 × 360 and the subject is a 28-pixel figure, so a 4K frame is mostly empty wall. The crop is checked against the take's own measured player range at build time |
| **Resampled** | **no.** B04 crops 368 × 154 logical = 2208 × 924 at the capture's 6× and is pasted 1:1. B06 crops 184 × 77 = 1104 × 462 and is **doubled with a nearest filter**, an exact doubling on nearest-filtered pixel art |
| **Brightened, retimed, re-ordered, composited** | **no** |
| **Slowed** | **no.** Both run at the rate they were recorded |
| **Held** | **yes, and labelled on screen.** See below |

### The held frames, which are labelled because they are not play

`scripts/build_media_clips.py` pads a beat whose narration outruns its take
with a cloned final frame. B04 holds **1.55 s** and B06 holds **2.02 s** —
3.57 s of the film's 229.6 s.

Assignment 8 asks for scripted captures and slowed replays to be labelled.
A frozen frame is neither, but it is still screen time in which nothing is
being played, so **it carries a burned-in label for exactly the seconds it is
frozen**, gated on the clip's own end time, with the figure read out of the
beat sheet. A viewer who cannot tell play from a still has been misled whether
or not anyone meant it.

> The label is an overlaid PNG and **not** ffmpeg's `drawtext`. The first
> version used `drawtext`; this ffmpeg build has no fontconfig and the filter
> **crashed the process** rather than failing, which would have silently
> dropped the label on exactly the machines that needed it.

## 3. The seven document boards

`GodotDesignBoard`, the toolkit's own GDD teaching component, seven times with
four different layouts. Each one shows an exact excerpt of the brief on the
left and a labelled interpretation on the right, and carries a status band:

| Status | Means | Beats |
|---|---|---|
| `implemented` | exists in the repository today | B04, B06 |
| `observed` | exists **and was measured** | B05 |
| `comparison` | a claim about another game, named by the author | B03 |
| `proposed` | **does not exist** | B02, B07, B08, B10 |
| `pending` | a question nothing has answered | B09 |

**The right-hand panels are explanatory diagrams, not screenshots.** The
component says so in its own footer on every frame: *"Reconstructed reading
view. Exact excerpt; interpretation at right."* No frame of the Godot editor
appears in this film, and no mock-up of an unbuilt level appears anywhere —
the unbuilt parts of this project are shown as **lists and labels**, never as
pictures of a game that does not exist.

## 4. Narration

| | |
|---|---|
| Voice | `am_onyx`, Kokoro, run locally |
| Generated by | `runtime/scripts/generate_audio_kokoro.py` in the brutalist toolkit |
| Cost | **$0.00** — no paid generation, no API key, no media account |
| Files | `mp3/beat-B00.mp3` … `beat-B12.mp3`, 13 beats |
| Not generated | `B13`, the locked outro, which carries `audio_policy: "silence"` |

**The narration is first person and speaks as Tiantong Zhang.** Assignment 8
allows AI narration but requires it to speak as the author, so this film does
not use the toolkit's default "Liam, in for Bear" framing and the instructor's
name and persona appear nowhere in it.

> **One thing I could not change, and am naming rather than leaving to be
> found.** The outro card is `ClaudeTitleOutro`, which the toolkit locks in
> `OUTRO-LOCK.md` with a hardcoded `@NikBearBrown` handle. It is a toolkit
> lock on a rendered card, not a credit line this submission is claiming, and
> no narration plays over it. `pitch/FRICTIONAL.md` records the tension with
> the assignment's "do not use the instructor's credit line" rule.

**The measured durations are the film's clock.** Nothing is cut to a target
length; the beat sheet's second pass re-authors every cue and every footage
window against the measured seconds. The first-pass estimates are **derived**
from 3.533 words per second — 2168 narrated words across 613.7 s of
Assignment 6's finished sheet — rather than hand-typed.

## 5. The game's own assets, and their licences

Unchanged from Assignment 7's statement; `ATTRIBUTION.md` is the full record.
What this film puts on screen:

| Asset | Origin | Licence |
|---|---|---|
| The seven pose PNGs behind the sprite sheet | generated with GPT-6 for `walker-ninja-TiantongZhang`, 2026-10 | mine, credited in `ATTRIBUTION.md`; **unmodified on disk**, the sheet is cut from them and the cut is asserted lossless |
| `player_sheet.png`, `leg_front.png`, `leg_back.png`, `sword.png` | written by `tools/make_sprites.py` in this repository | mine |
| The room's tiles | written by `godot/tools/write_textures.gd` | mine |
| `sfx-*.ogg` | synthesised by `scripts/synth_placeholder_sfx.py` | mine |
| `music-loop.ogg` | **Suno**. Suno retains ownership | **personal / non-commercial only.** Not a free-licence asset and not presented as one. **It is not audible in this film** — the captures are rendered without the music bus |

**No asset in this film was downloaded from an asset library and no 3D
generator was used.** No copyrighted character, brand, logo or commercial
music appears. **Hollow Knight is named in the narration and in one card as a
comparable game the author has played; no footage, art, audio or trademark of
it appears**, and the comparison is a statement about two design structures,
not a market claim.

## 6. What Claude contributed, and what did not come from Claude

| Claude did | The author did |
|---|---|
| Read the repository and the GDD, and drafted `pitch/PROJECT-BRIEF.md` | **Chose the project**, and settled the four items the first draft left open |
| Proposed candidate comparables | **Named Hollow Knight**, as a game they have played. Claude must not supply that and did not |
| Proposed "gameplay programmer" from the evidence | **Confirmed the target role** |
| Proposed desktop-or-web pending a measurement | **Decided desktop only**, which is what retires the renderer risk |
| Wrote the three build scripts, the beat sheet, the ledger and this reel's documents | Reviewed the draft brief and sent corrections before any of it was built |
| Mapped sections to beats, hashed the evidence, ran the checks | **Owns the scope, the honesty of it, and whether any of it is worth playing** |

**The risk in §6 of the brief is derived from this repository's own revision
history** — revisions 7.0.6, 7.0.9 and 7.0.10, each of which the author
started by playing the game — rather than from a generic risk list.

## 7. The master

| | |
|---|---|
| File | `exports/landscape/claude-liam-walker-the-lost-pitch-gdd.mp4` |
| Rendered by | `./art final`, 3840 × 2160, 30 fps, h264 + aac 48 kHz |
| Length | **3:54.20** — 234.200 s |
| SHA-256 | `fc2ebbe4f632dc7155cc21a1e66aaef762a393e0f0933c35f1b0859728527de5` |
| Link | recorded in `pitch/README.md`, which is the one place the link, the length and the hash sit together so they cannot disagree |
| Beats | 14, of which 13 are narrated |

`build-state.json` is not committed: it is rewritten on every render and full
of absolute paths. Its one durable fact, the master's SHA-256, is recorded in
`pitch/README.md` instead, so it lives in exactly one place.
