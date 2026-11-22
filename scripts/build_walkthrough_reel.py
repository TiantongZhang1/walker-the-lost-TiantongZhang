#!/usr/bin/env python3
"""Write Assignment 8's walkthrough beat sheet AND its coverage contract.

    python -X utf8 scripts/build_walkthrough_reel.py

**One script, two files, one source of truth.** `coverage.json` names beat
ids and `beat_sheet.json` names captures; if they were authored separately
they would drift, and the checker would catch the drift rather than the
mistake. Here each feature below carries both its evidence window and the
beat that shows it, and the two files are projections of the same table.

Run it twice, like every beat sheet in this repository: the first pass gives
`generate_audio_kokoro.py` something to measure, the second re-authors every
cue and every footage window against the measured narration. There is no
third pass -- see `BUILD-PROMPT.md`.

**The feature table is the thing to review.** The machine check validates
hashes, dimensions, time ranges and references. It cannot tell you that the
inventory is complete, that a window actually contains what its observation
says, or that a feature listed `planned` is really unbuilt. Those are
`_qc/REPORT.md` and `FACTCHECK.md`.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-walkthrough"
SLUG = "claude-liam-walker-the-lost-walkthrough"
TITLE = "TheLostWalkthrough_TiantongZhang"
TOPIC = "WALKER - THE LOST, PLAYED"

# Kokoro's measured rate, from Assignment 7's finished sheet: 2277 words
# across 570.3 s. The first pass only needs plausible windows.
WORDS_PER_SECOND = 3.53


def probe_seconds(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# THE FEATURE TABLE.
#
# `status` is `implemented` or `planned`. An implemented feature with no
# evidence makes the check FAIL, which is the behaviour the skill asks for:
# a feature that is built and not shown prevents the complete-walkthrough
# claim, and relabelling it `planned` to get a pass is named in the reference
# as the thing not to do.
#
# `window` is [start, action, end] in the CAPTURE's own seconds. Those are
# read off the take logs, not guessed: `tools/check_walkthrough_windows.py`
# re-derives each one and fails if the stated action is not in it.
# ---------------------------------------------------------------------------
FEATURES = [
    # --- the states, take a ------------------------------------------------
    dict(id="idle-at-rest", beat="B02", take="a", window=(1.30, 1.50, 2.10),
         obs="The player settles on the floor and holds the idle cell; no key "
             "is down and nothing moves except the room.",
         riff="Idle is a held frame rather than a clip, which is why it costs "
              "nothing and why it cannot breathe. The trade is visible: this "
              "character stands perfectly still, and a player reads that as "
              "waiting rather than as alive."),
    dict(id="run-cycle-loops", beat="B03", take="a", window=(2.20, 2.60, 4.60),
         obs="A direction key is held; the two cut-out legs alternate and the "
             "cycle wraps five times across the take.",
         riff="The cycle's half-second is not a taste decision -- it is two "
              "strides at twenty-four pixels against a speed of ninety-six. "
              "Retime the run and that arithmetic changes first."),
    dict(id="facing-mirrors-the-rig", beat="B03", take="a",
         window=(3.30, 3.60, 4.60),
         obs="The player reverses; the whole rig mirrors, legs and sword arm "
             "together, and the gait keeps alternating in the new facing.",
         riff="Facing is one scale flip on the rig root, not a property of "
              "the animation. That is why one set of keys is correct both "
              "ways round -- and why a mid-swing turn is forbidden."),
    dict(id="step-dust-on-the-footfall", beat="B03", take="a",
         window=(2.60, 3.00, 4.40),
         obs="A puff of dust is left every twenty-four pixels travelled, "
             "under the planted foot.",
         riff="The dust is driven by distance, not by the animation, and the "
              "cycle's length was derived from that same distance. They agree "
              "because they were made to; nothing enforces it at runtime."),
    dict(id="jump-rising-and-falling", beat="B04", take="a",
         window=(5.10, 5.40, 6.60),
         obs="Space leaves the floor on the next physics frame; the sprite "
             "shows the rising cell, then the falling cell, then lands.",
         riff="Two states, one key. The split is the sign of the vertical "
              "velocity, which means the character reads as committed to the "
              "arc before it has reached the top of it."),
    dict(id="floating-key-simple-animation", beat="B05", take="a",
         window=(0.20, 1.00, 3.00),
         obs="The key between the first two traps bobs three pixels and turns "
             "a full revolution every 2.4 s, with no input and nothing "
             "driving it.",
         riff="One sprite, two tracks, no rig and no frames. It autoplays, so "
              "nothing in the game has to remember to start it -- and nothing "
              "collects it either, which the brief says out loud rather than "
              "letting a key in a dungeon imply a door."),
    # --- the committing action, take b -------------------------------------
    dict(id="swing-three-phases", beat="B06", take="b", window=(1.00, 1.10, 1.80),
         obs="One attack press plays all eighteen frames: wind-up, strike, "
             "recovery. The strike is the fastest segment on the timeline.",
         riff="The arm nearly stops before it goes -- ten degrees in the two "
              "frames before the window opens, then a hundred and fifty in "
              "four. That pause is what makes it read as a strike."),
    dict(id="swing-commits", beat="B06", take="b", window=(1.00, 1.30, 1.80),
         obs="Once started the clip runs to its own end; no input shortens it.",
         riff="Committing is not the same as freezing the player. You can "
              "walk and jump out of this swing -- what you cannot do is "
              "cancel it or turn it around."),
    dict(id="attack-during-attack-ignored", beat="B07", take="b",
         window=(2.20, 2.42, 3.10),
         obs="A second attack is pressed 0.1 s into a swing -- inside the "
             "0.2 s startup -- and no new swing begins. The log shows the "
             "swing counter unchanged across the press.",
         riff="This is the edge the assignment asks for, and the interesting "
              "half is that it would pass by accident: calling play() with "
              "the name already playing does nothing. The code checks the "
              "playhead instead, so the rule is a decision rather than a "
              "side effect."),
    dict(id="attack-during-attack-buffered", beat="B07", take="b",
         window=(3.50, 3.95, 5.30),
         obs="A second attack pressed 0.45 s in -- inside recovery -- is "
             "buffered, and a fresh swing starts when the first one ends.",
         riff="Same key, same clip, opposite answer, and the only difference "
              "is where the playhead was. A buffer is how a game stops "
              "punishing a player for being early."),
    # --- the two revisions, take c -----------------------------------------
    dict(id="swing-while-moving", beat="B08", take="c", window=(1.00, 1.75, 2.60),
         obs="A direction is held through a swing; the player travels and the "
             "gait keeps running under the body cell.",
         riff="The legs have their own player and never hear that a sword "
              "exists, so nothing seeks them and the gait keeps its phase "
              "straight through the swing."),
    dict(id="jump-during-swing", beat="B08", take="c", window=(3.30, 3.55, 4.80),
         obs="Space is pressed mid-swing; the player leaves the floor and the "
             "swing continues from where it was, ending on its own clock.",
         riff="The jump writes one field and nothing else, so there is no "
              "path from it to the clip's clock. That is why it cannot "
              "interrupt -- structural, rather than careful."),
    # --- the hazard and failure, take d ------------------------------------
    dict(id="trap-warning-then-strike", beat="B09", take="d",
         window=(1.80, 2.40, 3.60),
         obs="A trap lights its warning band, then fires; grit comes off the "
             "floor line with the spikes.",
         riff="The warning is four tenths of a second and the swing's startup "
              "is two. That ratio is the whole reason you can read a trap and "
              "still choose to attack near it."),
    dict(id="damage-does-not-interrupt", beat="B09", take="d",
         window=(2.40, 2.60, 3.60),
         obs="The player takes a hit and keeps walking; no animation state "
             "changes and no clip restarts.",
         riff="Damage is a number here, not a state. There is no hurt "
              "animation, and the brief lists that as a limit rather than "
              "letting the absence pass as a decision."),
    dict(id="death-state", beat="B10", take="d", window=(9.60, 10.60, 12.90),
         obs="The fifth trap hit takes health to zero; the dead cell plays "
             "once and holds, and input stops moving the character.",
         riff="This is the only one of the five states no key can reach. It "
              "is entered by a game condition that an action caused, which is "
              "what the assignment means by a state wired to a player action."),
    # --- planned, with reasons ---------------------------------------------
    dict(id="respawn-or-retry", status="planned",
         reason="There is no recovery from death in this slice: no respawn, "
                "no retry key, no reload. The film shows the death and says "
                "so rather than cutting away before the question arises."),
    dict(id="enemies", status="planned",
         reason="The swing's hitbox is real, measured and switched by the "
                "clip's own timeline, and it can hit NOTHING -- this room has "
                "no enemy. CHANGE-BRIEF.md section 11.3 said so before any of "
                "it was built."),
    dict(id="roll-cast-and-combo-2-3", status="planned",
         reason="GDD.md:393 lists idle / run / jump / roll / combo-1,2,3 / "
                "cast. Five states are built. Roll, cast and the second and "
                "third combo steps are not, and are named here rather than "
                "left looking forgotten."),
    dict(id="hurt-animation", status="planned",
         reason="Damage changes a number and plays a sound; no clip. Adding "
                "one would mean a sixth state and an interrupt rule for it, "
                "which is a later assignment."),
    dict(id="menus-pause-and-settings", status="planned",
         reason="The slice boots straight into the room. There is no menu, no "
                "pause and no settings screen; F9 toggles vsync and prints to "
                "the console, which is a debug key rather than a setting."),
]


def lines_of(rel: str, start: int, end: int) -> str:
    rows = (ROOT / rel).read_text(encoding="utf-8").split("\n")
    if not (1 <= start <= end <= len(rows)):
        raise SystemExit("%s: %d-%d is outside 1..%d" % (rel, start, end, len(rows)))
    return "\n".join(rows[start - 1:end])


def footage(bid, act, note, narration, take, window, show):
    """A gameplay beat. `window` is [start, end] in the take's own seconds and
    is **the real action at normal speed**.

    The narration may be longer than the action, and when it is,
    `build_media_clips.py` writes a `hold_s` and the compositor holds the
    final frame. That is the mechanism the skill asks for in those words --
    *"extend a labeled final-frame hold if additional narration time is
    needed, not the action"* -- and it is the opposite of the rule Assignment
    7's film worked to, where a hold was a defect to design out. The
    difference is what the shot is OF: there the window was the subject, here
    the subject is a feature and the window is the moment it happens.
    """
    return {
        "beat_id": bid,
        "act": act,
        "role_note": note,
        "narration_text": narration,
        "voice": "am_onyx",
        "engine": "kokoro",
        "estimated_duration_s": 1.0,
        "shot": {
            "type": "FOOTAGE",
            "class": "SHOW",
            "source": "capture",
            "motion": "gameplay",
            "capture": "take-" + take,
            "evidence_media": "capture/take-%s.mp4" % take,
            "window_s": list(window),
            "hold_label":
                "FINAL FRAME HELD - the action above plays once, at speed",
            "show": show,
        },
    }


def graphic(bid, act, note, narration, pattern, props, motion, show):
    return {
        "beat_id": bid, "act": act, "role_note": note,
        "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
        "estimated_duration_s": 1.0,
        "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
                 "motion": motion, "show": show,
                 "remotion": {"pattern": pattern, "props": props}},
    }


def still(bid, act, note, narration, media, title, path, label, show):
    return {
        "beat_id": bid, "act": act, "role_note": note,
        "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
        "estimated_duration_s": 1.0,
        "shot": {"type": "STILL", "class": "SHOW", "source": "capture",
                 "motion": "hold", "evidence_media": media, "title": title,
                 "path": path, "image_label": label, "show": show},
    }


def beats():
    out = []

    out.append(graphic(
        "B00", "ASK",
        "WALKER BOOKEND 1/4 - ClaudeComposerAsk. The prompt is a "
        "reconstruction and is said aloud to be one.",
        "Sawubona - this is Liam, in for Bear. The prompt on screen is a "
        "reconstruction, written to be illustrative. It was never sent. What "
        "it describes is real: The Lost, a side-view dungeon slice in Godot "
        "four, where every hazard announces itself before it can hurt you. We "
        "are going to play all of it - every state the character can be in, "
        "every animation, and the edges where two things are asked for at "
        "once.",
        "ClaudeComposerAsk",
        {"greeting": "Sawubona, Liam", "topic": TOPIC,
         "segment": "The Lost, played",
         "command": (
             "Please use Walker to convert my game design document about The "
             "Lost - a side-view dungeon crawler where every hazard announces "
             "itself before it can hurt you, and where attacking is a "
             "commitment you cannot take back - into a playable Godot "
             "project. One room, three spike traps, a character who runs, "
             "jumps and swings. Build the states and the checks; the verdict "
             "on how it feels is mine."),
         "runningText": "RECONSTRUCTION - this prompt was never sent",
         "modelLabel": "Claude Opus 5", "effortLabel": "High"},
        "type-on",
        [{"at": 0.03, "event": "composer card fades in"},
         {"at": 0.14, "event": "greeting lands"},
         {"at": 0.32, "event": "the Walker prompt types on"},
         {"at": 0.82, "event": "RECONSTRUCTION label holds"}]))

    out.append(graphic(
        "B01", "RESULT",
        "WALKER BOOKEND 2/4 - what was built, in plain language, with the "
        "slice's limits rather than the GDD's promises.",
        "Here is what actually exists. One room, three spike traps, and a "
        "character with five animation states: resting, running, in the air, "
        "swinging, and dead. Three animations behind them - a looping run "
        "cycle on a cut-out rig, a sword swing on a sprite sheet, and a "
        "floating key that bobs and turns and is the only thing here that "
        "needs nobody to do anything. Now the limits, and they are real - "
        "correction - and they are not small. The hitbox hits nothing, "
        "because this room has no enemy. There is no respawn. There is no "
        "menu. Three hundred automated checks stand behind what is here, and "
        "not one of them can tell you whether it reads.",
        "BrutalistHesitantWriter",
        {"text": ("One room. Three traps.\n"
                  "Five states, three animations.\n"
                  "300 checks, 7 mutations.\n"
                  "No enemy. No respawn. No menu."),
         "triggerWords": "real", "replacementWords": "not small",
         "charMs": 16, "face": "serif", "fontSize": 60, "lineSpacing": 1.35,
         "align": "left", "contextTitle": "The slice",
         "brandLabel": "@NikBearBrown",
         "contextItems": [
             {"label": "Built",
              "detail": "5 states, 3 animations, 1 committing action."},
             {"label": "Not built",
              "detail": "Enemies, respawn, menus, roll, cast."},
             {"label": "Judged by playing",
              "detail": "Every tuning verdict is the author's."}]},
        "write-on",
        [{"at": 0.06, "event": "the summary begins writing"},
         {"at": 0.42, "event": "'real' struck through, 'not small' written in"},
         {"at": 0.80, "event": "the limits land"}]))

    out.append(footage(
        "B02", "BUILD", "take-a, SCRIPTED INPUT. Idle, held.",
        "We start where the game starts: dropped into the room, with no key "
        "down. This is the idle state, and it is a single held frame rather "
        "than a clip. That costs nothing and it cannot breathe - the "
        "character stands perfectly still, and a player reads that as waiting "
        "rather than as alive. It is the cheapest of the five states and the "
        "one with the least to say.",
        "a", (1.30, 2.10),
        [{"at": 0.10, "event": "the fall settles"},
         {"at": 0.50, "event": "idle holds"}]))

    out.append(footage(
        "B03", "BUILD",
        "take-a, SCRIPTED INPUT. The run cycle, both facings, and the dust "
        "that shares its clock.",
        "Hold a direction and the run cycle starts. Two cut-out legs, half a "
        "second a cycle, and that half second is not a taste decision - it is "
        "two strides at twenty-four pixels against a speed of ninety-six "
        "pixels a second. Watch the dust: a puff every twenty-four pixels "
        "travelled, which is the same number, so the puff and the footfall "
        "are the same event. Now the turn. The whole rig mirrors - legs and "
        "sword arm together - because facing is one scale flip on the rig "
        "root rather than a property of the animation. One set of keys is "
        "correct both ways round, and that is also why a turn in the middle "
        "of a swing is forbidden.",
        "a", (2.20, 4.60),
        [{"at": 0.08, "event": "the cycle starts"},
         {"at": 0.40, "event": "dust under the planted foot"},
         {"at": 0.70, "event": "the turn, and the mirrored gait"}]))

    out.append(footage(
        "B04", "BUILD", "take-a, SCRIPTED INPUT. Rising and falling.",
        "Space, and two more states for one key. Rising while the vertical "
        "velocity is negative, falling the moment it is not. The split is the "
        "sign of a number, which means the character reads as committed to "
        "the arc before it has reached the top of it - and the landing is a "
        "state change the player never asked for.",
        "a", (5.10, 6.60),
        [{"at": 0.12, "event": "leaves the floor"},
         {"at": 0.45, "event": "rising becomes falling"},
         {"at": 0.80, "event": "the landing"}]))

    out.append(footage(
        "B05", "BUILD",
        "take-a, SCRIPTED INPUT. The simple animation, running behind "
        "everything else.",
        "And the thing that has been looping behind all of this. A key, "
        "between the first two traps: one sprite, two tracks, no rig and no "
        "frames. It bobs three pixels and turns one full revolution every two "
        "point four seconds, it autoplays so nothing has to remember to start "
        "it, and nothing collects it. It is decorative, and saying that out "
        "loud matters - a key in a dungeon implies a door, and there is no "
        "door.",
        "a", (0.20, 3.00),
        [{"at": 0.15, "event": "the key, bobbing"},
         {"at": 0.55, "event": "a full turn"},
         {"at": 0.85, "event": "nothing collects it"}]))

    out.append(footage(
        "B06", "BUILD",
        "take-b, SCRIPTED INPUT. The committing action, all eighteen frames.",
        "The core action. One press plays eighteen frames at thirty: a "
        "wind-up, a strike, a recovery. Watch the wind-up end - the arm "
        "nearly stops. Ten degrees in the two frames before the window opens, "
        "then a hundred and fifty in the next four. That pause is what makes "
        "it read as a strike rather than a gesture. And once it starts, it "
        "finishes: no input shortens it. You can walk out of this swing, and "
        "you can jump out of it, but you cannot cancel it and you cannot turn "
        "it around.",
        "b", (1.00, 1.80),
        [{"at": 0.15, "event": "the wind-up"},
         {"at": 0.45, "event": "the strike"},
         {"at": 0.78, "event": "recovery, and the blade sheathes"}]))

    out.append(footage(
        "B07", "BUILD",
        "take-b, SCRIPTED INPUT. The edge the assignment names: an action "
        "requested during another action, twice, with the two answers.",
        "Now the edge. An action asked for while another action is running - "
        "and this game gives two different answers depending on when. Here is "
        "the first: a second attack one tenth of a second in, inside the "
        "startup. Nothing happens. The swing counter does not move. And here "
        "is the second: a press four and a half tenths in, inside the "
        "recovery - that one is buffered, and a fresh swing starts the moment "
        "the first one ends. Same key, same clip, opposite answer, and the "
        "only difference is where the playhead was. The uncomfortable part is "
        "that the first one would pass by accident: calling play with the "
        "name already playing does nothing at all. The code reads the "
        "playhead instead, so it is a decision rather than a side effect.",
        "b", (2.20, 5.30),
        [{"at": 0.18, "event": "the press in startup - ignored"},
         {"at": 0.55, "event": "the press in recovery"},
         {"at": 0.82, "event": "the buffered swing plays"}]))

    out.append(footage(
        "B08", "BUILD",
        "take-c, SCRIPTED INPUT. Two revisions the author asked for after "
        "playing.",
        "Two more things, both of which exist because the author played an "
        "earlier version and said it was wrong. First: a direction held "
        "through a swing. The character travels and the gait keeps running "
        "underneath, because the legs have their own animation player and "
        "never hear that a sword exists. Second: a jump, mid-swing. The "
        "player leaves the floor and the swing carries on from exactly where "
        "it was, ending on its own clock. It cannot interrupt, and the reason "
        "is structural rather than careful - that branch writes one field, "
        "the vertical velocity, and there is no path from it to the clip.",
        "c", (1.00, 4.80),
        [{"at": 0.12, "event": "a swing that travels"},
         {"at": 0.45, "event": "the gait continues under it"},
         {"at": 0.78, "event": "and one jumped out of"}]))

    out.append(footage(
        "B09", "BUILD",
        "take-d, SCRIPTED INPUT. The hazard, and what damage does not do.",
        "The hazard, and the reason the whole game is built around warnings. "
        "The trap lights its band, waits four tenths of a second, and fires. "
        "Four tenths against a swing's two-tenth wind-up is the whole reason "
        "you can read a trap and still choose to attack near it. And watch "
        "what the hit does to the animation: nothing. Damage is a number "
        "here, not a state. There is no hurt clip, no stagger, no "
        "invulnerability - which is a limit rather than a decision, and the "
        "brief lists it as one.",
        "d", (1.80, 3.60),
        [{"at": 0.15, "event": "the warning band"},
         {"at": 0.45, "event": "the spikes, and the grit"},
         {"at": 0.80, "event": "the hit changes no state"}]))

    out.append(footage(
        "B10", "RESULT",
        "take-d, SCRIPTED INPUT. The fifth state, and the end of the slice.",
        "Five hits, and the fifth state - the only one of the five that no "
        "key can reach. It is entered by a game condition that a player "
        "action caused, which is exactly the shape the assignment asks for. "
        "The dead cell plays once and holds. And then nothing: there is no "
        "respawn in this slice, no retry key, no reload. The film shows that "
        "rather than cutting away before the question comes up.",
        "d", (9.60, 12.90),
        [{"at": 0.20, "event": "the fatal hit"},
         {"at": 0.55, "event": "the dead cell holds"},
         {"at": 0.85, "event": "and nothing follows it"}]))

    out.append(still(
        "B11", "RESULT",
        "CAUSE AND EFFECT, before and after. Two captures of the SAME preview "
        "fixture at the same table frame, from revision r1 and the shipped "
        "r4, beside the key table that changed between them.",
        "One cause and effect, because the assignment asks for one and this "
        "is the clearest in the project. On the left, the swing as it first "
        "shipped. The author played it and said: the sword is not swinging "
        "out, it is spinning in circles above the body. On the right, the "
        "same frame after the change - the rotation keys stopped reversing "
        "direction, and the pivot became part of the animation instead of a "
        "constant in the scene. What is worth saying is that the defect was "
        "in the numbers the whole time. The tip is never below minus three "
        "pixels in any of the eighteen frames of the first version. That is "
        "the range of a function over a key table, not an impression - and no "
        "check was asking, because nobody had thought to ask it.",
        "media/B11.png", "One change, and what the player saw",
        "captures/swing/r1 and r4, same table frame",
        "preview-fixture captures, cropped and not otherwise altered",
        [{"at": 0.10, "event": "before"},
         {"at": 0.40, "event": "after"},
         {"at": 0.75, "event": "the key table that changed"}]))

    out.append(graphic(
        "B12", "VERDICT",
        "WALKER BOOKEND 3/4 - Verdict. Observed working features, then "
        "defects, untested claims and planned work, kept apart.",
        "The verdict, and it comes in three parts because they are three "
        "different kinds of thing. Observed working, in the footage you just "
        "watched: five states each entered by its own input or by a condition "
        "an input caused, three animations, a committing action with two "
        "different interrupt answers, and a cycle that wraps without a seam. "
        "Checked but not watchable: three hundred automated checks and seven "
        "deliberate breakages, including the one that proves a jump does not "
        "disturb the swing's clock - the same swing run twice and compared "
        "frame by frame, agreeing to zero. Not built, and named rather than "
        "implied: no enemy, so the hitbox hits nothing; no respawn; no menu; "
        "no hurt animation; no roll and no cast. And one thing still open - "
        "whether a braced stance hanging in mid-air reads at all. Nobody has "
        "judged that yet, and no test can.",
        "ClaudeVerdictArtifact",
        {"artifactTitle": "Verdict",
         "artifactHeading": "Observed, checked, and not built",
         "artifactLines": [
             "OBSERVED: 5 states, each from its own input or condition.",
             "OBSERVED: 3 animations; the cycle wraps without a seam.",
             "OBSERVED: attack-in-startup ignored, in-recovery buffered.",
             "CHECKED: 300 checks, 7 mutations, 0 failures.",
             "CHECKED: a jump does not move the swing's clock. 0.000000 s.",
             "NOT BUILT: no enemy, no respawn, no menu, no hurt clip.",
             "NOT BUILT: roll and cast, from the GDD's state list.",
             "OPEN: does a braced stance read in mid-air? Unjudged."],
         "brandLabel": "@NikBearBrown"},
        "artifact-reveal",
        [{"at": 0.06, "event": "the artifact opens"},
         {"at": 0.35, "event": "observed"},
         {"at": 0.62, "event": "checked"},
         {"at": 0.88, "event": "not built, and the open question"}]))

    out.append(graphic(
        "B13", "TURN",
        "WALKER BOOKEND 4/4 - Your Turn. One concrete experiment, and Liam "
        "signs off here, before the final card.",
        "Your turn, and make it one thing. Take the game you are building and "
        "find its committing action - the move that cannot be taken back. "
        "Then press its own button again, halfway through, and find out what "
        "happens. Not what you intended: what happens. In this project the "
        "answer during the startup was nothing at all, and nothing at all is "
        "also what a completely unwired version would have done. The two look "
        "identical from outside, and the only way to tell them apart is to "
        "ask the clip where its playhead was. That is Liam, in for Bear. "
        "Thanks for watching.",
        "ClaudeComposerAsk",
        {"greeting": "Your turn", "topic": TOPIC,
         "segment": "One concrete experiment",
         "command": (
             "Find the committing action in your own game. Press its button "
             "again halfway through and record what happens, with the clip's "
             "playhead logged. Then decide whether that answer is the one you "
             "want - and if it is, write the check that would fail if it "
             "silently changed."),
         "runningText": "A thing that does nothing looks exactly like a thing "
                        "that is not wired up",
         "modelLabel": "Claude Opus 5", "effortLabel": "High"},
        "type-on",
        [{"at": 0.05, "event": "the turn card opens"},
         {"at": 0.40, "event": "the experiment types on"},
         {"at": 0.86, "event": "Liam signs off"}]))

    out.append({
        "beat_id": "B14", "act": "OUTRO",
        "role_note": "LOCKED ClaudeTitleOutro. Exact title, @NikBearBrown, no "
                     "narration, no gameplay audio - OUTRO-LOCK.md.",
        "narration_text": "", "voice": "am_onyx", "engine": "kokoro",
        "audio_policy": "silence", "estimated_duration_s": 5,
        "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
                 "motion": "hold",
                 "show": [{"at": 0.10, "event": "the locked outro holds"}],
                 "remotion": {"pattern": "ClaudeTitleOutro",
                              "props": {"title": TITLE,
                                        "channel": "@NikBearBrown",
                                        "durationSeconds": 5}}},
    })
    return out


def main() -> int:
    REEL.mkdir(parents=True, exist_ok=True)
    path = REEL / "beat_sheet.json"

    measured: dict[str, float] = {}
    previous: dict[str, dict] = {}
    if path.is_file():
        old = json.load(io.open(path, encoding="utf-8"))
        for b in old.get("beats", []):
            rem = b.get("shot", {}).get("remotion")
            if rem and rem.get("props") is not None:
                carried = dict(rem["props"])
                if rem.get("rendered"):
                    carried["rendered"] = rem["rendered"]
                previous[b["beat_id"]] = carried
            if b.get("actual_duration_s"):
                measured[b["beat_id"]] = float(b["actual_duration_s"])

    takes = {}
    for mp4 in sorted((REEL / "capture").glob("take-*.mp4")):
        takes[mp4.stem] = probe_seconds(mp4)
    if not takes:
        raise SystemExit("no take-*.mp4 in %s -- render them first"
                         % (REEL / "capture"))

    sheet_beats = []
    for b in beats():
        bid = b["beat_id"]
        words = len(b["narration_text"].split())
        if words:
            b["estimated_duration_s"] = round(words / WORDS_PER_SECOND, 1)
        seconds = measured.get(bid, float(b["estimated_duration_s"]))

        take = b["shot"].get("capture")
        if take is not None:
            if take not in takes:
                raise SystemExit("%s names %s, which is not in capture/"
                                 % (bid, take))
            start, end = (float(v) for v in b["shot"]["window_s"])
            if end > takes[take] + 0.001:
                raise SystemExit(
                    "%s's window ends at %.2f s but %s is %.2f s long"
                    % (bid, end, take, takes[take]))
            action = end - start
            hold = max(0.0, seconds - action)
            print("  %-5s %-7s %5.2f-%5.2f of %5.2f s   action %4.2f s  "
                  "narration %5.2f s  hold %4.2f s"
                  % (bid, take, start, end, takes[take], action, seconds,
                     hold))
        props = b["shot"].get("remotion", {}).get("props")
        if props is not None:
            props["durationSeconds"] = round(seconds, 2)
            was = previous.get(bid)
            if was is not None:
                stamp = was.pop("rendered", None)
                if stamp is not None and was == props:
                    b["shot"]["remotion"]["rendered"] = stamp
        for mark in b["shot"].get("show", []) or []:
            mark["at"] = "%.2f" % float(mark["at"])
        if bid in measured:
            b["actual_duration_s"] = round(seconds, 2)
            if (REEL / "mp3" / ("beat-%s.mp3" % bid)).is_file():
                b["audio_file"] = "mp3/beat-%s.mp3" % bid
            else:
                b.pop("audio_file", None)
        sheet_beats.append(b)

    sheet = {
        "metadata": {
            "title": TITLE, "slug": SLUG, "topic": TOPIC,
            "kind": "walkthrough", "playlist": "Brutalist",
            "brand": "claude-liam",
            "audience":
                "Course reviewers watching an animation-and-state pass played",
            "register": "Walkthrough", "engine": "kokoro", "voice": "am_onyx",
            "voice_kokoro": "am_onyx", "palette": "claude",
            "style_preset": "claude", "ground": "#FAF9F5",
            "aspect_ratio": "16:9", "fit": "contain", "captions": False,
            "channel_title": "@NikBearBrown", "channel": "@NikBearBrown",
            "folderLabel": "@NikBearBrown", "greeting": "Sawubona, Liam",
            "greeting_note": "hello lexicon: Sawubona (Zulu), one word.",
            "mode": "walker", "game": "godot",
        },
        "beats": sheet_beats,
    }
    io.open(path, "w", encoding="utf-8", newline="\n").write(
        json.dumps(sheet, ensure_ascii=False, indent=2) + "\n")

    # ---- coverage.json, from the same table ------------------------------
    snap = json.load(io.open(REEL / "SOURCE-SNAPSHOT.json", encoding="utf-8"))
    build_id = snap["build_id"]
    by_id = {b["beat_id"]: b for b in sheet_beats}

    captures = {}
    for mp4 in sorted((REEL / "capture").glob("take-*.mp4")):
        log = REEL / "capture" / (mp4.stem + "-inputs.jsonl")
        if not log.is_file():
            raise SystemExit("no input log beside %s" % mp4.name)
        captures[mp4.stem] = {
            "path": "capture/%s" % mp4.name,
            "sha256": sha(mp4),
            "build_id": build_id,
            "method": "scripted-input",
            "input_log": "capture/%s" % log.name,
        }

    features = []
    for f in FEATURES:
        if f.get("status") == "planned":
            features.append({"id": f["id"], "status": "planned",
                             "reason": f["reason"], "evidence": []})
            continue
        bid = f["beat"]
        if bid not in by_id:
            raise SystemExit("%s names beat %s, which does not exist"
                             % (f["id"], bid))
        if not by_id[bid]["narration_text"].strip():
            raise SystemExit("%s names beat %s, which has no narration"
                             % (f["id"], bid))
        take = "take-" + f["take"]
        if take not in captures:
            raise SystemExit("%s names %s" % (f["id"], take))
        s, a, e = f["window"]
        if not (0 <= s <= a <= e <= takes[take] + 0.001):
            raise SystemExit("%s: window %s is not inside %s (%.2f s)"
                             % (f["id"], f["window"], take, takes[take]))
        features.append({
            "id": f["id"], "status": "implemented",
            "evidence": [{"capture": take, "beat_id": bid,
                          "start_s": s, "action_s": a, "end_s": e,
                          "observation": f["obs"], "riff": f["riff"]}],
        })

    coverage = {
        "schema_version": 1,
        "game": {"name": "walker-the-lost-TiantongZhang",
                 "build_id": build_id},
        "captures": captures,
        "features": features,
    }
    io.open(REEL / "coverage.json", "w", encoding="utf-8",
            newline="\n").write(
        json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

    total = sum(float(b.get("actual_duration_s") or b["estimated_duration_s"])
                for b in sheet_beats)
    impl = sum(1 for f in features if f["status"] == "implemented")
    plan = len(features) - impl
    print("wrote %s" % path)
    print("  %d beats, %s %.1f s (%d:%02d)"
          % (len(sheet_beats), "measured" if measured else "estimated",
             total, total // 60, total % 60))
    print("wrote %s" % (REEL / "coverage.json"))
    print("  %d captures, %d implemented feature(s), %d planned"
          % (len(captures), impl, plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
