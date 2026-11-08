# SUBMISSION.md

**Assignment:** Assignment 6 - Creating Particle Effects with Godot and Claude

**Student:** Tiantong Zhang · zhang.tiant@northeastern.edu · GitHub `TiantongZhang1`

**Project name:** The Lost

**GitHub repository URL:** <https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang>

**Git tag and submitted commit SHA:** tag **`a6.1`**. A commit cannot carry
its own SHA, so it is in the Canvas note and is recoverable with
`git rev-list -n 1 a6.1`.

There is also a tag `a6`. It is the first cut of the film, whose narration
said the GPU budgets had not been measured. `a6.1` measures them and re-cuts
the beat that said so. `a6` is left where it is rather than moved, because
`TEST-REPORT.md` finding 5 cites what was verified at it — a tag that moves
takes its own evidence with it.

**Game-source revision shown in the film:** **`31fb5a7`** — *A6 film capture
driver: three takes, each asserting its own outcome*. Every code panel, every
hash and every capture in the film was taken at it. Commits after it add film
documentation only and change no file under `godot/`;
`git diff 31fb5a7..a6 -- godot/` is the check and it prints nothing.

**Godot version, renderer, and operating system:** Godot
**4.7.2.stable.official** `ed1daf0bf`, **Forward+** (Vulkan 1.4.357), Windows
11.

**GPU used for the GPU price:** NVIDIA GeForce RTX 5080 Laptop GPU.
Whole frame at the design ceiling **0.022 ms** against a combined budget of
**0.60 ms** — `evidence/a6/gpu-cost-effects-run1.txt` and `-run2.txt`,
`CHANGE-BRIEF.md` revision 6.0.6.

---

## The effects

**Effect A — the grit burst.**

| | |
|---|---|
| Event | `signal fired` on `godot/features/traps/spike_trap.gd:24`, emitted at `:98` on entering `State.FIRING` |
| Node type | **`GPUParticles2D` × 3** (`Flash`, `Grit`, `Dust`) under one `Node2D` |
| Retrigger rule | **overlap** — one instance per event, nothing cut off and nothing dropped |

**Effect B — the dungeon motes.**

| | |
|---|---|
| Job | **ambience** |
| Condition | starts with the scene, stops on `signal died` — `godot/features/player/player.gd:16`, emitted `:48` |
| Node type | **`GPUParticles2D` × 1** |
| Feature Effect A does not use | **`preprocess = 8.0`**, one full lifetime, so the field is at steady state on the first drawn frame. Secondary: a **Box** emission shape against A's Point and Sphere. |

**Effect C — the step dust.** Not required; the assignment asks for two. It
was added on the author's verdict on Effect B — *dust falling from the sky,
but none at the floor* — and is specified in `CHANGE-BRIEF.md` revision
6.0.4. Its event **does not exist in the game**: `player.gd` has no footstep
signal and §3 keeps it out of scope, so `step_dust_driver.gd` derives one from
measured position delta, one puff per 24 px travelled. It is the only effect
that uses **`amount_ratio`** (0.6 a stride, 1.0 a landing) and the only one
whose state test runs at 30, 60 and 144 fps.

**Budgets, and the price each is compared on.** All three are GPU nodes, so
all three are budgeted on **GPU time**; the headless CPU price is run as a
control, because the prediction that it reads ≈ 0 is itself a claim worth
testing.

| | Peak particle count | GPU budget | GPU, measured | Headless CPU, measured |
|---|---|---|---|---|
| Effect A | 96 (design ceiling; in play it is 32 — revision 6.0.2) | **0.30 ms** | +0.001 ms | +13.5 µs over baseline |
| Effect B | 60 | **0.20 ms** | +0.005 ms | +0.5 µs, below the instrument's noise |
| Effect C | 21 | **0.10 ms** | +0.001 ms | +8.5 µs |
| **all three at once** | 177 | **0.60 ms** | **whole frame 0.022 ms** | — |

