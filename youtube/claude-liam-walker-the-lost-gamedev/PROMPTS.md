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

**None for any asset in the game.** No image model, 3D generator or audio
model produced a file under `godot/`, so there is no prompt to log, no model
version to pin and no terms to record for the game. Every texture and sprite
the film shows is written by committed code: `tools/make_sprites.py` and
`godot/tools/write_textures.gd`.

**One generative model runs in this film, and its input is not a prompt but a
script.** The narration is **Kokoro** text-to-speech, voice `am_onyx`, run
locally. What it is given is the exact sentence to say, and every one of those
sentences is in `beat_sheet.json` as `narration_text`, checked line by line in
`FACTCHECK.md` and listed beat by beat in `SHOTLIST.md`. There is no creative
instruction to archive separately: the model chooses the voice and nothing
else, and archiving the "prompt" would mean committing the narration twice.

The constraint the course places on generative prompts — no named living
artist, no brand, no copyrighted character, no existing music — holds. It is
satisfied vacuously for the game, and for the narration by the fact that the
text is the film's own script.

`../../ASSET-LOG.md` therefore has nothing to list for this assignment, and
says so in those words rather than being left blank.
