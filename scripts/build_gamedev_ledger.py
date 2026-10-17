#!/usr/bin/env python3
"""Fix B09 from the recorded file, then write gamedev-evidence.json.

B09 had numbers I typed from memory of an earlier run. The playback positions
move slightly run to run, so the film would have shown figures that disagreed
with its own hashed evidence file. It now quotes media/B09-suite-output.txt
verbatim.
"""
import base64, hashlib, io, json, os

ROOT = r"D:\Graduate\2026Fall\7270\walker-ninja-TiantongZhang"
os.chdir(ROOT)
GAME, REEL = "godot", "youtube/claude-liam-walker-ninja-gamedev"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ------------------------------------------------------------------ B09 fix
recorded = io.open(os.path.join(REEL, "media/B09-suite-output.txt"),
                   encoding="utf-8", newline="").read().rstrip("\n")
doc = json.load(io.open(os.path.join(REEL, "beat_sheet.json"), encoding="utf-8"))
by = {b["beat_id"]: b for b in doc["beats"]}

b09 = by["B09"]
# `tree` mode, not `code` mode. This beat shows RECORDED TOOL OUTPUT, not a
# source excerpt, and the checker rightly rejects displayed code that has no
# excerpt record ("Displayed code lacks an excerpt record"). `tree` is a
# labelled panel of lines, which is what recorded output is.
b09_img = base64.b64encode(
    open(os.path.join(REEL, "media/B09-suite-output.png"), "rb").read()).decode()
b09["shot"]["remotion"]["props"].update({
    # `asset` mode, because the contract requires the result evidence to be
    # VISIBLE media and a .txt is not ("Result evidence must be visible media").
    # The image is a faithful monospace render of the recorded file - same bytes
    # of text, no reflow and no editing - so what is shown and what is hashed
    # are the same artefact.
    "mode": "asset",
    "code": "",
    "image": "data:image/png;base64," + b09_img,
    "imageLabel": "recorded output, rendered verbatim",
    "treeLabel": "Recorded output - godot --headless --script res://tests/test_game.gd",
    "notes": [{
        "label": "What this is",
        "value": "Quoted from a headless run and hashed into the evidence ledger. "
                 "Not a live terminal, and not re-run inside the film."},
        {"label": "Why the positions are not round",
         "value": "They are audio-clock readings and move slightly run to run. An "
                  "earlier draft of this card carried numbers typed from memory of a "
                  "different run; they disagreed with this file."}],
    "output": ["99 checks", "0 failures", "recorded, not re-run"],
})
b09["shot"]["evidence_media"] = "media/B09-suite-output.png"
b09["narration_text"] = (
    "Both of those are checks now, and this is the recorded output, not a terminal I "
    "am driving for the camera. An ordinary retry moves the playhead forward. Pause, "
    "then retry, and it resumes at exactly the position it was paused at - the same "
    "reading to the millisecond. That second check exists because once, it did not.")
# duration comes from the measured narration, set by the timing pass
b09.setdefault("estimated_duration_s", 17)

doc["beats"] = [by[b["beat_id"]] for b in doc["beats"]]
io.open(os.path.join(REEL, "beat_sheet.json"), "w", encoding="utf-8",
        newline="\n").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------ ledger
ROLES = {
    "project.godot": "config", ".gitignore": "config",
    "game/main.tscn": "scene", "game/session.gd": "runtime",
    "features/player/player.gd": "runtime", "features/player/tuning.gd": "resource",
    "ui/hud.gd": "runtime", "levels/first_steps.json": "level",
}

