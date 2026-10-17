#!/usr/bin/env python3
"""Write the A3 film's beat_sheet.json.

Plan A: a short, plain film, which the assignment explicitly allows -- "A
short, plain film is fine", "Duration follows the explanation, with no
minimum". The explainer is 8 of 100 marks and Assignment 2's film consumed
more time than everything else in that assignment put together.

Walker bookends, per the skill: ClaudeComposerAsk -> BrutalistHesitantWriter
-> body -> Verdict -> Your Turn -> locked ClaudeTitleOutro.

The teaching unit is code -> visible result, adjacent, three times:
  B02 build_spike_trap.py   -> B03 the trap in Blender
  B04 build_slime.py        -> B05 the slime before and after
  B06 check_assets_3d.gd    -> B07 the check's own output

Every excerpt is sliced out of the file on disk by line range, so a beat
cannot drift from its source. Two lessons from A2 are enforced here rather
than rediscovered: excerpts stay <= 14 lines and note values <= 100
characters, because the panel clips, and the title stays <= 26 characters,
because at 31 it overflowed the safe right edge and failed Gate V.
"""
import base64
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REEL = os.path.join(ROOT, "youtube", "claude-liam-walker-ninja-a3-blender")
MEDIA = os.path.join(REEL, "media")

TITLE = "NewWalker3D_TiantongZhang"          # 25 chars; the Gate V limit is 26
MAX_EXCERPT_LINES = 14
MAX_NOTE_CHARS = 100
MAX_NOTES = 2            # the pilot clipped a third note off the panel's bottom


def excerpt(rel, first, last):
    """Lines [first, last] of a file, verbatim, 1-indexed and inclusive."""
    path = os.path.join(ROOT, rel)
    lines = io.open(path, encoding="utf-8", newline="").read().splitlines()
    cut = lines[first - 1:last]
    assert len(cut) <= MAX_EXCERPT_LINES, "%s: %d lines, panel clips over %d" % (
        rel, len(cut), MAX_EXCERPT_LINES)
    return "\n".join(cut)


def image(name):
    with open(os.path.join(MEDIA, name), "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def notes(pairs):
    assert len(pairs) <= MAX_NOTES, "%d notes; the panel clips past %d" % (
        len(pairs), MAX_NOTES)
    for _, value in pairs:
        assert len(value) <= MAX_NOTE_CHARS, "note %d chars, panel clips over %d: %s" % (
            len(value), MAX_NOTE_CHARS, value)
    return [{"label": a, "value": b} for a, b in pairs]


def code_beat(bid, title, rel, first, last, narration, note_pairs, cues, secs):
    return {
        "beat_id": bid, "act": "BUILD",
        "role_note": "CODE. %s lines %d-%d, verbatim." % (rel, first, last),
        "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
        "estimated_duration_s": secs,
        "shot": {
            "type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "code-highlight", "show": [],
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "code", "title": title,
                "project": "walker-ninja-TiantongZhang",
                "path": rel, "source": rel,
                "code": excerpt(rel, first, last),
                "startLine": first, "codeFontSize": 26,
                "inspectorLabel": "Source notes - not Inspector values",
                "notes": notes(note_pairs), "cues": cues,
                "durationSeconds": secs}}},
    }


def asset_beat(bid, title, path_label, img, img_label, narration, note_pairs, secs,
               evidence_media=None):
    shot = {
        "type": "GRAPHIC", "class": "SHOW", "source": "remotion",
        "motion": "asset-preview", "show": [],
    }
    if evidence_media:
        shot["evidence_media"] = evidence_media
    return {
        "beat_id": bid, "act": "RESULT",
        "role_note": "RESULT. Real engine or session evidence, hashed in the ledger.",
        "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
        "estimated_duration_s": secs,
        "shot": {
            **shot,
            "remotion": {"pattern": "GodotDevWorkbench", "props": {
                "mode": "asset", "title": title,
                "project": "walker-ninja-TiantongZhang",
                "path": path_label, "source": path_label,
                "code": "", "startLine": 1,
                "image": image(img), "imageLabel": img_label,
                "notes": notes(note_pairs), "cues": [],
                "durationSeconds": secs}}},
    }


beats = []

