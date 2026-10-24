# TEST-REPORT.md — Assignment 5

**Source revision:** `ca8151c`+ · **Godot** 4.7.2.stable.official `ed1daf0bf` ·
**Renderer** Forward+ *(confirmed on hardware 2026-10-24)* · **OS** Windows 11

Every row below is either a recorded result or an explicit **not yet**. Nothing
is marked done that has not been run.

---

## Baseline

Assignment 5 asks for "every earlier test, before and after, with pinned frame
rate and counts". **This repository had no earlier suite.** It was created on
2026-10-17 for the course's one permitted change of game and held no game until
today. The baseline is therefore the suite as it stands at the start of the
shader work, run from a **fresh clone** of `732b5aa` with one `--import`:

| Test | fps | Exit | Result | `SHADER ERROR` lines |
|---|---|---|---|---|
| `test_input_map.gd` | 60 | 0 | 5 checks, 0 failures | 0 |
| `check_assets_3d.gd` | 60 | 0 | ALL CHECKS PASSED (12 measurements) | 0 |
| `test_trap_warning.gd` | 30 | 0 | 22 checks, 0 failures | 0 |
| `test_trap_warning.gd` | 60 | 0 | 22 checks, 0 failures | 0 |
| `test_trap_warning.gd` | 144 | 0 | 22 checks, 0 failures | 0 |

Import errors from a clean clone: **0**.

`check_assets_3d.gd` is Assignment 3's own geometry check, copied with the 3D
scene; it passes here unchanged, which is the evidence that the copy arrived
intact.

## R2 — frame-rate independence

Specified: **0.40 s** (revision 5.0.3), tolerance **one frame period**.

| fps | Modal delta (of 40 frames) | Window | Tolerance | |
|---|---|---|---|---|
| 30 | 0.033333 — 39/40 | **0.433 s** | ±0.0333 | pass |
| 60 | 0.016667 — 40/40 | **0.417 s** | ±0.0167 | pass |
| 144 | 0.006944 — 35/40 | **0.403 s** | ±0.0069 | pass |

The overshoot is bounded by one frame because the ramp is checked once per
`_process`, so the window ends on the first frame at or past `WARN_SECONDS`.
It shrinks as the frame rate rises, which is what it should do.

**The frames at 144 fps are not uniform.** 1/144 s is 6944.44 µs and Godot
works in whole microseconds, so the delta alternates between 0.006944 (144 fps)
and 0.006667 (150 fps) with the occasional 0.008. 30, 60 and 240 divide evenly
and are uniform. The test takes the modal delta over 40 frames for this reason.

**The frame period itself was wrong until 2026-10-24.** The test read
`Engine.max_fps`, which `--fixed-fps` does not set, so every run judged itself
against a 60 fps tolerance — 2× too strict at 30, 2.4× too loose at 144. The
durations recorded in earlier revisions were real; the verdict "within one
frame" was not reliably earned. `scripts/run-test.sh` now exports `TEST_FPS`
and the test cross-checks it against the engine's modal delta within 1 %.

Under `Engine.time_scale = 0.5` the window is unchanged in game time, as R4
says.

## F6 — the trap can actually hit someone

Added 2026-10-24 after the author noticed the trap was firing once the player
had already walked past.

| | |
|---|---|
| Player offset when the trap warns | **−33.6 px** (short of the trap) |
| Player offset when the spikes arrive | **+6.4 px** (hurt box is ±13) |
| Health | **5 → 4** |

Identical at 30, 60 and 144 fps.

## Geometry — the derivation is asserted, not maintained

| | |
|---|---|
| `DetectArea` half-width | 33 px; `SPEED × WARN_SECONDS − 5` = 33.4 px |
| Detection zones | 175–241, 287–353, 399–465 — no overlap |

Changing `WARN_SECONDS` without changing the shape now fails the suite.
**22 checks, 0 failures** at each rate.

## The evidence table

| Check | Status |
|---|---|
| Baseline | **done** — above |
| Shaders parse | **not yet** — no shader exists |
| Both shader mutations exit 1 (semicolon, rename) | **not yet** |
| Driver sampled at 30/60/144 through a real event, incl. retrigger | **partial** — the game state is, at all three rates (R1–R6, 16 checks). The *uniform* is not, because there is no uniform yet. |
| Controlled values (HUMAN) | **not yet** |
| In play (HUMAN) | **not yet** — nobody has played the slice |
| Hint experiment (HUMAN) | **not yet** |
| Interface sweep (HUMAN) | **not yet** |
| One shader, two materials (HUMAN) | **not yet** |
| Material wiring after fresh import; `source_color` mutation exits 1 | **not yet** |
| Texture data — curl ratio | **not applicable as planned** — the brief's material plan uses code-written colour and data textures and no normal map. If that changes, the calibration pair comes with it. |
| Import settings — `.import` diffs the editor rewrote | **not yet** — the editor has not been opened on this project |

## Renderer, confirmed

A real windowed run, 2026-10-24. Not a headless run: headless reports
`forward_plus` and `vulkan` while leaving the adapter name empty and the window
0 × 0, because it initialises no device. The adapter name is the evidence.

```
Vulkan 1.4.357 - Forward+ - Using Device #0: NVIDIA - NVIDIA GeForce RTX 5080 Laptop GPU
--- renderer check ---
  project.godot asks for : forward_plus
  actually running       : forward_plus
  driver                 : vulkan
  adapter                : NVIDIA GeForce RTX 5080 Laptop GPU
  adapter vendor         : NVIDIA
  window size            : (1280, 720)
----------------------
```

Exit code 0, no errors. §6 and §7 of `CHANGE-BRIEF.md` therefore keep the
Forward+/Mobile assumption their predictions are written under.

## Known limitations

1. ~~Forward+ has never run on real hardware here.~~ **Resolved 2026-10-24** —
   see "Renderer, confirmed" below.
2. **The restart exploit.** R3 restarts the warning on every entry, so a player
   who backs out of the detection zone and re-enters repeatedly is never hit. This is the
   accepted price of "every trigger gets its own warning" and is recorded in
   `CHANGE-BRIEF.md` revision 5.0.1 rather than discovered later. A cooldown on
   re-entry would fix it and is not in scope here.
3. **The player has move and jump only.** No combat, no magic, no dodge roll.
   Deliberate: the brief's boundaries say movement and input do not change.
4. **No human check has been performed yet.** Every HUMAN row above is
   outstanding. A passing headless suite establishes that the state behaves;
   it establishes nothing about what the screen shows.
