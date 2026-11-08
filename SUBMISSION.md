# SUBMISSION.md

**Assignment:** Assignment 6 - Creating Particle Effects with Godot and Claude

**Student:** Tiantong Zhang · zhang.tiant@northeastern.edu · GitHub `TiantongZhang1`

**Project name:** The Lost

**GitHub repository URL:** <https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang>

**Git tag and submitted commit SHA:** tag `a6`. A commit cannot carry its own
SHA, so it is in the Canvas note and is recoverable with
`git rev-list -n 1 a6`.

**Game-source revision shown in the film:** _PENDING — filled in when the film
is rendered. Commits after it add film documentation only and must change no
file under `godot/`, which `git diff <rev>..a6 -- godot/` confirms._

**Godot version, renderer, and operating system:** Godot
**4.7.2.stable.official** `ed1daf0bf`, **Forward+** (Vulkan 1.4.357), Windows
11.

**GPU used for the GPU price:** NVIDIA GeForce RTX 5080 Laptop GPU.
_The GPU times themselves are PENDING — see "Known limitations"._

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

| | Peak particle count | GPU budget | Headless CPU, measured |
|---|---|---|---|
| Effect A | 96 (design ceiling; in play it is 32 — revision 6.0.2) | **0.30 ms** | +13.5 µs over baseline |
| Effect B | 60 | **0.20 ms** | +0.5 µs, below the instrument's noise |
| Effect C | 21 | **0.10 ms** | +8.5 µs |

The noise floor of that measurement is 8.0 µs, measured by running the
baseline twice; `TEST-REPORT.md` reports it beside every figure.

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

**Final film URL and filename:** _PENDING_

**Final film SHA-256:** _PENDING_

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

- **The GPU times are not yet read.** Every budget in `CHANGE-BRIEF.md` §5 and
  §C.6 — 0.30, 0.20 and 0.10 ms — is still a prediction. The Visual Profiler
  numbers are the primary on-screen price and §4 puts that row under HUMAN.
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

**Changed games since Assignment 2:** No. Same game, same repository, since
Assignment 2.
