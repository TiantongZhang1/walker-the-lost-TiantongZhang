# PROMPTS.md — the prompts this film shows, and the ones it does not

## Shown on screen

Two, both in the walker bookends, both labelled on screen as what they are.

### B00 — `RECONSTRUCTION`

> Please use Walker to convert my game design document about The Lost — a
> side-view dungeon crawler where every hazard announces itself before it can
> hurt you — into a Godot project. I will write the shader that does the
> announcing by hand; you write the driver and the tests that prove it.

**This was never sent.** It is written to be illustrative of the division of
labour the assignment requires, and the narration says so in the first ten
seconds. No build receipt, transcript or token count is shown anywhere in the
film. The division it describes is real and is recorded in `CLAUDE.md`'s
Ownership section and in `../../SOURCES.md`.

### B13 — `YOUR TURN`

> Please use Walker to add a second controlled value to my shader capture
> rig, write the predicted pixel into the brief before the rig can run, and
> tell me plainly if the capture disagrees with what I wrote.

A prompt a viewer could actually use, paired in narration with a bounded
exercise they can do without it: predict the base plate pixel at
`warn_amount = 0.5`, then capture it in engine and see whether the number
survives. The film deliberately does **not** say the answer out loud.

## Generative prompts

**None.** No generative model produced any asset in this repository, so there
is no prompt to log, no model version to pin and no terms to record. Every
texture and sprite the film shows is written by committed code:
`tools/make_sprites.py` and `godot/tools/write_textures.gd`.

The constraint the course places on such prompts — no named living artist, no
brand, no copyrighted character — is therefore satisfied vacuously, and
`../../ASSET-LOG.md` has nothing to list for this assignment.

## Agent prompts behind the work

Assignment 5's Step 1 and Step 2 prompts were run against this repository and
their effects are in the git history rather than in this film. The film shows
the *result* of that division — which files carry a Claude trailer and which
do not — in B12, and `git log --format='%h %an' -- godot/shaders/` is the
check a reviewer can run in one line.

Nothing in this film was produced by a paid call.
