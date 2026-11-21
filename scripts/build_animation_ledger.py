#!/usr/bin/env python3
"""Write Assignment 7's film ledger, gamedev-evidence.json, from the repository.

    python -X utf8 scripts/build_animation_ledger.py

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

**A file added under `godot/` that is in no component and in no exclusion
stops this script.** It prints `unassociated files:` and writes nothing, which
is the behaviour you want -- the alternative is a checker failure at handoff
with no hint about which file caused it. Assignment 7 added fifteen files
under `godot/`, which is why this list is longer than Assignment 6's.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GAME = ROOT / "godot"
REEL = ROOT / "youtube/claude-liam-walker-the-lost-animation-gamedev"

SKIP_DIRS = {".godot", ".import"}


def role_of(rel: str) -> str:
    """The vocabulary the earlier ledgers established: config, asset,
    resource, level, runtime, test. A .tscn is a level; a shader is runtime,
    because it is program text that executes - on the GPU rather than the CPU.
    For THIS film the `resource` role carries most of the design, because both
    clips are AnimationLibraries in .tres files rather than anything built in
    code."""
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
        "id": "the-sheet",
        "explanation": (
            "What both clips are made of, and the one decision this "
            "assignment turned on. The sheet is CUT from seven pose PNGs "
            "generated with GPT-6 for an earlier project - the generator "
            "recomposites every cut and exits unless it equals the source "
            "pixel for pixel, so 'the cut is lossless' is proved rather than "
            "claimed, and NO POSE FILE IS EVER EDITED. Three cells are cut "
            "legless, because the rig drives the legs under them; the other "
            "five keep their own painted legs and the leg clips switch the "
            "rig's off. The two leg textures and the blade are drawn by the "
            "same generator in the character's own two greys."),
        "beat_ids": ["B02", "B04"],
        "files": pairs(
            "assets/sprites/player_sheet.png",
            "assets/sprites/leg_front.png", "assets/sprites/leg_back.png",
            "assets/sprites/sword.png",
            "assets/poses/p1-idle.png", "assets/poses/p2-run.png",
            "assets/poses/p3-rising.png", "assets/poses/p4-falling.png",
            "assets/poses/p6-windup.png", "assets/poses/p7-live.png",
            "assets/poses/p8-death.png"),
    },
    {
        "id": "clip-run-the-cycle",
        "explanation": (
            "The looping clip, and the arithmetic under it. A 2D cutout rig: "
            "two Node2D legs keyed on rotation_degrees, as resource text, "
            "never built in code at runtime. Its length is DERIVED - two "
            "strides at 24 px against SPEED 96 gives 0.500 s exactly - so "
            "the cycle and the step dust share a clock and the planted foot "
            "and the puff under it are the same event. Front plus back is "
            "constant on every key, which is exact antiphase as arithmetic "
            "rather than as description. The seam rule that applies is the "
            "CONTINUOUS one: every interpolated track ends where it started."),
        "beat_ids": ["B02", "B03"],
        "files": ["animations/legs.tres",
                  "previews/run_preview.tscn", "previews/run_preview.gd",
                  "tests/test_player_clips.gd"],
    },
    {
        "id": "clip-swing-the-committing-action",
        "explanation": (
            "The clip that commits: 18 frames at 30 fps, LOOP_NONE, with the "
            "body on a discrete frame track and the sword arm on a keyed "
            "cutout pivot. Both the arm's rotation AND its position are "
            "keyed, because a blade rotating about a fixed hilt inside the "
            "silhouette is a clock hand whichever way it turns. The hitbox's "
            "`monitoring` is a discrete track on the same timeline, which is "
            "the assignment's point about a gameplay fact not depending on a "
            "tween. Three read-back rules came out of the author playing it: "
            "the arc travels one way while the blade is visible, it finishes "
            "below the hand, and the hilt crosses the torso."),
        "beat_ids": ["B04", "B05", "B12", "B13"],
        "files": ["animations/player.tres",
                  "previews/swing_preview.tscn", "previews/swing_preview.gd",
                  "previews/swing_move_preview.tscn",
                  "previews/swing_move_preview.gd",
                  "tests/test_swing_clip.gd", "tests/test_swing_edges.gd"],
    },
    {
        "id": "one-authority",
        "explanation": (
            "The assignment's hardest rule, and what it actually says. This "
            "project broke it on day one - a pose driver wrote the sprite's "
            "texture every _process and the new clip keyed the same node - "
            "and that driver is deleted. The interesting half came later: the "
            "rule is one authority per NODE, so a SECOND AnimationPlayer over "
            "a disjoint set of nodes breaks nothing, and the legs got their "
            "own. The read-back asserts the partition in both directions, "
            "because a partition checked one way round is only a subset. "
            "player.gd owns the state machine because committing is gameplay; "
            "player_anim.gd reads it, plays both players, and writes no "
            "animated property at all."),
        "beat_ids": ["B06", "B07", "B10", "B11"],
        "files": ["features/player/player.gd", "features/player/player.tscn",
                  "features/player/player_anim.gd",
                  "tests/test_player_states.gd",
                  "tests/pin_player_states.gd"],
    },
    {
        "id": "two-clocks",
        "explanation": (
            "Which tick each clip advances on, which tick gameplay reads the "
            "active window on, and what the disagreement actually is. Both "
            "players are set to the PHYSICS callback mode rather than left at "
            "the engine's idle default, so writer and reader share a tick. "
            "The brief predicted what the default would cost and tagged the "
            "prediction [proposal]; the measurement was built to test it and "
            "found it wrong in sign - idle is one step EARLY, not late, and "
            "the cause is where the mixer's advance falls inside the frame "
            "rather than read latency. The claim underneath survived: the "
            "window opens at playhead 0.2000 in both modes. project.godot is "
            "here because the physics tick is 60 by being UNSET, and a tick "
            "that is the engine default is still the tick every frame count "
            "in this film is stated at."),
        "beat_ids": ["B08", "B09"],
        "files": ["tests/measure_clocks.gd", "project.godot"],
    },
    {
        "id": "the-room-and-the-harness",
        "explanation": (
            "What the clips play in, and what the footage rests on. The "
            "three-trap room, the backdrop and audio the contrast was judged "
            "against, the trap whose own warning window the swing's active "
            "window is sized against, and Assignment 6's step dust - which is "
            "here rather than excluded because the run cycle is timed to it: "
            "one puff per 24 px is the same event as one footfall, and the "
            "dust is how a viewer can see that the cycle and the game agree. "
            "The capture driver records all three takes and asserts its own "
            "outcome before a frame of it counts as evidence; the input-map "
            "check presses the real keys, because an action can exist with "
            "the wrong key on it and a test that only asks whether it exists "
            "stays green."),
        "beat_ids": ["B03", "B05", "B11"],
        "files": ["game/main.tscn", "game/main.gd", "game/room_backdrop.gd",
                  "game/room_audio.gd", "game/debug_keys.gd",
                  "features/traps/spike_trap.gd",
                  "features/traps/spike_trap.tscn",
                  "features/traps/trap_warning_driver.gd",
                  "effects/step_dust.tscn", "effects/step_dust.gd",
                  "effects/step_dust_driver.gd",
                  "tests/test_step_dust_state.gd",
                  "tests/capture_animation.gd", "tests/test_input_map.gd"]
        + pairs("assets/sprites/floor_tile.png", "assets/sprites/player.png",
                "assets/sprites/spike_trap.png",
                "assets/sprites/spike_trap_fired.png",
                "assets/music-loop.ogg", "assets/sfx-death.ogg",
                "assets/sfx-jump.ogg", "assets/sfx-slash.ogg",
                "assets/sfx-trap.ogg"),
    },
]

A6 = ("Assignment 6's particle work, carried forward unchanged. Its suites "
      "still run and still pass - but two of the three effects have nothing "
      "to do with an animation clip, and claiming them as components would "
      "make this ledger say otherwise. The third, step dust, IS claimed, "
      "because the run cycle is timed against it.")
A5 = ("Assignment 5's shader and material work, carried forward unchanged. "
      "`git diff` shows godot/shaders/ untouched by this assignment.")
A3 = ("Assignment 3's 3D asset work, carried across with the showcase scene. "
      "Nothing animated in this assignment touches it - and the glTF probe on "
      "2026-11-15 found skins: 0 and no animations in all three .glb files, "
      "which is why this assignment's rig is cut out of 2D art instead.")

EXCLUSIONS = [
    {"path": "MATERIALS.md", "reason":
     "Assignment 5's material audit. It sits inside the Godot project because "
     "that assignment named the path, but it is a document about the game "
     "rather than a file the game loads."},
    # --- A6 -------------------------------------------------------------
    {"path": "effects/hit_burst.tscn", "reason": A6},
    {"path": "effects/hit_burst.gd", "reason": A6},
    {"path": "effects/hit_burst_spawner.gd", "reason": A6},
    {"path": "effects/dungeon_motes.tscn", "reason": A6},
    {"path": "effects/dungeon_motes.gd", "reason": A6},
    {"path": "previews/hit_burst_preview.tscn", "reason": A6},
    {"path": "previews/hit_burst_preview.gd", "reason": A6},
    {"path": "previews/dungeon_motes_preview.tscn", "reason": A6},
    {"path": "previews/dungeon_motes_preview.gd", "reason": A6},
    {"path": "previews/step_dust_preview.tscn", "reason":
     "Assignment 6's preview fixture for the dust. The dust itself IS a "
     "component here, but this film's fixtures are run_preview, "
     "swing_preview and swing_move_preview; showing a fourth would imply the "
     "dust was re-tuned, and it was not."},
    {"path": "previews/step_dust_preview.gd", "reason":
     "As above - A6's fixture for a component this film uses but did not "
     "change."},
    {"path": "previews/step6_scratch.tscn", "reason": A6},
    {"path": "shaders/particles_generated.gdshader", "reason": A6},
    {"path": "tests/test_hit_burst_config.gd", "reason": A6},
    {"path": "tests/test_hit_burst_state.gd", "reason": A6},
    {"path": "tests/test_dungeon_motes_config.gd", "reason": A6},
    {"path": "tests/test_dungeon_motes_state.gd", "reason": A6},
    {"path": "tests/test_step_dust_config.gd", "reason":
     "A6's 63-check read-back of the dust emitter's settings. The dust's "
     "STATE suite is a component here because this film re-ran it at three "
     "frame rates to show the cycle and the dust still agree; its settings "
     "were not touched and are not explained."},
    {"path": "tests/cost_effects.gd", "reason": A6},
    {"path": "tests/gpu_cost_effects.gd", "reason": A6},
    {"path": "tests/capture_particles.gd", "reason":
     "Assignment 6's capture driver. This film's driver is "
     "tests/capture_animation.gd, which is in the-room-and-the-harness."},
    # --- A5 -------------------------------------------------------------
    {"path": "shaders/dungeon_surface.gdshader", "reason": A5},
    {"path": "shaders/hint_bands.gdshader", "reason": A5},
    {"path": "shaders/standard_generated.gdshader", "reason": A5},
    {"path": "shaders/trap_warning.gdshader", "reason":
     "Assignment 5's warning shader. The trap it draws for IS in a component "
     "here, because the swing's active window is sized against that trap's "
     "lethal window - but the shader is A5's subject and is hand-written by "
     "the author, who does not let an agent edit it."},
    {"path": "scenes/hint_experiment.tscn", "reason": A5},
    {"path": "scenes/asset_showcase.tscn", "reason": A3},
    {"path": "assets/materials/hint_with_source_color.tres", "reason": A5},
    {"path": "assets/materials/hint_without_source_color.tres", "reason": A5},
    {"path": "assets/materials/stone_dry.tres", "reason": A5},
    {"path": "assets/materials/stone_flooded.tres", "reason": A5},
    {"path": "tests/capture_shader.gd", "reason": A5},
    {"path": "tests/test_materials.gd", "reason": A5},
    {"path": "tests/test_trap_shader_driver.gd", "reason": A5},
    {"path": "tests/test_trap_warning.gd", "reason":
     "Assignment 5's warning-window suite. The trap's timings are out of "
     "scope here and CHANGE-BRIEF.md section 11 keeps them there; the suite "
     "runs unchanged and is cited in TEST-REPORT.md rather than explained."},
    {"path": "tests/check_assets_3d.gd", "reason": A3},
    {"path": "tools/capture_hint.gd", "reason": A5},
    {"path": "tools/capture_materials.gd", "reason": A5},
    {"path": "tools/capture_rig.gd", "reason":
     "Assignment 5's capture helper, which freezes a TRAP for a still. It "
     "touches no player node, which was checked rather than assumed when "
     "this assignment went looking for second writers."},
    # --- carried across, and superseded ---------------------------------
    {"path": "tests/route_driver.gd", "reason":
     "walker-ninja's fixed input route, carried across with Assignment 3's "
     "files. Its marks are for that level and nothing here uses it."},
    {"path": "tests/test_keyboard.gd", "reason":
     "walker-ninja's keyboard smoke test. It does not even LOAD here - it "
     "preloads res://game/session.gd, a walker-ninja file that has never "
     "existed in this repository, so it has been broken since 2026-10-17. "
     "TEST-REPORT.md records that rather than quietly deleting it; "
     "tests/test_input_map.gd is what replaced it and that one is in a "
     "component."},
    {"path": "tools/setup_input_map.gd", "reason":
     "One-off that wrote the input map through the engine on 2026-10-23. Not "
     "runtime code, and nothing in the film depends on re-running it."},
    {"path": "tools/write_textures.gd", "reason":
     "The code-written texture generator for the room's tiles. It is why this "
     "project has no downloaded art to license for the LEVEL - but this "
     "film's sheet is cut by tools/make_sprites.py, outside the Godot "
     "project, and this file draws none of it."},
    # --- carried art that nothing loads ---------------------------------
    {"path": "assets/poses/p5-dash.png", "reason":
     "Copied across in revision 7.0.1 together with p6-windup and p7-live, "
     "because all three were missing from this repository. Only p6 and p7 are "
     "cut into the sheet. It stays committed and credited in ATTRIBUTION.md, "
     "and NOTHING LOADS IT - which is said here rather than left for a "
     "reviewer to discover by grepping."},
    {"path": "assets/poses/p5-dash.png.import", "reason":
     "The sidecar of a pose nothing loads. See assets/poses/p5-dash.png."},
    {"path": "assets/textures/hint_bands.png", "reason": A5},
    {"path": "assets/textures/hint_bands.png.import", "reason": A5},
    {"path": "assets/textures/stone_albedo.png", "reason": A5},
    {"path": "assets/textures/stone_albedo.png.import", "reason": A5},
    {"path": "assets/textures/wetness_mask.png", "reason": A5},
    {"path": "assets/textures/wetness_mask.png.import", "reason": A5},
]
EXCLUSIONS += [
    {"path": p, "reason": A3}
    for p in pairs("assets/models/slime.glb", "assets/models/spike_trap.glb",
                   "assets/models/torch.glb")
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