COMPONENTS = [
    {"id": "C1-pose-mapping",
     "explanation":
        "Eight generated sprites, one per state the engine can already distinguish. "
        "pose_key() returns a STRING and _draw() looks the texture up from it, so the "
        "state-to-pose mapping can be asserted without a renderer. death is tested "
        "first because a disabled body keeps whatever is_on_floor() last returned, so "
        "a pose derived from movement would differ by cause of death. The cost is one "
        "dictionary lookup per frame and the pose names living in two places, where a "
        "mismatch is a missing texture rather than a wrong one.",
     "beat_ids": ["B02", "B03"],
     "files": ["features/player/player.gd",
               "assets/poses/p1-idle.png", "assets/poses/p2-run.png",
               "assets/poses/p3-rising.png", "assets/poses/p4-falling.png",
               "assets/poses/p5-dash.png", "assets/poses/p6-windup.png",
               "assets/poses/p7-live.png", "assets/poses/p8-death.png",
               "tests/capture_gamedev.gd", "tests/test_game.gd"]},
    {"id": "C2-directional-rim",
     "explanation":
        "The character is navy armour on a dungeon wall at 1.60:1, so something has to "
        "break the silhouette. A rim grown on four sides costs a part 2 px of width, "
        "which left a 3 px arm with 1 px of armour and rendered the limbs as grey "
        "pipes. The rim is directional instead: 1 px toward the back and 1 px up, "
        "which costs no width, and because x is measured forward it mirrors with the "
        "body the way a light source does and an outline does not. player.gd applies "
        "it to the code-drawn fallback; scripts/import_pose.py applies the same rule "
        "to every generated pose, which is an edit to a generated asset and is "
        "declared as one in ASSET-LOG.md.",
     "beat_ids": ["B04", "B05"],
     "files": ["features/player/player.gd",
               "assets/poses/p1-idle.png", "assets/poses/p8-death.png",
               "project.godot"]},
    {"id": "C3-trap-warning-timing",
     "explanation":
        "A trap arms when the player crosses trigger_x and the spike rises over "
        "TRAP_RISE_TICKS = 15. The warning sound fires on the tick trap_risen leaves "
        "0 - the arming, not the contact - because a sound hung off the damage is a "
        "death sound arriving after the information is useless, and it would still "
        "pass a check that only asked whether something played when the trap killed "
        "you. session.sfx_log records {id, tick} per attempt, which is what makes the "
        "lead assertable: 35 ticks in both the suite and the capture driver.",
     "beat_ids": ["B06", "B07"],
     "files": ["game/session.gd", "levels/first_steps.json",
               "assets/sfx-trap.ogg", "assets/sfx-death.ogg",
               "tests/capture_gamedev.gd", "tests/test_game.gd"]},
    {"id": "C4-music-retry-guard",
     "explanation":
        "restart_attempt() runs on every death, so an unconditional play() would "
        "restart a 16-bar loop at bar 1 every 0.55 s. The guard resumes instead. The "
        "first version tested `playing` alone, which reports FALSE while "
        "stream_paused is true - correct for an ordinary death and wrong for "
        "pause-then-retry, where the track jumped to bar 1. Found by printing what "
        "the engine reports in each state before writing the assertion, because the "
        "code reads correctly.",
     "beat_ids": ["B08", "B09"],
     "files": ["game/session.gd", "assets/music-loop.ogg", "tests/test_game.gd"]},
    {"id": "C5-blade-stays-in-code",
     "explanation":
        "The sprites carry the body, the scarf, the rim and the visor; they do not "
        "carry the blade. _draw_swing() draws it from ATTACK_PIVOT, attack_angle() and "
        "tuning.attack_reach - the same three numbers the kill hitbox is built from - "
        "and the arc wedge appears only while attack_phase() >= 2, so the bright "
        "sweep marks exactly the ticks that can kill. The poses were prompted 'empty "
        "hand, NO weapon' to keep this true, because a baked-in blade would stop "
        "tracking the hitbox silently: both attack-hitbox-on-the-blade checks measure "
        "the hitbox against the numbers, not against the picture. The honest cost is "
        "that the character's most characteristic object is not generated art.",
     "beat_ids": ["B10", "B11"],
     "files": ["features/player/player.gd", "features/player/tuning.gd",
               "tests/test_game.gd"]},
]

