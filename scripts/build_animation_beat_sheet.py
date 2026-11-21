#!/usr/bin/env python3
"""Write Assignment 7's film beat sheet from the repository as it stands.

    python -X utf8 scripts/build_animation_beat_sheet.py

Every code panel's text is READ OUT OF THE FILE at build time, never typed
here: a beat names a path and a line range and this script puts the bytes on
the panel. If a source line moves, the panel moves with it, and
`scripts/build_animation_ledger.py` refuses to write a ledger whose excerpt
does not match. That pair of checks is what keeps a film's code honest.

**Run it twice, and not a third time.** The first pass writes the sheet with
estimated durations so `generate_audio_kokoro.py` has narration to measure;
that script writes `actual_duration_s` and `audio_file` back. Running this
again re-authors every cue and show-marker against the MEASURED seconds,
because the cue times below are fractions of a beat rather than absolute
times. A third pass, after `build_media_clips.py` has refined a duration to
the real file's length, rounds that refined value back down and silently
costs the beat its Remotion stamp.

There is no separate timing pass. **`scripts/finalise_beat_timing.py` and
`scripts/fit_beat_panels.py` must NOT be run** -- both are carried-over
scripts that `chdir` into walker-ninja-TiantongZhang, and on 2026-10-28 one of
them rewrote that repository's beat sheet.

Panel capacities, measured off rendered frames and recorded in A5's and A6's
BUILD-PROMPT.md: the workbench code panel holds about 13 WRAPPED rows at
codeFontSize 23-26, its notes column holds 2 cards and about 160 characters of
value text, ClaudeVerdictArtifact holds about 8 lines, and the hesitant
writer's context card holds 2 rows of roughly 37 characters. Overflowing any
of them clips SILENTLY, which is why the pilot render exists.
"""
from __future__ import annotations

import io
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-animation-gamedev"
SLUG = "claude-liam-walker-the-lost-animation-gamedev"
TITLE = "TheLostAnimation_TiantongZhang"
TOPIC = "WALKER - GODOT ANIMATION TEARDOWN"

# **Kokoro's measured speaking rate, from Assignment 6's finished sheet:**
# 2168 narrated words across 613.7 s of generated audio = 3.533 words/s, with
# every individual beat between 3.20 and 3.77.
#
# The per-beat `seconds` arguments below are DERIVED from this rather than
# typed, because the first pass's only job is to put a plausible window on
# each footage beat before any audio exists -- and eighteen hand-typed
# estimates are eighteen numbers that go stale the moment a narration is
# edited. That is this repository's most repeated fault and it is not going
# to be repeated here. The second pass replaces all of it with the measured
# length anyway.
WORDS_PER_SECOND = 3.533


