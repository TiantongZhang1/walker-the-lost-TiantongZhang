# SOURCES.md — where every frame and every file in this film came from

The repository's own `../../SOURCES.md` records the game's provenance. This
file records the **film's**: the captures, their hashes, the revision they
were taken at, and the documentation consulted. No secrets, no `.env`, no
absolute developer paths inside anything reusable.

Game-source revision **`31fb5a7`**. Godot **4.7.2.stable.official**
`ed1daf0bf`, **Forward+**, Vulkan 1.4.357, NVIDIA GeForce RTX 5080 Laptop
GPU, Windows 11.

Commits after `31fb5a7` add film documentation only and change no file under
`godot/`. `git diff 31fb5a7..a6 -- godot/` is the check, and it is run at
handoff rather than assumed.

---

## 1. Native engine captures

All three are 3840 × 2160, 60 fps, recorded by Godot's Movie Maker with the
engine audio carried through. None is a screen recording and none is a
reconstruction.

| File | What it is | Frames | Length | sha256 |
|---|---|---|---|---|
| `capture/take-p.mp4` | **PLAYED.** Held keys only | 638 | 10.63 s | `1b5a586c73d6dffd41b24237314bb1f812c05646969e1abaecfd5c95e6e12efd` |
| `capture/take-r.mp4` | **SCRIPTED.** `fired.emit()` on a rotation | 963 | 16.05 s | `3442483e607e8dcb0dd7fd5d18873325352ae28f0890624b8aecee0fc3de63da` |
| `capture/take-c.mp4` | **PLAYED.** Pause, death, and the tail | 1216 | 20.27 s | `2d0958a3f031bc5297e37eca6251725c373c3f337f21fd58a3ed9c7a36d2d95b` |

Their input logs — `capture/logs/take-{p,r,c}-inputs.jsonl`, 637 / 962 / 1215
rows — carry game time, player x, live burst count, live step-dust count,
whether Effect B was emitting, and health, one row per frame. Every number on
the five gameplay cards is computed from them by
`scripts/frame_particles_footage.py` at build time.

**Method.** `scripts/render_takes.py p r c --driver
res://tests/capture_particles.gd`, which writes a temporary
`godot/override.cfg` because Movie Maker fixes its output size from the window
size at engine startup — before `--resolution` and before any script runs.
Without it the same command silently records 1280 × 720. The override is
removed when the render finishes and is in `.gitignore` so that a `git add -A`
during a render cannot commit it.

**Nothing was teleported in takes p and c.** The only input is held keys
parsed through the real input map. No position, velocity or health is written
and no effect is poked. Each take asserts its own outcome and the render is
evidence only because it printed `CAPTURE OK`:

| Take | What it asserted before a frame of it counted |
|---|---|
| p | all three traps reached `FIRING` on their own, ≥ 3 distinct bursts, ≥ 12 distinct step-dust instances, both facings seen, Effect B still emitting at the end |
| r | ≥ 3 bursts alive **at the same moment**, ≥ 6 in all |
| c | > 30 paused frames with the player's x unmoved, player health 0, Effect B's `emitting` false |

**Take r is scripted and is labelled as such everywhere it appears** — in the
beat's own title card, in its narration, and in `SHOTLIST.md`. It emits
`fired` directly at the spawner on a 0.20 s rotation. Revision 6.0.2 measured
that three bursts cannot be alive at once by playing this room: the traps are
112 px apart, the player walks at 96 px/s, so consecutive events are 1.17 s
apart and a burst lives 0.60 s. Take p's recorded peak is **1**.

**Time intervals used.** Two beats take non-identical windows of take p
(0.40–9.06 s and 1.90–10.58 s) and two take windows of take c (0.30–9.64 s
and 10.30–20.13 s). They overlap; that is a framing choice and `SHOTLIST.md`
says so. Every window and every labelled final-frame hold is written into
`beat_sheet.json` by `scripts/build_media_clips.py`, which refuses to let a
window be longer than its beat.

**Cropping and framing.** B03, B03A and B11 are cropped to the action band —
logical x 107–533, y 80–320, derived from the trap positions and the floor
line, not eyeballed — and rescaled with nearest-neighbour, because the game is
nearest-filtered pixel art. B07A and B07B are **not** cropped: the mote field
is the whole room. All five are then inset on the brand ground with the
numbers their own take log recorded. Nothing is brightened, retimed,
composited or re-ordered, and no pixel value is altered.