beats.append({
    "beat_id": "B00", "act": "ASK",
    "role_note": "WALKER BOOKEND 1/4 - ClaudeComposerAsk. Reconstruction, labelled.",
    "narration_text": (
        "Sawubona. The prompt on screen is a reconstruction, not a transcript. "
        "Assignment three asks for three simple 3D assets, built with Claude "
        "through the Blender MCP, and shown together in Godot. The game is the "
        "same dungeon the last film took apart. The assets are three things it "
        "already draws in code."),
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 18.0,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "type-on", "show": [],
             "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                 "greeting": "Sawubona, Liam",
                 "topic": "WALKER - FIRST 3D ASSETS",
                 "segment": "Blender MCP to Godot",
                 "command": (
                     "Please use Walker to convert my game design document about a "
                     "cyber-ninja in a torchlit dungeon into three simple 3D assets "
                     "I can put in Godot: the wall torch, the pop-up spike trap and "
                     "the slime. Build them in my open Blender through the MCP, from "
                     "basic shapes only, at the sizes my 2D level already uses."),
                 "runningText": "reconstruction - illustrative, not a transcript",
                 "output": ["three assets, built not generated",
                            "every size taken from the 2D game",
                            "no asset library, no 3D generator"],
                 "folderLabel": "@NikBearBrown",
                 "modelLabel": "Claude Opus 5", "effortLabel": "High",
                 "durationSeconds": 18.0}}}})

beats.append({
    "beat_id": "B01", "act": "RESULT",
    "role_note": "WALKER BOOKEND 2/4 - BrutalistHesitantWriter, one-word correction.",
    "narration_text": (
        "One correction before we start. Nothing here was generated. A 3D "
        "generator was available in the same add-on and the assignment forbids "
        "it, so the geometry is built: eleven primitives, placed and scaled by "
        "scripts you can read, two hundred and ten triangles for all three."),
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 20.0,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "hesitant-write", "show": [],
             "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
                 "contextTitle": "What Assignment 3 added",
                 "text": "Claude generated three assets.\nClaude built them.",
                 "face": "serif", "fontSize": 86, "lineSpacing": 1.35,
                 "align": "center",
                 "triggerWords": "generated", "replacementWords": "built",
                 "mistakeRate": 0, "hesitateWithin": 0, "hesitateBetween": 6,
                 "charMs": 28, "jitter": 15,
                 "contextItems": [
                     {"label": "Built", "detail": "torch, spike trap, slime - 11 primitives, 210 triangles"},
                     {"label": "Off, by rule", "detail": "Poly Haven, Sketchfab, Poly Pizza, Hyper3D, Hunyuan3D, Tripo"},
                     {"label": "Unchanged", "detail": "the 2D slice - no level, sprite, sound or gameplay number"}],
                 "durationSeconds": 20.0}}}})

beats.append(asset_beat(
    "B02", "Three teeth, because the game says three",
    "tools/blender/build_spike_trap.py",
    "code-spike-trap.png",
    "lines 98-111, verbatim - the file the MCP executed",
    "The trap is four shapes. The tooth count is not a choice: the 2D game's "
    "spike_count is the rect width over the pitch, twenty-four over eight, "
    "three. Pitch here is the width over that same count, so the 3D asset and "
    "the thing it stands for are built from one number.",
    [("Where the size comes from", "levels/first_steps.json trap rect [1160, 304, 24, 16] at 16 px = 1 m"),
     ("Why 8 segments", "a cone costs 2N-2 triangles; the course limit is 500 per asset")],
    21.0))

beats.append(asset_beat(
    "B03", "The trap, in the live Blender session",
    "design/blender/spike_trap.blend",
    "spike-angles-panel.png",
    "four views from the running Blender, with the measurements beside them",
    "There it is, from four sides. Fifty-four triangles. One point five metres "
    "wide and one metre tall, which is the level file's own trap rect. The "
    "teeth read as teeth from the side, and the top view shows the eight-sided "
    "cones the budget bought.",
    [("Capture", "the MCP look tool, pointed at the live session - not a redraw"),
     ("Measured", "4 shapes, 54 triangles, 1.500 x 0.500 x 1.000 m, base on z = 0")],
    15.0))

beats.append(asset_beat(
    "B04", "Measure, then scale - not a magic constant",
    "tools/blender/build_slime.py",
    "code-slime-fit.png",
    "lines 98-109, verbatim - the file the MCP executed",
    "The slime missed its own brief by fifteen per cent. An icosphere is a "
    "faceted solid, and there is no ring of vertices on the plane it gets cut "
    "at, so a dome built at one point three seven five measured one point one "
    "seven. This measures the mesh after the cut and scales it to the number "
    "the brief promised.",
    [("The quick fix, rejected", "multiplying by 1.174, a constant taken from one measurement"),
     ("Why that matters", "raising SUBDIV later would have moved it off the brief, silently")],
    23.0))

beats.append(asset_beat(
    "B05", "Round, because it was looked at",
    "tools/blender/build_slime.py",
    "slime-before-after.png",
    "subdivision 1 and subdivision 2, both from the live session",
    "Every check passed on the one on the left. Correct size, origin on the "
    "floor, scale one. It also has a pointed top, and the 2D game draws a "
    "smooth dome. No assertion was going to catch that. Subdivision two, "
    "twenty more triangles, still inside the budget the brief wrote down.",
    [("What caught it", "a person looking at a render - not a check"),
     ("Recorded as", "CHANGE-BRIEF.md revision 3.0.1, added rather than editing 3.0.0")],
    20.0))

