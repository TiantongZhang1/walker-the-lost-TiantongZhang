# SOURCES.md — every asset in this film, and where it came from

> ## This reel's ledger describes `b200c86`, not the `a8` tag
>
> **`./art godot-gamedev --check` FAILS against the submitted tree, and that
> is correct rather than broken.** Assignment 8 added files under `godot/`
> after this film was rendered — a floating key, its read-back, a second
> capture driver — and changed two more. A ledger inventories *every* file
> under `godot/` with its hash, so a tree that has moved no longer matches
> one that describes an older tree.
>
> **It passes at the revision it is a record of**, and this is the command:
>
> ```bash
> git worktree add --detach /tmp/verify-old b200c86
> cd "$ART" && PYTHONUTF8=1 bash art godot-gamedev --check >     /tmp/verify-old/youtube/claude-liam-walker-the-lost-animation-gamedev >     --game /tmp/verify-old/godot
> # {"status": "PASS", "source_files": 72, "exclusions": 64, ...}
> ```
>
> **The ledger was not rebuilt to make the failure go away.** Rebuilding it
> against the current tree would produce a passing check whose hashes
> describe a room with a floating key in it — and this film's footage was
> recorded before that key existed. A passing check that misdescribes its own
> film is worse than a failing one with a date on it.
>
> **This is also not the submitted film.** The submission is
> `claude-liam-walker-the-lost-walkthrough`, whose checker passes in a fresh
> clone of `a8`.

Game-source revision **`b33b06c`**. Every code panel, every hash, every
capture frame and every number in this film is taken at that revision.
`git diff b33b06c..a7 -- godot/` is the check that nothing under `godot/`
moved afterwards; commits after it add film documentation and film scripts
only.

---

## 1. The three engine takes

Rendered by `scripts/render_takes.py` at 3840 × 2160 through Godot's Movie
Maker, driven by `godot/tests/capture_animation.gd`.

**All three are PLAYED.** Held keys, parsed through the real input map.
Nothing is teleported, no state is written, no clip is seeked. Assignment 6's
film needed one scripted take because three particle bursts alive at once
cannot be produced by walking the room; nothing in this assignment is like
that, and the label does not appear.

| Take | Frames | Length | What it asserts before a frame of it counts |
|---|---|---|---|
| `take-c` | 536 | 8.93 s | ≥ 5 cycle wraps, both facings, ≥ 12 distinct dust puffs, **and zero swings** |
| `take-s` | 330 | 5.50 s | exactly 4 swings, the window opening exactly 4 times, every clip 34–38 physics frames |
| `take-m` | 616 | 10.27 s | ≥ 30 frames of swing with `legs_run` under it, ≥ 2 swings that left the floor, ≥ 4 swings all 34–38 frames |

**A render is evidence only if it printed `CAPTURE OK`.** Each take asserts
its own outcome and exits nonzero otherwise, so a completed render is not by
itself the claim.

**`take-c` never crosses a trap, deliberately.** The first version walked the
length of the room and back; five hits kill and six crossings happen, so the
player arrived dead. It paces the clear 190 px west of the first trap now and
ends on 5/5. A take about the gait that ends in the death pose is a take about
two things.

| File | Tracked | Why |
|---|---|---|
| `capture/take-{c,s,m}.mp4` | yes | the ledger hashes them as the result half of three code→result pairs |
| `capture/logs/take-{c,s,m}-inputs.jsonl` | yes | every number on the three footage cards is computed from these at build time |
| `capture/take-*/frame*.png` | **no** | 245 MB of lossless 4K sequence, reproducible by `render_takes.py` |

> **`take-m.mp4` and `take-s.mp4` were `.gitignore`d, and `take-c.mp4` was not
> — by luck**, because Assignment 6's take `c` shares the letter. That is the
> `take-w.mp4` failure of 2026-10-28 arriving by a new door: the file is
> present, `git status` is clean, the ledger hashes it, and a fresh clone of
> the tag cannot verify anything. Found by running `git check-ignore -v` over
> every file the ledger would hash, before the reel's first commit.

## 2. The four evidence cards

`media/B07.png`, `B09.png`, `B13.png`, `B14.png`, composed by
`scripts/compose_animation_evidence.py` at 3840 × 2160. **Every figure on
them is computed at build time** from the committed resources, the committed
take logs and the recorded evidence files; the same measurements are written
to `evidence/a7/*.txt` so a reviewer can read them without opening a PNG.
Delete a frame or a resource and the script stops rather than drawing a stale
number.

| Card | Picture | Table |
|---|---|---|
| B07 | two take frames: the same body clip with `legs_planted` and with `legs_run` under it | both players' track paths, parsed out of `player.tres` and `legs.tres` as resource text |
| B09 | the last frame with the hitbox off and the first with it live | `evidence/a7/clocks.txt`, verbatim |
| B13 | **a grounded frame and an airborne frame at the same playhead, found by searching `take-m`'s own log** | section E's three phase comparisons, and mutation M7 |
| B14 | r1's windmill and r4's shipped strike at the same table frame | the ten revisions, who reported each, and what kind of thing it was |

**B13's two frames are not chosen by eye.** The script searches every
grounded/airborne pair in the take for the smallest playhead difference and
exits if none is within one millisecond. The pair it found differs by
0.000000 s.

## 3. The three footage cards