def probe_seconds(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def lines_of(rel: str, start: int, end: int) -> str:
    """Source lines start..end inclusive, one-based, exactly as they are on
    disk. The ledger re-reads the same range and compares."""
    rows = (ROOT / rel).read_text(encoding="utf-8").split("\n")
    if not (1 <= start <= end <= len(rows)):
        raise SystemExit("%s: %d-%d is outside 1..%d" % (rel, start, end, len(rows)))
    return "\n".join(rows[start - 1:end])


# --------------------------------------------------------------------------
# Beat constructors. `cues` and `show` carry FRACTIONS of the beat; main()
# turns them into seconds once the measured narration length is known.
# --------------------------------------------------------------------------

def workbench(bid, act, note, narration, seconds, title, rel, start, end,
              notes, cues, font=24, show=None):
    code = lines_of(rel, start, end)
    return {
        "beat_id": bid,
        "act": act,
        "role_note": note,
        "narration_text": narration,
        "voice": "am_onyx",
        "engine": "kokoro",
        "estimated_duration_s": seconds,
        "shot": {
            "type": "GRAPHIC",
            "class": "SHOW",
            "source": "remotion",
            "motion": "code-highlight",
            "show": show or [
                {"at": 0.04, "event": "the excerpt is framed"},
                {"at": 0.45, "event": "the named line highlights"},
                {"at": 0.80, "event": "the note column holds"},
            ],
            "remotion": {
                "pattern": "GodotDevWorkbench",
                "props": {
                    "mode": "code",
                    "title": title,
                    "project": "walker-the-lost-TiantongZhang",
                    "path": "%s  lines %d-%d" % (rel, start, end),
                    "source": rel,
                    "code": code,
                    "startLine": start,
                    "codeFontSize": font,
                    "inspectorLabel": "Source notes - not Inspector values",
                    "notes": notes,
                    "cues": cues,
                },
            },
        },
    }


def footage(bid, act, note, narration, seconds, take, window, show):
    """`window` is [start, preferred_end]. main() moves the END to wherever
    the MEASURED narration finishes, clamped to the take's own length, so a
    beat never asks build_media_clips.py to drop footage and never pads a long
    narration with a frozen frame. Two beats may draw overlapping windows from
    one take; that is a framing choice and SHOTLIST.md records it."""
    return {
        "beat_id": bid,
        "act": act,
        "role_note": note,
        "narration_text": narration,
        "voice": "am_onyx",
        "engine": "kokoro",
        "estimated_duration_s": seconds,
        "shot": {
            "type": "FOOTAGE",
            "class": "SHOW",
            "source": "capture",
            "motion": "gameplay",
            "capture": "take-" + take,
            "evidence_media": "capture/take-%s.mp4" % take,
            "window_s": window,
            "show": show,
        },
    }


def still(bid, act, note, narration, seconds, media, title, path, label, show):
    return {
        "beat_id": bid,
        "act": act,
        "role_note": note,
        "narration_text": narration,
        "voice": "am_onyx",
        "engine": "kokoro",
        "estimated_duration_s": seconds,
        "shot": {
            "type": "STILL",
            "class": "SHOW",
            "source": "capture",
            "motion": "hold",
            "evidence_media": media,
            "title": title,
            "path": path,
            "image_label": label,
            "show": show,
        },
    }


def graphic(bid, act, note, narration, seconds, pattern, props, motion, show):
    return {
        "beat_id": bid,
        "act": act,
        "role_note": note,
        "narration_text": narration,
        "voice": "am_onyx",
        "engine": "kokoro",
        "estimated_duration_s": seconds,
        "shot": {
            "type": "GRAPHIC",
            "class": "SHOW",
            "source": "remotion",
            "motion": motion,
            "show": show,
            "remotion": {"pattern": pattern, "props": props},
        },
    }


def beats():
    out = []

    # ---------------------------------------------------- WALKER BOOKEND 1/4
    out.append(graphic(
        "B00", "ASK",
        "WALKER BOOKEND 1/4 - ClaudeComposerAsk. The prompt is a "
        "reconstruction and is said aloud to be one. Liam is named in the "
        "first breath.",
        "Sawubona - this is Liam, in for Bear. The prompt on screen is a "
        "reconstruction, written to be illustrative. It was never sent. The "
        "game under it is real: a dungeon slice in Godot four, a character "
        "who could walk and jump and nothing else. What we are taking apart "
        "is two animation clips - one that loops and one that commits - and "
        "the question that turned out to matter more than either of them. "
        "Which questions was anything actually asking.",
        25, "ClaudeComposerAsk",
        {
            "greeting": "Sawubona, Liam",
            "topic": TOPIC,
            "segment": "The Lost, in motion",
            "command": (
                "Please use Walker to animate the player in The Lost - a "
                "side-view dungeon crawler where every hazard announces "
                "itself before it can hurt you. A run that loops and a sword "
                "swing that commits. Write the clips and the read-backs; "
                "the verdict on how they look in play is mine."),
            "runningText": "RECONSTRUCTION - this prompt was never sent",
            "modelLabel": "Claude Opus 5",
            "effortLabel": "High",
        },
        "type-on",
        [{"at": 0.03, "event": "composer card fades in"},
         {"at": 0.14, "event": "greeting lands"},
         {"at": 0.32, "event": "the Walker prompt types on"},
         {"at": 0.82, "event": "RECONSTRUCTION label holds"}]))

    # ---------------------------------------------------- WALKER BOOKEND 2/4
    out.append(graphic(
        "B01", "RESULT",
        "WALKER BOOKEND 2/4 - hesitant writer, one working single-word "
        "correction with measured time to complete it. The correction is the "
        "film's thesis in one word: the revisions were not FOUND, they were "
        "REPORTED.",
        "Here is what actually changed. Two clips. A run cycle on a cut-out "
        "rig, and a sword swing on a sprite sheet - which is the opposite way "
        "round from the obvious one, for a reason that is about art rather "
        "than about animation. Two hundred and eighty automated checks stand "
        "behind them, and seven deliberate breakages stand behind the checks. "
        "And ten tuning revisions, nine of them found - correction - nine of "
        "them reported, by the author, playing the game. The tenth came from "
        "a measurement written to test a prediction. Not one of the ten "
        "started with a test that had been passing and started failing.",
        36, "BrutalistHesitantWriter",
        {
            "text": ("Two clips. One authority.\n"
                     "Ten revisions in six days.\n"
                     "280 checks, 7 mutations.\n"
                     "Started by a failing test: 0."),
            "triggerWords": "found",
            "replacementWords": "reported",
            "charMs": 16,
            "face": "serif",
            "fontSize": 62,
            "lineSpacing": 1.35,
            "align": "left",
            "contextTitle": "What was built",
            "brandLabel": "@NikBearBrown",
            "contextItems": [
                {"label": "By hand",
                 "detail": "The brief, every verdict, every revision asked for."},
                {"label": "By Claude",
                 "detail": "2 clips, 2 players, 280 checks, the rigs."},
                {"label": "Predicted first",
                 "detail": "7 failures named in the brief before any code."},
            ],
        },
        "write-on",
        [{"at": 0.06, "event": "the summary begins writing"},
         {"at": 0.38, "event": "'found' struck through, 'reported' written in"},
         {"at": 0.78, "event": "the zero lands"}]))

    # ------------------------------------------- PAIR 1: the cycle is derived
    out.append(workbench(
        "B02", "BUILD",
        "C1 CODE. The cycle's length is arithmetic, not taste. Paired with "
        "B03.",
        "Start with the loop. This is the whole cycle as resource text - "
        "never built in code at runtime - and the number to look at is the "
        "first one. Length, nought point five seconds. That is not a choice. "
        "The game already spawns a puff of dust every twenty four pixels and "
        "the player walks at ninety six pixels a second, so a stride takes a "
        "quarter of a second and a gait cycle is two strides. Half a second, "
        "exactly. Step is nought point one two five - a quarter cycle, "
        "because a gait has four landmarks: contact, pass, contact, pass. And "
        "the values: thirty eight, twelve, minus fourteen, twelve, thirty "
        "eight. Front leg. The back leg runs the same five numbers in the "
        "opposite order, so front plus back is twenty four on every single "
        "key. The facing mirrors the whole rig, so one set of keys is correct "
        "both ways round and a cycle that only ran one way would never show "
        "it. That is exact antiphase as arithmetic, and the read-back checks "
        "it as arithmetic, because the cycle this replaced had two legs that "
        "came within two degrees of each other and read as two legs wobbling.",
        58,
        "The cycle, and why it is 0.500 s",
        "godot/animations/legs.tres", 24, 38,
        [{"label": "Why 0.500 s",
          "value": "2 x stride_px / SPEED = 48 / 96. Retime it and this arithmetic changes first, not the keys."},
         {"label": "Why loop_mode = 1",
          "value": "LOOP_LINEAR. Godot 3's boolean `loop` loads without complaint and plays the cycle once."}],
        [{"at": 0.10, "line": 24, "label": "derived from the stride, not chosen"},
         {"at": 0.40, "line": 26, "label": "a quarter cycle: four landmarks"},
         {"at": 0.72, "line": 37, "label": "front; back is these five reversed"}]))

    out.append(footage(
        "B03", "RESULT",
        "C1 RESULT. take-c, PLAYED: held keys through the real input map, "
        "nothing teleported. The take asserts nine cycle wraps, both facings "
        "and twenty three dust puffs before a frame of it counts. It never "
        "crosses a trap, deliberately.",
        "There it is, in play. Both facings - and the dust lands under the "
        "planted foot, because the cycle and the dust share a clock.",
        8, "c", [0.6, 8.93],
        [{"at": 0.05, "event": "the first strides, facing right"},
         {"at": 0.40, "event": "dust under the planted foot"},
         {"at": 0.72, "event": "the turn - the same gait, mirrored"}]))

    # -------------------------------------- PAIR 2: the window is on the clip
    out.append(workbench(
        "B04", "BUILD",
        "C2 CODE. The hitbox window is a track, not a timer. Paired with B05.",
        "Now the clip that commits. Eighteen frames at thirty, nought point "
        "six seconds, and it does not loop. The track on screen is the "
        "interesting one, and it is not a drawing. It is the hitbox. "
        "Monitoring goes true at nought point two and false at nought point "
        "three three three, which makes the sword dangerous for exactly four "
        "frames out of eighteen - and the strike itself, frame six to frame "
        "ten, is a hundred and fifty degrees in a hundred and thirty three "
        "milliseconds, five times the speed of the wind-up. That difference "
        "is the whole reason it reads as a strike rather than a gesture. Two "
        "things about the track. Update equals one - "
        "discrete - so the value cuts rather than interpolating, which for a "
        "boolean is the difference between a hitbox and a dimmer switch. And "
        "it is on the clip's own timeline rather than in a timer somewhere, "
        "which is the point the course notes make in so many words: a "
        "gameplay fact like the hitbox is live should not depend on a tween "
        "that can be killed halfway. The window is narrower than the spike "
        "trap's own lethal window on purpose. You cannot trade with a trap.",
        56,
        "The active window, as a track",
        "godot/animations/player.tres", 110, 121,
        [{"label": "Why discrete",
          "value": "update = 1. A continuous track would interpolate a bool and the window would have edges."},
         {"label": "Why on the clip",
          "value": "0.200 to 0.3333 = 4 of 18 frames. The trap's own lethal window is 0.18 s - wider."}],
        [{"at": 0.14, "line": 113, "label": "a gameplay fact, keyed"},
         {"at": 0.46, "line": 117, "label": "opens 0.200, closes 0.3333"},
         {"at": 0.76, "line": 119, "label": "discrete: it cuts, it does not blend"}]))

    out.append(footage(
        "B05", "RESULT",
        "C2 RESULT. take-s, PLAYED: four fresh swings with a half-second gap, "
        "so none of them is a buffered second attack. The take asserts the "
        "window opened exactly four times and every clip ran its own 36 "
        "physics frames.",
        "Four swings. Startup, strike, recovery - and the strike is five "
        "times the speed of the wind-up.",
        5, "s", [0.45, 5.50],
        [{"at": 0.08, "event": "the wind-up, blade drawn back"},
         {"at": 0.34, "event": "the strike - the fastest thing on the timeline"},
         {"at": 0.66, "event": "recovery, and the blade sheathes"}]))

    # ------------------------------------------ PAIR 3: one authority is a partition
    out.append(workbench(
        "B06", "BUILD",
        "C3 CODE. The assignment's one-authority rule, and the thing it "
        "actually says. Paired with B07.",
        "This assignment's hardest rule is one authority per animated node, "
        "and this project broke it on day one: a pose driver was writing the "
        "sprite's texture every frame and the new clip keyed the same node. "
        "That one is easy - delete the driver. The interesting version came "
        "later. The author asked for the legs to keep moving during a moving "
        "swing, and a design document in this repository said that would "
        "require an animation tree, because it needs two clips at once. That "
        "sentence was wrong, and nobody had checked it. The rule is one "
        "authority per NODE. A second animation player breaks nothing as long "
        "as the two players' track paths do not intersect. So the legs got "
        "their own player - and the check on screen asserts the partition in "
        "BOTH directions. Read the last one. No track on the body player "
        "names a leg. That is not redundant with the other two: a partition "
        "checked one way round is only a subset, and a scene where both "
        "players write the legs satisfies the easy version perfectly.",
        60,
        "One authority - asserted as a partition",
        "godot/tests/test_player_clips.gd", 217, 230,
        [{"label": "Why both directions",
          "value": "\"LegAnim writes the legs\" is true in a scene where BOTH players write them. That is the failure."},
         {"label": "Why no AnimationTree",
          "value": "Nothing blends. One clip per player, two players, disjoint node sets."}],
        [{"at": 0.30, "line": 217, "label": "no node is on both lists"},
         {"at": 0.58, "line": 224, "label": "every leg track is on LegAnim"},
         {"at": 0.82, "line": 230, "label": "and NO leg track is on the other"}]))

    out.append(still(
        "B07", "RESULT",
        "C3 RESULT. The partition read back out of the two committed "
        "resources, plus the mutation that puts one leg track back on the "
        "body player and the two assertions it turns red.",
        "Read out of the two resource files, not typed. Six tracks on one "
        "player, six on the other, and the intersection is empty. Put a "
        "single leg track back on the body player and two of the three checks "
        "go red - which is how you know the third one was worth writing.",
        26, "media/B07.png",
        "The authority, as a partition",
        "godot/animations/player.tres + legs.tres",
        "read back from the committed resources",
        [{"at": 0.08, "event": "the two track lists"},
         {"at": 0.46, "event": "the empty intersection"},
         {"at": 0.78, "event": "the mutation, and what it turns red"}]))

    # --------------------------------------------- PAIR 4: the two clocks
    out.append(workbench(
        "B08", "BUILD",
        "C4 CODE. The two-clocks measurement, which disagreed with the "
        "brief's own prediction. Paired with B09.",
        "Two clocks. The clip advances on one tick and gameplay reads the "
        "hitbox on another, and this assignment asks what the largest "
        "disagreement is. The brief predicted that leaving the player on "
        "Godot's default idle tick would make the window open up to one "
        "physics step LATE, and jitter between runs. It is on screen being "
        "tested rather than being agreed with, and it was wrong - wrong in "
        "sign. Idle is one step EARLY, not late, and the reason is not read "
        "latency at all. Both modes make the clip current on the same physics "
        "frame; the difference is where the playhead is ON that frame. The "
        "physics-mode mixer already took its step for that frame before "
        "anything called play. The idle-mode mixer takes its step afterwards. "
        "One frame, gained at the start, carried for the whole clip. And the "
        "claim underneath the prediction survives intact: in both modes the "
        "window opens on the frame whose playhead reads nought point two "
        "exactly, so writer and reader disagree by zero seconds.",
        62,
        "The measurement, not the setting",
        "godot/tests/measure_clocks.gd", 131, 138,
        [{"label": "What was predicted",
          "value": "Up to one physics step LATE, jittering. Tagged [proposal] in the brief, which is why it was tested."},
         {"label": "What was measured",
          "value": "One step EARLY. The window still opens at playhead 0.2000 in both modes: disagreement 0 s."}],
        [{"at": 0.42, "line": 132, "label": "the claim that survived"},
         {"at": 0.70, "line": 136, "label": "and the one that did not"}]))

    out.append(still(
        "B09", "RESULT",
        "C4 RESULT. The recorded output of measure_clocks.gd, both modes, "
        "from evidence/a7/clocks.txt. It also states what the run CANNOT "
        "see, which is the jitter half of the prediction.",
        "The run, both modes. And read the last line before the numbers: "
        "this cannot see the jitter. The test wrapper locks the render tick "
        "to the physics tick on purpose, so every run of this file is "
        "identical, and running a deterministic measurement three times is "
        "one measurement printed three times. The file says so in its own "
        "output rather than letting you assume a repeated number is a "
        "replicated one.",
        30, "media/B09.png",
        "Two clocks, measured in both modes",
        "evidence/a7/clocks.txt",
        "recorded run - scripts/run-test.sh measure_clocks.gd 60",
        [{"at": 0.10, "event": "the two rows"},
         {"at": 0.44, "event": "the playhead column"},
         {"at": 0.76, "event": "what the run cannot see"}]))

    # ----------------------- PAIR 5: the jump, and what the request really was
    out.append(workbench(
        "B10", "BUILD",
        "C5 CODE. The last revision, and the two different claims hiding in "
        "one sentence. Paired with B11.",
        "The tenth revision, and the shortest. The author asked to be able to "
        "jump while swinging, without interrupting the swing. That is one "
        "sentence and two completely different claims. The jump happening is "
        "this branch moving out of an else. The swing not noticing is the "
        "fact that this branch writes one field - vertical velocity - and "
        "nothing else. It does not touch the action state, the swing counter, "
        "the buffered attack, or any animation player. There is no code path "
        "from a jump to the clip's clock, so the clip cannot notice. Which "
        "means the second half of the request is not something you can see by "
        "looking at the jump at all.",
        44,
        "Four lines, and one of them is the argument",
        "godot/features/player/player.gd", 111, 118,
        [{"label": "Why it cannot interrupt",
          "value": "It writes velocity.y. Not `action`, not `swing_count`, not any AnimationPlayer. Structural, not careful."},
         {"label": "Why is_on_floor stays",
          "value": "It is the only gate now. No double jump - the lock stopped being the reason."}],
        [{"at": 0.22, "line": 115, "label": "the only gate left"},
         {"at": 0.56, "line": 116, "label": "one field written, and nothing else"}]))

    out.append(footage(
        "B11", "RESULT",
        "C5 RESULT. take-m, PLAYED: a direction held through two swings, then "
        "two swings jumped out of. The take asserts a hundred and eight "
        "frames of travelling swing with the gait playing under it, and two "
        "swings that left the floor without the swing counter moving.",
        "Both of the last two revisions, in one take. A swing that travels "
        "with its gait still under it, and a swing jumped out of.",
        10, "m", [0.5, 10.27],
        [{"at": 0.08, "event": "a swing with a direction held"},
         {"at": 0.42, "event": "the gait continues under it"},
         {"at": 0.74, "event": "and one jumped out of"}]))

    # ------------------------ PAIR 6: proving a negative about the clip's clock
    out.append(workbench(
        "B12", "BUILD",
        "C6 CODE. How you establish that something did NOT happen. Paired "
        "with B13.",
        "So how do you check that a swing did not notice? You cannot. Not by "
        "watching the swing. What you can do is run the same swing twice - "
        "once with a jump through it, once without - and compare the two "
        "clocks frame by frame. That is this loop. Playhead, hitbox window, "
        "lock, clip name, on all thirty six physics frames, in all three "
        "phases. The legs, by the way, keep their phase straight through a "
        "swing because nothing ever seeks them - that is the ninth revision, "
        "and the whole point of giving them their own player. And here is why "
        "this comparison is not over-engineering. There is a "
        "deliberate breakage in this repository that makes the jump restart "
        "the clip every time it is pressed. Every single check that the jump "
        "WORKS stays green under it. All three of them. Eight others go red, "
        "and all eight come from this comparison.",
        45,
        "Proving a negative about a clock",
        "godot/tests/test_swing_edges.gd", 428, 438,
        [{"label": "Why run it twice",
          "value": "\"It did not interrupt\" is a claim about the SWING. The jump is the wrong thing to look at."},
         {"label": "What mutation M7 shows",
          "value": "A jump that restarts the clip: 3 'jump works' checks green, 8 comparison checks red."}],
        [{"at": 0.28, "line": 428, "label": "every frame of both runs"},
         {"at": 0.62, "line": 436, "label": "the claim, as a measurement"}]))

    out.append(still(
        "B13", "RESULT",
        "C6 RESULT. The recorded section E output, and beside it mutation M7, "
        "whose point is that it still jumps. From evidence/a7/mutations.txt.",
        "Nought point zero zero zero zero zero zero seconds, in all three "
        "phases. And beside it the mutation, kept because of what stayed "
        "green rather than what went red. One more thing from that run, "
        "recorded rather than hidden: in the recovery case, one of the "
        "comparison checks passed under the mutation too - restarting at "
        "frame twenty six puts the next window past the end of what the trace "
        "records. An assertion that is green because the evidence ran out is "
        "not an assertion that passed.",
        34, "media/B13.png",
        "The same swing, twice, compared",
        "evidence/a7/mutations.txt + test_swing_edges.gd section E",
        "recorded run - 60 checks, 0 failures; mutation M7, 8 failures",
        [{"at": 0.12, "event": "the three phases, and the drift column"},
         {"at": 0.48, "event": "M7: what stayed green"},
         {"at": 0.80, "event": "the blind spot, named"}]))

    # ------------------------------------------------- the thesis, stated once
    out.append(still(
        "B14", "TURN",
        "The film's actual subject, as a table: ten revisions, who started "
        "each one, and whether a headless run could have seen the defect. "
        "Composed from TUNING.md and CHANGE-BRIEF.md.",
        "Here is the thing this assignment actually taught, and it is not "
        "about animation. Ten revisions. Nine of them started with the author "
        "playing the game and saying something was wrong. Now look at the "
        "last column, because the honest version of this is not that "
        "everything was missed. Three of the ten were design calls - the game "
        "was not wrong, the author wanted something else. Two were judgements "
        "about how a thing looks, and there is no fact to check in those. But "
        "three of them say read-back, and those three are the subject. The "
        "sword spinning above the head was literally what the key table "
        "described - the tip is never below minus three pixels in any of the "
        "eighteen frames, and that is the range of the function, not an "
        "impression. The pivot sitting on the character's spine was a "
        "correctly computed bounding box of the wrong quantity, because it "
        "included a trailing scarf. And the legs that waggled had a planted "
        "foot three pixels through the floor while the assertion about that "
        "foot was green, because the band it was checked against had been "
        "measured in the wrong sign. The read-backs did not miss these. They "
        "were never asked. A read-back only sees the questions it was written "
        "to ask, and the questions came from someone playing the game.",
        56, "media/B14.png",
        "Ten revisions, and who found each one",
        "TUNING.md + CHANGE-BRIEF.md revisions 7.0.1 - 7.0.10",
        "composed from the committed revision history",
        [{"at": 0.10, "event": "the ten rows"},
         {"at": 0.42, "event": "the 'who reported it' column"},
         {"at": 0.76, "event": "and what headless could have seen"}]))

    # ---------------------------------------------------- WALKER BOOKEND 3/4
    out.append(graphic(
        "B15", "VERDICT",
        "WALKER BOOKEND 3/4 - verdict. Implemented work, limits named, and "
        "the open HUMAN rows left open rather than quietly closed.",
        "The verdict, and the limits with it. Two clips, both as resource "
        "text, both on the physics tick. Two animation players over a "
        "partition that is asserted in both directions. The active window on "
        "the clip's own timeline, measured at both tick settings. Two hundred "
        "and eighty checks and seven mutations, every mutation naming the "
        "assertion that has to fire. Now the limits, and these are real. The "
        "hitbox can hit nothing, because this room has no enemy - the window "
        "is real, measured and tested, and what it would do is a later "
        "assignment. The run cycle alternates but it does not stride: the "
        "cut-out leg moves its foot about ten pixels against a twenty four "
        "pixel step, and the only fix is drawing a longer leg, which changes "
        "the character's art. And three questions in the evidence table are "
        "still open, because no headless run can answer them and the author "
        "has not judged them yet. They are listed as open rather than covered "
        "by a general it all looks fine.",
        70, "ClaudeVerdictArtifact",
        {
            "title": "What holds, and what does not",
            "artifactLines": [
                "Two clips as resource text, never built at runtime.",
                "TWO AnimationPlayers, partitioned BY NODE, asserted both ways.",
                "Hitbox window on the clip's timeline: 0.200 to 0.3333.",
                "Clocks measured in both modes. Disagreement: 0 s.",
                "280 checks, 7 mutations, 0 failures.",
                "LIMIT: the hitbox can hit nothing. No enemy in this room.",
                "LIMIT: the cycle alternates. It does not stride.",
                "OPEN: 3 of 9 HUMAN rows. Listed as open.",
            ],
            "brandLabel": "@NikBearBrown",
            "verdictLabel": "Assignment 7 - The Lost",
        },
        "artifact-reveal",
        [{"at": 0.06, "event": "the artifact card opens"},
         {"at": 0.40, "event": "the built lines"},
         {"at": 0.70, "event": "the limits"},
         {"at": 0.90, "event": "the open rows hold"}]))

    # ---------------------------------------------------- WALKER BOOKEND 4/4
    out.append(graphic(
        "B16", "TURN",
        "WALKER BOOKEND 4/4 - Your Turn. One bounded change a viewer can make "
        "in their own project, with the check that would catch it.",
        "Your turn, and make it small. Go and find one sentence in your own "
        "design notes that says a thing is impossible, or that some feature "
        "would require some big piece of machinery. Then check it. Not "
        "rewrite it - check it. The sentence that cost this project a day "
        "said that showing two things at once needs an animation tree, and it "
        "was written into a design document as a reason, accepted, and quoted "
        "back as settled. It was never measured. A limitation accepted on an "
        "unexamined claim looks exactly like a measurement once it is in a "
        "table.",
        34, "ClaudeComposerAsk",
        {
            "greeting": "Your turn",
            "topic": TOPIC,
            "segment": "One bounded change",
            "command": (
                "Find one sentence in your own notes that says something is "
                "impossible or needs a big piece of machinery. Check it "
                "against the engine rather than against the sentence. Write "
                "down what you measured, including if the sentence was right."),
            "runningText": "A limitation accepted on an unexamined claim "
                           "looks like a measurement",
            "modelLabel": "Claude Opus 5",
            "effortLabel": "High",
        },
        "type-on",
        [{"at": 0.05, "event": "the turn card opens"},
         {"at": 0.40, "event": "the bounded change types on"},
         {"at": 0.84, "event": "the running line holds"}]))

    # -------------------------------------------------------- LOCKED OUTRO
    out.append({
        "beat_id": "B17",
        "act": "OUTRO",
        "role_note": "LOCKED ClaudeTitleOutro. Exact title, @NikBearBrown, no "
                     "narration over it - OUTRO-LOCK.md.",
        "narration_text": "",
        "voice": "am_onyx",
        "engine": "kokoro",
        "audio_policy": "silence",
        "estimated_duration_s": 5,
        "shot": {
            "type": "GRAPHIC",
            "class": "SHOW",
            "source": "remotion",
            "motion": "hold",
            "show": [{"at": 0.10, "event": "the locked outro card holds"}],
            "remotion": {
                "pattern": "ClaudeTitleOutro",
                "props": {
                    "title": TITLE,
                    "channel": "@NikBearBrown",
                    "durationSeconds": 5,
                },
            },
        },
    })

    return out


def main() -> int:
    REEL.mkdir(parents=True, exist_ok=True)
    path = REEL / "beat_sheet.json"

    measured: dict[str, float] = {}
    previous_props: dict[str, dict] = {}
    if path.is_file():
        old = json.load(io.open(path, encoding="utf-8"))
        for b in old.get("beats", []):
            rem = b.get("shot", {}).get("remotion")
            if rem and rem.get("props") is not None:
                carried = dict(rem["props"])
                if rem.get("rendered"):
                    carried["rendered"] = rem["rendered"]
                previous_props[b["beat_id"]] = carried
            if b.get("actual_duration_s"):
                measured[b["beat_id"]] = float(b["actual_duration_s"])
            elif b.get("shot", {}).get("remotion", {}).get("props", {}).get("durationSeconds"):
                measured[b["beat_id"]] = float(
                    b["shot"]["remotion"]["props"]["durationSeconds"])

    takes = {}
    for mp4 in sorted((REEL / "capture").glob("take-*.mp4")):
        takes[mp4.stem] = probe_seconds(mp4)

    sheet_beats = []
    for b in beats():
        bid = b["beat_id"]
        # Derived from the word count at the measured rate -- see
        # WORDS_PER_SECOND. The locked outro has no narration and keeps its
        # own fixed length.
        words = len(b["narration_text"].split())
        if words:
            b["estimated_duration_s"] = round(words / WORDS_PER_SECOND, 1)
        seconds = measured.get(bid, float(b["estimated_duration_s"]))

        take = b["shot"].get("capture")
        if take is not None and take in takes:
            start, preferred = (float(v) for v in b["shot"]["window_s"])
            end = min(start + seconds, takes[take], preferred)
            b["shot"]["window_s"] = [round(start, 3), round(end, 3)]
            hold = seconds - (end - start)
            note = "fits" if hold < 0.05 else "HOLD %.2f s" % hold
            print("  %-5s %-7s %6.2f-%6.2f of %5.2f s   narration %5.2f s  %s"
                  % (bid, take, start, end, takes[take], seconds, note))
        props = b["shot"].get("remotion", {}).get("props")
        if props is not None:
            props["durationSeconds"] = round(seconds, 2)
            for cue in props.get("cues", []):
                cue["at"] = round(float(cue["at"]) * seconds, 2)
            was = previous_props.get(bid)
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
            "title": TITLE,
            "slug": SLUG,
            "topic": TOPIC,
            "kind": "gamedev",
            "playlist": "Brutalist",
            "brand": "claude-liam",
            "audience": "Course reviewers reading a Godot animation pass",
            "register": "Teardown",
            "engine": "kokoro",
            "voice": "am_onyx",
            "voice_kokoro": "am_onyx",
            "palette": "claude",
            "style_preset": "claude",
            "ground": "#FAF9F5",
            "aspect_ratio": "16:9",
            "fit": "contain",
            "captions": False,
            "channel_title": "@NikBearBrown",
            "channel": "@NikBearBrown",
            "folderLabel": "@NikBearBrown",
            "greeting": "Sawubona, Liam",
            "greeting_note": "hello lexicon: Sawubona (Zulu), one word. "
                             "Wagwan is Bear's alone.",
            "mode": "walker",
            "teaching_contract": "code-then-result-v1",
            "game": "godot",
        },
        "beats": sheet_beats,
    }
    io.open(path, "w", encoding="utf-8", newline="\n").write(
        json.dumps(sheet, ensure_ascii=False, indent=2) + "\n")

    total = sum(float(b.get("actual_duration_s") or b["estimated_duration_s"])
                for b in sheet_beats)
    print("wrote %s" % path)
    print("  %d beats, %s %.1f s (%d:%02d)"
          % (len(sheet_beats), "measured" if measured else "estimated",
             total, total // 60, total % 60))
    code = [b["beat_id"] for b in sheet_beats
            if b["shot"].get("remotion", {}).get("props", {}).get("mode") == "code"]
    print("  %d code beats: %s" % (len(code), ", ".join(code)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