beats.append(code_beat(
    "B06", "The check that was wrong before any asset was",
    "godot/tests/check_assets_3d.gd", 150, 161,
    "This walks the imported scene and accumulates each node's local "
    "transform. The first version read global transform instead, from nodes a "
    "script in underscore init has not put in the tree yet. Every transform "
    "came back identity, and it reported a correct asset as sunk four hundred "
    "millimetres into the floor.",
    [("The giveaway", "0.850 m tall and -0.425 m low: exactly the cone's local half-height"),
     ("The assignment's warning", "an agent's check can prove less than it claims")],
    [{"at": "0.14", "line": 151}, {"at": "0.46", "line": 154},
     {"at": "0.72", "line": 158}, {"at": "0.90", "line": 161}], 23.0))

beats.append(asset_beat(
    "B07", "Twelve measurements, beside the brief",
    "godot/tests/check_assets_3d.gd",
    "check-output.png",
    "headless output - the run's own stdout, not a transcription",
    "Headless, in Godot. Each asset's bounding box printed beside the number "
    "the brief predicted, which axis it stands along, its node scale, and how "
    "far its lowest point sits from the floor. Twelve measurements, no "
    "failures. What it cannot tell you is whether any of them looks like a "
    "torch.",
    [("Exit code", "0 on pass, 1 on any failure - the script quits itself"),
     ("What it does not show", "whether an asset reads, whether a face is missing, whether it suits")],
    20.0, evidence_media="media/check-output.png"))

beats.append(asset_beat(
    "B08", "The hand edit, in my own Blender",
    "design/blender/slime.blend",
    "hand-edit-panel.png",
    "my own session, cropped to the evidence - not a reconstruction",
    "The assignment wants one change made by hand, with the mouse. The eyes "
    "were too small to read beside a player who is one point seven five "
    "metres, so I scaled them in the viewport. One frame carries the file "
    "name, the selected eye, its position to five decimals, and a scale of "
    "one, because the transform was applied afterwards.",
    [("Not a reconstruction", "the author's own Blender window, screenshotted by them"),
     ("What changed", "Slime_Eye_1 to scale 1.526, Eye_2 to 1.570, both about 27 mm lower")],
    22.0))

beats.append(asset_beat(
    "B09", "All three, in the running Godot scene",
    "godot/scenes/asset_showcase.tscn",
    "godot-showcase.png",
    "a frame from a real run of the scene, at game scale",
    "A floor, one light, a camera, and the three assets one point nine metres "
    "apart. Each sits on the floor because each origin is at the centre of its "
    "underside. That is the brief's third prediction made into the scene's "
    "layout, where floating would be visible rather than merely measurable.",
    [("One light", "the DirectionalLight3D. The WorldEnvironment is ambient, not a second light"),
     ("Why ambient at all", "without it an unlit face reads as a hole and the human check fails")],
    18.0))

beats.append({
    "beat_id": "B10", "act": "VERDICT",
    "role_note": "WALKER BOOKEND 3/4 - ClaudeVerdictArtifact.",
    "narration_text": (
        "What this film can defend. Three assets, built not generated, every "
        "size traced to a line in the 2D game. Twelve automated measurements, "
        "no failures. Two revisions that no check asked for, because a person "
        "looked. One human check, one sentence long, recorded as one sentence. "
        "The assets chosen, the sizes approved, the hand edit and that check "
        "are the author's. The scripts, the scene, the checks and this film are "
        "Claude's, including the check that was wrong. Everything you have seen "
        "is the repository at tag a3."),
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 30.0,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "verdict-columns", "show": [],
             "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
                 "artifactTitle": "Verdict",
                 "artifactHeading": "Built, measured, and what stayed unmeasured",
                 # Eight lines, not eleven. Eleven overflowed the title-safe
                 # bottom edge and ./art final refused the cut -- the same
                 # class of failure as A2's 31-character title. Every line
                 # here is <= 65 characters so none of them wraps.
                 "artifactLines": [
                     "Built: torch, spike trap, slime - 11 primitives, 210 triangles.",
                     "Generated: nothing. All six libraries and generators off.",
                     "Sizes: every one traced to the level file or a draw function.",
                     "Checked: 12 measurements, 0 failures - the check was wrong first.",
                     "Revised twice on sight. Human check: one sentence, so recorded.",
                     "Author: the assets, the sizes, the hand edit, the looking.",
                     "Claude: the scripts, the scene, the checks, the film, the bug.",
                     "Shown: tag a3. Not shown: the assets inside the 2D game."],
                 "brandLabel": "@NikBearBrown",
                 "durationSeconds": 30.0}}}})

