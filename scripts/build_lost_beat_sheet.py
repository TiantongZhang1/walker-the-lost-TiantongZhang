#!/usr/bin/env python3
"""Write the Assignment 5 film's beat_sheet.json.

Every code excerpt is READ FROM THE FILE at build time and its line range is
recorded beside it, so a panel cannot quote source that has moved. The checker
compares excerpt text against both the file and the beat's props; building it
any other way means typing the code twice and hoping.

Result stills are copied into the reel's media/ so the ledger can hash a
reel-relative path, as references/evidence.md requires.

    python -X utf8 scripts/build_lost_beat_sheet.py

Durations are estimates until Kokoro has spoken the lines.
generate_audio_kokoro.py writes actual_duration_s and audio_file back into
the sheet itself, so the order is: build, speak, build again. The second
build carries the measured numbers forward for every beat whose words did
not change, and drops the render stamp of any beat whose props or duration
did. There is no separate timing pass - scripts/finalise_beat_timing.py is
walker-ninja's and refuses to run.
"""
from __future__ import annotations

import base64
import io
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-gamedev"
MEDIA = REEL / "media"

SWEEP = "captures/a5/materials/SWEEP-REPORT.txt"
TRAP = "godot/shaders/trap_warning.gdshader"
DRIVER = "godot/features/traps/trap_warning_driver.gd"
HINT = "godot/shaders/hint_bands.gdshader"
SURF = "godot/shaders/dungeon_surface.gdshader"
# Godot's own output, saved unedited: StandardMaterial3D -> Convert to
# ShaderMaterial. It is in the film as the engine's statement of the
# language, and because the assignment asks for two of its lines beside
# their equivalents in the hand-written shader.
GEN = "godot/shaders/standard_generated.gdshader"

# The five result-beat cards, written by scripts/compose_lost_evidence.py
# from captures that are committed elsewhere in the repository. Run that
# script (and compose_a5_extras.py before it) first; these are inputs here,
# not outputs.
CARDS = ("B03A", "B07", "B09", "B11", "B11B")


def excerpt(rel: str, start: int, end: int) -> str:
    """Lines start..end inclusive, one-based, joined without a final newline."""
    rows = (ROOT / rel).read_text(encoding="utf-8").split("\n")
    if end > len(rows):
        raise SystemExit("%s has %d lines, asked for %d" % (rel, len(rows), end))
    return "\n".join(rows[start - 1:end])


def beat(bid, act, role, narration, seconds, shot):
    return {"beat_id": bid, "act": act, "role_note": role,
            "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
            "estimated_duration_s": seconds, "shot": shot}


def code_shot(title, rel, start, end, notes, cues, show, font=23):
    return {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "code-highlight", "show": show,
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "code", "title": title,
                "project": "walker-the-lost-TiantongZhang",
                "path": "%s  lines %d-%d" % (rel, start, end),
                "source": rel, "code": excerpt(rel, start, end),
                "startLine": start, "codeFontSize": font,
                "inspectorLabel": "Source notes - not Inspector values",
                "notes": notes, "cues": cues}}}


def footage_shot(window, show):
    return {"type": "FOOTAGE", "class": "SHOW", "source": "capture",
            "motion": "gameplay", "capture": "take-w",
            "evidence_media": "capture/take-w.mp4",
            "window_s": window, "show": show}


def recorded(report: str, start: str, stop: str) -> str:
    """A block of a recorded report, verbatim. Nothing here is retyped."""
    rows, on = [], False
    for line in (ROOT / report).read_text(encoding="utf-8").splitlines():
        if start in line:
            on = True
        if on:
            rows.append(line.rstrip())
        if on and stop in line and len(rows) > 1:
            break
    if not rows:
        raise SystemExit("no block %r in %s" % (start, report))
    return chr(10).join(rows)


def line_of(report: str, needle: str) -> str:
    """One recorded line, verbatim. `recorded()` cannot take a single line:
    its stop test needs a second match, so start == stop ran to end of file
    and put the report's prose on screen."""
    for line in (ROOT / report).read_text(encoding="utf-8").splitlines():
        if needle in line:
            return line.rstrip()
    raise SystemExit("no line containing %r in %s" % (needle, report))


def still_shot(title, bid, label, image_label, show):
    """A result beat: one full-frame card, no editor chrome.

    These used to be GodotDevWorkbench `asset` beats. Two things were wrong
    with that, and both were found by rendering a beat and looking at it.

    `asset` lays out {code}{image}, so the measured table went in the `code`
    prop - and verify_gamedev.py:68 requires every GodotDevWorkbench beat
    with a non-empty `code` to carry a source excerpt record and to be the
    code half of a pair. A table of measurements is neither, so the official
    check failed: 'Displayed code lacks an excerpt record'. Emptying `code`
    passes the check and renders half a frame of blank dark panel.

    And the workbench's chrome reads "Godot editor reconstruction". That is
    true of the code beats and false of these: they are frames a real GPU
    drew. SHOTLIST.md always said so; the component was saying otherwise.

    So the card is composed at full 3840 x 2160 by
    scripts/compose_lost_evidence.py and dropped as media/<bid>.png, which
    the compiler resolves as a STILL. `motion: "hold"` keeps it still - a
    Ken Burns move across a table of numbers is unreadable."""
    return {"type": "STILL", "class": "SHOW", "source": "capture",
            "motion": "hold", "evidence_media": "media/%s.png" % bid,
            "title": title, "path": label, "image_label": image_label,
            "show": show}


