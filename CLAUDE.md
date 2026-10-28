# CLAUDE.md

Godot 4 game repository, GDScript, project in `godot/`.

## Project context

Every fact carries the file it came from. Check them; do not trust them.

| Fact | Value | Reference |
|---|---|---|
| Engine | Godot **4.7.2.stable.official** `ed1daf0bf` | banner printed by every `scripts/run-test.sh` run |
| Renderer | **Forward+** | `godot/project.godot:15` (`config/features`). Not `rendering_method`: it equals the default, so editor saves delete it |
| Main scene | `res://game/main.tscn` | `godot/project.godot:14` |
| Logical resolution | 640 × 360, nearest-neighbour filtering | `godot/project.godot:19`, `:59` |
| Scale | 16 px = 1 m | `godot/features/player/player.gd:13` |

**Scenes are referenced by node name, never by line.** An editor save
rewrites a `.tscn`: it renumbers nodes, strips `;` comments and drops any
property equal to its default. Names survive; `tools/check_claude_refs.py`
asserts them.

**The object the colour effect changes.** A spike trap in
`godot/features/traps/spike_trap.tscn`, drawn by one `Sprite2D` — one sprite,
not two, because firing swaps the texture rather than moving a child, so there
is exactly one material to drive. `SpikeTrap1/2/3` sit in
`godot/game/main.tscn`. Two Area2Ds there, not interchangeable: `DetectArea`
is 66 px and starts the warning, `HurtArea` is 16 px and is the only one that
damages. DetectArea's width is **derived from `WARN_SECONDS`**.

**The script that owns the game state.** `godot/features/traps/spike_trap.gd`.

| | |
|---|---|
| The driven value | `var warn_amount: float` — `:50` |
| State enum | `:27` |
| Window length | `const WARN_SECONDS := 0.40` — `:39` |
| Early end | `disarm()` — `:110` |
| Test helper | `warning_remaining()` — `:119` |
| What begins the state | `_on_detect_body_entered` — `:125`, wired to `DetectArea` in the scene |

`warn_amount` is advanced only by that script. Presentation reads it and must
never write it.

**The thing that reads it.** `godot/features/traps/trap_warning_driver.gd`,
the `WarningDriver` child of each trap, tested by
`godot/tests/test_trap_shader_driver.gd`. It duplicates the `ShaderMaterial`
in `_ready()` — sub-resources are shared across scene instances, so otherwise
all three warn together — and writes one uniform at `process_priority = 100`.

**The player.** `godot/features/player/player.gd` — move and jump only, plus
`take_damage()` at `:42`. Combo, magic and roll are absent on purpose.

**The 3D objects for the textured shader.** Two slimes in
`godot/scenes/asset_showcase.tscn`. `Slime` takes `stone_dry.tres` **from the
importer** (`use_external` on `A3_SlimeBody` in `slime.glb.import`, so a
reimport keeps it); `SlimeFlooded` overrides the node with
`stone_flooded.tres`. Same geometry, same light — `Sun` is energy 1.0, which
being the default is not written in the file. `CameraMaterials` frames both.

**Test commands.** Always through the wrapper: it is the only thing that fails on a `SHADER ERROR` or `SCRIPT ERROR`, which Godot prints while exiting 0.

```bash
godot --headless --path godot --import     # once after cloning
./scripts/run-test.sh <test>.gd <fps>
```

`test_input_map.gd` and `check_assets_3d.gd` at 60; `test_trap_warning.gd` and
`test_trap_shader_driver.gd` at **30, 60 and 144** — a duration that is only
ever measured at one rate has not been measured. `godot` is not on PATH here;
the wrapper resolves it relative to the repository and `GODOT=` overrides it —
`scripts/run-test.sh:25`.

### Headless facts

- A headless run uses a **dummy renderer and draws nothing**. It can show a
  shader parses, what it declares, and a float on a given frame — never colour.
- It does **not** report uniform defaults. Assert names, types and hints with `get_shader_uniform_list()`; read defaults from the shader source.
- Never add `--rendering-driver` to a test command.
- Sample a uniform from a high-`process_priority` node, so it reads after every
  other `_process()` in the frame — `godot/tests/test_trap_warning.gd:33`.

## Current change

@CHANGE-BRIEF.md

## Ownership

**Files in `godot/shaders/` are hand-written by the human and are never
edited by an agent** — no agent creates, edits or reformats a `.gdshader`.
If one looks wrong or cannot meet the specification, say so and stop.

`LANGUAGE-NOTES.md` is the human's too; an agent may check its line references
point where it says, but does not write the answers.

After any agent session, `git diff --stat godot/shaders/` must print nothing;
diff `scripts/run-test.sh` too, since an agent can edit the wrapper.

## Out of scope

Do not touch: collision layers or shapes, player movement or the input map, the
trap's state machine or its timings, any existing test or its expectations, the
`.glb` model files, or anything that is not a `SpikeTrap`.

Do not add the GDD's combo, magic or dodge roll: the brief's boundaries say
movement and input do not change. Presentation reads game state, never writes.

## Unconfirmed

- ~~Forward+ untried on real hardware.~~ **Confirmed 2026-10-24**: Vulkan
  1.4.357, RTX 5080 Laptop, 1280 × 720. Evidence in `TEST-REPORT.md`.
- ~~Whether 0.40 s is enough warning.~~ **Played 2026-10-24: it is.**
- ~~Whether `source_color` changes the value the shader *receives*.~~
  **Measured 2026-10-24: it does not** (H1, exact), and `hint_range` does
  not clamp a value set from code. `TEST-REPORT.md`, `captures/a5/`.
- Drafted by the session that built the repository, not a cold agent: more
  accurate, and so a weaker thing for a human review to test.
  `tools/check_claude_refs.py` asserts all 50 claims above. It has caught
  seventeen, three of which a bare `:NN` had hidden from it.
