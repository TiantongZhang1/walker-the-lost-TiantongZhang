# walker-the-lost-TiantongZhang

**CSYE 7270, Building Virtual Environments — Fall 2026.**
Tiantong Zhang · `zhang.tiant@northeastern.edu`

**The Lost** — a 2D side-view dungeon crawler. Four themed floors, one boss
each, and the boss drops the key to the floor below. You do not kill the
bosses: each is an adventurer who went down before you and was corrupted by the
dungeon's miasma, and beating one purifies them back into a person who joins
your hub. Progress is not a percentage in a save file; it is the number of
people standing in the room you come home to.

| | |
|---|---|
| Repository | <https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang> |
| Engine | Godot **4.7.2.stable.official** `ed1daf0bf`, Forward+ |
| Resolution | 640 × 360 logical, 1280 × 720 windowed, `canvas_items` stretch |
| Scale convention | 16 px = 1 m |
| Design document | `../the-lost-gdd/GDD.md` — moves into `design/` when A4 starts |
| Automated checks | **33 — 0 failures** (5 + 12 + 16), from a clean clone |

---

## Status, stated plainly

**Assignment 5 is in progress; neither shader is written yet.** What runs today
is the prerequisite slice: a player who can walk and jump, a floor, and three
spike traps that warn before they fire. Assignment 5 assumes a game exists from
Assignment 2, and the change of game on 2026-10-17 left this repository empty,
so the slice was built to give the shaders something to attach to.

- `CHANGE-BRIEF.md` — the Assignment 5 specification, committed before any
  shader and before the first build prompt
- `CLAUDE.md` — the agent draft; the author's review is a separate commit
- `TEST-REPORT.md` — the baseline, and every check still outstanding
- `FRICTIONAL.md` — the change-of-game justification and the working log
- `TOOLCHAIN.md` — every file carried over from `walker-ninja`, classified

Assignments 1–3 are **not** here. They were submitted from
`walker-ninja-TiantongZhang` under the tags `a2-submitted` and `a3`, and that
repository has not been modified since. Per the assignment rule, the tags
continue here: this repository's first tag will be `a5`.

**`godot/shaders/` is written by hand by the author and never by an agent.**
`git diff --stat godot/shaders/` across any agent commit must print nothing.

## Run it

Double-click **`run-game.bat`**.

There is no standalone `.exe` — this is a Godot project, so the editor binary
runs it from `godot/project.godot`. The `.bat` finds Godot by a path relative
to itself, so moving the whole course folder is fine; separating this
repository from the Godot download is not.

There is no main scene set, so Godot will open the editor rather than a running
game. That is correct for now.

## Layout

```
godot/            the Godot project (empty shell)
  game/           main scene and autoloads
  scenes/         composed scenes
  features/       per-feature nodes and scripts
  levels/         the hub and four floors
  ui/             HUD and dialogue
  assets/         art, audio, models
  tests/          headless check scripts
scripts/          film and evidence build chain      (see TOOLCHAIN.md)
tools/            Blender and 3D asset build scripts (see TOOLCHAIN.md)
design/           design documents
docs/             notes
```

## The documents, and what each is for

| File | What goes in it |
|---|---|
| `FRICTIONAL.md` | Dated log of the design thinking, written the same day |
| `TOOLCHAIN.md` | What was carried over from walker-ninja and what state it is in |
| `CONCEPT.md` | The game in one page, with dated revisions appended |
| `SOURCES.md` | Where every file came from — mine, generated, or third-party |
| `ASSET-LOG.md` | Every asset, its prompt, its licence, and whether it shipped |
| `PROMPTS.md` | The generation prompts, ready to paste |

`CONCEPT.md`, `SOURCES.md`, `ASSET-LOG.md` and `PROMPTS.md` are currently
skeletons. They are tracked from the first commit on purpose, so that the git
history shows when each claim was first made.