**The GPU budgets are measured** — `CHANGE-BRIEF.md` revision 6.0.6,
2026-11-08. The whole frame, with all three effects at the brief's design
ceiling, costs **0.022 ms** of GPU time against a combined budget of
**0.60 ms**; a 60 fps frame is 16.67 ms, so the three effects are about
**0.13 %** of one. Every budget is met with more than an order of magnitude
to spare.

**The per-effect figures are not prices.** Two controls in the same run say
so: Effect B measured twice drifts by up to 0.0010 ms, which is the entire
measured cost of A and of C; and "all three" measured *cheaper* than Effect B
alone, which cannot be true, because all three contains B. Both runs
reproduced to the last digit — repeatable is not the same as true. What the
measurement establishes is the ceiling, not the price.


**That table is two runs, and the second run is the point.** The *ordering*
is stable and the instances column is identical between runs; the microsecond
figures are not. Effect B reads +1.3 µs in one run and +4.3 µs in the other,
while each run's own twice-measured baseline claims a resolution of 0.5 µs.
The reading that survives is the instances column — 30, 0 and 22 — and what it
says is that a headless run can weigh scene instancing and nothing else.
`evidence/a6/cost-effects-run1.txt` and `run2.txt` are the recorded output; a
third, earlier run was discarded because it was taken while a 4K render was
using the CPU, and it is not in the repository.

**Texture sources and licences (or model, version, and terms):**

**None of the three effects uses a texture.** Every emitter draws Godot's
default point with no texture assigned, and the look comes from
`color_ramp`, `scale_curve` and the blend mode. There is nothing to credit
and nothing to license for this assignment's own work.

The textures already in the game are unchanged and were all **written by
code**: `tools/make_sprites.py` and `godot/tools/write_textures.gd`, both
committed. `ATTRIBUTION.md` and `SOURCES.md` carry the full accounting,
including the five generated character poses carried from
walker-ninja-TiantongZhang and the film's locally run narration model.

**The film.** `youtube/claude-liam-walker-the-lost-particles-gamedev/`.
Twenty beats, six code-then-result pairs, built with the course-provided
Brutalist `godot-gamedev` workflow in `walker` mode. Its evidence ledger
passes the course checker — 67 source files, 40 exclusions, 6 components, 6
exact excerpts. Five beats are engine footage from three 4K Movie Maker takes,
each of which asserted its own outcome before a frame of it counted; take r is
labelled SCRIPTED everywhere it appears, because the ceiling it shows cannot
be reached by playing this room. Four beats are evidence cards whose every
figure is recomputed from committed capture frames at build time. The reel's
`FACTCHECK.md` marks every narrated claim MEASURED, SOURCE, REASONING or
AUTHOR, and records the one claim that was wrong and was corrected before the
master was rendered.

**Final film URL and filename:**
`claude-liam-walker-the-lost-particles-gamedev.mp4` —
**TheLostParticles_TiantongZhang**, H.264 **3840 × 2160**, 30 fps, AAC 48 kHz
stereo, **619.00 s** (10:19.00), 20 beats, 39,013,712 bytes.
_URL PENDING — the file is stored in the course media storage and linked from
`README.md`; it is kept out of GitHub by the assignment's MP4-and-25-MB rule._

**Final film SHA-256:** `d9a8e521248352d96ae48d8b8b3c47812c5b7cd72e007c80f6ca8aa8b8efb36a`

---

## Summary of my work

**The specification came first.** `CHANGE-BRIEF.md` was committed as `725a940`
before the first agent prompt of this assignment, and the first build commit
is `fb04465`. It holds an intent block per effect — timing phases, contrast
against the named background, scale against the character, change over life,
variation, and each emitter's job — the settings those are meant to produce,
the observable rules, seven predicted failures, and a price prediction and
budget for each effect.

**Three things were measured on the pinned engine before anything was
specified**, and they changed what the brief could say. The one that mattered
most: on 4.7.2 `ParticleProcessMaterial` **has** `initial_velocity`, `scale`
and `damping` as `Vector2` properties with usage flag 12, which are never
written to a scene file. `set("initial_velocity", 7.0)` is accepted and
discarded. So the Godot 3 name the assignment warns about is worse here than
described — it does not error, it silently runs at the default. Both mutations
were run and both made the configuration test exit 1.