METADATA = {
    "title": "TheLostShaders_TiantongZhang",
    "slug": "claude-liam-walker-the-lost-gamedev",
    "topic": "WALKER - GODOT SHADERS AND MATERIALS TEARDOWN",
    "kind": "gamedev", "playlist": "Brutalist", "brand": "claude-liam",
    "audience": "Course reviewers reading a Godot shader and material pass",
    "register": "Teardown", "engine": "kokoro", "voice": "am_onyx",
    "voice_kokoro": "am_onyx", "palette": "claude", "style_preset": "claude",
    "ground": "#FAF9F5", "aspect_ratio": "16:9", "fit": "contain",
    "captions": False, "channel_title": "@NikBearBrown", "channel": "@NikBearBrown",
    "folderLabel": "@NikBearBrown", "greeting": "Sawubona, Liam",
    "greeting_note": "hello lexicon: Sawubona (Zulu), one word. Wagwan is Bear's alone.",
    "mode": "walker", "teaching_contract": "code-then-result-v1", "game": "godot",
}


def require_cards() -> None:
    """The compiler resolves media/<bid>.png as a beat's STILL, so a card
    that was never composed becomes a grey slate in the master rather than
    an error. Fail here instead, and name the script that makes them."""
    missing = [c for c in CARDS if not (MEDIA / (c + ".png")).is_file()]
    if missing:
        raise SystemExit(
            "missing result cards: %s - run scripts/compose_a5_extras.py and "
            "then scripts/compose_lost_evidence.py first" % ", ".join(missing))


require_cards()

B = []

# ------------------------------------------------------- WALKER BOOKEND 1/4
B.append(beat(
    "B00", "ASK",
    "WALKER BOOKEND 1/4 - ClaudeComposerAsk. Reconstructed prompt, said aloud "
    "to be a reconstruction. Liam named in the first breath.",
    "Sawubona - this is Liam, in for Bear. The prompt on screen is a "
    "reconstruction, written to be illustrative. It is not a transcript. The "
    "game under it is real: a dungeon slice in Godot four. What we are taking "
    "apart today is not the game logic. It is three hand-written shaders, and "
    "one stubborn question - what does a hint actually do to a number.",
    23,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
     "show": [{"at": "0.03", "event": "composer card fades in"},
              {"at": "0.14", "event": "greeting lands"},
              {"at": "0.32", "event": "the Walker prompt types on"},
              {"at": "0.82", "event": "RECONSTRUCTION label holds"}],
     "remotion": {"pattern": "ClaudeComposerAsk", "props": {
         "greeting": "Sawubona, Liam",
         "topic": "WALKER - GODOT SHADERS AND MATERIALS TEARDOWN",
         "segment": "The Lost, lit",
         "command": (
             "Please use Walker to convert my game design document about The "
             "Lost - a side-view dungeon crawler where every hazard announces "
             "itself before it can hurt you - into a Godot project. I will "
             "write the shader that does the announcing by hand; you write the "
             "driver and the tests that prove it."),
         "runningText": "RECONSTRUCTION - this prompt was never sent",
         "modelLabel": "Claude Opus 5", "effortLabel": "High"}}}))

# ------------------------------------------------------- WALKER BOOKEND 2/4
B.append(beat(
    "B01", "RESULT",
    "WALKER BOOKEND 2/4 - hesitant writer, one working single-word correction "
    "with measured time to complete it.",
    "Here is what actually changed. A spike trap that turns - correction - "
    "that ramps red across four tenths of a second before it fires. Two "
    "materials from one shader, on two identical slimes. And a three-pixel "
    "image, sampled twice through the same file, that settles an argument "
    "about colour. Ninety-nine automated checks stand behind that, and four "
    "deliberate breakages stand behind the checks.",
    36,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "write-on",
     "show": [{"at": "0.06", "event": "the summary begins writing"},
              {"at": "0.30", "event": "'turns' struck through, 'ramps' written in"},
              {"at": "0.72", "event": "the counts land"}],
     "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
         # Short on purpose. A hesitant writer types at human speed, so a
         # long block leaves the card half empty for most of the beat - at
         # 26 ms a character and six lines, three were still missing at 85 %
         # of the beat's length, which Gate V reads as underfill and is
         # right to.
         "text": chr(10).join([
             "Three shaders, written by hand.",
             "A spike trap that turns red before it fires.",
             "Ninety-nine checks. Four mutations.",
             "Fourteen predicted values, none wrong."]),
         # triggerWords and replacementWords are positionally matched: the
         # writer types the first, reconsiders, and replaces it with the
         # second. Setting only triggerWords leaves replacementWords at its
         # demo default and "turns" became "wolf" on screen.
         "triggerWords": "turns",
         "replacementWords": "ramps",
         # 50 ms a character spends 14 s of a 19.7 s beat still typing, so
         # the card is half empty for most of its length.
         "charMs": 16,
         "face": "serif", "fontSize": 62, "lineSpacing": 1.35,
         "align": "left",
         # contextTitle and contextItems are the component's own way to carry
         # more than the typed block: a serif heading at the top and a row of
         # bordered cards below it. Without them this card is four lines of
         # text on an empty page, which measured 4-18 % of the safe area.
         "contextTitle": "What was built",
         "brandLabel": "@NikBearBrown",
         # TWO lines per card, measured off a render. The card is a fixed
         # height that fits two rows of detail text at about 37 characters
         # each; a third row sets ON the bottom border and past it. All
         # three of these were three rows and all three clipped. Nothing
         # warned - the component has no overflow guard and Gate V reads
         # fill, not legibility.
         "contextItems": [
             {"label": "By hand",
              "detail": "3 shaders, 4 commits, one author, plus the "
                        "language notes."},
             {"label": "By Claude",
              "detail": "The per-trap driver, 99 checks, three rigs, "
                        "the audit."},
             {"label": "Predicted first",
              "detail": "8 pixels and 6 bands, written into the "
                        "brief first. None wrong."}]}}}))

