#!/usr/bin/env python3
"""Write Assignment 8's walkthrough beat sheet AND its coverage contract.

    python -X utf8 scripts/build_walkthrough_reel.py

**One script, two files, one source of truth.** `coverage.json` names beat
ids and `beat_sheet.json` names captures; authored separately they would
drift, and the checker would catch the drift rather than the mistake. Here
each feature carries both its evidence window and the beat that shows it,
and the two files are projections of the same table.

Run it twice, like every beat sheet in this repository: the first pass gives
`generate_audio_kokoro.py` something to measure, the second re-authors
against the measured narration. There is no third pass -- `BUILD-PROMPT.md`
says why.

## The thing this file got wrong twice, and what it cost

**A walkthrough's body has to be mostly moving.** The first cut made each
take a few seconds -- the moment a feature happens -- and the beats carried
nineteen to thirty-four seconds of FROZEN FINAL FRAME apiece. The takes were
re-recorded four times longer.

**That was not enough, because the narration was still four times the
footage.** Fifteen beats of explanation against eighty-six seconds of play
is a slideshow with gameplay in it. So the gameplay body is SIX beats, each
playing a long continuous stretch of one take, with the narration sized to
the action rather than the other way round.

The rule used here, and it is worth stating because the temptation runs the
other way all day: **narration is allowed to be about fifteen per cent
longer than its window, and no more.** The remainder is a labelled
final-frame hold, which is the mechanism the skill asks for -- and a hold
that is a fifth of a beat is a breath, while a hold that is five times the
action is a still with a voice over it.
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
# **Shortened on 2026-11-22 because Gate V refused the locked outro.**
# "TheLostWalkthrough_TiantongZhang" is 32 characters and its last glyphs
# crossed the title-safe right edge; the other reel's 30-character title
# clears it. The outro card is LOCKED -- its layout, mascot and handle are
# not mine to move -- but the episode title IS mine, so that is what gave.
# 27 characters, still distinct from the other film, still carrying the
# student name the course wants in the filename.
TITLE = "TheLostPlayed_TiantongZhang"
TOPIC = "WALKER - THE LOST, PLAYED"

# Kokoro's measured rate, from Assignment 7's finished sheet: 2277 narrated
# words across 570.3 s. The first pass only needs plausible windows.
WORDS_PER_SECOND = 3.53

# **The guard is on the HOLD, not on the ratio.** The first version capped
# narration at 1.15x its action, and that is the wrong shape: 1.15x of a
# sixty-second beat is a nine-second frozen frame, while 1.3x of a six-second
# beat is under two. What a viewer notices is the absolute length of the
# still, so that is what is bounded -- with a proportional cap as well, so a
# short beat cannot be mostly hold.
# A third shape, and the last. 0.30 flagged two beats whose holds were 2.8
# and 3.2 seconds -- short enough that nobody would notice, on actions short
# enough that the percentage was large. The rule that survives contact with
# the measured numbers is: **a hold is never longer than five seconds, and
# never longer than the action it follows.** Both halves are needed; the
# first alone would allow four seconds of still after four seconds of play.
MAX_HOLD_S = 5.0


def probe_seconds(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# THE FEATURE TABLE. `window` is [start, action, end] in the CAPTURE's own
# seconds, and every one of these times was READ OFF THE TAKE'S LOG -- the
# frame a clip became current, the frame a facing flipped, the frame health
# dropped -- rather than counted forward from the driver's own sleeps.
#
# An implemented feature with no evidence makes the check FAIL, which is what
# the skill asks for: a built feature that is not shown prevents the
# complete-walkthrough claim, and relabelling it `planned` to pass is named
# in the reference as the thing not to do.
# ---------------------------------------------------------------------------
FEATURES = [
    dict(id="idle-at-rest", beat="B02", take="a", window=(0.30, 1.00, 3.00),
         obs="The player settles on the floor at 0.25 s and holds the idle "
             "cell for two and three quarter seconds with no key down.",
         riff="Idle is a held frame rather than a clip. It costs nothing and "
              "it cannot breathe -- the character stands perfectly still, and "
              "a player reads that as waiting rather than as alive."),
    dict(id="run-cycle-loops", beat="B02", take="a", window=(3.03, 4.00, 10.88),
         obs="Four held runs between x 10 and x 174; the cut-out legs "
             "alternate and the cycle wraps eighteen times across the take.",
         riff="Half a second a cycle is not taste -- it is two strides at "
              "twenty-four pixels against ninety-six pixels a second. Retime "
              "the run and that arithmetic changes first, not the keys."),
    dict(id="facing-mirrors-the-rig", beat="B02", take="a",
         window=(3.93, 4.53, 7.00),
         obs="The facing flips at 4.53 s; the whole rig mirrors -- legs and "
             "sword arm together -- and the gait keeps alternating.",
         riff="Facing is one scale flip on the rig root, not a property of "
              "the animation, which is why one set of keys is correct both "
              "ways and why a mid-swing turn is forbidden."),
    dict(id="step-dust-on-the-footfall", beat="B02", take="a",
         window=(4.53, 5.20, 6.25),
         obs="A puff of dust is left every twenty-four pixels travelled, "
             "under the planted foot.",
         riff="The dust is driven by distance and the cycle's length was "
              "derived from the same distance. They agree because they were "
              "made to; nothing enforces it at runtime."),
    dict(id="jump-rising-and-falling", beat="B03", take="a",
         window=(11.20, 11.68, 12.60),
         obs="Space at 11.68 s leaves the floor on the next physics frame; "
             "`rising` holds until 11.98 s, then `falling` until the landing "
             "at 12.27 s.",
         riff="Two states for one key, split on the sign of the vertical "
              "velocity -- so the character reads as committed to the arc "
              "before it has reached the top of it."),
    dict(id="jump-while-running", beat="B03", take="a",
         window=(13.10, 14.30, 15.00),
         obs="A jump taken at speed: `run` at 13.10 s, `rising` at 14.30 s, "
             "`falling` at 14.60 s, and back to `run` on the landing.",
         riff="The horizontal velocity is carried straight through the arc. "
              "Nothing about the jump touches it, which is why a running "
              "jump feels like one movement rather than two."),
    dict(id="floating-key-simple-animation", beat="B03", take="a",
         window=(20.15, 21.50, 26.10),
         obs="The key between the first two traps bobs three pixels and "
             "turns one full revolution every 2.4 s, with no input and "
             "nothing driving it.",
         riff="One sprite, two tracks, no rig and no frames. It autoplays, so "
              "nothing has to remember to start it -- and nothing collects "
              "it, which the brief says out loud rather than letting a key in "
              "a dungeon imply a door."),
    dict(id="swing-three-phases", beat="B04", take="b", window=(1.42, 1.60, 2.02),
         obs="One press plays all eighteen frames: `swing` at 1.42 s, back to "
             "`idle` at 2.02 s -- 0.600 s exactly.",
         riff="The arm nearly stops before it goes: ten degrees in the two "
              "frames before the window opens, then a hundred and fifty in "
              "four. That pause is what makes it read as a strike."),
    dict(id="swing-commits", beat="B04", take="b", window=(3.05, 3.30, 5.48),
         obs="Three separate presses, three clips, each exactly 0.600 s. No "
             "input shortens one.",
         riff="Committing is not freezing the player. You can walk out of "
              "this swing and jump out of it; what you cannot do is cancel it "
              "or turn it around."),
    dict(id="attack-during-attack-ignored", beat="B05", take="b",
         window=(7.25, 7.35, 9.00),
         obs="A swing starts at 7.25 s and a second attack is pressed 0.1 s "
             "in -- inside the 0.2 s startup. No new swing begins; the next "
             "one in the log is at 9.82 s, from a separate press.",
         riff="The uncomfortable part is that this would pass by accident: "
              "calling play with the name already playing does nothing at "
              "all. The code reads the playhead instead, so it is a decision "
              "rather than a side effect."),
    dict(id="attack-during-attack-buffered", beat="B05", take="b",
         window=(9.82, 10.42, 11.02),
         obs="A swing starts at 9.82 s; a press 0.45 s in -- inside recovery "
             "-- is buffered, and the log shows the next swing beginning at "
             "10.42 s, 0.600 s after the first.",
         riff="Same key, same clip, opposite answer, and the only difference "
              "is where the playhead was. A buffer is how a game stops "
              "punishing a player for being early."),
    dict(id="swing-while-moving", beat="B06", take="c", window=(1.32, 2.12, 3.13),
         obs="A direction is held through a swing at 2.12 s; the player "
             "travels from x 174 to x 232 with the gait running under the "
             "body cell.",
         riff="The legs have their own animation player and never hear that a "
              "sword exists, so nothing seeks them and the gait keeps its "
              "phase straight through."),
    dict(id="jump-during-swing", beat="B06", take="c", window=(7.15, 7.75, 9.00),
         obs="A swing starts at 7.15 s; space is pressed mid-clip and the "
             "player leaves the floor at 7.75 s. The swing finishes on its "
             "own clock and no new one starts.",
         riff="The jump writes one field and nothing else, so there is no "
              "path from it to the clip's clock. It cannot interrupt -- "
              "structural, rather than careful."),
    dict(id="trap-warning-then-strike", beat="B07", take="d",
         window=(1.63, 2.83, 4.20),
         obs="A trap lights its warning band, then fires at 2.83 s; health "
             "goes from 5 to 4 on that frame and grit comes off the floor.",
         riff="The warning is four tenths of a second and the swing's startup "
              "is two. That ratio is the whole reason you can read a trap and "
              "still choose to attack near it."),
    dict(id="damage-does-not-interrupt", beat="B07", take="d",
         window=(2.83, 3.15, 6.10),
         obs="Health drops at 2.83, 5.62 and 8.40 s and the animation state "
             "does not change on any of them; the player keeps walking.",
         riff="Damage is a number here, not a state. No hurt clip, no "
              "stagger, no invulnerability -- a limit rather than a decision, "
              "and the brief lists it as one."),
    dict(id="death-state", beat="B07", take="d", window=(16.83, 17.90, 25.20),
         obs="The fifth hit takes health to zero at 17.88 s; `dead` becomes "
             "current at 17.90 s and holds for the remaining seven seconds "
             "while input does nothing.",
         riff="The only one of the five states no key can reach. It is "
              "entered by a game condition that a player action caused, which "
              "is the shape the assignment asks for."),

    # --- planned, each with a reason ---------------------------------------
    dict(id="respawn-or-retry", status="planned",
         reason="There is no recovery from death in this slice: no respawn, "
                "no retry key, no reload. The film holds on the death for "
                "seven seconds rather than cutting away before the question "
                "arises."),
    dict(id="enemies", status="planned",
         reason="The swing's hitbox is real, measured, and switched by the "
                "clip's own timeline -- and it can hit NOTHING, because this "
                "room has no enemy. CHANGE-BRIEF.md section 11.3 said so "
                "before any of it was built."),
    dict(id="roll-cast-and-combo-2-3", status="planned",
         reason="GDD.md:393 lists idle / run / jump / roll / combo-1,2,3 / "
                "cast. Five states are built. Roll, cast and the second and "
                "third combo steps are not, and are named rather than left "
                "looking forgotten."),
    dict(id="hurt-animation", status="planned",
         reason="Damage changes a number and plays a sound; no clip. Adding "
                "one would mean a sixth state and an interrupt rule for it, "
                "which is a later assignment."),
    dict(id="menus-pause-and-settings", status="planned",
         reason="The slice boots straight into the room. No menu, no pause, "
                "no settings screen. F9 toggles vsync and prints to the "
                "console, which is a debug key rather than a setting."),
]


def footage(bid, act, note, narration, take, window, show):
    """A gameplay beat. `window` is [start, end] in the take's own seconds and
    is **the real action, at normal speed, uncut**."""
    return {
        "beat_id": bid, "act": act, "role_note": note,
        "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
        "estimated_duration_s": 1.0,
        "shot": {
            "type": "FOOTAGE", "class": "SHOW", "source": "capture",
            "motion": "gameplay", "capture": "take-" + take,
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
        "it describes is real: The Lost, a dungeon slice in Godot four where "
        "every hazard announces itself before it can hurt you. We are going "
        "to play all of it.",
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
         {"at": 0.16, "event": "greeting lands"},
         {"at": 0.36, "event": "the Walker prompt types on"},
         {"at": 0.84, "event": "RECONSTRUCTION label holds"}]))

    out.append(graphic(
        "B01", "RESULT",
        "WALKER BOOKEND 2/4 - what was built, in plain language, with the "
        "slice's limits rather than the GDD's promises.",
        "Here is what exists. One room, three spike traps, and a character "
        "with five animation states: resting, running, in the air, swinging, "
        "and dead. Three animations behind them - a looping run cycle on a "
        "cut-out rig, a sword swing on a sprite sheet, and a floating key "
        "that needs nobody to do anything. Now the limits, and they are real "
        "- correction - and they are not small. The hitbox hits nothing. "
        "There is no respawn and no menu. Three hundred automated checks "
        "stand behind this, and not one of them can tell you whether it "
        "reads.",
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
         {"at": 0.44, "event": "'real' struck through, 'not small' written in"},
         {"at": 0.82, "event": "the limits land"}]))

    # ---- the gameplay body: six beats, each a long continuous stretch -----
    out.append(footage(
        "B02", "BUILD",
        "take-a, SCRIPTED INPUT. Idle, the run cycle, both facings, and the "
        "dust that shares the cycle's clock. 10.6 s of continuous play.",
        "No key down: idle is a single held frame, not a clip. Now a "
        "direction. The cycle is half a second - two strides at twenty-four "
        "pixels against ninety-six a second. The dust spawns on the same "
        "twenty-four. On the turn, the whole rig mirrors.",
        "a", (0.30, 11.00),
        [{"at": 0.08, "event": "idle, held"},
         {"at": 0.32, "event": "the cycle starts"},
         {"at": 0.58, "event": "dust under the planted foot"},
         {"at": 0.80, "event": "the turn, and the mirrored gait"}]))

    out.append(footage(
        "B03", "BUILD",
        "take-a, SCRIPTED INPUT. Two more states, a running jump, and the "
        "simple animation that has been looping behind all of it. 15.2 s.",
        "Space: two states for one key, split on the sign of the vertical "
        "velocity. The same jump at speed - the horizontal velocity carries "
        "through, so it reads as one movement. And the thing turning behind "
        "all of it: a key. No rig, no frames, two tracks. It autoplays, and "
        "nothing collects it - a key in a dungeon implies a door, and there "
        "is none.",
        "a", (11.00, 26.10),
        [{"at": 0.06, "event": "rising, then falling"},
         {"at": 0.26, "event": "a jump taken at speed"},
         {"at": 0.58, "event": "the key, bobbing and turning"},
         {"at": 0.86, "event": "nothing collects it"}]))

    out.append(footage(
        "B04", "BUILD",
        "take-b, SCRIPTED INPUT. The committing action, three separate "
        "presses, each the clip's own full 0.600 s. 8.0 s.",
        "Eighteen frames at thirty: wind-up, strike, recovery. The arm "
        "nearly stops before it goes - ten degrees in two frames, then a "
        "hundred and fifty in four.",
        "b", (1.00, 7.25),
        [{"at": 0.08, "event": "the wind-up"},
         {"at": 0.22, "event": "the strike"},
         {"at": 0.45, "event": "recovery, and the blade sheathes"},
         {"at": 0.78, "event": "and again, the same 0.600 s"}]))

    out.append(footage(
        "B05", "BUILD",
        "take-b, SCRIPTED INPUT. **The edge the assignment names**: an "
        "action requested during another action, with both answers. 7.2 s.",
        "The edge: a second attack a tenth of a second in, inside the "
        "startup - nothing. Now one four and a half tenths in, inside "
        "recovery - buffered, and a fresh swing starts. Same key, opposite "
        "answer; the playhead decides.",
        "b", (7.25, 16.20),
        [{"at": 0.10, "event": "the press in startup - ignored"},
         {"at": 0.42, "event": "the press in recovery"},
         {"at": 0.62, "event": "the buffered swing plays"},
         {"at": 0.88, "event": "and once more, to show it is a rule"}]))

    out.append(footage(
        "B06", "BUILD",
        "take-c, SCRIPTED INPUT. The two revisions the author asked for "
        "after playing. 10.7 s.",
        "Two things the author asked for after playing. A direction held "
        "through a swing: the character travels and the gait keeps running "
        "underneath, because the legs have their own animation player and "
        "never hear that a sword exists. And a jump, mid-swing - the swing "
        "carries on from where it was. It cannot interrupt: that branch "
        "writes one field, and there is no path from it to the clip's clock.",
        "c", (1.32, 18.20),
        [{"at": 0.08, "event": "a swing that travels"},
         {"at": 0.26, "event": "the gait continues under it"},
         {"at": 0.58, "event": "a swing jumped out of"},
         {"at": 0.84, "event": "and one taken at speed"}]))

    out.append(footage(
        "B07", "RESULT",
        "take-d, SCRIPTED INPUT. The hazard, what damage does not do, and "
        "the fifth state. 16.9 s, ending on the held death pose.",
        "The hazard. The trap lights its band, waits four tenths of a "
        "second, and fires - four tenths against a swing's two-tenth "
        "wind-up, which is why you can read a trap and still attack near it. "
        "Watch what the hit does to the animation: nothing. Damage is a "
        "number here, not a state. No hurt clip, no invulnerability - a "
        "limit, not a decision. Five hits kill, and the fifth state is the "
        "only one no key can reach: a condition a player action caused. The "
        "dead cell plays once and holds. Then nothing - no respawn, no "
        "retry.",
        "d", (1.63, 25.20),
        [{"at": 0.06, "event": "the warning band"},
         {"at": 0.16, "event": "the spikes, and the grit"},
         {"at": 0.34, "event": "the hit changes no state"},
         {"at": 0.74, "event": "the fifth hit"},
         {"at": 0.88, "event": "dead, and held"}]))

    out.append(still(
        "B08", "RESULT",
        "CAUSE AND EFFECT, before and after. The same preview fixture at the "
        "same table frame, from revision r1 and the shipped r4.",
        "One cause and effect, because the assignment asks for one. On the "
        "left, the swing as it first shipped. The author played it and said: "
        "the sword is not swinging out, it is spinning in circles above the "
        "body. On the right, the same frame after the change - the rotation "
        "keys stopped reversing direction and the pivot became part of the "
        "animation instead of a constant in the scene. What is worth saying "
        "is that the defect was in the numbers the whole time. In the first "
        "version the blade's tip is never below minus three pixels in any of "
        "the eighteen frames. That is the range of a function over a key "
        "table, not an impression - and no check was asking, because nobody "
        "had thought to ask it.",
        "media/B08.png", "One change, and what the player saw",
        "captures/swing/r1 and r4, same table frame",
        "preview-fixture captures, cropped and not otherwise altered",
        [{"at": 0.08, "event": "before"},
         {"at": 0.36, "event": "after"},
         {"at": 0.70, "event": "the number that was there all along"}]))

    out.append(graphic(
        "B09", "VERDICT",
        "WALKER BOOKEND 3/4 - Verdict. Observed, checked, and not built, "
        "kept apart.",
        "The verdict, in three parts, because they are three different kinds "
        "of thing. Observed working, in the footage you just watched: five "
        "states each entered by its own input or by a condition an input "
        "caused, three animations, a committing action with two different "
        "interrupt answers, and a cycle that wraps without a seam. Checked "
        "but not watchable: three hundred automated checks and seven "
        "deliberate breakages, including the one that shows a jump does not "
        "move the swing's clock - the same swing run twice and compared frame "
        "by frame, agreeing to zero. Not built, and named rather than "
        "implied: no enemy, so the hitbox hits nothing; no respawn; no menu; "
        "no hurt animation; no roll and no cast. And one thing still open: "
        "whether a braced stance hanging in mid-air reads at all. Nobody has "
        "judged that, and no test can.",
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
         {"at": 0.32, "event": "observed"},
         {"at": 0.58, "event": "checked"},
         {"at": 0.86, "event": "not built, and the open question"}]))

    out.append(graphic(
        "B10", "TURN",
        "WALKER BOOKEND 4/4 - Your Turn. One concrete experiment. Liam signs "
        "off here, before the final card.",
        "Your turn, and make it one thing. Find the committing action in the "
        "game you are building - the move that cannot be taken back. Press "
        "its own button again, halfway through, and record what happens. Not "
        "what you intended: what happens. In this project the answer during "
        "the startup was nothing at all - and nothing at all is also what a "
        "completely unwired version would have done. The two look identical "
        "from outside, and the only way to tell them apart is to ask the clip "
        "where its playhead was. That is Liam, in for Bear. Thanks for "
        "watching.",
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
         {"at": 0.38, "event": "the experiment types on"},
         {"at": 0.88, "event": "Liam signs off"}]))

    out.append({
        "beat_id": "B11", "act": "OUTRO",
        "role_note": "LOCKED ClaudeTitleOutro. Exact title, @NikBearBrown, no "
                     "narration and no gameplay audio - OUTRO-LOCK.md.",
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

    sheet_beats, long_beats = [], []
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
            flag = ""
            if hold > MAX_HOLD_S or hold > action:
                flag = "  LONG"
                long_beats.append((bid, seconds, action, hold))
            print("  %-5s %-7s %5.2f-%5.2f of %5.2f s   action %5.2f s  "
                  "narration %5.2f s  hold %4.2f s%s"
                  % (bid, take, start, end, takes[take], action, seconds,
                     hold, flag))
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
            "path": "capture/%s" % mp4.name, "sha256": sha(mp4),
            "build_id": build_id, "method": "scripted-input",
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
        # **The evidence window has to be inside the beat that shows it.**
        # A feature whose moment falls outside its own beat's window is
        # pointing a reviewer at footage the film never plays.
        bs, be = (float(v) for v in by_id[bid]["shot"]["window_s"])
        if not (bs - 0.001 <= s and e <= be + 0.001):
            raise SystemExit(
                "%s: evidence %.2f-%.2f s is outside %s's window %.2f-%.2f s"
                % (f["id"], s, e, bid, bs, be))
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
        "captures": captures, "features": features,
    }
    io.open(REEL / "coverage.json", "w", encoding="utf-8",
            newline="\n").write(
        json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

    total = sum(float(b.get("actual_duration_s") or b["estimated_duration_s"])
                for b in sheet_beats)
    action = sum(float(b["shot"]["window_s"][1]) - float(b["shot"]["window_s"][0])
                 for b in sheet_beats if b["shot"].get("capture"))
    impl = sum(1 for f in features if f["status"] == "implemented")
    print("wrote %s" % path)
    print("  %d beats, %s %.1f s (%d:%02d); %.1f s of it is moving gameplay"
          % (len(sheet_beats), "measured" if measured else "estimated",
             total, total // 60, total % 60, action))
    print("wrote %s" % (REEL / "coverage.json"))
    print("  %d captures, %d implemented, %d planned"
          % (len(captures), impl, len(features) - impl))
    if long_beats:
        print("")
        print("  %d beat(s) hold a frozen frame for more than %.1f s, or "
              "longer than the action it follows:" % (len(long_beats), MAX_HOLD_S))
        for bid, sec, act, hold in long_beats:
            print("    %s  %.1f s hold after %.1f s of action (%.0f%%)"
                  % (bid, hold, act, 100.0 * hold / act))
        print("  Cut the narration. Do not extend the window to cover it:")
        print("  the window is the action, and the action is the evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