**The tuning loop ran on strips, and the verdicts are mine.** Effect A's `Flash`
was invisible at the size the brief first gave it; I approved raising
`scale_min/max` from 1.6 / 2.4 to 5.0 / 7.0 and kept it after seeing it in the
running game. Claude's prediction for that recapture was right on five frames
of six and **wrong on frame 12**, where the two strips turned out bit-identical;
that disagreement is in `TUNING.md` rather than quietly resolved.

**What I verified, and what I caught.** The one that matters: Step 6's
generated shader was produced from a default, empty material by mistake, and
Claude had already pronounced it fine — it loaded, reported `MODE_PARTICLES`,
declared 38 uniforms and printed no `SHADER ERROR`, all true. **I found it
while counting line numbers**: the file had no `texture()` call anywhere, so
two of the seven references the assignment asks for did not exist in it. The
file was regenerated from Effect A's `Dust` material, which is the one
carrying both a `color_ramp` and a `scale_curve`.

**What Claude wrote, and where it was wrong.** Claude updated `CLAUDE.md`,
built all three effect scenes, the previews, the trigger code, the tests and
the cost script, read the strips and proposed every tuning change. It also
shipped four checks that could not fail — one written as `x or true`, one as
`arr.size() >= 0`, one comparing two runs that shared a scene tree, and one
counting events over a different window than it measured distance over — and
every one of them was green. `TEST-REPORT.md` records each with how it was
caught. `FRICTIONAL.md` separates what I accepted, modified and rejected.

**Authorship.** `godot/shaders/` is mine and `git log -- godot/shaders/` shows
it, with one dated exception recorded in `CLAUDE.md`: on 2026-11-08 I
converted the material in the editor, saved it, and told Claude to extract
`particles_generated.gdshader` from the saved resource. The closing answer in
`TEST-REPORT.md`'s process-shader section was written by Claude at my
instruction and is labelled as Claude's in the file itself.

---

## Known limitations

- **The GPU figures are a ceiling, not a price.** Every budget is met, with
  more than an order of magnitude to spare — but the per-effect differences
  are below the instrument's own floor, and the run demonstrates that rather
  than asserting it: Effect B measured twice drifts by as much as A and C
  cost in total, and "all three" measures cheaper than Effect B alone, which
  cannot be true. `CHANGE-BRIEF.md` revision 6.0.6 §3. One by-eye
  cross-check in the Visual Profiler — of the instrument, not of the effects
  — has not been done.
- **Effect B and Effect C have an author verdict but no tuning revision yet.**
  B's r0 verdict was *keep*, with no setting changed; the assignment asks for
  at least one observation-driven revision per effect.
- **Both B and C drift dust below the floor line** — 14–22 % of the motes and
  11–29 % of the step dust, measured against a field-off control. Neither is
  visible in play; both are recorded in `TUNING.md` with candidate fixes.
- **A5's evidence checker fails on `main` by construction**, from the first
  file this assignment adds under `godot/`. The `a5` tag is unaffected and a
  clone of it still passes. `CHANGE-BRIEF.md` §0.3 verified this by experiment
  before any of A6 was built.
- **Three effects instead of two** is more surface than the assignment asks
  for, and Effect C is the least settled of them.
- **One claim in the film was wrong and was corrected before the master was
  rendered.** It said `Dust` was the only emitter carrying both a `color_ramp`
  and a `scale_curve`; three of the six do. `TEST-REPORT.md`'s process-shader
  section, which said the same thing, carries a dated correction rather than a
  silent edit, and the reel's `FACTCHECK.md` records it.
- **Two note panels in the film clipped mid-sentence** in their first render,
  because the workbench's notes column holds about 165 characters and nothing
  enforces it. Found by extracting one frame per code beat and reading them;
  fixed and re-rendered. It is the same class of fault as everything else in
  this report: a step that produced output, passed every automatic check, and
  was wrong.

**Changed games since Assignment 2:** No. Same game, same repository, since
Assignment 2.