# ------------------------------------------- PAIR 1  the colour line -> ramp
B.append(beat(
    "B02", "BUILD",
    "C1 CODE. trap_warning.gdshader in full, hand-written. Paired with B03.",
    "This is the whole shader. Four lines of declaration and one line that "
    "changes a colour. Mix takes the pixel the sprite already has, the warning "
    "red, and a number between them. The number is not time - it is game "
    "state, and it arrives from outside. The window is four tenths of a "
    "second, and the detection box that starts it is one seven five - not a "
    "number anybody chose, but the walking speed multiplied by that window. "
    "Note what the first argument is: "
    "COLOR, not a texture sample. COLOR already carries the sprite's texture "
    "multiplied by its modulate. Sampling the texture again by hand would "
    "throw that multiplication away, and a trap the game had faded out would "
    "ignore the fade entirely.",
    32,
    code_shot("One line changes the colour", TRAP, 1, 7,
              [{"label": "Why COLOR, not TEXTURE",
                "value": "COLOR arrives as texture x modulate x vertex colour. Re-sampling discards two of the three."},
               {"label": "Why not TIME",
                "value": "TIME is global engine time. It cannot express time since THIS trap armed."}],
              [{"at": 3.0, "line": 2, "label": "the driven uniform, 0 to 1"},
               {"at": 11.0, "line": 3, "label": "the warning red, set by the material"},
               {"at": 19.0, "line": 6, "label": "the one line that changes a colour"}],
              [{"at": "0.04", "event": "the excerpt is framed"},
               {"at": "0.18", "event": "line 2 highlights"},
               {"at": "0.38", "event": "line 3 highlights"},
               {"at": "0.62", "event": "line 6 highlights"}], font=26)))

B.append(beat(
    "B03", "RESULT",
    "C1 RESULT. take-w, trap 1's cycle. The log puts the warning at frame 109, "
    "t 1.82, player_x 174.4; the window runs 0.30-4.85 s so the footage "
    "outlasts the narration.",
    "There it is. Red before the player arrives, spikes while they are "
    "standing on it.",
    6,
    footage_shot([0.30, 4.85],
                 [{"at": "0.05", "event": "the trap is flush and nearly invisible"},
                  {"at": "0.22", "event": "the red begins, player still short of it"},
                  {"at": "0.70", "event": "full red, player centred"},
                  {"at": "0.86", "event": "the spikes arrive"}])))

# --------------------------------- the controlled series, all four at once
# Not a pair. B03 is already B02's result; this is the measurement the
# assignment asks for by name - "your controlled-value captures" - and a
# single beat of four side-by-side frames is the only way a controlled
# series reads as one. The table beside it is captures/a5/REPORT.txt,
# verbatim, which is why no excerpt record claims it.
B.append(beat(
    "B03A", "RESULT",
    "Controlled-value captures, trap 1, windowed run 2026-10-24. Four values "
    "of warn_amount set from code; the two named pixels sampled from the "
    "image, not from the logical coordinate. Grid composed by "
    "scripts/compose_a5_extras.py from the four committed PNGs.",
    "Four controlled values, written from code, captured in engine. Nought. "
    "Nought point five. One. And two, which the range hint was supposed to "
    "forbid. All eight pixel values were written into the brief before the "
    "capture rig existed, and all eight landed exact - worst channel "
    "difference, zero. Look at the last one. Two point zero went straight "
    "through the hint. Mix extrapolates past the target instead of stopping "
    "at it, two of the spike tip's channels go negative, the write to COLOR "
    "clamps them, and the tip comes out pure red. That is a result no other "
    "explanation produces by accident.",
    34,
    still_shot("Four controlled values, and the pixels they predicted", "B03A",
               "captures/a5/ - windowed run 2026-10-24, Forward+, RTX 5080",
               "the four captures, and REPORT.txt beneath them, verbatim",
               [{"at": "0.06", "event": "the four frames appear"},
                {"at": "0.40", "event": "the measured and predicted columns align"},
                {"at": "0.78", "event": "the 2.0 row is marked - pure red"}])))

