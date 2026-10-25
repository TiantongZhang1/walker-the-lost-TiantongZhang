"""Verify every claim CLAUDE.md makes about another file still holds.

Three versions, each written after the previous one let something through.

  1. Checked that the referenced LINE EXISTED. Two references drifted when
     their scenes were edited; the line numbers still resolved, just to the
     wrong nodes, and it passed.
  2. Checked the line's CONTENT. It still only parsed full `path.gd:42`
     references and not the bare `:42` continuations, while a comment claimed
     those were covered. Three of them were wrong when that was found.
  3. This one. Bare continuations resolve against the file named above them,
     the way a reader resolves them -- and scene files are checked by NODE
     NAME instead of by line, because every editor save renumbers a .tscn,
     strips its `;` comments and deletes properties equal to their defaults.
     Four separate drifts came from that one habit before the line numbers
     were given up.

Run:  python -I tools/check_claude_refs.py
"""
import pathlib
import re
import sys

# path:line -> a substring the target line must contain. Text files only:
# anything the Godot editor rewrites belongs in CONTAINS instead.
EXPECT = {
    "godot/project.godot:14": "main_scene",
    "godot/project.godot:15": "Forward Plus",
    "godot/project.godot:19": "viewport_width",
    "godot/project.godot:59": "default_texture_filter",
    "godot/features/player/player.gd:13": "16 px = 1 m",
    "godot/features/player/player.gd:42": "take_damage",
    "godot/features/traps/spike_trap.gd:27": "enum State",
    "godot/features/traps/spike_trap.gd:39": "WARN_SECONDS",
    "godot/features/traps/spike_trap.gd:50": "warn_amount",
    "godot/features/traps/spike_trap.gd:110": "func disarm",
    "godot/features/traps/spike_trap.gd:119": "func warning_remaining",
    "godot/features/traps/spike_trap.gd:125": "_on_detect_body_entered",
    "godot/features/traps/trap_warning_driver.gd:1": "class_name TrapWarningDriver",
    "godot/tests/test_trap_warning.gd:33": "process_priority",
    "scripts/run-test.sh:25": "GODOT:=",
}

# path -> substrings the file must contain somewhere. For scenes, shaders and
# import files, where position is the editor's to decide and only the names
# are ours.
CONTAINS = {
    "godot/features/traps/spike_trap.tscn": [
        'name="Sprite2D"', 'name="DetectArea"', 'name="HurtArea"',
        'name="WarningDriver"', "_on_detect_body_entered",
    ],
    "godot/game/main.tscn": [
        'name="SpikeTrap1"', 'name="SpikeTrap2"', 'name="SpikeTrap3"',
        'name="CaptureRig"',
    ],
    "godot/scenes/asset_showcase.tscn": [
        'name="WorldEnvironment"', 'name="Sun"', 'name="Camera3D"',
        'name="Slime"', 'name="SlimeFlooded"', 'name="CameraMaterials"',
        "stone_flooded.tres",
    ],
    "godot/assets/models/slime.glb.import": [
        '"A3_SlimeBody"', '"use_external/enabled": true',
        "res://assets/materials/stone_dry.tres",
    ],
    "godot/shaders/trap_warning.gdshader": ["warn_amount", "warn_color"],
    "godot/shaders/dungeon_surface.gdshader": [
        "stone_albedo", "wetness_mask", "group_uniforms",
    ],
    "godot/shaders/hint_bands.gdshader": [
        "bands_srgb", "bands_data", "use_source_color", "unshaded",
    ],
    "godot/assets/materials/stone_dry.tres": ["dungeon_surface.gdshader"],
    "godot/assets/materials/stone_flooded.tres": ["dungeon_surface.gdshader"],
}

doc = pathlib.Path("CLAUDE.md").read_text(encoding="utf-8")
bad = 0

n_lines = len(doc.splitlines())
print(f"CLAUDE.md is {n_lines} lines (Assignment 5 limit: under 120)")
if n_lines >= 120:
    print("  OVER THE LIMIT")
    bad += 1

# CLAUDE.md writes some references in full and others as a bare `:NN`
# continuation of the file named before them. A reader resolves the bare form
# against the most recent file above it, so that is what this does: one pass
# in document order, tracking the current file.
TOKEN = re.compile(
    r"`(?:res://)?([\w./-]+\.(?:gd|tscn|godot|sh|gdshader|tres|import))(?::(\d+))?`"
    r"|`:(\d+)`"
)

refs = set()
current = None
for m in TOKEN.finditer(doc):
    path, num, bare = m.group(1), m.group(2), m.group(3)
    if path is not None:
        current = path
        if num is not None:
            refs.add(f"{path}:{num}")
    elif bare is not None:
        if current is None:
            print(f"  LOOSE `:{bare}` with no file named before it")
            bad += 1
        else:
            refs.add(f"{current}:{bare}")

for ref in sorted(refs | set(EXPECT)):
    path, num = ref.rsplit(":", 1)
    num = int(num)
    body = pathlib.Path(path)
    if not body.exists():
        print(f"  MISS  {ref}  file not found")
        bad += 1
        continue
    rows = body.read_text(encoding="utf-8", errors="replace").splitlines()
    if num > len(rows):
        print(f"  MISS  {ref}  only {len(rows)} lines")
        bad += 1
        continue
    want = EXPECT.get(ref)
    got = rows[num - 1].strip()
    if want is None:
        print(f"  ????  {ref}  not in EXPECT -> {got[:48]}")
        bad += 1
    elif want not in got:
        print(f"  DRIFT {ref}  expected {want!r}, found {got[:48]!r}")
        bad += 1
    else:
        print(f"  OK    {ref}  {got[:50]}")

for path in sorted(CONTAINS):
    body = pathlib.Path(path)
    if not body.exists():
        print(f"  MISS  {path}  file not found")
        bad += len(CONTAINS[path])
        continue
    text = body.read_text(encoding="utf-8", errors="replace")
    missing = [w for w in CONTAINS[path] if w not in text]
    if missing:
        for w in missing:
            print(f"  GONE  {path}  no longer contains {w!r}")
        bad += len(missing)
    else:
        print(f"  OK    {path}  all {len(CONTAINS[path])} names present")

total = len(EXPECT) + sum(len(v) for v in CONTAINS.values())
print(f"\n{total} assertions ({len(EXPECT)} by line, "
      f"{total - len(EXPECT)} by name), {bad} problem(s)")
sys.exit(1 if bad else 0)