EXCLUSIONS = [
    {"path": "tests/capture_walkthrough.gd",
     "reason": "Assignment 1's film capture driver. Carried forward so that film stays "
               "reproducible, and unused by this one, which has its own driver in "
               "tests/capture_gamedev.gd."},
    {"path": "game/main.tscn",
     "reason": "168 bytes. It instantiates session.gd and nothing else, so there is no "
               "mechanism in it to teach."},
    {"path": ".gitignore",
     "reason": "8 bytes - it ignores .godot/. Not a runtime component."},
    {"path": "assets/README.md",
     "reason": "Documentation, not runtime. It is the one-table answer to which assets "
               "are generated, and SOURCES.md carries that into the film's records."},
    {"path": "assets/death-laugh.ogg",
     "reason": "A documented placeholder: 3.42 s of silence standing in for Assignment "
               "1's undocumented-rights laugh. Named in the verdict rather than taught."},
    {"path": "assets/death-laugh-cat.png",
     "reason": "The matching placeholder: a flat colour card. Same treatment."},
    {"path": "assets/sfx-jump.ogg",
     "reason": "Synthesised placeholder, not generated. The trap effect is the one of "
               "the four with a design argument behind it, so C3 teaches that one and "
               "the verdict declares all four."},
    {"path": "assets/sfx-slash.ogg", "reason": "As sfx-jump.ogg."},
    {"path": "tests/capture_character.gd",
     "reason": "Produces the 11-frame character contact sheet. Its output is cited in "
               "the verdict as the check a human has to look at, but the script itself "
               "is not a beat."},
    {"path": "tests/capture_enemies.gd",
     "reason": "Assignment 1's enemy-visibility capture. Still passing, not this "
               "film's subject."},
    {"path": "tests/capture_game.gd",
     "reason": "Produces the level screenshots used in the repository's documents, not "
               "in this film."},
    {"path": "tests/route_driver.gd",
     "reason": "The scripted input route that completes the level. Assignment 1's "
               "evidence; this film's takes drive their own input."},
    {"path": "tests/test_keyboard.gd",
     "reason": "14 checks over the real InputMap. Counted in the verdict's 113, and "
               "the bindings themselves are unchanged by this assignment."},
    {"path": "ui/hud.gd",
     "reason": "The mute indicator added this assignment is visible in take-t's "
               "footage, but the HUD's drawing is original vector art explained in "
               "Assignment 1's film."},
]
for n in ("death-laugh-cat.png", "death-laugh.ogg", "music-loop.ogg",
          "sfx-death.ogg", "sfx-jump.ogg", "sfx-slash.ogg", "sfx-trap.ogg"):
    EXCLUSIONS.append({"path": "assets/%s.import" % n,
                       "reason": "Editor-generated sidecar. Every parameter is a Godot "
                                 "default, there is no texture-filter setting in it at "
                                 "all, and the game never reads it: every asset loads "
                                 "through globalize_path into load_from_file, an "
                                 "absolute OS path that bypasses res:// import so a "
                                 "headless run on a fresh checkout works."})
for n in ("p1-idle", "p2-run", "p3-rising", "p4-falling", "p5-dash",
          "p6-windup", "p7-live", "p8-death"):
    EXCLUSIONS.append({"path": "assets/poses/%s.png.import" % n,
                       "reason": "As the audio sidecars: a Godot default set the game "
                                 "never reads."})

# ---- files, with component association
# Walked here, every run. The first version read a _inventory.json written
# earlier in the session, and by the time the ledger was built that file was
# missing tests/capture_gamedev.gd -- this film's own capture driver, created
# after it. The checker caught it as "Inventory coverage mismatch", which is
# what it is for. A snapshot that can go stale between two steps should not
# exist.
inv = []
for dp, dn, fn in os.walk(GAME):
    dn[:] = [d for d in dn if d not in (".godot", ".git")]
    for f in sorted(fn):
        full = os.path.join(dp, f)
        rel = os.path.relpath(full, GAME).replace("\\", "/")
        if rel.endswith(".uid"):
            continue
        inv.append({"path": rel, "sha256": sha(full)})
excluded = {e["path"] for e in EXCLUSIONS}
assoc = {}
for c in COMPONENTS:
    for f in c["files"]:
        assoc.setdefault(f, []).append(c["id"])

# A path may not be in both lists: the checker rejects "File both included and
# excluded". So `files` carries the inventoried files this film teaches, and
# `exclusions` carries the rest with a reason each. Together they are the whole
# inventory, which is what "still counted and visible to the reviewer" asks for.
files = []
for row in inv:
    p = row["path"]
    if p in excluded:
        continue
    role = ROLES.get(p)
    if role is None:
        role = ("test" if p.startswith("tests/") else
                "import-sidecar" if p.endswith(".import") else
                "doc" if p.endswith(".md") else "asset")
    files.append({"path": p, "sha256": row["sha256"], "role": role,
                  "component_ids": assoc.get(p, [])})