`scripts/frame_animation_footage.py` crops each gameplay clip to the action
band and insets it in a card whose figures come from that take's own log.

**Cropping is a framing choice and not a change to the evidence.** Nothing is
brightened, retimed, composited or re-ordered. **Nothing is resampled
either**: each crop is sized so that it lands on the inset at an integer
scale — B03 and B11 are pasted 1:1, B05 is doubled with a nearest filter,
which on pixel art is an exact doubling of the pixels the engine drew.

The frame exists because this game's floor is `#16242B` against a `#17141B`
sky — a largest channel difference of 16, under the compositor's content
threshold of 28 — so a full frame of this room measures underfilled however it
is cropped. The two honest options were to brighten the capture, which would
misreport what the engine drew, or to frame it.

## 4. Narration

| | |
|---|---|
| Voice | `am_onyx`, Kokoro, run locally |
| Generated by | `runtime/scripts/generate_audio_kokoro.py` in the brutalist toolkit |
| Cost | $0.00 |
| Files | `mp3/beat-B00.mp3` … `beat-B16.mp3`, 17 beats |
| Not generated | `B17`, the locked outro, which carries `audio_policy: "silence"` |

**The measured durations are the film's clock.** Nothing is cut to a target
length; the beat sheet's second pass re-authors every cue and every footage
window against the measured seconds.

**The first-pass estimates are derived, not typed.** 3.533 words per second,
computed from Assignment 6's finished sheet — 2168 narrated words across
613.7 s. Eighteen hand-typed estimates would be eighteen numbers that go stale
on the next edit of a sentence.

## 5. Graphics

Remotion patterns from the brutalist toolkit: `ClaudeComposerAsk`,
`BrutalistHesitantWriter`, `GodotDevWorkbench`, `ClaudeVerdictArtifact`,
`ClaudeTitleOutro`. The outro is **locked** — exact title, `@NikBearBrown`, no
narration over it, per `OUTRO-LOCK.md`.

**The `GodotDevWorkbench` panels are a reconstruction of an editor, not a
screenshot of one.** The code in them is byte-exact — read from the file at
build time, and re-read by the ledger — but the surrounding chrome is drawn by
Remotion. **No frame of the Godot editor appears in this film.**

## 6. The game's own assets, and their licences

Unchanged from Assignment 6's statement; `ATTRIBUTION.md` is the full record.
What this film puts on screen:

| Asset | Origin | Licence |
|---|---|---|
| The seven pose PNGs in `godot/assets/poses/` | generated with GPT-6 for `walker-ninja-TiantongZhang`, 2026-10 | mine, credited in `ATTRIBUTION.md`. **Unmodified on disk** — the sheet is cut from them and the cut is asserted lossless |
| `player_sheet.png`, `leg_front.png`, `leg_back.png`, `sword.png` | written by `tools/make_sprites.py` in this repository | mine |
| The room's tiles | written by `godot/tools/write_textures.gd` | mine |
| `music-loop.ogg` | **Suno**. Suno retains ownership | **personal / non-commercial use only.** Not a free-licence asset and not presented as one |
| `sfx-*.ogg` | synthesised by `scripts/synth_placeholder_sfx.py` | mine |

**No asset in this film was downloaded from an asset library, and no 3D
generator was used.** The three `.glb` files in the project came from
Assignment 3 and are excluded from this film's ledger — and the reason they
are excluded is itself in the film: the glTF probe on 2026-11-15 found
`skins: 0` and no animations in all three, which is *why* this assignment's
rig is cut out of 2D art.

## 7. Film build chain

See `BUILD-PROMPT.md` for the commands in order. The scripts this film added
to the repository:

| Script | What it does |
|---|---|
| `godot/tests/capture_animation.gd` | the three takes, each asserting its own outcome |
| `scripts/build_animation_beat_sheet.py` | the beat sheet; every code panel read from disk |
| `scripts/compose_animation_evidence.py` | the four evidence cards, and `evidence/a7/*.txt` |
| `scripts/frame_animation_footage.py` | crops and frames the three gameplay beats |
| `scripts/build_animation_ledger.py` | `gamedev-evidence.json` |

Two existing scripts were changed, and both changes are fixes to faults this
film found in them:

- **`scripts/encode_captures.py`** had a hard-coded tuple of take letters and
  **silently did not encode two of this film's three takes.** It discovers
  takes from the render root now.
- **`scripts/render_takes.py`** gained a third per-driver `--quit-after`
  table. The letter `c` now means a different take in each of three tables,
  which is exactly why they are keyed by driver path and not merged.

## 8. The master

| | |
|---|---|
| File | `exports/landscape/claude-liam-walker-the-lost-animation-gamedev.mp4` |
| Rendered by | `./art final`, 3840 × 2160, 30 fps, h264 + aac 48 kHz |
| Length | **9:30.57** — 570.567 s, 18/18 slots filled |
| Size | 35,983,725 bytes |
| SHA-256 | `6eb488d454fc98899c4ed77445250247c80bd2b5883810db88469c39e8e5646f` |
| Link | _PENDING — the upload is the author's_ |

**`build-state.json` is not committed.** It is rewritten on every render, full
of absolute paths, and names the export under its pre-rename slug. Its one
durable fact — the master's SHA-256 — is recorded here instead, so it lives in
exactly one place.
