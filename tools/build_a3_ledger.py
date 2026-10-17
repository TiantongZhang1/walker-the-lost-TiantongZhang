#!/usr/bin/env python3
"""Write the A3 film's gamedev-evidence.json.

The checker requires that `files` plus `exclusions` cover the Godot project's
whole inventory exactly, that every excerpt resolve inside the project and
match both its file and the beat's displayed code, and that each code beat be
followed immediately by a narrated result whose media is hashed here.

Assignment 3 touches nine of the project's fifty-five files. The other
forty-six are Assignment 1 and 2 material, excluded with a reason rather than
left out, because leaving one out fails the inventory check.

The three Blender build scripts are deliberately NOT here. They live in
tools/, outside the Godot project, and `inside(game, path)` would reject
them. Their excerpts are shown as rendered images instead, hashed as result
media, which is why this film has one source excerpt rather than three.
"""
import hashlib
import io
import json
import os
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME = ROOT / "godot"
REEL = ROOT / "youtube" / "claude-liam-walker-ninja-a3-blender"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory():
    return sorted(p.relative_to(GAME).as_posix() for p in GAME.rglob("*")
                  if p.is_file()
                  and not any(x in (".godot", ".git") for x in p.relative_to(GAME).parts)
                  and p.suffix != ".uid")


COMPONENTS = [
    {
        "id": "C1-glb-assets",
        "explanation": (
            "The three assets Assignment 3 adds, as Godot imported them. Each "
            "was built in Blender from basic shapes by a script in "
            "tools/blender/ that the MCP executed directly, exported as binary "
            "glTF with +Y Up, and sized from the 2D game: the trap's 1.50 x "
            "1.00 m is the level file's own trap rect at 16 px = 1 m, the "
            "slime's 1.375 x 1.00 m is SLIME_SIZE, and the torch's 0.70 m is "
            "the handle rect in _draw_torch plus its flame. 11 primitives and "
            "210 triangles for all three, against a course limit of 6 shapes "
            "and 500 triangles each. The .import sidecars are included rather "
            "than excluded because for these three files Godot's import "
            "settings are what turns a .glb into the PackedScene the scene "
            "instances."),
        "beat_ids": ["B02", "B03", "B04", "B05", "B08"],
        "files": [
            "assets/models/torch.glb", "assets/models/torch.glb.import",
            "assets/models/spike_trap.glb", "assets/models/spike_trap.glb.import",
            "assets/models/slime.glb", "assets/models/slime.glb.import",
        ],
    },
    {
        "id": "C2-showcase-scene",
        "explanation": (
            "The scene the assignment asks for: a floor, one light, a camera "
            "and the three assets 1.9 m apart, all placed at y = 0. Sitting on "
            "the floor is the default rather than an adjustment, because each "
            "asset's origin is the centre of its underside, so the brief's "
            "third prediction is built into the layout where floating would be "
            "visible rather than merely measurable. The WorldEnvironment is "
            "not a second light: it supplies flat ambient at 0.25 so faces "
            "turned away from the sun can be inspected instead of reading as "
            "holes. project.godot is included because the project runs on "
            "gl_compatibility and that is the renderer this scene is judged "
            "under."),
        "beat_ids": ["B09"],
        "files": ["scenes/asset_showcase.tscn", "project.godot"],
    },
    {
        "id": "C3-asset-check",
        "explanation": (
            "The headless check. It loads each .glb, walks the instanced "
            "hierarchy accumulating local transforms, and prints the bounding "
            "box, the longest axis, the node scale and the distance from the "
            "floor beside the number CHANGE-BRIEF 3.0.0 predicted, exiting "
            "non-zero on any mismatch. Its first version read global_transform "
            "from nodes a script running in _init() has not put in the tree, "
            "got identity back for every one, and reported a correct asset as "
            "0.850 m tall and 0.425 m below the floor - exactly the cone's "
            "local half-height. Its own header states what it cannot show: "
            "size, orientation, scale and origin are geometry, and whether an "
            "asset reads as a torch is not."),
        "beat_ids": ["B06", "B07"],
        "files": ["tests/check_assets_3d.gd"],
    },
]