unassoc = [f["path"] for f in files if not f["component_ids"]]
if unassoc:
    raise SystemExit("included but associated with no component: %s" % unassoc)
missing = {r["path"] for r in inv} - {f["path"] for f in files} - excluded
if missing:
    raise SystemExit("inventoried but neither included nor excluded: %s" % sorted(missing))
ghost = excluded - {r["path"] for r in inv}
if ghost:
    raise SystemExit("excluded but not in the inventory: %s" % sorted(ghost))

# ---- excerpts, read from the files again so they cannot drift
# The ranges are DERIVED FROM THE BEAT SHEET, not restated here. They were
# hardcoded once, and when the panel-fitting pass shortened two excerpts the
# ledger kept the old numbers and the checker said "Displayed code differs from
# excerpt". A fact written in two places is a fact that will disagree with
# itself.
EX = {}
for bid, b in by.items():
    rem = b["shot"].get("remotion")
    if not rem or not rem["props"].get("code"):
        continue
    props = rem["props"]
    rel = props["source"].split("godot/", 1)[-1]
    a = props["startLine"]
    EX[bid] = (rel, a, a + len(props["code"].splitlines()) - 1)
excerpts = []
for bid, (rel, a, b) in sorted(EX.items()):
    lines = io.open(os.path.join(GAME, rel), encoding="utf-8", newline="").read().split("\n")
    text = "\n".join(lines[a - 1:b])
    if by[bid]["shot"]["remotion"]["props"]["code"] != text:
        raise SystemExit("%s: props.code does not match the file" % bid)
    excerpts.append({"beat_id": bid, "path": rel, "start_line": a,
                     "end_line": b, "text": text})

PAIRS = [("B02", "B03", "capture/take-p.mp4",
          "The pose sequence the capture driver logged: idle, run, rise, fall, run, "
          "idle, rise, dash, fall, idle - each transition a logged event with its tick."),
         ("B04", "B05", "media/B05-poses.png",
          "All eight poses at 32 px, on the dungeon wall, as silhouettes, and on the "
          "torchlit edge. 6.3% of the figure read against the wall without the rim, "
          "24.2% with it."),
         ("B06", "B07", "capture/take-t.mp4",
          "Trap 0 arms at t=6.800 with the player at x 1064.9 against a trigger at "
          "1064; the death is at t=7.383. A 35-tick lead, read out of sfx_log by the "
          "driver and reported independently by test_game.gd."),
         ("B08", "B09", "media/B09-suite-output.png",
          "An ordinary retry moves the playhead 0.557 -> 0.651 s. Pause then retry "
          "resumes at exactly the paused position."),
         ("B10", "B11", "capture/take-p.mp4",
          "The wind-up and live poses with the code-drawn blade over them, from the "
          "pivot the hitbox uses. Worst endpoint error 3.8e-6 px.")]

pairs = []
for code_beat, result_beat, media, obs in PAIRS:
    full = os.path.join(REEL, media)
    if not os.path.isfile(full):
        raise SystemExit("missing media for %s: %s" % (result_beat, media))
    if by[result_beat]["shot"].get("evidence_media") != media:
        raise SystemExit("%s evidence_media != %s" % (result_beat, media))
    pairs.append({"code_beat": code_beat, "result_beat": result_beat,
                  "observation": obs,
                  "media": {"path": media, "sha256": sha(full)}})

ledger = {"schema_version": 1, "game": GAME,
          "teaching_contract": "code-then-result-v1",
          "files": files, "components": COMPONENTS, "excerpts": excerpts,
          "code_result_pairs": pairs, "exclusions": EXCLUSIONS}
io.open(os.path.join(REEL, "gamedev-evidence.json"), "w", encoding="utf-8",
        newline="\n").write(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n")

print("gamedev-evidence.json")
print("  files        %d included + %d excluded = %d inventoried" % (
    len(files), len(EXCLUSIONS), len(inv)))
print("  components   %d" % len(COMPONENTS))
print("  excerpts     %d, all matching their beat's props.code and the file" % len(excerpts))
print("  pairs        %d, every media file present and hashed" % len(pairs))
total = sum(b["estimated_duration_s"] for b in doc["beats"])
print("beat_sheet.json  %d beats, %d:%02d estimated" % (len(doc["beats"]), total // 60, total % 60))