beats.append({
    "beat_id": "B11", "act": "TURN",
    "role_note": "WALKER BOOKEND 4/4 - Your Turn. One bounded change, prediction first.",
    "narration_text": (
        "Your turn. Give the torch a light. Predict the number before you run "
        "it: the 2D glow is sixteen nested discs with an outer radius of sixty "
        "pixels, which at sixteen pixels to the metre is three point seven five "
        "metres of reach. Then look, because the check measures geometry and a "
        "light is not geometry. Liam, signing off."),
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 24.0,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "turn-card", "show": [],
             "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                 "greeting": "Your turn, Liam",
                 "topic": "WALKER - GIVE THE TORCH A LIGHT",
                 "segment": "One bounded change",
                 "command": (
                     "In walker-ninja, add an OmniLight3D as a child of the Torch in "
                     "scenes/asset_showcase.tscn, with a range derived from the 2D "
                     "glow in _draw_torch. Write the predicted range in the commit "
                     "message before you run it, then look at the frame."),
                 "runningText": "predict the range first - then look",
                 "output": ["2D glow: 16 discs, outer radius 60 px",
                            "at 16 px = 1 m that is 3.75 m of reach",
                            "check_assets_3d.gd will not notice either way"],
                 "folderLabel": "@NikBearBrown",
                 "modelLabel": "Claude Opus 5", "effortLabel": "High",
                 "durationSeconds": 24.0}}}})

beats.append({
    "beat_id": "B12", "act": "OUTRO",
    "role_note": "OUTRO LAW / OUTRO-LOCK.md - locked ClaudeTitleOutro, no narration.",
    "narration_text": "", "voice": "none", "engine": "none",
    "estimated_duration_s": 5.0, "audio_policy": "silence",
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "title-outro", "show": [],
             "remotion": {"pattern": "ClaudeTitleOutro", "props": {
                 "title": TITLE, "channel": "@NikBearBrown",
                 "slug": "claude-liam-walker-ninja-a3-blender"}}}})

sheet = {
    "metadata": {
        "title": TITLE,
        "slug": "claude-liam-walker-ninja-a3-blender",
        "topic": "WALKER - FIRST 3D ASSETS WITH THE BLENDER MCP",
        "kind": "gamedev", "playlist": "Brutalist", "brand": "claude-liam",
        "audience": "Course reviewers reading an Assignment 3 Blender-to-Godot pass",
        "register": "Teardown", "engine": "kokoro",
        "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "style_preset": "claude", "ground": "#FAF9F5",
        "aspect_ratio": "16:9", "fit": "contain", "captions": False,
        "channel_title": "@NikBearBrown", "channel": "@NikBearBrown",
        "folderLabel": "@NikBearBrown",
        "greeting": "Sawubona, Liam",
        "greeting_note": ("hello lexicon: Sawubona (Zulu), one word, the Liam "
                          "persona budget. Wagwan is Bear's alone and is not used."),
        "mode": "walker",
        "teaching_contract": "code-then-result-v1",
        "game": "walker-ninja-TiantongZhang",
    },
    "beats": beats,
}

# Bind to the measured narration if it exists.
#
# This lives here rather than in a separate pass because the estimates in the
# beat definitions above are guesses, and every rebuild of this file would
# otherwise quietly throw the measured durations away. Kokoro's output is
# ground truth; the padding is so a cut does not clip the last word.
TAIL_PAD = 0.45
timings_path = os.path.join(REEL, "mp3", "timings.json")
if os.path.exists(timings_path):
    measured = json.load(io.open(timings_path, encoding="utf-8"))
    for b in beats:
        bid = b["beat_id"]
        if bid not in measured:
            b["render_duration_s"] = b["estimated_duration_s"]
            continue
        secs = round(float(measured[bid]) + TAIL_PAD, 2)
        b["actual_duration_s"] = float(measured[bid])
        b["audio_file"] = "mp3/beat-%s.mp3" % bid
        b["render_duration_s"] = secs
        props = b["shot"]["remotion"]["props"]
        if "durationSeconds" in props:
            props["durationSeconds"] = secs
    print("bound to measured narration (+%.2fs tail)" % TAIL_PAD)
else:
    print("NO mp3/timings.json yet - durations are still estimates")

out = os.path.join(REEL, "beat_sheet.json")
io.open(out, "w", encoding="utf-8", newline="\n").write(
    json.dumps(sheet, indent=2, ensure_ascii=False))

total = sum(b.get("render_duration_s", b["estimated_duration_s"]) for b in beats)
print("wrote %s" % out)
print("%d beats, %.1f s estimated (%d:%02d)" % (
    len(beats), total, int(total) // 60, int(total) % 60))
for b in beats:
    pr = b["shot"]["remotion"]
    print("  %-4s %-9s %-24s %s" % (
        b["beat_id"], b["act"], pr["pattern"],
        (pr["props"].get("title") or pr["props"].get("topic") or "")[:44]))
