# PROMPTS.md — what was asked of the agent, and what is reproducible

Constraints that apply to every prompt in this file, carried over from the
earlier assignments and from the course's rules:

- No named living artist, no copyrighted character, no brand, no existing
  music or recording.
- Every generated asset gets a row in `ASSET-LOG.md` with its licence, whether
  or not it ships.
- Never paste an API key or credential into a prompt or commit one.

---

## 0. There is no `claude -p` transcript, and here is why

Assignment 5's agent work was done in **interactive Claude Code sessions**, not
one-shot `claude -p` runs. There is therefore no single pasteable prompt and no
saved transcript in this repository, and inventing one after the fact would be
a reconstruction presented as a record.

What exists instead is better for reproducing the work, because it is what the
agent actually read:

| | |
|---|---|
| **`CLAUDE.md`** | The standing contract for every session. It is loaded automatically, states the ownership rule (`godot/shaders/` is hand-written and never touched by an agent), lists the out-of-scope files, and records the headless facts that stop an agent claiming colour from a dummy renderer. |
| **`CHANGE-BRIEF.md`** | Imported into `CLAUDE.md` with `@CHANGE-BRIEF.md`, so it *is* part of every prompt. Committed 2026-10-23, before any shader existed and before the first agent session, with the uniform table, six measurable rules and five predicted failure cases the agent had to satisfy. |
| **`youtube/.../BUILD-PROMPT.md`** | The film, as a command sequence rather than a request. Run it from a clean cache and the same film comes out. |
| **`tools/check_claude_refs.py`** | Asserts all 50 claims in `CLAUDE.md` by content, so the contract cannot quietly drift away from the code it describes. It has caught seventeen drifts. |

Running `tools/check_claude_refs.py` and reading those two files together is
the honest answer to "what did you ask it to do?".

## 1. The film's two on-screen prompts

Both are in `youtube/claude-liam-walker-the-lost-gamedev/PROMPTS.md`, verbatim,
with the labels they carry on screen. The opening one is a **reconstruction**,
written to be illustrative and never sent; the film says so out loud in its
first ten seconds and shows a `RECONSTRUCTION` label for the whole beat. No
build receipt, transcript or token count appears anywhere in the film.

## 2. Generative prompts

**None for any asset in the game.** No image model, 3D generator or audio model
produced a file under `godot/`. Every texture and sprite is written by a
committed script (`tools/make_sprites.py`, `godot/tools/write_textures.gd`) and
every model is my own Blender work from Assignment 3. Assignment 3's asset
libraries and 3D generators were not used here at all.

So there is no prompt to log, no model version to pin and no terms to record,
and the course's constraint on such prompts is satisfied vacuously.
`ASSET-LOG.md` says the same in its own words rather than being left blank.

**One generative model runs in the project**, and its input is a script rather
than a prompt: the film's narration is Kokoro text-to-speech, voice `am_onyx`,
run locally. Every sentence it speaks is committed in the film's
`beat_sheet.json` as `narration_text`. The model picks the voice and nothing
else, so there is no creative instruction to archive — the "prompt" is the
film's own script, already in the repository and already fact-checked line by
line. `ATTRIBUTION.md` §2.1 records it.

## 3. What a reader should check instead of a transcript

1. `git log --oneline` — the order the work happened in, which is the real
   evidence of who wrote which lines.
2. `git log --format='%h %an' -- godot/shaders/` — four commits, one author,
   no co-author trailer.
3. `git diff --stat godot/shaders/` across any agent commit — empty.
4. `CHANGE-BRIEF.md`'s commit date against the first `.gdshader` commit date —
   the specification came first, which is the claim a transcript would be
   trying to support.