# ------------------------------------- PAIR 2  the driver -> one trap at a time
B.append(beat(
    "B04", "BUILD",
    "C2 CODE. trap_warning_driver.gd 62-76, agent-written. Paired with B05.",
    "The shader is the author's; this driver is not. It does two things. It "
    "duplicates the material, because a sub-resource inside a packed scene is "
    "shared by every instance of that scene - without this line all three "
    "traps hold one material and warn together. Then, once a frame, it copies "
    "the trap's state into the uniform. It reads game state and never writes "
    "it. And it asks the shader whether that uniform exists, because setting a "
    "name the shader does not declare writes nowhere and reports nothing.",
    34,
    code_shot("One material per trap, one write per frame", DRIVER, 62, 76,
              [{"label": "F1, avoided",
                "value": "Sub-resources are shared. Without duplicate(), one red lights all three."},
               {"label": "F5, caught at startup",
                "value": "Writing an undeclared uniform name is silent, so the driver asks first."}],
              [{"at": 8.0, "line": 65, "label": "this trap's own parameter block"},
               {"at": 20.0, "line": 68, "label": "ask the shader what it declares"},
               {"at": 28.0, "line": 76, "label": "state in, uniform out, once a frame"}],
              [{"at": "0.05", "event": "the excerpt is framed"},
               {"at": "0.24", "event": "line 65 highlights"},
               {"at": "0.58", "event": "line 68 highlights"},
               {"at": "0.82", "event": "line 76 highlights"}])))

B.append(beat(
    "B05", "RESULT",
    "C2 RESULT. take-w across all three traps, 0.60-11.33 s. The take's own "
    "probe counted zero frames in 709 with more than one trap lit.",
    "Watch the red move. Three traps, one shader, three materials - and the "
    "warning never appears on two at once. The driver counted it: seven "
    "hundred and nine frames, zero with more than one lit.",
    10,
    footage_shot([0.60, 11.33],
                 [{"at": "0.04", "event": "trap one warns, two and three stay flush"},
                  {"at": "0.34", "event": "trap one retracts"},
                  {"at": "0.52", "event": "trap two takes the red"},
                  {"at": "0.84", "event": "trap three, and the first two are dark"}])))

# --------------------------------- PAIR 3  the hint experiment -> the numbers
B.append(beat(
    "B06", "BUILD",
    "C3 CODE. hint_bands.gdshader 1-7, hand-written. Paired with B07.",
    "Two samplers. The same file is bound to both. The only difference between "
    "them is four words on line four - source colour - and a boolean picks "
    "which one reaches the screen. Unshaded matters here: without it the light "
    "would scale the result and the numbers would measure the lamp instead of "
    "the sampler. Nearest filtering matters too, because the image is three "
    "pixels wide and linear filtering would blend the answer.",
    30,
    code_shot("The same file, sampled two ways", HINT, 1, 7,
              [{"label": "Why unshaded",
                "value": "Any lighting multiplies ALBEDO, and the band stops being evidence."},
               {"label": "Why nearest",
                "value": "The image is 3 x 1. Linear filtering would average the bands away."}],
              [{"at": 2.0, "line": 2, "label": "no lighting may touch this"},
               {"at": 10.0, "line": 4, "label": "this one decodes"},
               {"at": 16.0, "line": 5, "label": "this one does not"}],
              [{"at": "0.04", "event": "the excerpt is framed"},
               {"at": "0.14", "event": "line 2 highlights"},
               {"at": "0.40", "event": "line 4 highlights"},
               {"at": "0.60", "event": "line 5 highlights"}], font=26)))

B.append(beat(
    "B07", "RESULT",
    "C3 RESULT. captures/a5/hint_experiment.png, real windowed run. All six "
    "bands exact against the prediction committed on 2026-10-23.",
    "Both quads, one frame. The file stores sixty four, one twenty eight and "
    "one ninety two. Through the sampler that decodes, those are the numbers "
    "that come out - decoding and the display's encoding are inverses. Through "
    "the one that does not, every band is brighter: one thirty seven, one "
    "eighty eight, two twenty five. All six were predicted in writing two days "
    "before anything could render them, and all six landed exactly.",
    27,
    still_shot("The hint is worth seventy three counts", "B07",
               "captures/a5/hint_experiment.png + HINT-REPORT.txt",
               "engine capture above, recorded numbers below, rendered verbatim",
               [{"at": "0.06", "event": "the two quads appear"},
                {"at": "0.40", "event": "the measured table reveals"},
                {"at": "0.80", "event": "64 -> 137 is marked as the largest error"}])))

# ------------------------------- PAIR 4  the textured shader -> two materials
B.append(beat(
    "B08", "BUILD",
    "C4 CODE. dungeon_surface.gdshader fragment, lines 15-27, hand-written. "
    "Paired with B09. Author's comments are in Chinese and shown verbatim.",
    "The spatial shader. One read from the mask, one read from the stone, and "
    "then two outputs. Albedo gets the stone darkened where the mask says "
    "water pools. Roughness is mixed between a dry value and a wet one by the "
    "same mask. Two numbers written, and Godot does the lighting - in plain "
    "GLSL the whole reflectance model would be yours to write. The mask is "
    "data, not a picture: its numbers mean how submerged, not how bright.",
    31,
    code_shot("Two outputs, one mask", SURF, 15, 27,
              [{"label": "Data, not a picture",
                "value": "No source_color here: decoded, 0.5 becomes 0.21 and the waterline moves."},
               {"label": "What Godot does next",
                "value": "These feed the engine's lighting. Plain GLSL means writing the BRDF."}],
              [{"at": 4.0, "line": 17, "label": "how submerged, 0 to 1"},
               {"at": 14.0, "line": 23, "label": "darkened where water pools"},
               {"at": 22.0, "line": 26, "label": "dry to wet, by the same mask"}],
              [{"at": "0.05", "event": "the excerpt is framed"},
               {"at": "0.20", "event": "line 17 highlights"},
               {"at": "0.52", "event": "line 23 highlights"},
               {"at": "0.76", "event": "line 26 highlights"}])))

