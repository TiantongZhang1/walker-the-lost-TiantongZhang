# ASSET-LOG.md

One row per asset: what it is, what produced it, the prompt, the licence, and
whether it actually shipped. Rejected assets are logged too — a rejection with
a reason is evidence of judgement, and leaving it out would overstate the hit
rate.

> **Not empty any more.** Up to the `a5` tag there was nothing to log: every
> asset was written by committed code or was the author's own Blender work.
> The Assignment 6 port brought in two generated assets, and the rows below
> are what this file exists for. `ATTRIBUTION.md` is the licence accounting
> and carries the verbatim prompts; this file is the per-asset log.
>
> It is tracked from the first commit on purpose, so the git history shows
> when each claim was first made — including the four days it honestly said
> there was nothing to log.

---

## Music

| | |
|---|---|
| Asset | `godot/assets/music-loop.ogg`, 31.0 s, 154 kbps |
| Produced by | **Suno `v6-mini`**, 2026-10-01, on the free Basic tier |
| Prompt | `driving 124 bpm, pulsing bass with tight muted percussion, urgent and forward-moving, loop for a side-scrolling platformer, metal walkways and machinery, near-future industrial, no vocals, seamless loop` |
| Seed | None — Suno exposes none |
| Licence | **Suno retains ownership.** Personal and non-commercial use only; this project must not be monetised while the track is in it. `ATTRIBUTION.md` §1.7 has the reasoning and the date checked. |
| Shipped? | **Yes**, wired in `godot/game/room_audio.gd` at −14 dB |

## Sound effects

**Not generated — written by arithmetic**, so there is no model and no prompt
to log, only the script. Listed here anyway because they are placeholders and
a reader should not have to find that out from a docstring.

| Asset | Produced by | Shipped? |
|---|---|---|
| `sfx-trap.ogg` | `scripts/synth_placeholder_sfx.py`, seed 727001 | **Yes** — plays on every `fired`, one voice per trap |
| `sfx-death.ogg` | same | **Yes** — plays on `died` |
| `sfx-jump.ogg` | same | No. Needs a signal `player.gd` does not emit, and emitting one means editing a file A5's `CLAUDE.md` puts out of scope. |
| `sfx-slash.ogg` | same | No. Belongs to a combat move this slice does not have. |

Licence: mine. Re-running the script reproduces the WAVs byte for byte.

## Art

**Textures: none generated, none downloaded.** The four sprites are written by
`tools/make_sprites.py` and the three textures by
`godot/tools/write_textures.gd`, both committed. `ATTRIBUTION.md` §1.1.

**The dungeon: none generated, none downloaded.** `godot/game/room_backdrop.gd`
draws the masonry, arches, torches and lit floor lip as vector geometry.
There is no file to credit; the code is the asset.

**The character: generated, and logged.**

| | |
|---|---|
| Assets | `godot/assets/poses/p1-idle.png`, `p2-run`, `p3-rising`, `p4-falling`, `p8-death`, 32 × 32 |
| Produced by | **GPT-6**, one request each from a reference image, 2026-10 in walker-ninja |
| Prompts | Verbatim in `ATTRIBUTION.md` §1.6 — one reference prompt and five pose lines |
| Seed | None exposed |
| Licence | OpenAI Terms of Use, read 2026-10-06. The *"if any"* qualifier is quoted and discussed in §1.6. |
| Shipped? | **Yes**, selected by `godot/features/player/pose_driver.gd` from state the player already has |
| Rejected, logged | Four Civitai generations failed before these, each with what it failed on; three have screenshots. The record is in walker-ninja's `ASSET-LOG.md` and was not duplicated here. |

## 3D assets

_None generated and none downloaded._ `slime.glb`, `spike_trap.glb` and
`torch.glb` are my own Blender 5.2.2 work from Assignment 3, copied here on
2026-10-23. Assignment 3's asset libraries and 3D generators
(`search_assets`, `import_asset`, `generate_3d`) were not used in this
repository at all.

Still true at `a6`: the port brought in no 3D asset.

## Rejected, logged without downloading

_None._ Nothing was browsed for, so nothing was rejected. The one design
trade-off of this kind is recorded where the decision was made, not here:
`CHANGE-BRIEF.md` §8 chose code-written textures over the Poly Haven
`_nor_gl` / `_nor_dx` calibration pair, and states in the specification that
this forgoes the normal map and Step 3's curl check.
