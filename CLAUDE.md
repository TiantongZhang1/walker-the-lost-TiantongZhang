# CLAUDE.md

Godot 4 game repository, GDScript, project in `godot/`.

## Project context

Every fact carries the file it came from. Check them; do not trust them.

| Fact | Value | Reference |
|---|---|---|
| Engine | Godot **4.7.2.stable.official** `ed1daf0bf` | banner printed by every `scripts/run-test.sh` run |
| Renderer | **Forward+** | `godot/project.godot:63`, and `config/features` at `:15` |
| Main scene | `res://game/main.tscn` | `godot/project.godot:14` |
| Logical resolution | 640 × 360, nearest-neighbour filtering | `godot/project.godot:19`, `:59` |
| Scale | 16 px = 1 m | `godot/features/player/player.gd:13` |

**The object the colour effect changes.** A spike trap, drawn by one `Sprite2D`
child of the trap's `Node2D` root — `godot/features/traps/spike_trap.tscn:15`.
It is one sprite, not two: firing swaps the texture rather than moving a child,
so the trap has exactly one material to drive. Three instances sit in the room
at `godot/game/main.tscn:49`, `:52`, `:55`.

Two Area2Ds, not interchangeable: `DetectArea`
(`godot/features/traps/spike_trap.tscn:18`) is 48 px and starts the warning,
`HurtArea` is 16 px and is the only one that damages. DetectArea's width is
**derived from `WARN_SECONDS`**, so changing one without the other breaks it.

**The script that owns the game state.** `godot/features/traps/spike_trap.gd`.

| | |
|---|---|
| The driven value | `var warn_amount: float` — `:51` |
| State enum | `:27` |
| Window length | `const WARN_SECONDS := 0.30` — `:40` |
| What begins the state | `_on_detect_body_entered` — `:126`, wired at `godot/features/traps/spike_trap.tscn:34` |
| Early end | `disarm()` — `:111` |
| Test helper | `warning_remaining()` — `:120` |

`warn_amount` is advanced only by that script. Presentation reads it and must
never write it.

**The player.** `godot/features/player/player.gd` — move and jump only, plus
`take_damage()` at `:42`. Combo, magic and roll are absent on purpose.

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
  given frame — nothing about colour, contrast or look.
- A headless engine does not report uniform **defaults**. Assert declared names
  and types with `get_shader_uniform_list()`; read defaults from the shader
  source text.
- Never add `--rendering-driver` to a test command.
- Sample a uniform from a high-`process_priority` node, so it reads after every
  other `_process()` in the frame — `godot/tests/test_trap_warning.gd:33`.

## Current change

@CHANGE-BRIEF.md

## Ownership

**Files in `godot/shaders/` are hand-written by the human and are never edited
by an agent.** No agent creates, edits or reformats a `.gdshader` file. If a
shader looks wrong or cannot meet the specification, say so and stop.

`LANGUAGE-NOTES.md` is the human's too; an agent may check its line references
point where it says, but does not write the answers.

After any agent session, `git diff --stat godot/shaders/` must print nothing;
diff `scripts/run-test.sh` too, since an agent can edit the wrapper.

## Out of scope

Do not touch: collision layers or shapes, player movement or the input map, the
trap's state machine or its timings, any existing test or its expectations, the
`.glb` model files, or anything that is not a `SpikeTrap`.

Do not add the GDD's combo, magic or dodge roll: the specification's
boundaries say movement and input do not change.

Presentation code may read game state. It never writes it.

## Unconfirmed

- ~~Forward+ has never been run on real hardware here.~~ **Confirmed
  2026-10-24**: Vulkan 1.4.357, NVIDIA GeForce RTX 5080 Laptop GPU, window
  1280 × 720. Evidence in `TEST-REPORT.md`.
- Whether 0.45 s is enough warning to react to is unjudged; nobody has played
  the slice yet.
- Whether `source_color` changes the value the shader receives is **predicted
  both ways** in `CHANGE-BRIEF.md` §6 and settled by capture, not by assertion.
- This file was drafted by the same session that built the repository, not a
  cold agent reading it: more accurate, and therefore a weaker thing for a
  human review to test. `tools/check_claude_refs.py` checks every reference
  above by content; it caught two that had drifted.
