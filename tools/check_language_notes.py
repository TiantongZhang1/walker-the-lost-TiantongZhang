"""Verify every line reference LANGUAGE-NOTES.md makes still points where it says.

Assignment 5: "The agent may check that your line references point where you
say. It does not write the answers." This script is that check and nothing
more. The answers in LANGUAGE-NOTES.md are the author's; no agent writes or
edits them, and this file never reads them for meaning - only the targets
they cite.

Why a script rather than a reading. Six references in CLAUDE.md drifted
during this assignment when the editor rewrote a scene, and not one was
caught by looking. A shader gains a line, every number below it moves, and a
document that cited them is quietly wrong in a way that survives proofreading
and fails an oral check.

Run:  python -I tools/check_language_notes.py
"""
import pathlib
import sys

G = "godot/shaders/standard_generated.gdshader"
T = "godot/shaders/trap_warning.gdshader"
D = "godot/shaders/dungeon_surface.gdshader"
H = "godot/shaders/hint_bands.gdshader"
V = "godot/features/traps/trap_warning_driver.gd"

# (section, file, line, a substring that line must contain)
CLAIMS = [
    ("Part 1", G, 3, "shader_type"),
    ("Part 1", G, 4, "render_mode"),
    ("Part 1", G, 6, "albedo : source_color"),
    ("Part 1", G, 20, "normal_scale"),
    ("Part 1", G, 7, "texture_albedo"),
    ("Part 1", G, 19, "texture_normal"),
    ("Part 1", G, 35, "ALBEDO ="),
    ("Part 1", G, 43, "ROUGHNESS ="),
    ("Part 1", G, 46, "NORMAL_MAP ="),
    ("Q1", T, 1, "shader_type canvas_item"),
    ("Q1", D, 1, "shader_type spatial"),
    ("Q1", H, 1, "shader_type spatial"),
    ("Q2", T, 6, "mix(COLOR.rgb"),
    ("Q3", T, 6, "COLOR"),
    ("Q3", D, 17, "UV"),
    ("Q3", D, 20, "UV"),
    ("Q3", D, 23, "ALBEDO ="),
    ("Q3", D, 26, "ROUGHNESS ="),
    ("Q4", T, 2, "hint_range(0.0, 1.0)"),
    ("Q4", D, 4, "hint_default_black"),
    ("Q4", H, 4, "source_color"),
    ("Q4", T, 3, "warn_color"),
    ("Q5", T, 2, "hint_range"),
    ("Q6", G, 7, "source_color"),
    ("Q6", G, 19, "hint_roughness_normal"),
    ("Q6", D, 3, "stone_albedo : source_color"),
    ("Q6", D, 4, "wetness_mask"),
    ("Q7", T, 2, "warn_amount"),
    ("Q7", V, 76, "set_shader_parameter"),
    ("Q7", T, 6, "warn_amount"),
    ("Q7", V, 42, "process_priority = 100"),
    ("Q8", D, 6, "group_uniforms"),
    ("Q8", D, 10, "group_uniforms"),
    ("Q8", D, 13, "group_uniforms"),
    ("Q8", D, 23, "ALBEDO"),
    ("Q8", D, 26, "ROUGHNESS"),
]

notes = pathlib.Path("LANGUAGE-NOTES.md")
bad = 0
if not notes.exists():
    print("LANGUAGE-NOTES.md not found")
    sys.exit(1)

cache: dict[str, list[str]] = {}
for section, path, num, want in CLAIMS:
    if path not in cache:
        p = pathlib.Path(path)
        if not p.exists():
            print(f"  MISS  {section:<6} {path}  file not found")
            bad += 1
            cache[path] = []
            continue
        cache[path] = p.read_text(encoding="utf-8", errors="replace").splitlines()
    rows = cache[path]
    if not rows:
        continue
    if num > len(rows):
        print(f"  MISS  {section:<6} {path}:{num}  only {len(rows)} lines")
        bad += 1
        continue
    got = rows[num - 1].strip()
    if want in got:
        print(f"  OK    {section:<6} {path.split('/')[-1]}:{num}  {got[:48]}")
    else:
        print(f"  DRIFT {section:<6} {path}:{num}  expected {want!r}, found {got[:48]!r}")
        bad += 1

print(f"\n{len(CLAIMS)} line references checked by content, {bad} problem(s)")
print("The answers themselves are the author's and are not checked here.")
sys.exit(1 if bad else 0)
