#!/usr/bin/env python3
"""Write the film's gamedev-evidence.json from the repository as it stands.

Per skills/make/godot-gamedev/references/evidence.md: every authored file
under the Godot project is inventoried with its hash, except `.godot/` and the
generated `.uid` identifiers; `.import` sidecars are included because they
carry authored import settings. Every file is either associated with a
component or listed as an explicit exclusion with a reason. Excerpts are read
from the beat sheet and re-read from disk, and the two must agree.

    python -I scripts/build_lost_ledger.py

The checker fails on stale hashes, drifted source lines, missing components,
unassociated files, extra unlisted files or invented excerpts. It cannot
decide whether a mechanism was explained clearly or whether an exclusion is
honest - those are in FACTCHECK.md and are mine to defend.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GAME = ROOT / "godot"
REEL = ROOT / "youtube/claude-liam-walker-the-lost-gamedev"

SKIP_DIRS = {".godot", ".import"}


def role_of(rel: str) -> str:
    """The vocabulary walker-ninja's ledger established: config, asset,
    resource, level, runtime, test. Shaders are runtime - they are program
    text that executes, on the GPU rather than the CPU. The three texture
    .import sidecars are config, and unlike the previous film they are
    component files here, because their settings are part of what this one
    explains."""
    if rel == "project.godot" or rel.endswith(".import"):
        return "config"
    if rel.endswith((".png", ".glb", ".ogg", ".wav")):
        return "asset"
    if rel.endswith(".tres"):
        return "resource"
    if rel.endswith(".tscn"):
        return "level"
    if rel.startswith("tests/") or rel.startswith("tools/"):
        return "test"
    return "runtime"


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory() -> list[str]:
    out = []
    for p in sorted(GAME.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(GAME).as_posix()
        if any(part in SKIP_DIRS for part in p.relative_to(GAME).parts):
            continue
        if rel.endswith(".uid"):
            continue
        out.append(rel)
    return out


# Each component: what it is, which beats narrate it, which files it owns.
# A file may appear in exactly one component; anything left over must be an
# exclusion with a reason a reviewer can argue with.
COMPONENTS = [
    {
        "id": "warning-shader",
        "explanation": (
            "The hand-written canvas_item shader that turns a spike trap red, "
            "and the trap whose state drives it. One Sprite2D, one material, "
            "one line inside fragment(). The state machine owns warn_amount "
            "and the shader only reads it."),
        "beat_ids": ["B02", "B03"],
        "files": ["shaders/trap_warning.gdshader",
                  "features/traps/spike_trap.gd",
                  "features/traps/spike_trap.tscn"],
    },
    {
        "id": "material-driver",
        "explanation": (
            "Agent-written presentation. Duplicates the ShaderMaterial per "
            "trap instance so three traps do not share one warn_amount, asks "
            "the shader at startup whether the uniform it is about to write "
            "exists, and copies state into that uniform once a frame after "
            "the state machine has run."),
        "beat_ids": ["B04", "B05"],
        "files": ["features/traps/trap_warning_driver.gd",
                  "tests/test_trap_shader_driver.gd"],
    },
    {
        "id": "hint-experiment",
        "explanation": (
            "One unshaded spatial shader with two samplers bound to the same "
            "three-pixel file, differing only by source_color, and a bool "
            "that picks which reaches ALBEDO. The scene fixes the pipeline "
            "the measurement depends on: Linear tonemap at exposure 1.0, no "
            "light, every post effect off."),
        "beat_ids": ["B06", "B07", "B10", "B11"],
        "files": ["shaders/hint_bands.gdshader",
                  "scenes/hint_experiment.tscn",
                  "assets/materials/hint_with_source_color.tres",
                  "assets/materials/hint_without_source_color.tres",
                  "assets/textures/hint_bands.png",
                  "assets/textures/hint_bands.png.import",
                  "tools/write_textures.gd",
                  "tools/capture_hint.gd"],
    },
    {
        "id": "textured-surface",
        "explanation": (
            "The hand-written spatial shader, its colour and data samplers "
            "and four grouped parameters, with two materials that differ in "
            "three values. One slime takes its material from the importer so "
            "a reimport keeps it; the other overrides at the node, so the "
            "pair is identical geometry under identical light."),
        "beat_ids": ["B08", "B09"],
        "files": ["shaders/dungeon_surface.gdshader",
                  "assets/materials/stone_dry.tres",
                  "assets/materials/stone_flooded.tres",
                  "assets/textures/stone_albedo.png",
                  "assets/textures/stone_albedo.png.import",
                  "assets/textures/wetness_mask.png",
                  "assets/textures/wetness_mask.png.import",
                  "scenes/asset_showcase.tscn",
                  "assets/models/slime.glb", "assets/models/slime.glb.import",
                  "tools/capture_materials.gd",
                  "tests/test_materials.gd"],
    },
    {
        "id": "the-room",
        "explanation": (
            "What the shader is attached to and what drives it in play: the "
            "three-trap room, the player who can only walk and jump, the "
            "code-drawn sprites the pixel predictions were written against, "
            "and the project settings that fix the renderer and resolution."),
        "beat_ids": ["B03", "B05"],
        "files": ["game/main.tscn", "game/main.gd",
                  "features/player/player.gd", "features/player/player.tscn",
                  "assets/sprites/spike_trap.png", "assets/sprites/spike_trap.png.import",
                  "assets/sprites/spike_trap_fired.png", "assets/sprites/spike_trap_fired.png.import",
                  "assets/sprites/player.png", "assets/sprites/player.png.import",
                  "assets/sprites/floor_tile.png", "assets/sprites/floor_tile.png.import",
                  "project.godot",
                  "tools/capture_rig.gd"],
    },
    {
        "id": "evidence-harness",
        "explanation": (
            "What the claims rest on. The state suite at three pinned frame "
            "rates, the input-map check, Assignment 3's geometry check "
            "carried across, and the capture driver that records the warning "
            "as real motion and asserts its own outcome before a frame counts "
            "as evidence."),
        "beat_ids": ["B03", "B05", "B12"],
        "files": ["tests/test_trap_warning.gd", "tests/test_input_map.gd",
                  "tests/check_assets_3d.gd", "tests/capture_shader.gd"],
    },
    {
        "id": "generated-reference",
        "explanation": (
            "Godot's own output, produced by converting a StandardMaterial3D "
            "with albedo, normal-map and roughness textures enabled. Nothing "
            "loads it. It is in the project to be read: its line 7 marks the "
            "albedo sampler as colour and its line 19 leaves the normal map "
            "as data, which is the distinction the hand-written shader makes "
            "on its own lines 3 and 4."),
        "beat_ids": ["B10"],
        "files": ["shaders/standard_generated.gdshader"],
    },
]

EXCLUSIONS = [
    {"path": "MATERIALS.md", "reason":
     "The part 3 material audit. Assignment 5 names this path, so it sits inside the Godot project, but it is a document about the game rather than a file the game loads."},
    {"path": "assets/models/torch.glb", "reason":
     "Assignment 3's torch, carried across with the showcase scene. No shader "
     "or material in this assignment touches it."},
    {"path": "assets/models/torch.glb.import", "reason": "sidecar of the above"},
    {"path": "assets/models/spike_trap.glb", "reason":
     "Assignment 3's 3D spike trap. The trap this film explains is the 2D one; "
     "the model appears only as scenery in the showcase scene."},
    {"path": "assets/models/spike_trap.glb.import", "reason": "sidecar of the above"},
    {"path": "tests/route_driver.gd", "reason":
     "Walker-ninja's fixed input route, carried across with Assignment 3's "
     "files. Its marks are for that level and it is not used here; "
     "tests/capture_shader.gd is this film's driver."},
    {"path": "tests/test_keyboard.gd", "reason":
     "Walker-ninja's keyboard smoke test, carried across. Superseded here by "
     "tests/test_input_map.gd, which is in evidence-harness."},
    {"path": "tools/setup_input_map.gd", "reason":
     "One-off that wrote the input map through the engine on 2026-10-23. Not "
     "runtime code and nothing in the film depends on re-running it."},
]


# Empty directory markers. Listed rather than silently skipped, because the
# reference asks for omissions to be explicit and arguable.
EXCLUSIONS += [
    {"path": rel, "reason":
     "Empty .gitkeep placeholder. It holds a directory in git and contains "
     "nothing authored."}
    for rel in sorted(
        p.relative_to(GAME).as_posix() for p in GAME.rglob(".gitkeep"))
]


def main() -> int:
    beats = json.load(io.open(REEL / "beat_sheet.json", encoding="utf-8"))["beats"]
    by_id = {b["beat_id"]: b for b in beats}

    owner: dict[str, str] = {}
    for c in COMPONENTS:
        for f in c["files"]:
            if f in owner:
                raise SystemExit("%s is claimed by %s and %s" % (f, owner[f], c["id"]))
            owner[f] = c["id"]
    excluded = {e["path"] for e in EXCLUSIONS}

    files = []
    missing = []
    for rel in inventory():
        p = GAME / rel
        if rel in owner:
            files.append({"path": rel, "sha256": sha(p), "role": role_of(rel),
                          "component_ids": [owner[rel]]})
        elif rel in excluded:
            # Counted and visible through `exclusions`; listing it in `files`
            # as well is what "File both included and excluded" rejects.
            continue
        else:
            missing.append(rel)
    if missing:
        raise SystemExit("unassociated files:\n  " + "\n  ".join(missing))

    for c in COMPONENTS:
        for f in c["files"]:
            if not (GAME / f).is_file():
                raise SystemExit("%s lists %s, which does not exist" % (c["id"], f))

    # Excerpts, read back from disk and checked against what the beat displays.
    excerpts = []
    pairs = []
    for i, b in enumerate(beats):
        props = b["shot"].get("remotion", {}).get("props", {})
        if props.get("mode") != "code":
            continue
        rel = props["source"]
        start = props["startLine"]
        shown = props["code"]
        rows = (ROOT / rel).read_text(encoding="utf-8").split("\n")
        end = start + len(shown.split("\n")) - 1
        on_disk = "\n".join(rows[start - 1:end])
        if on_disk != shown:
            raise SystemExit("%s: panel text does not match %s:%d-%d"
                             % (b["beat_id"], rel, start, end))
        excerpts.append({"beat_id": b["beat_id"],
                         "path": rel[len("godot/"):] if rel.startswith("godot/") else rel,
                         "start_line": start, "end_line": end, "text": shown})
        nxt = beats[i + 1]
        nprops = nxt["shot"].get("remotion", {}).get("props", {})
        if nprops.get("mode") == "code":
            raise SystemExit("%s's result beat %s is another code excerpt"
                             % (b["beat_id"], nxt["beat_id"]))
        if not nxt["narration_text"].strip():
            raise SystemExit("%s's result beat %s has no narration"
                             % (b["beat_id"], nxt["beat_id"]))
        media = nxt["shot"].get("evidence_media")
        if not media:
            raise SystemExit("%s has no evidence_media" % nxt["beat_id"])
        mpath = REEL / media
        if not mpath.is_file():
            raise SystemExit("%s names %s, which does not exist" % (nxt["beat_id"], media))
        pairs.append({"code_beat": b["beat_id"], "result_beat": nxt["beat_id"],
                      "observation": nxt["role_note"],
                      "media": {"path": media, "sha256": sha(mpath)}})

    ledger = {
        "schema_version": 1,
        "game": "godot",
        "teaching_contract": "code-then-result-v1",
        "files": files,
        "components": [{"id": c["id"], "explanation": c["explanation"],
                        "beat_ids": c["beat_ids"], "files": c["files"]}
                       for c in COMPONENTS],
        "excerpts": excerpts,
        "exclusions": EXCLUSIONS,
        "code_result_pairs": pairs,
    }
    out = REEL / "gamedev-evidence.json"
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    print("wrote %s" % out)
    tally = {}
    for f in files:
        tally[f["role"]] = tally.get(f["role"], 0) + 1
    print("  %d component files (%s), %d exclusions"
          % (len(files), ", ".join("%s %d" % kv for kv in sorted(tally.items())),
             len(EXCLUSIONS)))
    print("  %d components, %d excerpts, %d code->result pairs"
          % (len(COMPONENTS), len(excerpts), len(pairs)))
    for p in pairs:
        print("    %s -> %s  %s" % (p["code_beat"], p["result_beat"], p["media"]["path"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