B.append(beat(
    "B09", "RESULT",
    "C4 RESULT. captures/a5/materials/00-baseline.png under section 8's "
    "lighting. Sweep numbers from captures/a5/materials/SWEEP-REPORT.txt.",
    "Same mesh, same light, same shader. The difference is three values in a "
    "text file. The right-hand slime is darker, slightly green, and carries a "
    "sharp highlight where the dry one is matte - that highlight is roughness "
    "nought point nought eight. Across twelve sweep captures the dry slime "
    "measured fifty, fifty six, fifty five every single time, unchanged to the "
    "count, while the flooded one moved for every uniform. One material, one "
    "object.",
    28,
    still_shot("One shader, two materials", "B09",
               "captures/a5/materials/00-baseline.png + SWEEP-REPORT.txt",
               "engine capture above, two of the four swept uniforms below",
               [{"at": "0.06", "event": "the pair appears"},
                {"at": "0.42", "event": "the highlight on the flooded slime is marked"},
                {"at": "0.78", "event": "the sweep numbers reveal"}])))

# --------------------------------- PAIR 5  the mutation -> the silent failure
B.append(beat(
    "B10", "BUILD",
    "C5 CODE. hint_bands.gdshader lines 4-5, the two samplers at reading size. "
    "The mutation deleted source_color from line 4 and was restored. Paired "
    "with B11.",
    "Back to those two lines. Delete source colour from the first one and "
    "nothing complains. The shader still compiles. There is no shader error in "
    "the log. And here is the part that matters: ask the engine to describe "
    "both uniforms and it returns the same answer for each - type twenty four, "
    "hint seventeen, texture two D. The engine cannot see this hint on a "
    "sampler at all. On a vector three it can. So a test built on the uniform "
    "list passes while the thing it was written to protect is gone.",
    36,
    code_shot("The hint the engine cannot see", HINT, 4, 5,
              [{"label": "What the engine reports",
                "value": "Both samplers come back type 24, hint 17, 'Texture2D'. Identical."},
               {"label": "The asymmetry",
                "value": "On a vec3 the same keyword IS visible: TYPE_COLOR, not TYPE_VECTOR3."}],
              [{"at": 4.0, "line": 4, "label": "delete four words here"},
               {"at": 18.0, "line": 5, "label": "and this line is now its twin"}],
              [{"at": "0.05", "event": "two lines, large"},
               {"at": "0.16", "event": "source_color highlights on line 4"},
               {"at": "0.55", "event": "the two lines are shown as identical to the engine"}], font=30)))

B.append(beat(
    "B11", "RESULT",
    "C5 RESULT. evidence/a5-mutations/mutation3a-hint-sampler_capture.png, the "
    "capture taken with the mutation in place. Restored afterwards.",
    "This is the same scene with those four words gone. Both quads now read "
    "one thirty seven, one eighty eight, two twenty five. The two sides of the "
    "experiment have become identical and its entire result has disappeared - "
    "silently. No error, no warning, no change in the uniform list. The only "
    "thing that caught it was a test that reads the shader's source text, and "
    "the suite now asserts the blindness itself so nobody simplifies that check "
    "away later.",
    28,
    still_shot("The same scene, four words lighter", "B11",
               "evidence/a5-mutations/ - captured with the shader mutated",
               "the same scene with source_color deleted; both quads identical",
               [{"at": "0.08", "event": "both quads appear, identical"},
                {"at": "0.46", "event": "the table reveals - the left column has moved"},
                {"at": "0.84", "event": "SHADER ERROR: 0 is marked"}])))

