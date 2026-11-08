#!/usr/bin/env python3
"""Write Assignment 6's film beat sheet from the repository as it stands.

    python -X utf8 scripts/build_particles_beat_sheet.py

Every code panel's text is READ OUT OF THE FILE at build time, never typed
here: a beat names a path and a line range and this script puts the bytes on
the panel. If a source line moves, the panel moves with it and
`scripts/build_particles_ledger.py` refuses to write a ledger whose excerpt
does not match, which is the pair of checks that keeps a film's code honest.

**Run it twice.** The first pass writes the sheet with estimated durations so
`generate_audio_kokoro.py` has narration to measure; that script writes
`actual_duration_s` and `audio_file` back into the sheet. Running this again
re-authors every cue and show-marker against those MEASURED seconds, because
the cue times here are fractions of a beat, not absolute times. There is no
separate timing pass -- `scripts/finalise_beat_timing.py` must NOT be run; it
is a carried-over script that `chdir`s into walker-ninja-TiantongZhang.

Panel capacities, measured off rendered frames and recorded in A5's
BUILD-PROMPT.md: the workbench code panel holds about 13 WRAPPED rows at
codeFontSize 23-26, its notes column holds 2 cards and about 160 characters of
value text, ClaudeVerdictArtifact holds about 8 lines, and the hesitant
writer's context card holds 2 rows of roughly 37 characters. Overflowing any
of them clips silently.
"""
from __future__ import annotations

import io
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-particles-gamedev"
SLUG = "claude-liam-walker-the-lost-particles-gamedev"
TITLE = "TheLostParticles_TiantongZhang"
TOPIC = "WALKER - GODOT PARTICLE EFFECTS TEARDOWN"


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
# The beats. `cues` and `show` carry FRACTIONS of the beat; main() turns them
# into seconds once the measured narration length is known.
# --------------------------------------------------------------------------

