#!/usr/bin/env python3
"""Write Assignment 6's film ledger, gamedev-evidence.json, from the repository.

    python -X utf8 scripts/build_particles_ledger.py

Per skills/make/godot-gamedev/references/evidence.md: every authored file under
the Godot project is inventoried with its hash, except `.godot/` and the
generated `.uid` identifiers; `.import` sidecars are included because they
carry authored import settings. Every file is either associated with a
component or listed as an explicit exclusion with a reason a reviewer can
argue with. Excerpts are read from the beat sheet and re-read from disk, and
the two must agree or this refuses to write.

The course checker fails on stale hashes, drifted source lines, missing
components, unassociated files, extra unlisted files or invented excerpts. It
cannot decide whether a mechanism was explained clearly or whether an
exclusion is honest. Those are FACTCHECK.md's and COMPONENTS.md's job.

**`godot/override.cfg` must not exist when this runs.** It is the temporary 4K
window override `scripts/render_takes.py` writes and removes; if a render is
still going, its presence would be inventoried into the ledger and the next
reviewer's clone would fail the hash check on a file that was never committed.
This stops rather than writing one.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GAME = ROOT / "godot"
REEL = ROOT / "youtube/claude-liam-walker-the-lost-particles-gamedev"

SKIP_DIRS = {".godot", ".import"}


def role_of(rel: str) -> str:
    """The vocabulary the two earlier ledgers established: config, asset,
    resource, level, runtime, test. A .tscn is a level; a shader is runtime,
    because it is program text that executes - on the GPU rather than the CPU.
    An effect's settings live in its .tscn, so for this film the `level` role
    carries most of the design."""
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
        parts = p.relative_to(GAME).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        rel = p.relative_to(GAME).as_posix()
        if rel.endswith(".uid"):
            continue
        out.append(rel)
    return out


def pairs(*stems: str) -> list[str]:
    """An asset and its .import sidecar, which carries authored settings."""
    out = []
    for s in stems:
        out += [s, s + ".import"]
    return out


COMPONENTS = [
    {
        "id": "effect-a-grit-burst",
        "explanation": (
            "Effect A and the event it rides on. Three GPUParticles2D under "
            "one Node2D - Flash owns frame one, Grit owns the shape, Dust "
            "owns the tail - plus the spike trap whose `fired` signal already "
            "existed and was not changed, and the spawner that instances one "
            "burst per event rather than reusing a node. The retrigger rule "
            "is overlap, which is what stops the second of two close events "
            "being silently dropped on a one_shot emitter."),
        "beat_ids": ["B02", "B03", "B03A", "B04", "B05"],
        "files": ["effects/hit_burst.tscn", "effects/hit_burst.gd",
                  "effects/hit_burst_spawner.gd",
                  "features/traps/spike_trap.gd",
                  "features/traps/spike_trap.tscn",
                  "previews/hit_burst_preview.tscn",
                  "previews/hit_burst_preview.gd",
                  "tests/test_hit_burst_config.gd",
                  "tests/test_hit_burst_state.gd"],
    },
    {
        "id": "effect-b-dungeon-motes",
        "explanation": (
            "Effect B: ambience, one emitter, sixty motes, no event. Its "
            "condition is the scene being loaded with the player alive and it "
            "stops on `died`. The feature Effect A does not use is "
            "`preprocess = 8.0`, one full lifetime simulated before the first "
            "frame is drawn - the one rule in this assignment that no "
            "headless run in this repository can see."),
        "beat_ids": ["B06", "B07", "B07A", "B07B"],
        "files": ["effects/dungeon_motes.tscn", "effects/dungeon_motes.gd",
                  "previews/dungeon_motes_preview.tscn",
                  "previews/dungeon_motes_preview.gd",
                  "tests/test_dungeon_motes_config.gd",
                  "tests/test_dungeon_motes_state.gd"],
    },
    {
        "id": "effect-c-step-dust",
        "explanation": (
            "Effect C: dust under the feet, on an event this game does not "
            "have. `player.gd` has a position, a velocity and a floor check "
            "and no footstep signal, so the driver derives the event from "
            "distance travelled on the ground - one puff per 24 px, "
            "back-dated by the overshoot so the spacing is the same at any "
            "frame rate. It is also the only effect that uses `amount_ratio`, "
            "0.6 for a stride against 1.0 for a landing."),
        "beat_ids": ["B10", "B11"],
        "files": ["effects/step_dust.tscn", "effects/step_dust.gd",
                  "effects/step_dust_driver.gd",
                  "previews/step_dust_preview.tscn",
                  "previews/step_dust_preview.gd",
                  "tests/test_step_dust_config.gd",
                  "tests/test_step_dust_state.gd"],
    },
    {
        "id": "process-shader",
        "explanation": (
            "Godot's own particle process shader, produced by converting "
            "Effect A's Dust material in the editor. Nothing in the game "
            "loads it; it is in the project to be read. Dust is the emitter "
            "that was converted because it is the only one carrying both a "
            "colour ramp and a scale curve, and the two lines that sample "
            "them only exist in a generated shader when the material "
            "actually has them. The scratch scene holds the verbatim copy of "
            "the material that was converted."),
        "beat_ids": ["B08", "B09"],
        "files": ["shaders/particles_generated.gdshader",
                  "previews/step6_scratch.tscn"],
    },
    {
        "id": "the-room",
        "explanation": (
            "What the effects are attached to and what drives them in play: "
            "the three-trap room, the player who can only walk and jump, the "
            "backdrop and audio the contrast decisions were judged against, "
            "the pose driver and warning driver that already kept the "
            "read-never-write boundary, the F9 vsync key this assignment "
            "added, and the project settings that pin the renderer and the "
            "logical resolution."),
        "beat_ids": ["B03", "B07A", "B07B", "B11"],
        "files": ["game/main.tscn", "game/main.gd", "game/room_backdrop.gd",
                  "game/room_audio.gd", "game/debug_keys.gd",
                  "features/player/player.gd", "features/player/player.tscn",
                  "features/player/pose_driver.gd",
                  "features/traps/trap_warning_driver.gd",
                  "shaders/trap_warning.gdshader",
                  "project.godot"]
        + pairs("assets/sprites/floor_tile.png", "assets/sprites/player.png",
                "assets/sprites/spike_trap.png",
                "assets/sprites/spike_trap_fired.png",
                "assets/poses/p1-idle.png", "assets/poses/p2-run.png",
                "assets/poses/p3-rising.png", "assets/poses/p4-falling.png",
                "assets/poses/p8-death.png",
                "assets/music-loop.ogg", "assets/sfx-death.ogg",
                "assets/sfx-jump.ogg", "assets/sfx-slash.ogg",
                "assets/sfx-trap.ogg"),
    },
    {
        "id": "evidence-harness",
        "explanation": (
            "What the price claims and the footage rest on. The cost script "
            "that runs the assignment's four named conditions with an "
            "empty-scene control and a twice-run baseline, so it states its "
            "own noise floor before reporting any difference; its windowed "
            "sibling, which reads GPU time off the same timestamp query the "
            "editor's Visual Profiler displays and refuses to run headless, "
            "because a dummy renderer would report 0.000 ms for every "
            "condition and look like three effects that cost nothing; the "
            "capture driver that records all three takes and asserts its own "
            "outcome before a frame of it counts as evidence; and the "
            "input-map check, which is how the F9 key is shown to have added "
            "no action."),
        "beat_ids": ["B11A", "B11B"],
        "files": ["tests/cost_effects.gd", "tests/gpu_cost_effects.gd",
                  "tests/capture_particles.gd", "tests/test_input_map.gd"],
    },
]

A5 = ("Assignment 5's subject, carried forward unchanged. Its suites still "
      "run and still pass, and `git diff` shows godot/shaders/ untouched by "
      "this assignment - but shaders and materials are not what this film "
      "explains, and claiming them as components would make the ledger say "
      "otherwise.")
A3 = ("Assignment 3's 3D asset work, carried across with the showcase scene. "
      "No particle effect in this assignment touches it.")

EXCLUSIONS = [
    {"path": "MATERIALS.md", "reason":
     "Assignment 5's material audit. It sits inside the Godot project because "
     "that assignment named the path, but it is a document about the game "
     "rather than a file the game loads."},
    {"path": "shaders/dungeon_surface.gdshader", "reason": A5},
    {"path": "shaders/hint_bands.gdshader", "reason": A5},
    {"path": "shaders/standard_generated.gdshader", "reason":
     "Assignment 5's generated reference shader, from a StandardMaterial3D. "
     "This film reads the PARTICLE process shader instead; keeping both in "
     "scope would invite a reviewer to think the wrong one was converted."},
    {"path": "scenes/hint_experiment.tscn", "reason": A5},
    {"path": "scenes/asset_showcase.tscn", "reason": A5},
    {"path": "assets/materials/hint_with_source_color.tres", "reason": A5},
    {"path": "assets/materials/hint_without_source_color.tres", "reason": A5},
    {"path": "assets/materials/stone_dry.tres", "reason": A5},
    {"path": "assets/materials/stone_flooded.tres", "reason": A5},
    {"path": "tests/capture_shader.gd", "reason":
     "Assignment 5's capture driver. This film's driver is "
     "tests/capture_particles.gd, which is in evidence-harness."},
    {"path": "tests/test_materials.gd", "reason": A5},
    {"path": "tests/test_trap_shader_driver.gd", "reason": A5},
    {"path": "tests/test_trap_warning.gd", "reason":
     "Assignment 5's warning-window suite. The trap's timings are out of "
     "scope here and CHANGE-BRIEF.md section 3 keeps them there; the suite "
     "runs unchanged and is cited in TEST-REPORT.md rather than explained."},
    {"path": "tests/check_assets_3d.gd", "reason": A3},
    {"path": "tests/route_driver.gd", "reason":
     "walker-ninja's fixed input route, carried across with Assignment 3's "
     "files. Its marks are for that level and nothing here uses it."},
    {"path": "tests/test_keyboard.gd", "reason":
     "walker-ninja's keyboard smoke test, carried across and superseded by "
     "tests/test_input_map.gd, which is in evidence-harness."},
    {"path": "tools/capture_hint.gd", "reason": A5},
    {"path": "tools/capture_materials.gd", "reason": A5},
    {"path": "tools/capture_rig.gd", "reason": A5},
    {"path": "tools/write_textures.gd", "reason":
     "The code-written texture generator. It is why this project has no "
     "downloaded or generated art to license, and ATTRIBUTION.md says so - "
     "but none of the six emitters in this film has a texture at all, so it "
     "is not a component of the particle work."},
    {"path": "tools/setup_input_map.gd", "reason":
     "One-off that wrote the input map through the engine on 2026-10-23. Not "
     "runtime code, and nothing in the film depends on re-running it."},
]
EXCLUSIONS += [
    {"path": p, "reason": A3}
    for p in pairs("assets/models/slime.glb", "assets/models/spike_trap.glb",
                   "assets/models/torch.glb")
]
EXCLUSIONS += [
    {"path": p, "reason": A5}
    for p in pairs("assets/textures/hint_bands.png",
                   "assets/textures/stone_albedo.png",
                   "assets/textures/wetness_mask.png")
]
EXCLUSIONS += [
    {"path": rel, "reason":
     "Empty .gitkeep placeholder. It holds a directory in git and contains "
     "nothing authored."}
    for rel in sorted(p.relative_to(GAME).as_posix()
                      for p in GAME.rglob(".gitkeep"))
]


def main() -> int:
    stray = GAME / "override.cfg"
    if stray.is_file():
        raise SystemExit(
            "godot/override.cfg exists. That is scripts/render_takes.py's "
            "temporary 4K window override - wait for the render to finish, or "
            "delete it. Inventorying it would put a file in the ledger that "
            "is never committed, and every reviewer's clone would fail on it.")

    beats = json.load(io.open(REEL / "beat_sheet.json", encoding="utf-8"))["beats"]
    by_id = {b["beat_id"]: b for b in beats}

    owner: dict[str, str] = {}
    for c in COMPONENTS:
        for f in c["files"]:
            if f in owner:
                raise SystemExit("%s is claimed by %s and %s"
                                 % (f, owner[f], c["id"]))
            owner[f] = c["id"]
        for b in c["beat_ids"]:
            if b not in by_id:
                raise SystemExit("%s names beat %s, which does not exist"
                                 % (c["id"], b))
            if not by_id[b]["narration_text"].strip():
                raise SystemExit("%s names beat %s, which has no narration"
                                 % (c["id"], b))
    excluded = {e["path"] for e in EXCLUSIONS}

    files, missing = [], []
    for rel in inventory():
        p = GAME / rel
        if rel in owner:
            files.append({"path": rel, "sha256": sha(p), "role": role_of(rel),
                          "component_ids": [owner[rel]]})
        elif rel in excluded:
            continue
        else:
            missing.append(rel)
    if missing:
        raise SystemExit("unassociated files:\n  " + "\n  ".join(missing))
    for e in EXCLUSIONS:
        if not (GAME / e["path"]).is_file():
            raise SystemExit("exclusion %s does not exist" % e["path"])
    for c in COMPONENTS:
        for f in c["files"]:
            if not (GAME / f).is_file():
                raise SystemExit("%s lists %s, which does not exist"
                                 % (c["id"], f))

    # Excerpts, re-read from disk and checked against what the beat displays.
    excerpts, code_pairs = [], []
    for i, b in enumerate(beats):
        props = b["shot"].get("remotion", {}).get("props", {})
        if props.get("mode") != "code":
            continue
        rel, start, shown = props["source"], props["startLine"], props["code"]
        rows = (ROOT / rel).read_text(encoding="utf-8").split("\n")
        end = start + len(shown.split("\n")) - 1
        if "\n".join(rows[start - 1:end]) != shown:
            raise SystemExit("%s: the panel text is not %s:%d-%d"
                             % (b["beat_id"], rel, start, end))
        excerpts.append({
            "beat_id": b["beat_id"],
            "path": rel[len("godot/"):] if rel.startswith("godot/") else rel,
            "start_line": start, "end_line": end, "text": shown})
        nxt = beats[i + 1]
        if nxt["shot"].get("remotion", {}).get("props", {}).get("mode") == "code":
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
            raise SystemExit("%s names %s, which does not exist"
                             % (nxt["beat_id"], media))
        code_pairs.append({
            "code_beat": b["beat_id"], "result_beat": nxt["beat_id"],
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
        "code_result_pairs": code_pairs,
    }
    out = REEL / "gamedev-evidence.json"
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")

    tally: dict[str, int] = {}
    for f in files:
        tally[f["role"]] = tally.get(f["role"], 0) + 1
    print("wrote %s" % out)
    print("  %d component files (%s), %d exclusions"
          % (len(files), ", ".join("%s %d" % kv for kv in sorted(tally.items())),
             len(EXCLUSIONS)))
    print("  %d components, %d excerpts, %d code->result pairs"
          % (len(COMPONENTS), len(excerpts), len(code_pairs)))
    for p in code_pairs:
        print("    %s -> %s  %s" % (p["code_beat"], p["result_beat"],
                                    p["media"]["path"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