# ------------------ PAIR 6  what Godot writes itself -> the interface sweep
#
# The excerpt is 3-12 at the component's minimum font of 23, and both numbers
# came from looking at rendered frames rather than from arithmetic.
#
# The code panel is a fixed box - about 470 px of body at 1920x1080 - and it
# counts VISUAL rows, not source lines: at font 23 this file's long uniform
# declarations wrap to two rows each, so thirteen source lines came out as
# sixteen rows and the panel clipped mid-line. Two renders were needed to
# find that. The first asked for lines 3-20 at font 20, below the schema's
# min(23), and lost everything past line 17 plus two of three notes; the
# second asked for 3-15 at 23 and still lost line 14 and half the second
# note. 3-12 is ten source lines, three of which wrap, so thirteen rows.
#
# Narrowing it also improved the beat. Line 12's texture_metallic carries
# hint_default_white - the SAME hint family as the hint_default_black on
# line 4 of my own dungeon_surface.gdshader - so the pair being compared is
# now an exact parallel rather than a loose one.
B.append(beat(
    "B11A", "BUILD",
    "C6 CODE. standard_generated.gdshader 3-12. NOT hand-written: this is "
    "Godot's own output from StandardMaterial3D -> Convert to ShaderMaterial, "
    "saved unedited. Two of its lines are annotated against their equivalents "
    "in the hand-written dungeon_surface.gdshader. Paired with B11B.",
    "This file is the only shader here I did not write. I made a standard "
    "material in the editor, pressed convert to shader material, and saved "
    "what Godot produced without touching it - because it is the engine's own "
    "statement of what this language is. The Godot shading language is GLSL "
    "ES three point oh with the scaffolding taken away. There is no main "
    "function anywhere in this file. Line three declares a shader type "
    "instead, and that one word decides which built-ins exist and which "
    "outputs you are allowed to write. Now line seven against line twelve. "
    "Both are sampler two D, and both carry a hint. The colour texture's hint "
    "is source colour, so the engine decodes it. The metallic texture's hint "
    "only says what to assume when no texture is bound - hint default white - "
    "and there is no decode anywhere on that line. That is the same split I "
    "drew by hand: colour sampler on line three of my dungeon surface shader "
    "with source colour, data mask on line four with hint default black and "
    "nothing else. Godot's own generator puts the line in exactly the place I "
    "put it.",
    48,
    code_shot("What Godot writes when you ask it to", GEN, 3, 12,
              [{"label": "Generated 7 = mine, line 3",
                "value": excerpt(SURF, 3, 3).strip()},
               {"label": "Generated 12 = mine, line 4",
                "value": excerpt(SURF, 4, 4).strip()}],
              [{"at": 14.0, "line": 3, "label":
                "the language starts here - shader_type, not main()"},
               {"at": 30.0, "line": 7, "label":
                "colour sampler: source_color, so the engine decodes it"},
               {"at": 37.0, "line": 12, "label":
                "data sampler: a default hint, and no source_color"}],
              [{"at": "0.05", "event": "Godot's own file is framed"},
               {"at": "0.29", "event": "line 3 highlights"},
               {"at": "0.62", "event": "line 7 highlights"},
               {"at": "0.77",
                "event": "line 12 highlights against it, no source_color"}])))

B.append(beat(
    "B11B", "RESULT",
    "C6 RESULT. captures/a5/materials/, the interface sweep: every "
    "non-texture uniform of dungeon_surface.gdshader at both ends of its "
    "range. Grid composed by scripts/compose_a5_extras.py; the numbers are "
    "SWEEP-REPORT.txt verbatim. Also carries limitation 3, still open.",
    "An interface is only worth declaring if every control does something, so "
    "here is all four of them at both ends. Tint. Dry roughness. Water "
    "darkening. Water roughness - two groups, four uniforms, twelve frames, "
    "and the mean colour of the slime after each one. The dry slime is in "
    "every frame on purpose. It carries the other material, and across the "
    "whole sweep it does not move: fifty, fifty six, fifty five, twelve "
    "times. Only the flooded one changes. Whether any of these settings "
    "breaks the look rather than merely changing it is a human judgement, and "
    "it is the one thing in this assignment I am still recording as open.",
    40,
    still_shot("Four uniforms, both ends, one material moving", "B11B",
               "captures/a5/materials/ - engine capture, Forward+, RTX 5080",
               "each uniform at min and max; dry slime left, flooded right",
               [{"at": "0.06", "event": "eight frames appear, four uniforms"},
                {"at": "0.42", "event": "the measured means reveal"},
                {"at": "0.80", "event": "the dry column holds at 50, 56, 55 throughout"}])))

# --------------------------------------------------------------- VERDICT
B.append(beat(
    "B12", "VERDICT",
    "WALKER BOOKEND 3/4 - verdict. Implemented work, limitations and human "
    "judgment kept apart. Human/AI split stated.",
    "So. Written by hand, by the author: three shaders and the language notes. "
    "Written by Claude: the driver, four test suites, the capture rigs and the "
    "material audit. Measured, not asserted: eight predicted pixels exact, six "
    "predicted bands exact, and hint range does not clamp a value set from "
    "code - two point zero passed straight through and the pixel went pure "
    "red. What no headless run established: any of it. The dummy renderer "
    "draws nothing, so every colour claim here came from a windowed capture on "
    "real hardware. Every texture in this repository was written by code - two "
    "committed generators, nothing downloaded, no generative model, nothing to "
    "license. Everything you have seen came from one game source revision, e "
    "eight a e e eight nine. Claude's own work needed catching twice: a "
    "capture rig that sampled the window's clear colour instead of the frame, "
    "and a framing pass that was not idempotent and quietly put a card inside "
    "a card - which the automatic gate passed. Both were found by pulling a "
    "frame out and looking at it. Still open: the slice has no audio and no "
    "art beyond code-drawn blocks, and that port is Assignment Six's first "
    "job. The next step for the shaders themselves is a normal map, which is "
    "the one check this plan gave up when it chose code-written textures.",
    76,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "reveal",
     "show": [{"at": "0.05", "event": "the three columns appear"},
              {"at": "0.40", "event": "the measured column fills"},
              {"at": "0.80", "event": "the open column holds"}],
     "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
         "artifactTitle": "Verdict",
         "artifactHeading": "Who wrote what, and what was measured",
         "brandLabel": "@NikBearBrown",
         # EIGHT lines, and that is a ceiling rather than a preference.
         # ClaudeVerdictArtifact sizes its card from its content with no cap:
         # a 74 px title bar, 102 px of body padding, a 107 px heading and
         # about 69 px per line. Twelve lines came to roughly 1116 px on a
         # 1080 px frame, so the card clipped top and bottom and covered the
         # @NikBearBrown handle. Eight is 812 px, inside the 864 px title-safe
         # band. Found by pulling a frame at t = 60 s; nothing warned.
         #
         # Nothing the spec audit asked for was dropped to get there - the
         # texture sources, the revision, the mistakes caught in Claude's own
         # work and the one next step all survive. Pairs of related findings
         # were merged onto one line each, and each merged line is under
         # about 95 characters so it still sets as a single row.
         "artifactLines": [
             "By hand: three shaders and the language notes. Four commits, one author.",
             "By Claude: the driver, 99 checks, three capture rigs, the audit.",
             "Measured: 8 predicted pixels and 6 predicted bands, 0 error; hint_range does not clamp.",
             "Measured: source_color changes a sampler, not a vec3; R6 held in 709 of 709 frames.",
             "Textures: written by code - no download, no generative model. Revision e8aee89 throughout.",
             "Caught in Claude's work: a rig that read the clear colour; a card inside a card.",
             "Next: a normal map, so the _nor_gl / _nor_dx curl check applies.",
             "Open: no audio or art yet, and six narrated claims are reasoning, not measurement."]}}}))