## 2. The four evidence cards

Each is a full-frame 3840 × 2160 PNG composed by
`scripts/compose_particles_evidence.py` and rendered as a STILL with
`motion: "hold"`. **Every figure on them is measured at build time from the
committed capture frames**, not typed in; the measurements are also written to
`evidence/a6/*.txt` so a reviewer can read them as text. Delete a frame and
the script stops rather than drawing a stale number.

| In the reel | What it frames | Numbers it draws | sha256 |
|---|---|---|---|
| `media/B05.png` | `captures/hit_burst/r0-vs-r1-frame10.png` | r0-vs-r1 difference per frame, recomputed | `fcdc632b3bdfc044cc083cc199a17420be1c06ed0aefd7cdc963663b1440ef45` |
| `media/B07.png` | `captures/dungeon_motes/{r0,f4-no-preprocess}/frame00000001.png` | mote pixels at frames 1/10/40/100, recomputed | `b7cadf51d7dadb8d79b9001498ac10202263ea8a3e8e880e416c59f873e85878` |
| `media/B09.png` | `captures/hit_burst/r1/frame0000001{5,20}.png`, cropped to the trap | lit pixels, brightest channel and extent per frame | `9e7abf4c9936bdf9a1aee39869951030702a67f6c72d044e15a7b1b96d9b5abf` |
| `media/B11B.png` | a frame of `capture/take-r.mp4` | the recorded cost output, verbatim | `c2d76a9e5fd582934029c204c0388837861e35f9fcab27e41a6f84b03e7b263a` |

**All six strip captures are FIXTURE captures** from the three preview scenes
in `godot/previews/`, and are labelled FIXTURE on every card they appear on.
They were taken on 2026-11-06 and 2026-11-07 at 30 fps and are committed under
`captures/`; `TUNING.md` records which revision each belongs to.

**B07's right-hand panel is a capture of deliberately mutated source.**
`preprocess` was set to 0.0 in `godot/effects/dungeon_motes.tscn`, the preview
was recaptured, and the scene was reverted immediately. The card says so and
the narration says so. The mutation is also the F4 row of
`CHANGE-BRIEF.md` §6.

**B11B's frame is chosen by the take's own log, not by eye.** The script
reads `capture/logs/take-r-inputs.jsonl`, finds the first frame where the
recorded live-burst count is ≥ 3, and extracts that exact timestamp. An
earlier version hardcoded 3.0 s; when the take was re-recorded longer, that
second no longer had a burst in it and the card captioned an empty room
"three bursts alive". Nothing in the pipeline noticed. It now stops instead.

## 3. The cost figures

`evidence/a6/cost-effects-run1.txt` and `run2.txt` are the recorded stdout of
two separate runs of `./scripts/run-test.sh cost_effects.gd 60 300`, on an
otherwise idle machine. A third, earlier run was discarded because it was
taken while a 4K Movie Maker render was using the CPU; it is not in the
repository and no number from it is used.

Both runs are shown because the difference between them is the finding. The
*ordering* is stable and the instances column is identical; the microsecond
figures are not, and Effect B moves by more between runs than either run's own
twice-measured baseline spread claims as its resolution.

**That script measures CPU wall clock, which is not what any budget is set
against.** The budgets are GPU time, and they are in
`evidence/a6/gpu-cost-effects-run1.txt` and `-run2.txt`, recorded by
`./scripts/run-gpu-cost.sh` — a **windowed** run, because
`RenderingServer.viewport_get_measured_render_time_gpu()` reads `0.000` ms
under a dummy renderer and `tests/gpu_cost_effects.gd` refuses to run
headless for that reason. Eight conditions, 400 frames each, two runs that
agree to the last digit.

**What they establish is the ceiling, not a price.** The whole frame with all
three effects at the brief's design ceiling costs **0.022 ms** against a
combined budget of **0.60 ms**. The per-effect differences are not readable:
the run repeats the Effect B condition and finds up to 0.0010 ms of drift —
the entire measured cost of A and of C — and "all three" measures *cheaper*
than Effect B alone, which cannot be true, because all three contains B.
`CHANGE-BRIEF.md` revision 6.0.6 and `TEST-REPORT.md` finding 6.