def workbench(bid, act, note, narration, seconds, title, rel, start, end,
              notes, cues, font=26, show=None):
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
    beat never asks scripts/build_media_clips.py to drop footage and never
    pads a long narration with twenty seconds of frozen frame. Two beats may
    draw overlapping windows from one take; that is a framing choice and
    SHOTLIST.md records it."""
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
        "WALKER BOOKEND 1/4 - ClaudeComposerAsk. The prompt is a reconstruction "
        "and is said aloud to be one. Liam is named in the first breath.",
        "Sawubona - this is Liam, in for Bear. The prompt on screen is a "
        "reconstruction, written to be illustrative. It was never sent. The "
        "game under it is real: a dungeon slice in Godot four, three spike "
        "traps and a character who can walk and jump. What we are taking apart "
        "is three particle effects, and the one question that decides whether "
        "any of this is evidence - what can a run that draws nothing actually "
        "tell you.",
        26, "ClaudeComposerAsk",
        {
            "greeting": "Sawubona, Liam",
            "topic": TOPIC,
            "segment": "The Lost, in dust",
            "command": (
                "Please use Walker to add particle effects to my game design "
                "document about The Lost - a side-view dungeon crawler where "
                "every hazard announces itself before it can hurt you. The "
                "spike trap needs grit when it strikes and the room needs air. "
                "Write the scenes and the tests; the verdict on how they look "
                "in play is mine."),
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
        "correction with measured time to complete it.",
        "Here is what actually changed. Three particle effects, six emitters "
        "between them. A grit burst that fires - correction - that spawns a "
        "fresh instance every time a trap strikes. A field of motes that is "
        "already full on the first frame the room is drawn. And dust under the "
        "feet, on an event this game does not have. Two hundred and forty nine "
        "automated checks stand behind that, twenty six of them run three "
        "times over at three different frame rates, and two deliberate "
        "breakages stand behind the checks.",
        38, "BrutalistHesitantWriter",
        {
            "text": ("Three effects. Six emitters.\n"
                     "A burst that fires per event.\n"
                     "249 checks, 301 results.\n"
                     "One tuning revision, kept."),
            "triggerWords": "fires",
            "replacementWords": "spawns",
            "charMs": 16,
            "face": "serif",
            "fontSize": 62,
            "lineSpacing": 1.35,
            "align": "left",
            "contextTitle": "What was built",
            "brandLabel": "@NikBearBrown",
            "contextItems": [
                {"label": "By hand",
                 "detail": "The brief, every verdict, the shader conversion."},
                {"label": "By Claude",
                 "detail": "3 scenes, 2 drivers, 249 checks, the rigs."},
                {"label": "Predicted first",
                 "detail": "7 failures named in the brief. 2 were run."},
            ],
        },
        "write-on",
        [{"at": 0.06, "event": "the summary begins writing"},
         {"at": 0.34, "event": "'fires' struck through, 'spawns' written in"},
         {"at": 0.74, "event": "the counts land"}]))

    # ------------------------------------------------------ PAIR 1: the event
    out.append(workbench(
        "B02", "BUILD",
        "C1 CODE. The event already existed. Paired with B03.",
        "Every effect needs an event, and this one was already here. The trap "
        "is a five-state machine, and the frame it enters FIRING it emits a "
        "signal called fired. That line was written for Assignment Five and "
        "nothing in this assignment touched it. The spawner connects to it, "
        "binds the trap that sent it so it knows where to put the burst, and "
        "instances a fresh scene. Note what it does not do. It does not reuse "
        "one node and set emitting to true, because on a one-shot emitter that "
        "is already emitting, that call does nothing at all - the second of "
        "two close events is silently dropped. And it parents the burst to the "
        "room, not to the trap, so nothing can free it mid-life.",
        44,
        "The event, and why it is a signal",
        "godot/features/traps/spike_trap.gd", 95, 102,
        [{"label": "Why not a new signal",
          "value": "fired already existed at line 24. Presentation reads game state; it never adds to it."},
         {"label": "Why an instance per event",
          "value": "emitting = true on a busy one_shot node does not restart it. Two close events, one burst."}],
        [{"at": 0.18, "line": 98, "label": "the signal the burst listens for"},
         {"at": 0.52, "line": 99, "label": "and the damage, on the same frame"}]))

    out.append(footage(
        "B03", "RESULT",
        "C1 RESULT. take-p, PLAYED: held keys through the real input map, "
        "nothing teleported. The take asserts three traps fired, four bursts "
        "and twenty five step-dust puffs before a frame of it counts.",
        "There it is, on the game's own event. The trap goes red, the spikes "
        "arrive, and the grit comes off the floor line with them. Three traps, "
        "three bursts, one walk.",
        10, "p", [0.4, 10.63],
        [{"at": 0.05, "event": "the first trap begins its warning"},
         {"at": 0.35, "event": "spikes, and the burst"},
         {"at": 0.70, "event": "the second trap, same cycle"}]))

    out.append(footage(
        "B03A", "RESULT",
        "SCRIPTED, not played. take-r emits `fired` at the spawner directly on "
        "a 0.20 s rotation. Revision 6.0.2 measured that the ceiling is "
        "unreachable in play: traps are 1.17 s apart at 96 px/s and a burst "
        "lives 0.60 s.",
        "Rapid repeats - and this is not gameplay. The signal is being "
        "emitted straight at the spawner, every two tenths of a second. "
        "Three alive at once is the ceiling the brief set its budget "
        "against, and playing this room reaches one: the traps are one "
        "point one seven seconds apart and a burst lives six tenths.",
        17, "r", [0.9, 16.0],
        [{"at": 0.04, "event": "SCRIPTED label holds through the beat"},
         {"at": 0.30, "event": "first burst, trap one"},
         {"at": 0.48, "event": "three alive at once"},
         {"at": 0.80, "event": "the overlap clears"}]))

    # -------------------------------------------- PAIR 2: the three parts, A
    out.append(workbench(
        "B04", "BUILD",
        "C2 CODE. The three parts of a particle system, on one node. "
        "Paired with B05.",
        "A particle system is three steps and this one node shows all three. "
        "Emission is when and how many: amount four, lifetime twelve "
        "hundredths of a second, one shot true, explosiveness one, so all four "
        "leave together. Process is how they move, and it is not here - it is "
        "behind process underscore material, a separate resource with velocity, "
        "spread, gravity, damping and the curves. Draw is what reaches the "
        "screen: the material property, which carries the additive "
        "blend, local coords off so a particle stays where it was born, and "
        "visibility rect, which decides when the whole node is culled and "
        "never clips a particle. Three names, three steps, and the file keeps "
        "them apart.",
        46,
        "Emission, process and draw - on one node",
        "godot/effects/hit_burst.tscn", 106, 116,
        [{"label": "Emission vs draw",
          "value": "amount, lifetime, one_shot, explosiveness: emission. material, visibility_rect: draw."},
         {"label": "The process half",
          "value": "PPM_flash holds velocity, spread, gravity, damping and the curves."}],
        [{"at": 0.22, "line": 109, "label": "emission: how many"},
         {"at": 0.46, "line": 110, "label": "process: the whole second step, by reference"},
         {"at": 0.70, "line": 116, "label": "draw: culls the node, never clips a particle"}],
        font=24))

    out.append(still(
        "B05", "RESULT",
        "Effect A's tuning revision 6.0.1, with the author's verdict. Fixture "
        "capture from godot/previews/hit_burst_preview.tscn, labelled. The "
        "per-frame difference counts are recomputed from the committed frames "
        "at build time by scripts/compose_particles_evidence.py.",
        "This is the tuning loop, and it is the part of the assignment that "
        "cannot be automated. Flash was given the job of owning frame one, and "
        "at a scale of one point six it came out the same size as the grit "
        "beside it. One setting moved - scale min and max, five and seven. "
        "Before the recapture, Claude predicted frames ten and twelve would "
        "change and the rest would be identical. Five of six landed. Frame "
        "twelve is where it was wrong, and not by a little: the two frames are "
        "bit-identical, zero pixels different. Flash is drawn additively, so if "
        "it contributed any light at all, tripling its base scale would have "
        "moved at least one pixel. It contributes nothing by then. The whole "
        "visible difference lives on one frame. The verdict in the running "
        "game was the author's, and it was keep.",
        50, "media/B05.png",
        "One setting, one frame, and the prediction that missed",
        "captures/hit_burst/ - FIXTURE, preview scene, 30 fps",
        "r0 left, r1 right, frame 10; the table is recomputed from the frames",
        [{"at": 0.06, "event": "the two frame tens appear"},
         {"at": 0.42, "event": "the prediction column aligns"},
         {"at": 0.74, "event": "the frame 12 row is marked - zero"}]))

    # ------------------------------------- PAIR 3: Effect B and its feature
    out.append(workbench(
        "B06", "BUILD",
        "C3 CODE. Effect B, and the feature Effect A does not use. "
        "Paired with B07.",
        "Effect B is ambience: one emitter, sixty motes, an eight second life, "
        "and no event at all. Its condition is the scene being loaded with the "
        "player alive, and it stops on the player's died signal. The feature "
        "Effect A does not use is on line fifty two. Preprocess, eight point "
        "zero - one whole lifetime. The engine simulates the entire field "
        "before the first frame is drawn, so the room is never seen filling "
        "up. Without it, every single scene load starts in an empty room that "
        "fills over eight seconds, and nothing errors, and no headless test in "
        "this repository can see it. That is the failure the brief named F4, "
        "and the only instrument that catches it is a picture.",
        44,
        "preprocess - the feature Effect A does not use",
        "godot/effects/dungeon_motes.tscn", 45, 55,
        [{"label": "Why one emitter",
          "value": "The effect has one job. A second would be a second job nobody asked for."},
         {"label": "What stops it",
          "value": "player.gd's died signal. emitting goes false; motes already born finish their 8 s."}],
        [{"at": 0.20, "line": 48, "label": "sixty motes, no event"},
         {"at": 0.58, "line": 52, "label": "one full lifetime, simulated before frame one"}]))

    out.append(still(
        "B07", "RESULT",
        "F4 demonstrated by mutation: the same preview with preprocess set to "
        "0.0 in the scene file and reverted immediately after. Both are FIXTURE "
        "captures. Mote pixels are recomputed at build time from the committed "
        "frames against frame 340 of the shipped run, which is the same field "
        "eight seconds after it stopped - an empty room.",
        "Both of these are frame one. Same scene, same preview, one number "
        "different. On the left, preprocess at eight: the field is at full "
        "density on the first frame anyone could see, and it stays flat. On "
        "the right, preprocess at zero: twelve pixels, which is two per cent "
        "of the other, climbing to ninety nine by frame forty - about a fifth "
        "of the way through a fill that takes eight seconds. Nothing errored. "
        "The configuration test passed on both. This difference is only "
        "visible to a capture, and that is exactly why the brief put it in the "
        "frame strip column and not in a test.",
        44, "media/B07.png",
        "The same effect, one number apart, on frame one",
        "captures/dungeon_motes/ - FIXTURE, preview scene, mutation reverted",
        "preprocess 8.0 left, 0.0 right; the table is recomputed from the frames",
        [{"at": 0.08, "event": "the two frame ones appear"},
         {"at": 0.46, "event": "the counts land under them"},
         {"at": 0.80, "event": "the climbing column holds"}]))

    out.append(footage(
        "B07A", "RESULT",
        "take-c, PLAYED: the field running, then the tree paused, then the "
        "player killed by walking onto a trap five times. The take asserts the "
        "player did not move for 78 paused frames and that emitting went false.",
        "The field is running. Now the tree is paused - and the motes freeze "
        "with it, because the node inherits its process mode. A paused game "
        "with drifting dust reads as a bug.",
        10, "c", [0.3, 10.2],
        [{"at": 0.06, "event": "the field, running"},
         {"at": 0.22, "event": "paused - everything holds"},
         {"at": 0.62, "event": "resumed, and the player walks"},
         {"at": 0.86, "event": "the first trap"}]))

    out.append(footage(
        "B07B", "RESULT",
        "take-c, second window: the fifth hit and the eight seconds after "
        "it. The tail is 8.6 s because that is one mote lifetime; a three "
        "second tail showed a field that looked unchanged, which is true "
        "and useless.",
        "And this is how it stops. The fifth hit kills the player, emitting "
        "goes false - and nothing is cut off. The sixty motes already in "
        "the air finish their eight seconds on the colour ramp.",
        11, "c", [10.3, 20.27],
        [{"at": 0.08, "event": "the fifth hit"},
         {"at": 0.20, "event": "emitting goes false"},
         {"at": 0.55, "event": "the field begins to thin"},
         {"at": 0.92, "event": "empty, at one full lifetime"}]))

    # ------------------------------------------- PAIR 4: the process shader
    out.append(workbench(
        "B08", "BUILD",
        "C4 CODE. The generated process shader. The author converted "
        "PPM_dust to a ShaderMaterial in the editor and saved it; the file is "
        "a copy, read-only, and nothing in the game loads it. Paired with B09.",
        "This is Godot's own process shader, generated by converting the dust "
        "emitter's material in the editor. Three hundred and eighty four "
        "lines; these two are the ones to read. Line one sixty one multiplies "
        "the particle's scale by a texture lookup into scale curve, at the "
        "particle's own normalised lifetime. Line one sixty two does the same "
        "to its colour through colour ramp. That is what a curve in the "
        "Inspector actually is - a one dimensional texture, sampled once per "
        "particle per frame, on the graphics card. And look at line one sixty: "
        "compile-time add textures. Those two lines only exist because this "
        "material carries a ramp and a curve. Convert an empty material and "
        "the comment is there with nothing under it.",
        48,
        "Two lines, and what a curve really is",
        "godot/shaders/particles_generated.gdshader", 159, 164,
        [{"label": "Dust 2.0 to 3.5",
          "value": "scale_min/max are one mix() at line 150. Line 161 is the curve over life."},
         {"label": "Why Dust",
          "value": "Flash carries both too but lives 0.12 s. Dust grows over 0.45 s, so a strip reads it."}],
        [{"at": 0.26, "line": 161, "label": "scale over life, sampled"},
         {"at": 0.50, "line": 162, "label": "colour over life, sampled"},
         {"at": 0.76, "line": 160, "label": "Godot's insertion point"}]))

    out.append(still(
        "B09", "RESULT",
        "The two shader lines beside the brief settings they implement, with "
        "the engine output those settings produce. Frames 15 and 20 of the "
        "kept r1 capture - FIXTURE - where Dust is the only emitter still "
        "alive. The deltas are recomputed at build time.",
        "And here is what those two lines do to a picture. Frame fifteen and "
        "frame twenty of the kept capture, cropped to the trap. Section one "
        "point three of the brief gives Dust a scale curve that rises from "
        "nought point six to one point eight, and a colour ramp that ends at "
        "nothing. Line one sixty one is the first of those and line one sixty "
        "two is the second, and between frame ten and frame twenty the burst "
        "goes from ten by twelve logical pixels to sixty nine by sixty nine "
        "while its brightest channel falls from two hundred and thirty to "
        "ninety two. Wider, and dimmer. The settings are rows in a table in a "
        "document. The lines are the arithmetic.",
        44, "media/B09.png",
        "The brief's rows, the shader's lines, and the frames they make",
        "captures/hit_burst/r1/ - FIXTURE, preview scene, 30 fps",
        "frames 15 and 20, cropped to the trap",
        [{"at": 0.08, "event": "the two frames appear"},
         {"at": 0.44, "event": "the setting and the line pair up"},
         {"at": 0.78, "event": "the measured widths land"}]))

    # ------------------------------------------ PAIR 5: the derived event, C
    out.append(workbench(
        "B10", "BUILD",
        "C5 CODE. Effect C's event does not exist in the game; it is derived "
        "from measured position delta. Paired with B11.",
        "Effect C is dust under the feet, and this game has no footstep "
        "signal. The player script has a position, a velocity and a floor "
        "check, and nothing that says a foot just landed. So the event is "
        "derived, and the four lines on screen are the whole derivation. "
        "Distance travelled on the ground accumulates; every twenty four "
        "pixels, one puff. Not a timer, which is right at exactly one speed, "
        "and not a per-frame chance, which changes with the frame rate. Two "
        "details earn their place. It is a while, not an if, because at thirty "
        "frames a second one frame can cover more than one stride. And the "
        "spawn is stepped back by the remainder, so the puff lands where the "
        "stride actually finished rather than where the player has already "
        "got to. Without that line the spacing was three point two pixels out "
        "at thirty frames a second and correct at sixty, which is the one "
        "thing this effect exists to not do.",
        56,
        "An event this game does not have",
        "godot/effects/step_dust_driver.gd", 112, 115,
        [{"label": "Why distance",
          "value": "A timer is right at one speed. Distance is right at any speed and rate."},
         {"label": "The back-date",
          "value": "_since_step IS the overshoot after the subtraction. Stepping back lands on the crossing."}],
        [{"at": 0.42, "line": 113, "label": "while, not if"},
         {"at": 0.72, "line": 115, "label": "the spawn, stepped back by the overshoot"}]))

    out.append(footage(
        "B11", "RESULT",
        "C5 RESULT. take-p again, the feet. Played: held keys only. The run "
        "east and the run west are in one unbroken take, so the mirror is "
        "visible rather than claimed.",
        "Twenty five puffs in that take. The trail runs two or three deep, "
        "because a puff outlives a stride - and when the player turns, the "
        "dust throws the other way.",
        10, "p", [1.9, 10.63],
        [{"at": 0.05, "event": "the trail, running east"},
         {"at": 0.34, "event": "the jump, and the landing puff"},
         {"at": 0.62, "event": "the turn"},
         {"at": 0.80, "event": "the dust throws the other way"}]))

    # ----------------------------------------------- PAIR 6: price and tests
    out.append(workbench(
        "B11A", "BUILD",
        "C6 CODE. What a headless run can and cannot price. Paired with B11B.",
        "Last pair, and it is about the instrument rather than the effect. All "
        "three of these are GPU particle nodes, and a headless run uses a "
        "dummy renderer: it draws nothing and it runs no particle process at "
        "all, because that process is a shader on the card. So the brief "
        "predicted that a headless measurement would read approximately zero "
        "for every one of them, and predicted it by construction rather than "
        "by hope. What is left to measure is the node's own bookkeeping, and "
        "the function under that comment is what counts it: how many "
        "scene instances each effect created and freed. That is CPU work a "
        "headless run does execute in full.",
        42,
        "What a dummy renderer can still weigh",
        "godot/tests/cost_effects.gd", 97, 104,
        [{"label": "Why instances",
          "value": "A one-shot effect spawns and frees a scene per event. That is ordinary CPU work."},
         {"label": "Why not FPS",
          "value": "With vsync on, FPS reads the refresh rate with the effects off and the same with them on."}],
        [{"at": 0.30, "line": 101, "label": "the only thing left to weigh"},
         {"at": 0.66, "line": 104, "label": "counted once per instance, not per frame"}]))

    out.append(still(
        "B11B", "RESULT",
        "The recorded output of scripts/run-test.sh cost_effects.gd 60 300, "
        "drawn verbatim at build time from evidence/a6/cost-effects.txt, above "
        "a frame of take-r with three bursts alive. The GPU budgets are NOT "
        "settled by this script and the card says so.",
        "The prediction held: microseconds, against budgets written in "
        "milliseconds. But read the table the right way round. The ordering "
        "is stable - Effect B, one persistent node that creates nothing, is "
        "the smallest in both runs, and A and C, which spawn and free a "
        "scene per event, are larger. The microsecond figures themselves are "
        "not. Effect B moves by three microseconds between the two runs, and "
        "each run's own baseline spread claims half of one. The column that "
        "holds still is instances, and that is what a headless run is really "
        "weighing: not the particle process, which never ran at all, but the "
        "cost of making and freeing a scene. None of this settles a budget. "
        "The budgets are GPU time, read in the Visual Profiler on hardware, "
        "and the brief puts that row under HUMAN for exactly this reason.",
        58, "media/B11B.png",
        "The headless price, and the one thing it can weigh",
        "evidence/a6/cost-effects.txt - 400 frames per condition, 60 fps",
        "take-r frame, three bursts alive; the table is the recorded output",
        [{"at": 0.06, "event": "the three bursts hold"},
         {"at": 0.40, "event": "the baseline and its noise floor"},
         {"at": 0.74, "event": "B below the floor, A and C above it"}]))

    # ---------------------------------------------------- WALKER BOOKEND 3/4
    out.append(graphic(
        "B12", "VERDICT",
        "WALKER BOOKEND 3/4 - verdict. Implemented work, limitations and human "
        "judgment kept apart. Human/AI split, texture sources, revision shown, "
        "one next step.",
        "So. Written by hand, by the author: the brief, every verdict in the "
        "tuning log, and the material conversion that produced the process "
        "shader. Written by Claude: three effect scenes, three preview scenes, "
        "the two drivers, two hundred and forty nine checks, the cost "
        "script and the capture rigs. Measured, not asserted: the stride "
        "cadence is the same distance at thirty, sixty and a hundred and forty "
        "four frames a second, deviation zero. Preprocess at eight gives a "
        "full field on frame one and at zero gives two per cent of it. Three "
        "bursts can be alive at once and playing this room reaches one. "
        "Textures: there are none. Not one of the six emitters has a texture "
        "assigned - the look is colour ramps, scale curves and a blend mode, "
        "so there is nothing to credit and nothing to license. Claude's own "
        "work needed catching more than once. Four checks that could not fail "
        "shipped green, one of them literally written as x or true. A capture "
        "helper threw on every call the moment an instance freed itself. And "
        "the first generated shader was converted from an empty material - it "
        "loaded, it reported the right mode, it declared thirty eight "
        "uniforms, and it had no texture call in it at all. The author found "
        "that one by counting lines. The budgets were measured last. In a "
        "real windowed run the whole frame, with all three effects at the "
        "brief's ceiling, costs twenty-two thousandths of a millisecond "
        "against a combined budget of six tenths - met with more than an "
        "order of magnitude to spare. And the table does not hold together: "
        "all three effects together measured cheaper than Effect B on its "
        "own, which cannot be true, because all three contains B. Both runs "
        "reproduced to the last digit, and repeatable is not the same as "
        "true. What it establishes is the ceiling, not the price. Still "
        "open, and this is the honest part: Effect B's loop produced a "
        "verdict of keep with no "
        "setting changed, which is not the same as a revision. Both B and C "
        "drift dust below the floor line, between eleven and twenty nine per "
        "cent of it, and the only instrument that sees it is a difference "
        "image. The next step is a tuning revision for B and for C, the two "
        "loops that never closed. Everything you have seen came from "
        "one game source revision, named on the card.",
        120, "ClaudeVerdictArtifact",
        {
            "artifactTitle": "Verdict",
            "artifactHeading": "Who wrote what, and what was measured",
            "brandLabel": "@NikBearBrown",
            "artifactLines": [
                "By hand: the brief, every tuning verdict, the material conversion.",
                "By Claude: 3 effect scenes, 3 previews, 2 drivers, 249 checks, the rigs.",
                "Measured: stride cadence identical at 30 / 60 / 144 fps, 0.0000 px deviation.",
                "Measured: preprocess 8.0 gives 518 mote px on frame 1; 0.0 gives 12.",
                "Measured: 3 bursts can overlap; playing this room reaches 1. Peak in play 32.",
                "Textures: none. No emitter has one - ramps, curves and a blend mode only.",
                "Caught in Claude's work: 4 checks that could not fail; a shader from an empty material.",
                "Measured: whole frame 0.022 ms GPU, three effects at the ceiling. Budget 0.60.",
                "Open: all three read cheaper than B alone - a ceiling, not a price. B and C unrevised.",
            ],
        },
        "reveal",
        [{"at": 0.05, "event": "the three columns appear"},
         {"at": 0.40, "event": "the measured column fills"},
         {"at": 0.82, "event": "the open column holds"}]))

    # ---------------------------------------------------- WALKER BOOKEND 4/4
    out.append(graphic(
        "B13", "TURN",
        "WALKER BOOKEND 4/4 - Your Turn. One bounded change with a prediction. "
        "Liam signs off here, not on the outro card.",
        "Your turn. Take the prompt on screen, then do the bounded version "
        "yourself. Open any particle effect you have and find the one setting "
        "whose job you could not demonstrate if someone asked. Write down what "
        "the frame should look like with that setting at its default, before "
        "you change anything. Then change it, capture the same frame in "
        "engine, and count the pixels that moved. If the number is zero, you "
        "have just learned that the setting does nothing where you thought it "
        "did - and that is a finding, not a mistake. The whole discipline is "
        "writing the prediction down first, because a prediction you write "
        "afterwards is a description. Liam, signing off.",
        44, "ClaudeComposerAsk",
        {
            "greeting": "Your turn",
            "topic": "WALKER - ONE BOUNDED CHANGE",
            "segment": "predict, then measure",
            "command": (
                "Please use Walker to capture the same six frames of my "
                "particle effect before and after one setting change, and "
                "count the pixels that differ on each frame. I will write the "
                "prediction into the brief first. Tell me plainly which frames "
                "disagree with what I wrote."),
            "runningText": "one setting, and a prediction written first",
            "modelLabel": "Claude Opus 5",
            "effortLabel": "High",
        },
        "type-on",
        [{"at": 0.04, "event": "the composer card returns"},
         {"at": 0.26, "event": "the prompt types on"},
         {"at": 0.76, "event": "the bounded exercise holds"}]))

    outro = graphic(
        "B14", "OUTRO",
        "LOCKED ClaudeTitleOutro. Exact title, @NikBearBrown, one slug-seeded "
        "mascot, no subline, stock jingle only. No narration and no game audio: "
        "`audio_policy: silence` is what keeps it mute - without it the "
        "compiler refuses the whole reel for a missing mp3, because every "
        "other beat has one.",
        "", 5, "ClaudeTitleOutro",
        {"title": TITLE, "slug": SLUG, "durationSeconds": 5.0},
        "hold", None)
    outro["audio_policy"] = "silence"
    outro["shot"].pop("show")
    out.append(outro)

    return out


def main() -> int:
    REEL.mkdir(parents=True, exist_ok=True)
    path = REEL / "beat_sheet.json"

    # Measured narration, if generate_audio_kokoro.py has already run. Cue
    # fractions become seconds against the MEASURED length; before the audio
    # exists they fall back to the estimate, which is only ever used to get
    # the first pass of narration generated.
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
            # Carry the Remotion provenance stamp across a rebuild when the
            # props it describes have not changed. `compile.py:485` refuses a
            # beat that has a pattern and no `rendered.at`, so a rebuild that
            # dropped every stamp would silently make the whole reel
            # uncompilable -- and the batch would not re-render anything,
            # because it skips any beat that already has a media file. A beat
            # whose props DID change keeps no stamp, which is the signal to
            # force it.
            was = previous_props.get(bid)
            if was is not None:
                stamp = was.pop("rendered", None)
                if stamp is not None and was == props:
                    b["shot"]["remotion"]["rendered"] = stamp
        for mark in b["shot"].get("show", []) or []:
            mark["at"] = "%.2f" % float(mark["at"])
        if bid in measured:
            b["actual_duration_s"] = round(seconds, 2)
            # Only when the file is really there. The locked outro carries
            # `audio_policy: "silence"` and has no mp3 on purpose; naming one
            # anyway points the compiler at a file that does not exist.
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
            "audience": "Course reviewers reading a Godot particle-effect pass",
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
            "greeting_note": "hello lexicon: Sawubona (Zulu), one word. Wagwan is Bear's alone.",
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