# -------------------------------------------------------------- YOUR TURN
B.append(beat(
    "B13", "TURN",
    "WALKER BOOKEND 4/4 - Your Turn. One bounded change with a prediction, "
    "not blind copying. Liam signs off here.",
    "Your turn. Take the prompt on screen, then do the bounded version "
    "yourself: open the warning shader, change nothing, and predict what the "
    "base plate pixel becomes at a warning of nought point five. Mix is linear "
    "- the arithmetic is one line. Then set it from code and capture the frame "
    "in engine, not with a screenshot tool, and see whether your number "
    "survives contact. If it does not, that is a finding, not a mistake. Write "
    "down which one you trust and why. Liam, signing off.",
    35,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
     "show": [{"at": "0.04", "event": "the composer card returns"},
              {"at": "0.26", "event": "the prompt types on"},
              {"at": "0.74", "event": "the bounded exercise holds"}],
     "remotion": {"pattern": "ClaudeComposerAsk", "props": {
         "greeting": "Your turn",
         "topic": "WALKER - ONE BOUNDED CHANGE",
         "segment": "predict, then measure",
         "command": (
             "Please use Walker to add a second controlled value to my shader "
             "capture rig, write the predicted pixel into the brief before the "
             "rig can run, and tell me plainly if the capture disagrees with "
             "what I wrote."),
         "runningText": "one bounded change, and a prediction first",
         "modelLabel": "Claude Opus 5", "effortLabel": "High"}}}))

# ------------------------------------------------------------------ OUTRO
outro = beat(
    "B14", "OUTRO",
    "LOCKED ClaudeTitleOutro. Exact title, @NikBearBrown, one slug-seeded "
    "mascot, no subline, stock jingle only. No narration, no game audio. "
    "`audio_policy: silence` is what keeps the card mute - without it the "
    "compiler refuses the whole reel for a missing mp3/beat-B14.mp3, because "
    "every other beat has one. Liam signs off in Your Turn, not here.",
    "", 5,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "hold",
     "remotion": {"pattern": "ClaudeTitleOutro", "props": {
         "title": "TheLostShaders_TiantongZhang",
         "slug": "claude-liam-walker-the-lost-gamedev"}}})
outro["audio_policy"] = "silence"
outro["actual_duration_s"] = 5.0
B.append(outro)


# Fields the narration pass writes back. Rebuilding the sheet used to drop
# them, so every change to a camera window cost a full re-synthesis; they are
# carried over for any beat whose spoken words are byte-identical.
SPOKEN = ("actual_duration_s", "audio_file", "render_duration_s")


# Keys the renderer injects into props after the fact. There are none: an
# earlier version listed `durationSeconds` here, on the belief that the
# renderer wrote it. It does not. Remotion READS it - every composition this
# film uses computes durationInFrames as ceil(durationSeconds * 30) - and
# nothing was setting it, so every beat rendered at its composition's
# DEFAULT length and remotion_scenes.py freeze-padded the rest. See
# bind_timing_to_audio below. Excluding it from the render key also meant a
# change to it did not invalidate a stamp, which would have hidden the fix.
RENDERER_INJECTED = ()


def _render_key(b: dict) -> str:
    """What the rendered mp4 actually depends on."""
    r = b.get("shot", {}).get("remotion", {})
    props = {k: v for k, v in (r.get("props") or {}).items()
             if k not in RENDERER_INJECTED}
    return json.dumps([r.get("pattern"), props, b.get("actual_duration_s")],
                      sort_keys=True, ensure_ascii=False)


def carry_rendered(beats: list[dict]) -> int:
    """Carry the render provenance for beats whose render inputs are
    unchanged. A rebuild must not throw away work that was done, and must
    not claim work that is now stale: if the pattern, the props or the
    measured duration moved, the stamp is dropped and remotion_scenes.py
    renders that beat again."""
    out = REEL / "beat_sheet.json"
    if not out.is_file():
        return 0
    try:
        old_beats = json.load(io.open(out, encoding="utf-8"))["beats"]
    except (ValueError, KeyError):
        return 0
    by_id = {b["beat_id"]: b for b in old_beats}
    kept = 0
    for b in beats:
        prev = by_id.get(b["beat_id"])
        if prev is None or _render_key(prev) != _render_key(b):
            continue
        stamp = prev.get("shot", {}).get("remotion", {}).get("rendered")
        if stamp is None:
            continue
        media = REEL / stamp.get("out", "")
        if not media.is_file():
            continue
        b["shot"]["remotion"]["rendered"] = stamp
        if "build" in prev:
            b["build"] = prev["build"]
        kept += 1
    return kept