## 4. Documentation consulted

- `skills/make/godot-gamedev/SKILL.md` and its `references/evidence.md`, from
  the course-provided Brutalist toolkit.
- `RENDER-TARGETS.md`, `OUTRO-LOCK.md` and `HOW-TO.md` from the same toolkit.
- The previous film's `BUILD-PROMPT.md` in
  `../claude-liam-walker-the-lost-gamedev/`, for the panel capacities it
  measured off rendered frames and for the warning that
  `scripts/finalise_beat_timing.py` must not be run.
- Godot 4.7.2's own generated particle process shader, read from the file the
  editor produced — not from online documentation.

## 5. Narration, music and art

**Narration** is local Kokoro `am_onyx` (Liam), generated by the toolkit's
`runtime/scripts/generate_audio_kokoro.py`. No paid call, no API key, cost
$0.00. The measured durations are the film's clock.

**The only music is the toolkit's existing stock jingle on the locked outro
card.** The game's own `music-loop.ogg` is not in this film; the engine audio
carried in the captures is muted by `build_media_clips.py`, which encodes the
clips with `-an`.

**No texture is credited because none of the six emitters has one.** Every
particle in this film is Godot's default point, coloured by a `color_ramp`,
sized by a `scale_curve` and composited by a blend mode. There is nothing to
license for this assignment's own work. The game's existing textures are
unchanged and were written by code — `tools/make_sprites.py` and
`godot/tools/write_textures.gd`, both committed; `../../ATTRIBUTION.md` carries
the full accounting.

## 6. The master

| | |
|---|---|
| File | `exports/landscape/claude-liam-walker-the-lost-particles-gamedev.mp4` |
| sha256 | `d9a8e521248352d96ae48d8b8b3c47812c5b7cd72e007c80f6ca8aa8b8efb36a` |
| Length | **619.00 s** — 10:19.00, 20 beats, drift from the beat sheet 0.000 s |
| Video | H.264, **3840 × 2160**, 30 fps |
| Audio | AAC, 48 kHz, stereo — per-beat narration timeline; the locked outro card is the only beat with music and it carries no narration |
| Size | 39,013,712 bytes (37.2 MB) |

**It is not in GitHub.** The assignment keeps MP4s and anything over 25 MB
out of the repository, and `.gitignore` excludes `exports/`. It goes to the
course media storage and `../../README.md` links it.

`build-state.json` is machine-local and is in `.gitignore`; the master's
SHA-256 is recorded here deliberately so it lives in exactly one place.

**The master was watched, one frame per beat, at each beat's own midpoint.**
`_qc/beat-contact-sheet.png` and `_qc/BEAT-FRAMES.md`, written by
`../../scripts/qc_particles_master.py`. That sheet is evidence the master was
looked at; it is not evidence the master is right.

**Those are not Gate V's filenames, and the distinction is load-bearing.**
Gate V — the toolkit's own `runtime/qc/final_frame_check.py` — writes
`_qc/REPORT.md` and `_qc/contact_sheet.png`, and reports 40 frames,
BLOCKER 0, MAJOR 0 for this master. An earlier version of the per-beat script
wrote `REPORT.md` too, ran after `art final`, and destroyed Gate V's result
for this reel without erroring. It was recovered by re-running Gate V; the
script was renamed and now asserts at startup that it cannot write either of
those two names. This file said `_qc/contact-sheet.png` and `_qc/REPORT.md`
until 2026-11-08, which was the old wording outliving the fix.

**Gate V's contact sheet is not a view of the whole film, and that was
measured rather than assumed.** It regenerated byte-for-byte identical after
the master was re-cut 27 seconds longer with a rebuilt B12 card, which should
be impossible. The reason is in `final_frame_check.py`'s `contact_sheet()`:
`frames[::max(1, len(frames)//16)][:16]` takes every second frame and then
truncates to sixteen, so for a twenty-beat film **the last four beats never
appear in the sheet at all** - B12, B13 and B14 among them. The *analysis*
does cover all forty frames and would have reported a defect in any of them;
only the human-eye backstop is truncated. This is why the per-beat sheet in
`_qc/BEAT-FRAMES.md` exists and why it is one frame per beat for all twenty.

