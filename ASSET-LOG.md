# ASSET-LOG.md

One row per asset: what it is, what produced it, the prompt, the licence, and
whether it actually shipped. Rejected assets are logged too — a rejection with
a reason is evidence of judgement, and leaving it out would overstate the hit
rate.

> **This file is empty by fact, not by neglect.** It exists to log *generated
> and third-party* assets: the prompt, the model, the licence. At the `a5` tag
> there are none. Every texture and sprite in the game is written by a
> committed script, every model is my own Blender work from Assignment 3, and
> nothing was downloaded. There is no prompt to record and no licence to track.
>
> `ATTRIBUTION.md` is the per-asset accounting that **does** apply, and
> `SOURCES.md` §4 lists each code-written file beside the script that draws it.
> The one generative model in the project — Kokoro TTS, for the film's
> narration — is recorded in both, and is film audio rather than a game asset.
>
> The file is tracked from the first commit on purpose, so the git history
> shows when each claim was first made.

---

## Music

_None._ The slice has no music. `walker-ninja`'s audio was deliberately not
carried across: Assignment 5's boundaries put audio outside this change, and
the port is Assignment 6's first work.

## Sound effects

_None_, for the same reason. `find godot -name '*.mp3' -o -name '*.ogg' -o
-name '*.wav'` returns nothing.

## Art

_None generated and none downloaded._ The four sprites are written by
`tools/make_sprites.py` and the three textures by `godot/tools/write_textures.gd`,
both committed. See `ATTRIBUTION.md` §1.1.

## 3D assets

_None generated and none downloaded._ `slime.glb`, `spike_trap.glb` and
`torch.glb` are my own Blender 5.2.2 work from Assignment 3, copied here on
2026-10-23. Assignment 3's asset libraries and 3D generators
(`search_assets`, `import_asset`, `generate_3d`) were not used in this
repository at all.

## Rejected, logged without downloading

_None._ Nothing was browsed for, so nothing was rejected. The one design
trade-off of this kind is recorded where the decision was made, not here:
`CHANGE-BRIEF.md` §8 chose code-written textures over the Poly Haven
`_nor_gl` / `_nor_dx` calibration pair, and states in the specification that
this forgoes the normal map and Step 3's curl check.