def carry_measured_audio(beats: list[dict]) -> int:
    out = REEL / "beat_sheet.json"
    if not out.is_file():
        return 0
    try:
        old_beats = json.load(io.open(out, encoding="utf-8"))["beats"]
    except (ValueError, KeyError):
        return 0
    by_id = {b["beat_id"]: b for b in old_beats}
    kept = 0
    for b in beats:
        prev = by_id.get(b["beat_id"])
        if prev is None or prev.get("narration_text") != b["narration_text"]:
            continue
        if not any(k in prev for k in SPOKEN):
            continue
        for k in SPOKEN:
            if k in prev:
                b[k] = prev[k]
        kept += 1
    return kept


def bind_timing_to_audio(beats: list[dict]) -> list[str]:
    """Give every Remotion beat the length of its own measured narration, and
    place every highlight at the fraction of that length the beat's `show`
    entry claims.

    **durationSeconds is an input, not an output.** Each composition computes
    `durationInFrames = ceil(durationSeconds * 30)`, and the defaults are
    GodotDevWorkbench 15 s, ClaudeComposerAsk 30, BrutalistHesitantWriter
    20.2, ClaudeVerdictArtifact 34, ClaudeTitleOutro 6. Nothing here was
    setting it, so every beat rendered at its default and
    remotion_scenes.py's extend_clip_to_duration freeze-held the last frame
    for the rest of the narration. B02 is 36.60 s of audio over a 15 s
    composition: it froze at 15 s on the line-3 highlight and its third cue,
    line 6 - the one line that changes a colour, the whole point of the beat
    - never fired. B11A was 56.56 s over 15. Found by pulling a frame at
    t = 30 s and looking at it; no check in the chain measures motion.

    The cue times written beside each excerpt above are guesses made before
    any audio existed, and they drifted. On 2026-10-28, with the narration
    measured, B04's third cue sat at 28.0 s in a 27.19 s beat and B08's at
    22.0 s in a 21.33 s beat: the component takes the last cue whose `at` has
    passed, so both of those highlights never appeared at all. Nothing caught
    it - the ledger checks that a cue names a line inside the excerpt, not
    that the clip is long enough to reach it.

    show[0] is always the "the excerpt is framed" entry, which is not a
    highlight, so cue i takes its fraction from show[i + 1].
    """
    moved = []
    for b in beats:
        rem = b.get("shot", {}).get("remotion")
        if not rem:
            continue
        props = rem.setdefault("props", {})
        dur = float(b.get("actual_duration_s") or b["estimated_duration_s"])
        if props.get("durationSeconds") != round(dur, 3):
            moved.append("%s durationSeconds %s -> %.3f"
                         % (b["beat_id"], props.get("durationSeconds", "unset"),
                            dur))
        props["durationSeconds"] = round(dur, 3)
        cues = props.get("cues")
        if not cues:
            continue
        fracs = [float(e["at"]) for e in b["shot"]["show"][1:]]
        if len(fracs) != len(cues):
            raise SystemExit("%s: %d cues but %d show fractions after the "
                             "framing entry" % (b["beat_id"], len(cues),
                                                len(fracs)))
        for cue, f in zip(cues, fracs):
            at = round(f * dur, 2)
            if at >= dur:
                raise SystemExit("%s: cue at %.2f s in a %.2f s beat"
                                 % (b["beat_id"], at, dur))
            if abs(at - cue["at"]) >= 0.01:
                moved.append("%s line %d  %.2f -> %.2f"
                             % (b["beat_id"], cue["line"], cue["at"], at))
            cue["at"] = at
    return moved


def main() -> int:
    kept = carry_measured_audio(B)
    # Audio first: the cues are placed against the measured length, and the
    # render stamp depends on both the cue times and actual_duration_s.
    moved = bind_timing_to_audio(B)
    kept_render = carry_rendered(B)
    doc = {"metadata": METADATA, "beats": B}
    out = REEL / "beat_sheet.json"
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

    words = sum(len(b["narration_text"].split()) for b in B)
    est = sum(b["estimated_duration_s"] for b in B)
    print("wrote %s" % out)
    print("  kept measured audio on %d of %d beats (narration unchanged)"
          % (kept, len(B)))
    print("  kept render stamps on %d beats (pattern, props and duration unchanged)"
          % kept_render)
    if moved:
        print("  timing set from the measured narration. A freshly built "
              "beat carries none of it, so every line below is what this "
              "pass wrote, not what changed since the last run:")
        for row in moved:
            print("    %s" % row)
    print("  %d beats, %d narration words, %.0f s estimated (%.1f min)"
          % (len(B), words, est, est / 60.0))
    pairs = [(B[i]["beat_id"], B[i + 1]["beat_id"]) for i in range(len(B) - 1)
             if B[i]["shot"].get("remotion", {}).get("props", {}).get("mode") == "code"]
    print("  code->result pairs: %s" % ", ".join("%s->%s" % p for p in pairs))
    for c in CARDS:
        print("  media/%s.png  full-frame card, motion hold" % c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
