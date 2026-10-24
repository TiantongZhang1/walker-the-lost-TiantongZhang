# CLAUDE.md

Godot 4 game repository, GDScript, project in `godot/`. Read this first, then
the specification it imports.

## Project context

Every fact here carries the file it came from. Check them; do not trust them.

| Fact | Value | Reference |
|---|---|---|
| Engine | Godot **4.7.2.stable.official** `ed1daf0bf` | banner printed by every `scripts/run-test.sh` run |
| Renderer | **Forward+** | `godot/project.godot:63`, and `config/features` at `:15` |
| Main scene | `res://game/main.tscn` | `godot/project.godot:14` |
| Logical resolution | 640 × 360, nearest-neighbour filtering | `godot/project.godot:19`, `:59` |
| Scale | 16 px = 1 m | `godot/features/player/player.gd:13` |

**The object the colour effect changes.** A spike trap, drawn by one `Sprite2D`
child of the trap's `Node2D` root — `godot/features/traps/spike_trap.tscn:12`.
It is one sprite, not two: firing swaps the texture rather than moving a child,
so the trap has exactly one material to drive. Three instances sit in the room
at `godot/game/main.tscn:47`, `:50`, `:53`.

**The script that owns the game state.** `godot/features/traps/spike_trap.gd`.

| | |
|---|---|
| The driven value | `var warn_amount: float` — `:43` |
| State enum | `:27` |
| Window length | `const WARN_SECONDS := 0.45` — `:32` |
| What begins the state | `_on_trigger_body_entered` — `:115`, wired at `godot/features/traps/spike_trap.tscn:23` |
| Early end | `disarm()` — `:100` |
| Test helper | `warning_remaining()` — `:109` |

`warn_amount` is advanced only by that script. Presentation reads it and must
never write it.

**The player.** `godot/features/player/player.gd` — move and jump only, plus
`take_damage()` at `:42`, which the trap calls when it fires. The GDD's combo,
magic and dodge roll are deliberately absent; see "Out of scope".

**The 3D object for the textured shader.** The slime in
`godot/scenes/asset_showcase.tscn:65`, instanced from
`res://assets/models/slime.glb`. The scene also holds a `WorldEnvironment`
(`:42`), one `DirectionalLight3D` named `Sun` (`:49`) and a `Camera3D` (`:54`).
**Its material today comes from the imported `.glb` itself** — there is no
`.tres` material override yet. The two `ShaderMaterial` resources this
assignment adds will be the first.

**Test commands.** Always through the wrapper; it is the only thing that fails
on a `SHADER ERROR` or `SCRIPT ERROR` that Godot prints while still exiting 0.

```bash
godot --headless --path godot --import     # once after cloning
./scripts/run-test.sh test_input_map.gd 60
./scripts/run-test.sh check_assets_3d.gd 60
./scripts/run-test.sh test_trap_warning.gd 30
./scripts/run-test.sh test_trap_warning.gd 60
./scripts/run-test.sh test_trap_warning.gd 144
```

`godot` is not on PATH on this machine; the wrapper resolves it relative to the
repository and `GODOT=` overrides it — `scripts/run-test.sh:25`.

### Headless facts

- A headless run uses a **dummy renderer and draws nothing**. It can establish
  that a shader parses, that uniforms are declared, and what a float was on a
  given frame. It can establish nothing about colour, contrast or look.
- A headless engine does not report uniform **defaults**. Assert declared names
  and types with `get_shader_uniform_list()`; read defaults from the shader
  source text.
- Never add `--rendering-driver` to a test command.
- Sample a uniform from a node with a high `process_priority` so it reads after
  every other `_process()` in the frame — `godot/tests/test_trap_warning.gd:33`.

## Current change

@CHANGE-BRIEF.md

## Ownership

**Files in `godot/shaders/` are hand-written by the human and are never edited
by an agent.** No agent creates, edits or reformats a `.gdshader` file. If a
shader looks wrong or cannot meet the specification, say so and stop.

`LANGUAGE-NOTES.md` is written by the human. An agent may check that its line
references point where it says they do; it does not write the answers.

After any agent session, `git diff --stat godot/shaders/` must print nothing,
and `scripts/run-test.sh` must be diffed too — an agent can edit the wrapper.

## Out of scope

Do not touch: collision layers or shapes, player movement or the input map, the
trap's state machine or its timings, any existing test or its expectations, the
`.glb` model files, or anything that is not a `SpikeTrap`.

Do not add the GDD's combo, magic or dodge roll. They are not needed for this
assignment, and the specification's boundaries say movement and input do not
change.

Presentation code may read game state. It never writes it.

## Unconfirmed

- ~~Forward+ has never been run on real hardware here.~~ **Confirmed
  2026-10-24**: Vulkan 1.4.357, NVIDIA GeForce RTX 5080 Laptop GPU, window
  1280 × 720. Evidence in `TEST-REPORT.md`.
- Whether 0.45 s is enough warning to react to is unjudged; nobody has played
  the slice yet.
- Whether `source_color` changes the value the shader receives is **predicted
  both ways** in `CHANGE-BRIEF.md` §6 and settled by capture, not by assertion.
- This file was drafted by the same session that built the repository, not by a
  cold agent reading it. That makes the draft more accurate and the human
  review *less* likely to catch a wrong reference by accident — so every line
  number above still needs checking by hand.
