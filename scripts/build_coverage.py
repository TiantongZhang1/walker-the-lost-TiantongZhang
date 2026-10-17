#!/usr/bin/env python3
"""Author coverage.json for the godot-waikthrough reel.

Times are NOT typed in. Every `start_s`, `action_s` and `end_s` below is a
label in a take's input log plus an offset, resolved at build time against
`capture/take-<letter>-inputs.jsonl`. If a label disappears because a take was
re-cut, this fails loudly instead of emitting a stale number - which is the
point, since the whole file is an evidence claim.

Beat ids are not typed in either: each interval is assigned to the gameplay beat
whose `shot.window_s` contains its action, read from beat_sheet.json. The body
tiles the takes end to end, so exactly one beat can own any given moment - and
re-cutting the body re-files the evidence instead of leaving it pointing at a
beat that has moved.

Observations and riffs are written by hand after watching the takes; the script
will not invent them.

    python scripts/build_coverage.py youtube/claude-liam-newwalkervideo-tiantongzhang-walkthrough
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BUILD_ID = "82696a5dc3e5c2f8fcfdfc2630a6f3254b1ea7ce2258c197b48229fe7b9cd436"
GAME = "walker-jumpman-TiantongZhang"
TAKES = ("a", "b", "c", "d")


# ---------------------------------------------------------------- evidence ---
# (start_label, start_offset), (action_label, action_offset), (end_label, end_offset)
# Labels are matched as substrings of an entry's "action" field; `occurrence`
# picks among repeats. Offsets are seconds.
def M(label, offset=0.0, occurrence=0):
    return {"label": label, "offset": offset, "occurrence": occurrence}


FEATURES = [
    {
        "id": "session-start-keyboard", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("press start", -0.25), "action": M("press start"),
            "end": M("reached: session started", 0.70),
            "observation": "The menu card is on screen; Enter at 1.250 s moves the session from MENU to PLAYING within two physics frames, and the level, HUD and character replace the card.",
            "riff": "Enter and the on-screen button both call the same start, which means there is no second start path to keep in sync - the price is that the menu cannot make the two inputs behave differently later without splitting them again.",
        }],
    },
    {
        "id": "session-start-mouse-button", "status": "implemented",
        "evidence": [{
            "capture": "take-c",
            "start": M("take-c begin", 0.20), "action": M("pointer on the start button", 0.05),
            "end": M("reached: started from the HUD button", 0.60),
            "observation": "The real pointer is placed at logical (320.0, 232.0), inside the button's Rect2(220, 215, 200, 34), and a left-click at 0.567 s starts the session by 0.600 s.",
            "riff": "The button hit-tests the live pointer rather than the click event's coordinates, which is what makes it feel like a button - and is also why proving it works needs a capture that warps the actual cursor instead of faking a position.",
        }],
    },
    {
        "id": "run-and-stop", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("press start", 0.05), "action": M("press move-right"),
            "end": M("reached: walked past x=150", 0.30),
            "observation": "Holding D accelerates to the tuning speed of 160 px/s; the character covers x=64 to x=150 in 0.60 s and the HUD progress bar advances with it.",
            "riff": "Acceleration and deceleration are separate values, so stopping is snappier than starting - it reads as weight without costing you the precision you need at a ledge.",
        }],
    },
    {
        "id": "facing-mirrors-the-character", "status": "implemented",
        "evidence": [{
            "capture": "take-c",
            "start": M("press move-left", -0.10), "action": M("press move-left", 0.15),
            "end": M("verified: the character faces left", 0.35),
            "observation": "Holding A flips facing to -1 by 0.933 s: the visor slit, the scarf and the sheathed blade all mirror with the body.",
            "riff": "Mirroring the whole silhouette rather than only the body is what keeps the visor reading as a face - the cost is that every drawn offset has to be expressed relative to facing, which is exactly where the sword's hitbox mirroring had to be written once and shared.",
        }],
    },
    {
        "id": "jump-fixed-height", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("press jump", -0.40), "action": M("press jump"),
            "end": M("press jump", 0.90),
            "observation": "Space at 1.933 s produces a 53.33 px arc and the key is released 0.05 s later with no effect on the height reached.",
            "riff": "A fixed height means the jump is a decision about WHERE, never about how long you hold - it costs expressiveness and buys a level that can be laid out in exact pixels, which is what makes the plank clearances provable instead of approximate.",
        }],
    },
    {
        "id": "coyote-time", "status": "implemented",
        "evidence": [{
            "capture": "take-c",
            "start": M("reached: landed past the spike", 0.10),
            "action": M("press coyote-jump"),
            "end": M("reached: landed across the gap", 0.20),
            "observation": "The character runs off the x=448 ledge at 3.917 s with no jump pressed, and a press on the same frame still produces a jump; afterwards air_jumps_left is still at its full value, so this spent the GROUND jump, not the second one. Six frames, from tuning.coyote_ticks.",
            "riff": "Six frames of forgiveness is invisible when it works and only shows up as the absence of unfair deaths - the trade-off is that the ground jump keeps precedence, so a player who wanted the air jump at a ledge gets the ground one and cannot tell the difference until they need the second jump 20 frames later.",
        }],
    },
    {
        "id": "jump-buffer", "status": "implemented",
        "evidence": [{
            "capture": "take-d",
            "start": M("verified: the air jump is spent", -0.20),
            "action": M("press buffered jump press"),
            "end": M("reached: the buffered jump fired on the landing frame", 0.60),
            "observation": "The air jump is deliberately spent first, so the press at 2.767 s can be neither a ground jump nor an air jump. One frame later nothing has fired; the jump counter increments on the landing frame at 2.817 s. Six frames, from tuning.buffer_ticks.",
            "riff": "Buffering an early press is the other half of coyote time and the two together are why this jump feels fair - the honest cost is that a buffered press is indistinguishable on screen from a well-timed one, so the only way to show it is to spend the air jump first and let the counters testify.",
        }],
    },
    {
        "id": "air-jump", "status": "implemented",
        "evidence": [{
            "capture": "take-c",
            "start": M("press jump 1 of 3", -0.15), "action": M("press jump 2 of 3"),
            "end": M("press dash", -0.05, 0),
            "observation": "The second jump fires at the first jump's apex (7.500 s) at the starter's unchanged jump_velocity, taking the total rise from 53.33 px to 106.7 px. One per takeoff; it is refilled only by touching the floor.",
            "riff": "Height is what the second jump buys, and the level is built so that is the only thing it buys - against the flying horses it is a liability, because more airtime means more time inside their band.",
        }],
    },
    {
        "id": "air-dash", "status": "implemented",
        "evidence": [{
            "capture": "take-c",
            "start": M("press jump 2 of 3", 0.10), "action": M("press dash", 0.0, 0),
            "end": M("reached: landed on the high plank", 0.25),
            "observation": "Shift at 7.850 s locks horizontal speed to 400 px/s for ten frames with vertical motion suspended, and the arc flattens visibly before gravity resumes; the character lands on the plank at y=224.",
            "riff": "Suspending gravity rather than adding impulse is what makes the dash a distance tool instead of a second jump - and because the leftover speed decays through the starter's own deceleration, it has a tail you can feel on landing.",
        }],
    },
    {
        "id": "air-dash-refused-on-ground", "status": "implemented",
        "evidence": [{
            "capture": "take-d",
            "start": M("verified: resumed after the focus pause", 0.05),
            "action": M("press dash", 0.0, 0),
            "end": M("verified: a refused dash costs nothing", 0.40),
            "observation": "Shift while standing at 1.617 s produces nothing: the dash counter does not move and dashes_left is still at its full value at 1.700 s.",
            "riff": "Refusing on the ground, and refusing for free, is the difference between a mechanic and a trap - a dash that was consumed by a mistimed ground press would punish exactly the player still learning when it is legal.",
        }],
    },
    {
        "id": "air-dash-is-not-invulnerability", "status": "implemented",
        "evidence": [{
            "capture": "take-d",
            "start": M("reached: in position beside the spike", 0.05),
            "action": M("press dash", 0.0, 1),
            "end": M("verified: the dash gave no invulnerability", 0.45),
            "observation": "Jump, then dash within three frames while the feet are still inside the spike's 304..320 band: the character drives straight through the risen spike at (1169.5, 314.6) and dies with 'Watch the spikes'.",
            "riff": "The dash was deliberately given no invulnerability frames, which keeps every hazard readable by geometry alone - the cost is that it cannot be used as an escape, so it is only ever an answer to distance, never to danger.",
        }],
    },
    {
        "id": "sword-slash", "status": "implemented",
        "evidence": [{
            "capture": "take-b",
            "start": M("release move-right (hold ground)", -0.35, 0),
            "action": M("release move-right (hold ground)", 0.0, 0),
            "end": M("press move-right", 0.85, 1),
            "observation": "The route stops at x=1559.6 rather than walking into the first slime and swings: 16 frames per swing, four of wind-up, nine live, three of recovery, sweeping -120 to +40 degrees. The slime is gone and the run continues.",
            "riff": "The hit is computed from the same pivot, angle and reach the blade is drawn with, so what you can see is what kills - that replaced an Area2D query that reported the previous physics step and therefore missed the only frame whose angle reaches floor level.",
        }],
    },
    {
        "id": "enemy-slime-ground-patrol", "status": "implemented",
        "evidence": [{
            "capture": "take-b",
            "start": M("press jump @1390", 0.40),
            "action": M("release move-right (hold ground)", -0.10, 0),
            "end": M("press move-right", 0.60, 1),
            "observation": "A slime patrols 1580..1690 at 60 px/s, turning at fixed bounds with no chasing, no edge detection and no randomness, so the same inputs always produce the same attempt. One slash kills it; contact kills the player.",
            "riff": "Fixed bounds instead of chasing is what makes this level learnable rather than reactive - the cost is that nothing about an enemy responds to you, so all the difficulty has to come from where they are placed.",
        }],
    },
    {
        "id": "enemy-horse-air-patrol", "status": "implemented",
        "evidence": [{
            "capture": "take-b",
            "start": M("press jump @2020", -0.35), "action": M("press jump @2020"),
            "end": M("press jump @2020", 0.75),
            "observation": "A horse holds the 2048..2112 gap at y=268, patrolling 2028..2132. The swing is opened before the takeoff so the blade is already live when the character leaves the ground at 13.567 s, and the horse is cut out of the air.",
            "riff": "Horses can only be hit from the air but collide about seven frames after takeoff, so the swing has to be open BEFORE you jump - that is the one piece of timing in this game that a player has to learn rather than read.",
        }],
    },
    {
        "id": "static-spike-hazard", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("press jump", 0.30), "action": M("DIED", -0.25),
            "end": M("reached: spike death", 0.35),
            "observation": "The starter's own spike at x=320..344 ends the attempt on contact at (318.2, 319.9) at 3.083 s, with the reason 'Watch the spikes'.",
            "riff": "This one hazard is the starter's and was left exactly where it was - everything added later had to join its overlap loop rather than open a second way to die, which is why the retry timing and the reaction are identical for all three reasons.",
        }],
    },
    {
        "id": "pop-up-trap", "status": "implemented",
        "evidence": [{
            "capture": "take-d",
            "start": M("reached: across T1's trigger at 1064", -0.30),
            "action": M("verified: the trap started rising when the trigger was crossed"),
            "end": M("trap fully risen", 0.70),
            "observation": "Crossing the trigger at x=1064 starts the spike at 1160..1184 rising; it takes 15 physics frames to reach full height, watched from x=1075.6, ninety pixels clear of it. The Area2D moves with the drawing, so the spike is lethal only where it is drawn.",
            "riff": "Fifteen frames of warning is the entire fairness contract for these, and it is 96 px of run-up at 160 px/s - the trap is a memory test on the first attempt and a timing test on every one after, which is the deal I-Wanna-style traps always make.",
        }],
    },
    {
        "id": "fall-death", "status": "implemented",
        "evidence": [{
            "capture": "take-d",
            "start": M("reached: landed past the spike", 0.15), "action": M("DIED", -0.30, 0),
            "end": M("reached: automatic retry", 0.30, 0),
            "observation": "Running off the x=448 ledge with nothing pressed crosses the level's fall boundary and ends the attempt at (505.1, 435.9) at 6.317 s, with the reason 'Missed the landing'. The death reaction plays for a fall exactly as for a spike.",
            "riff": "A separate sentence for the fall is the cheapest possible teaching tool - the same freeze, the same reaction, the same 0.55 s retry, and the only thing that changes is which mistake you are told you made.",
        }],
    },
    {
        "id": "enemy-contact-death", "status": "implemented",
        "evidence": [{
            "capture": "take-d",
            "start": M("verified: the slime is still alive to walk into", 0.05),
            "action": M("DIED", -0.25, 2),
            "end": M("reached: automatic retry", 0.35, 2),
            "observation": "Walking into a live slime with the sword down ends the attempt at (1570.2, 319.9) at 25.800 s with the reason 'It got you'. Enemies feed the same fatal flag as the spikes, not a parallel death path.",
            "riff": "Reusing the hazard path for enemies means the retry timing and the reaction could not drift apart from the spikes' - the cost is that an enemy cannot ever do anything except kill you, because that path has exactly one outcome.",
        }],
    },
    {
        "id": "death-reaction", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("DIED", -0.20), "action": M("verified: death reaction started"),
            "end": M("reached: automatic retry", 0.30),
            "observation": "On death a laughing cat is drawn at Rect2(476, 86, 150, 153) and a 3.42 s laugh plays once; the panel naming the reason sits at Rect2(180, 128, 280, 68) and the two do not intersect. The reaction ends with the sound rather than on a separate timer.",
            "riff": "Tying the overlay's lifetime to the audio's length is why the cat leaves exactly when the laugh stops instead of lingering - and the two rectangles are named constants precisely so 'they do not overlap' is something a test can assert rather than something I remember checking.",
        }],
    },
    {
        "id": "automatic-retry", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("reached: spike death", 0.05), "action": M("reached: automatic retry"),
            "end": M("verified: respawned at the start", 0.55),
            "observation": "0.55 s after the death the level resets itself and the character is back at the spawn (x < 80) at 3.650 s, with the deaths counter at 1. Reset does not wait for the reaction to finish.",
            "riff": "Making the reset independent of the animation is what keeps a joke overlay from becoming a tax - you can be laughed at and already be running again.",
        }],
    },
    {
        "id": "manual-retry", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("verified: resumed", 0.20), "action": M("press manual-retry"),
            "end": M("verified: manual retry is not a death", 0.45),
            "observation": "R at 6.817 s respawns the attempt by 6.900 s and the deaths counter stays at 1 - a manual restart is explicitly not counted as a death.",
            "riff": "Not counting a voluntary restart is the difference between a death counter that measures mistakes and one that measures impatience - the first is worth showing on the results card.",
        }],
    },
    {
        "id": "pause-and-resume", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("press pause", -0.25, 0), "action": M("press pause", 0.0, 0),
            "end": M("verified: resumed", 0.35),
            "observation": "Escape at 4.900 s enters PAUSED and the character's x does not move for a full second (asserted, not assumed); Enter at 5.983 s resumes from the same pixel.",
            "riff": "Freezing the player rather than the whole tree is what lets the menu stay operable while gameplay stops - and it is why the pause had to be checked by comparing positions instead of by trusting a state flag.",
        }],
    },
    {
        "id": "focus-loss-auto-pause", "status": "implemented",
        "evidence": [{
            "capture": "take-d",
            "start": M("reached: session started", 0.0),
            "action": M("another window took the focus"),
            "end": M("verified: resumed after the focus pause", 0.35),
            "observation": "A second real OS window takes the focus at 0.733 s and the engine's own focus_exited puts the session into PAUSED on the same frame; it stays paused until Enter at 1.333 s, because nothing auto-resumes on focus return.",
            "riff": "Pausing on focus loss is a courtesy to the player and a hazard to the person recording - it is also why every take in this film asserts its own outcome, so a stray click during a render fails the capture instead of quietly filming a paused game.",
        }],
    },
    {
        "id": "return-to-main-menu", "status": "implemented",
        "evidence": [{
            "capture": "take-a",
            "start": M("press pause", -0.15, 1), "action": M("press main-menu"),
            "end": M("verified: back at the menu", 0.45),
            "observation": "From PAUSED, M at 7.383 s returns the session to MENU by 7.467 s, disabling the player and stopping the death reaction if one is running.",
            "riff": "Leaving to the menu is only offered from the two states where an attempt is not live, which is why it needs no confirmation dialogue - the state machine is doing the work a modal would otherwise do.",
        }],
    },
    {
        "id": "two-road-fork", "status": "implemented",
        "evidence": [{
            "capture": "take-c",
            "start": M("on the high road", -0.20),
            "action": M("press off the plank, inside the coyote window"),
            "end": M("verified: landed past trap T3", 0.35),
            "observation": "From the high plank at y=224 the route leaves the right end inside the coyote window, air-jumps over the 1224..1280 gap, dashes a second time at the apex, and lands on the low road past trap T3 at x > 1456 - skipping all three low-road traps with no deaths and no kills.",
            "riff": "The plank's underside at y=232 is what makes this a choice rather than a shortcut: a plain double jump from the low road hits it from below, so the high road costs the dash both getting on and getting off. What it buys is three traps you never have to time.",
        }],
    },
    {
        "id": "finish-and-complete", "status": "implemented",
        "evidence": [{
            "capture": "take-b",
            "start": M("verified: reached the finish", -0.55),
            "action": M("verified: reached the finish"),
            "end": M("press replay", -0.20),
            "observation": "Touching the relocated finish at x=3030 enters COMPLETE at 20.767 s with 0 deaths and 10 of 11 enemies killed, and the results card replaces the HUD.",
            "riff": "Moving the finish from 916 to 3030 is the whole reason the progress bar had to stop being a hard-coded denominator - a number that agreed with the level only by coincidence is the kind of thing that survives every test until the day it is wrong.",
        }],
    },
    {
        "id": "replay", "status": "implemented",
        "evidence": [{
            "capture": "take-b",
            "start": M("press replay", -0.30), "action": M("press replay"),
            "end": M("verified: replay restarts at the spawn", 0.55),
            "observation": "Enter from the results card at 22.267 s restarts the session at the spawn (x=64.0) by 22.317 s with the counters reset.",
            "riff": "Replay resetting the session death count, where an automatic retry does not, is the line between 'this attempt' and 'this sitting' - it is a small decision that decides what the results card is actually measuring.",
        }],
    },
    {
        "id": "hud-readouts", "status": "implemented",
        "evidence": [{
            "capture": "take-b",
            "start": M("verified: finished without dying", -0.45),
            "action": M("finished"),
            "end": M("press replay", -0.35),
            "observation": "The HUD carries a progress bar derived from the level's own width, a deaths counter, the control hints, and on death the reason panel; on completion it shows the run's time, deaths and kills.",
            "riff": "Deriving progress from the level data rather than a literal is the difference between a bar that is right and a bar that was right once - and the results card is the only place the death counter earns its keep.",
        }],
    },
    {
        "id": "camera-follow", "status": "implemented",
        "evidence": [{
            "capture": "take-b",
            "start": M("press jump @2020", -0.90), "action": M("press jump @2020", -0.20),
            "end": M("press jump @2020", 0.90),
            "observation": "The camera tracks the character with a 100 px lead and is clamped to the level's bounds, so it stops at both ends instead of showing empty space beyond x=0 or x=3072.",
            "riff": "A fixed 100 px lead is generous going right and useless going left, which is honest for a level that only runs one way - it would be the first thing to change if the level ever doubled back.",
        }],
    },
    # ----------------------------------------------------------- planned -----
    {
        "id": "cherries", "status": "planned", "evidence": [],
        "reason": "GDD MECH-03 specifies twenty identified cherries per attempt with a collected/20 HUD readout. Never implemented, in the starter or in this extension; the HUD has no collection slot and the level data has no cherry entries.",
    },
    {
        "id": "moving-platforms", "status": "planned", "evidence": [],
        "reason": "GDD MECH-05, which the design document itself labels a follow-up and not MVP-blocking. No moving solid exists; every solid in first_steps.json is static.",
    },
    {
        "id": "settings-and-key-remapping", "status": "planned", "evidence": [],
        "reason": "GDD MECH-07 asks the pause menu to expose mute and keyboard remapping with conflict feedback and restore-defaults. The pause menu offers Resume, Restart and Main Menu only; the InputMap is built in code at startup and cannot be rebound in game.",
    },
    {
        "id": "music-and-sound-effects", "status": "planned", "evidence": [],
        "reason": "The GDD allows optional sound with a visual equivalent for jumps and collection. The only audio in the build is the death reaction's laugh; there is no music, footstep, jump, slash or victory sound. No sound was invented for the film either.",
    },
    {
        "id": "three-zone-level", "status": "planned", "evidence": [],
        "reason": "GDD section 4 describes crossing three increasingly combined zones. What exists is one level, extended twice, with a fork and an enemy half - not three authored zones.",
    },
]


# ------------------------------------------------------------------ build ----
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


class Logs:
    def __init__(self, reel: Path):
        self.rows: dict[str, list[dict]] = {}
        for letter in TAKES:
            path = reel / "capture" / ("take-%s-inputs.jsonl" % letter)
            if not path.is_file():
                raise SystemExit("missing input log: %s" % path)
            self.rows["take-%s" % letter] = [
                json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    def at(self, capture: str, mark: dict) -> float:
        hits = [r for r in self.rows[capture] if mark["label"] in r["action"]]
        if len(hits) <= mark["occurrence"]:
            raise SystemExit("%s: label %r occurrence %d not found (%d match)" % (
                capture, mark["label"], mark["occurrence"], len(hits)))
        return round(hits[mark["occurrence"]]["t_s"] + mark["offset"], 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reel", type=Path)
    args = parser.parse_args()
    reel = args.reel.resolve()
    logs = Logs(reel)

    sheet = json.loads((reel / "beat_sheet.json").read_text(encoding="utf-8"))
    windows = []
    for beat in sheet["beats"]:
        shot = beat.get("shot", {})
        if shot.get("capture") and shot.get("window_s"):
            if not (beat.get("narration_text") or "").strip():
                raise SystemExit("%s owns gameplay but has no narration" % beat["beat_id"])
            windows.append((shot["capture"], float(shot["window_s"][0]),
                            float(shot["window_s"][1]), beat["beat_id"]))

    def beat_for(capture: str, action_s: float) -> str:
        hits = [bid for cap, lo, hi, bid in windows
                if cap == capture and lo <= action_s < hi]
        if len(hits) != 1:
            raise SystemExit("%s at %.3f s is owned by %d beats (%s) - the body "
                             "must tile each take exactly once" % (
                                 capture, action_s, len(hits), hits or "none"))
        return hits[0]

    captures = {}
    durations = {}
    for letter in TAKES:
        cid = "take-%s" % letter
        video = reel / "capture" / ("%s.mp4" % cid)
        if not video.is_file():
            raise SystemExit("missing capture: %s" % video)
        durations[cid] = probe_duration(video)
        captures[cid] = {
            "path": "capture/%s.mp4" % cid,
            "sha256": sha256_file(video),
            "build_id": BUILD_ID,
            "method": "scripted-input",
            "input_log": "capture/%s-inputs.jsonl" % cid,
        }

    features = []
    intervals = 0
    for feature in FEATURES:
        entry = {"id": feature["id"], "status": feature["status"]}
        if feature["status"] == "planned":
            entry["reason"] = feature["reason"]
            entry["evidence"] = []
            features.append(entry)
            continue
        evidence = []
        for ev in feature["evidence"]:
            cid = ev["capture"]
            start = max(0.0, logs.at(cid, ev["start"]))
            action = logs.at(cid, ev["action"])
            end = min(durations[cid], logs.at(cid, ev["end"]))
            if not (0.0 <= start < action < end <= durations[cid] + 1e-9):
                raise SystemExit(
                    "%s/%s: need 0 <= start < action < end <= %.3f, got %.3f / %.3f / %.3f" % (
                        feature["id"], cid, durations[cid], start, action, end))
            evidence.append({
                "capture": cid, "beat_id": beat_for(cid, action),
                "start_s": start, "action_s": action, "end_s": end,
                "observation": ev["observation"], "riff": ev["riff"],
            })
            intervals += 1
        entry["evidence"] = evidence
        features.append(entry)

    coverage = {
        "schema_version": 1,
        "game": {"name": GAME, "build_id": BUILD_ID},
        "captures": captures,
        "features": features,
    }
    (reel / "coverage.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    implemented = sum(1 for f in features if f["status"] == "implemented")
    planned = len(features) - implemented
    print("coverage.json: %d implemented, %d planned, %d evidence intervals" % (
        implemented, planned, intervals))
    for cid, props in captures.items():
        print("  %-8s %6.2f s  %s" % (cid, durations[cid], props["sha256"][:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
