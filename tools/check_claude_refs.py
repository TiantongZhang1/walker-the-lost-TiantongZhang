"""Verify every `path:line` in CLAUDE.md points at what the text claims.

The first version of this only checked that the line EXISTED, and two
references silently drifted when their scenes were edited - the line numbers
still resolved, just to the wrong nodes. A reference check that cannot fail
when the target moves is not a check.

Each entry below pairs a reference with a substring the target line must
contain. Run:  python -I tools/check_claude_refs.py
"""
import pathlib
import re
import sys

EXPECT = {
    "godot/project.godot:63": "forward_plus",
    "godot/project.godot:14": "main_scene",
    "godot/project.godot:19": "viewport_width",
    "godot/features/player/player.gd:13": "16 px = 1 m",
    "godot/features/player/player.gd:42": "take_damage",
    "godot/features/traps/spike_trap.tscn:22": 'name="Sprite2D"',
    "godot/features/traps/spike_trap.tscn:26": 'name="DetectArea"',
    "godot/features/traps/spike_trap.tscn:42": 'name="WarningDriver"',
    "godot/features/traps/spike_trap.tscn:45": "_on_detect_body_entered",
    "godot/features/traps/spike_trap.gd:27": "enum State",
    "godot/features/traps/spike_trap.gd:39": "WARN_SECONDS",
    "godot/features/traps/spike_trap.gd:50": "warn_amount",
    "godot/features/traps/spike_trap.gd:110": "func disarm",
    "godot/features/traps/spike_trap.gd:119": "func warning_remaining",
    "godot/features/traps/spike_trap.gd:125": "_on_detect_body_entered",
    "godot/game/main.tscn:50": "SpikeTrap1",
    "godot/game/main.tscn:53": "SpikeTrap2",
    "godot/game/main.tscn:56": "SpikeTrap3",
    "godot/scenes/asset_showcase.tscn:65": 'name="Slime"',
    "scripts/run-test.sh:25": "GODOT:=",
    "godot/tests/test_trap_warning.gd:33": "process_priority",
}

doc = pathlib.Path("CLAUDE.md").read_text(encoding="utf-8")
lines = len(doc.splitlines())
bad = 0

print(f"CLAUDE.md is {lines} lines (Assignment 5 limit: under 120)")
if lines >= 120:
    print("  OVER THE LIMIT")
    bad += 1

refs = set()
for path, num in re.findall(r"`([\w./-]+\.(?:gd|tscn|godot|sh)):(\d+)`", doc):
    refs.add(f"{path}:{num}")
# bare `:NN` continuations are checked through EXPECT, which lists them in full
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
        print(f"  ????  {ref}  not in EXPECT -> {got[:50]}")
        bad += 1
    elif want not in got:
        print(f"  DRIFT {ref}  expected {want!r}, found {got[:50]!r}")
        bad += 1
    else:
        print(f"  OK    {ref}  {got[:52]}")

print(f"\n{len(EXPECT)} references checked by content, {bad} problem(s)")
sys.exit(1 if bad else 0)
