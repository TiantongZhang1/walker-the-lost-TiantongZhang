#!/usr/bin/env python3
"""Write the Assignment 5 film's beat_sheet.json.

Every code excerpt is READ FROM THE FILE at build time and its line range is
recorded beside it, so a panel cannot quote source that has moved. The checker
compares excerpt text against both the file and the beat's props; building it
any other way means typing the code twice and hoping.

Result stills are copied into the reel's media/ so the ledger can hash a
reel-relative path, as references/evidence.md requires.

    python -I scripts/build_lost_beat_sheet.py

Durations are estimates until Kokoro has spoken the lines; the timing pass
replaces them with the measured length.
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

TRAP = "godot/shaders/trap_warning.gdshader"
DRIVER = "godot/features/traps/trap_warning_driver.gd"
HINT = "godot/shaders/hint_bands.gdshader"
SURF = "godot/shaders/dungeon_surface.gdshader"

# Result stills already measured and committed elsewhere in the repository.
STILLS = {
    "B07-hint-experiment.png": "captures/a5/hint_experiment.png",
    "B09-two-materials.png": "captures/a5/materials/00-baseline.png",
    "B11-hint-mutated.png": "evidence/a5-mutations/mutation3a-hint-sampler_capture.png",
}


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


def still_shot(title, media, label, image_label, show):
    """`asset` mode lays out {code}{image}. `code` stays EMPTY: the checker
    rejects displayed code that has no excerpt record, and these beats show a
    capture, not source. The measured numbers are composed into the picture by
    scripts/compose_lost_evidence.py, read verbatim from the recorded report,
    which is also what gets hashed."""
    data = base64.b64encode((MEDIA / media).read_bytes()).decode("ascii")
    return {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "reveal", "evidence_media": "media/" + media, "show": show,
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "asset", "title": title,
                "project": "walker-the-lost-TiantongZhang",
                "path": label, "source": label,
                "code": "", "startLine": 1, "codeFontSize": 22,
                "image": "data:image/png;base64," + data,
                "imageLabel": image_label}}}


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
         "label": "RECONSTRUCTION"}}}))

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
         "title": "What was built",
         "correction": {"from": "turns", "to": "ramps"},
         "lines": ["3 hand-written shaders, 4 materials",
                   "1 agent-written driver, 99 checks",
                   "4 mutations, each caught by a different net",
                   "Every predicted pixel committed before it was measured"]}}}))

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
                "value": "Sub-resources are shared across scene instances. Without duplicate() one red lights all three."},
               {"label": "F5, caught at startup",
                "value": "set_shader_parameter on an undeclared name is silent. The driver asks the shader instead."}],
              [{"at": 8.0, "line": 65, "label": "this trap's own parameter block"},
               {"at": 20.0, "line": 68, "label": "ask the shader what it declares"},
               {"at": 28.0, "line": 76, "label": "state in, uniform out, once a frame"}],
              [{"at": "0.05", "event": "the excerpt is framed"},
               {"at": "0.24", "event": "line 65 highlights"},
               {"at": "0.58", "event": "line 68 highlights"},
               {"at": "0.82", "event": "line 76 highlights"}])))

B.append(beat(
    "B05", "RESULT",
    "C2 RESULT. take-w across all three traps, 0.60-11.40 s. The take's own "
    "probe counted zero frames in 709 with more than one trap lit.",
    "Watch the red move. Three traps, one shader, three materials - and the "
    "warning never appears on two at once. The driver counted it: seven "
    "hundred and nine frames, zero with more than one lit.",
    10,
    footage_shot([0.60, 11.40],
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
                "value": "Any lighting multiplies ALBEDO and the measured band stops being a statement about the sampler."},
               {"label": "Why nearest",
                "value": "The image is 3 x 1. Linear filtering averages neighbouring bands and no predicted value survives."}],
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
    still_shot("The hint is worth seventy three counts", "B07-evidence.png",
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
                "value": "wetness_mask is sampled without source_color. Decoded, 0.5 would become 0.21 and the waterline would move."},
               {"label": "What Godot does next",
                "value": "ALBEDO and ROUGHNESS feed the engine's lighting. Plain GLSL would make you write the BRDF."}],
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
    still_shot("One shader, two materials", "B09-evidence.png",
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
                "value": "stone_albedo and wetness_mask both come back type 24, hint 17, 'Texture2D'. Identical."},
               {"label": "The asymmetry",
                "value": "On a vec3 the same keyword IS visible - TYPE_COLOR with COLOR_NO_ALPHA instead of TYPE_VECTOR3."}],
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
    still_shot("The same scene, four words lighter", "B11-evidence.png",
               "evidence/a5-mutations/ - captured with the shader mutated",
               "the same scene with source_color deleted; both quads identical",
               [{"at": "0.08", "event": "both quads appear, identical"},
                {"at": "0.46", "event": "the table reveals - the left column has moved"},
                {"at": "0.84", "event": "SHADER ERROR: 0 is marked"}])))

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
    "real hardware. Still open: the slice has no audio and no art beyond code-"
    "drawn blocks, and that port is Assignment Six's first job.",
    44,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "reveal",
     "show": [{"at": "0.05", "event": "the three columns appear"},
              {"at": "0.40", "event": "the measured column fills"},
              {"at": "0.80", "event": "the open column holds"}],
     "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
         "title": "Verdict",
         "columns": [
             {"heading": "By hand, the author",
              "items": ["trap_warning.gdshader", "dungeon_surface.gdshader",
                        "hint_bands.gdshader", "LANGUAGE-NOTES.md, 36 references"]},
             {"heading": "By Claude, reviewed",
              "items": ["the material driver", "99 automated checks",
                        "two capture rigs", "MATERIALS.md audit"]},
             {"heading": "Measured, not asserted",
              "items": ["8 predicted pixels, 0 error", "6 predicted bands, 0 error",
                        "hint_range does not clamp", "R6 held 361 of 361 frames"]},
             {"heading": "Still open",
              "items": ["no audio, no art yet", "one sweep judgement outstanding",
                        "no normal map, so no curl check"]}]}}}))

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
         "label": "YOUR TURN"}}}))

# ------------------------------------------------------------------ OUTRO
B.append(beat(
    "B14", "OUTRO",
    "LOCKED ClaudeTitleOutro. Exact title, @NikBearBrown, one slug-seeded "
    "mascot, no subline, stock jingle only. No narration.",
    "", 5,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "hold",
     "remotion": {"pattern": "ClaudeTitleOutro", "props": {
         "title": "TheLostShaders_TiantongZhang",
         "channel": "@NikBearBrown",
         "slug": "claude-liam-walker-the-lost-gamedev"}}}))


# Fields the narration pass writes back. Rebuilding the sheet used to drop
# them, so every change to a camera window cost a full re-synthesis; they are
# carried over for any beat whose spoken words are byte-identical.
SPOKEN = ("actual_duration_s", "audio_file", "render_duration_s")


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


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)
    for name, src in STILLS.items():
        shutil.copyfile(ROOT / src, MEDIA / name)
    kept = carry_measured_audio(B)
    doc = {"metadata": METADATA, "beats": B}
    out = REEL / "beat_sheet.json"
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

    words = sum(len(b["narration_text"].split()) for b in B)
    est = sum(b["estimated_duration_s"] for b in B)
    print("wrote %s" % out)
    print("  kept measured audio on %d of %d beats (narration unchanged)"
          % (kept, len(B)))
    print("  %d beats, %d narration words, %.0f s estimated (%.1f min)"
          % (len(B), words, est, est / 60.0))
    pairs = [(B[i]["beat_id"], B[i + 1]["beat_id"]) for i in range(len(B) - 1)
             if B[i]["shot"].get("remotion", {}).get("props", {}).get("mode") == "code"]
    print("  code->result pairs: %s" % ", ".join("%s->%s" % p for p in pairs))
    for name in STILLS:
        print("  media/%s copied" % name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