ROLES = {
    "assets/models/torch.glb": "asset",
    "assets/models/torch.glb.import": "config",
    "assets/models/spike_trap.glb": "asset",
    "assets/models/spike_trap.glb.import": "config",
    "assets/models/slime.glb": "asset",
    "assets/models/slime.glb.import": "config",
    "scenes/asset_showcase.tscn": "scene",
    "project.godot": "config",
    "tests/check_assets_3d.gd": "test",
}

EXCLUSION_RULES = [
    (lambda p: p == ".gitignore",
     "Git configuration, not game source. Excludes .godot/ from the repository."),
    (lambda p: p.startswith("assets/poses/"),
     "Assignment 2's generated character sprites and their import sidecars. "
     "Unchanged by A3 and taught in the Assignment 2 film."),
    (lambda p: p.startswith("assets/") and ("sfx-" in p or "music-loop" in p),
     "Assignment 2's audio: one generated music loop and four synthesised "
     "placeholder effects. Unchanged by A3."),
    (lambda p: p.startswith("assets/death-laugh"),
     "Assignment 2's declared placeholder death reaction. Unchanged by A3."),
    (lambda p: p == "assets/README.md",
     "Assignment 2's asset provenance table. A3's provenance is in the "
     "repository SOURCES.md section 9."),
    (lambda p: p.startswith("features/") or p.startswith("game/") or p.startswith("ui/"),
     "The 2D slice's runtime: player, tuning, session and HUD. A3 changed "
     "none of it and the Assignment 2 film takes it apart."),
    (lambda p: p.startswith("levels/"),
     "The 2D level data. A3 reads two numbers out of it for asset sizes but "
     "does not modify it; the derivation is in CHANGE-BRIEF 3.0.0."),
    (lambda p: p.startswith("tests/"),
     "Assignment 1 and 2 test and capture drivers. A3 adds its own check, "
     "tests/check_assets_3d.gd, and leaves these untouched."),
]


def reason_for(path):
    for match, reason in EXCLUSION_RULES:
        if match(path):
            return reason
    return None


def main():
    inv = inventory()
    included = set(ROLES)
    missing = included - set(inv)
    assert not missing, "recorded files not on disk: %s" % sorted(missing)

    files = []
    for path in sorted(included):
        cids = [c["id"] for c in COMPONENTS if path in c["files"]]
        assert cids, "unassociated source: " + path
        files.append({"path": path, "sha256": sha(GAME / path),
                      "role": ROLES[path], "component_ids": cids})

    exclusions = []
    for path in inv:
        if path in included:
            continue
        reason = reason_for(path)
        assert reason, "no exclusion reason for: " + path
        exclusions.append({"path": path, "reason": reason})

    assert len(files) + len(exclusions) == len(inv), "inventory coverage mismatch"

    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}

    # The one excerpt: the only displayed code that lives inside the project.
    rel, first, last = "tests/check_assets_3d.gd", 150, 161
    lines = (GAME / rel).read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines[first - 1:last])
    shown = beats["B06"]["shot"]["remotion"]["props"]["code"]
    assert shown == text, "B06's displayed code is not lines %d-%d of %s" % (first, last, rel)

    media_rel = "media/check-output.png"
    ledger = {
        "schema_version": 1,
        "game": "godot",
        "teaching_contract": "code-then-result-v1",
        "files": files,
        "components": COMPONENTS,
        "excerpts": [{"beat_id": "B06", "path": rel,
                      "start_line": first, "end_line": last, "text": text}],
        "code_result_pairs": [{
            "code_beat": "B06", "result_beat": "B07",
            "observation": (
                "Twelve measurements over three assets, printed beside the "
                "numbers CHANGE-BRIEF 3.0.0 predicted: every bounding box "
                "exact, every node scale (1,1,1), every lowest point at "
                "y = +0.0000 m. ALL CHECKS PASSED, exit 0."),
            "media": {"path": media_rel, "sha256": sha(REEL / media_rel)},
        }],
        "exclusions": exclusions,
    }

    out = REEL / "gamedev-evidence.json"
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(ledger, indent=2, ensure_ascii=False))
    print("wrote", out)
    print("  files      %d included + %d excluded = %d inventoried"
          % (len(files), len(exclusions), len(inv)))
    print("  components %d" % len(COMPONENTS))
    print("  excerpts   %d, matching the file and the beat" % len(ledger["excerpts"]))
    print("  pairs      %d, media hashed" % len(ledger["code_result_pairs"]))


if __name__ == "__main__":
    main()
