#!/usr/bin/env python3
"""Write the Assignment 5 film's beat_sheet.json.

Every code excerpt is READ FROM THE FILE at build time and the line range is
recorded beside it, so the panel on screen cannot drift away from the source
it claims to quote. The checker compares the excerpt text to both the file and
the beat's props; building it any other way means typing the code twice and
hoping.

    python -I scripts/build_lost_beat_sheet.py

Durations here are estimates. `scripts/finalise_beat_timing.py` replaces them
with the measured narration length once Kokoro has spoken the lines.
"""
from __future__ import annotations

import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-gamedev"
GAME = "godot"


def excerpt(rel: str, start: int, end: int) -> str:
    """Lines start..end inclusive, one-based, as the ledger defines them."""
    text = (ROOT / rel).read_text(encoding="utf-8")
    rows = text.split("\n")
    if end > len(rows):
        raise SystemExit("%s has %d lines, asked for %d" % (rel, len(rows), end))
    return "\n".join(rows[start - 1:end])


TRAP = "godot/shaders/trap_warning.gdshader"
DRIVER = "godot/features/traps/trap_warning_driver.gd"
HINT = "godot/shaders/hint_bands.gdshader"
SURF = "godot/shaders/dungeon_surface.gdshader"

METADATA = {
    "title": "TheLostShaders_TiantongZhang",
    "slug": "claude-liam-walker-the-lost-gamedev",
    "topic": "WALKER - GODOT SHADERS AND MATERIALS TEARDOWN",
    "kind": "gamedev",
    "playlist": "Brutalist",
    "brand": "claude-liam",
    "audience": "Course reviewers reading a Godot shader and material pass",
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
}


def beat(bid, act, role, narration, seconds, shot):
    return {
        "beat_id": bid,
        "act": act,
        "role_note": role,
        "narration_text": narration,
        "voice": "am_onyx",
        "engine": "kokoro",
        "estimated_duration_s": seconds,
        "shot": shot,
    }


def workbench(title, path_label, source, code, start_line, notes, cues,
              mode="code", font=23):
    props = {
        "mode": mode,
        "title": title,
        "project": "walker-the-lost-TiantongZhang",
        "path": path_label,
        "source": source,
        "code": code,
        "startLine": start_line,
        "codeFontSize": font,
        "inspectorLabel": "Source notes - not Inspector values",
        "notes": notes,
        "cues": cues,
    }
    return {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "code-highlight",
            "remotion": {"pattern": "GodotDevWorkbench", "props": props}}


def evidence_panel(title, label, image, notes, cues, lines):
    """A result beat built from a real capture plus its measured numbers."""
    props = {
        "mode": "asset",
        "title": title,
        "project": "walker-the-lost-TiantongZhang",
        "path": label,
        "source": image,
        "image": image,
        "codeFontSize": 22,
        "treeLabel": "Engine capture - real windowed run, Forward+",
        "inspectorLabel": "Measured, beside the prediction committed first",
        "notes": notes,
        "cues": cues,
        "lines": lines,
    }
    return {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "reveal",
            "evidence_media": image,
            "remotion": {"pattern": "GodotDevWorkbench", "props": props}}


beats = []

# ----------------------------------------------------------- WALKER BOOKENDS

beats.append(beat(
    "B00", "ASK",
    "WALKER BOOKEND 1/4 - ClaudeComposerAsk. Reconstructed prompt, said aloud "
    "to be a reconstruction. Liam named in the first breath.",
    "Sawubona - this is Liam, in for Bear. The prompt on screen is a "
    "reconstruction. It was written to be illustrative and it is not a "
    "transcript. The game under it is real: a dungeon slice in Godot four, "
    "and this time the thing we are taking apart is not the game logic. It is "
    "the four shaders, and the question of what a hint actually does.",
    22,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
     "show": [{"at": "0.03", "event": "composer card fades in"},
              {"at": "0.12", "event": "greeting lands"},
              {"at": "0.30", "event": "the Walker prompt types on"},
              {"at": "0.80", "event": "RECONSTRUCTION label stays visible"}],
     "remotion": {"pattern": "ClaudeComposerAsk", "props": {
         "greeting": "Sawubona, Liam",
         "topic": "WALKER - GODOT SHADERS AND MATERIALS TEARDOWN",
         "segment": "The Lost, lit",
         "command": (
             "Please use Walker to convert my game design document about The "
             "Lost - a side-view dungeon crawler where every hazard announces "
             "itself before it can hurt you - into a Godot project, and then "
             "help me write the shader that does the announcing by hand, "
             "while you write the driver and the tests that prove it."),
         "label": "RECONSTRUCTION"}}}))

beats.append(beat(
    "B01", "RESULT",
    "WALKER BOOKEND 2/4 - hesitant writer. One working single-word correction, "
    "with measured time to complete it.",
    "Here is what actually changed. Three shaders, written by hand, line by "
    "line. A spike trap that turns - correction - that ramps red across four "
    "tenths of a second before it fires. Two materials from one shader on two "
    "identical slimes. And a three pixel image, sampled twice through the same "
    "file, that settles what source colour does to a number. Ninety-nine "
    "automated checks stand behind that, and four deliberate breakages stand "
    "behind the checks.",
    38,
    {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "write-on",
     "show": [{"at": "0.05", "event": "the summary begins writing"},
              {"at": "0.34", "event": "'turns' struck through, 'ramps' written in"},
              {"at": "0.70", "event": "the counts land"}],
     "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
         "title": "What was built",
         "correction": {"from": "turns", "to": "ramps"},
         "lines": [
             "3 hand-written shaders",
             "1 agent-written driver + 99 checks",
             "4 mutations, each caught by a different net",
             "Every predicted pixel committed before it was measured"]}}}))

json_path = REEL / "beat_sheet.json"
REEL.mkdir(parents=True, exist_ok=True)

# The remaining beats are appended by build_lost_beats_body.py so that this
# file stays readable; see that script for B02..B14.
io.open(json_path, "w", encoding="utf-8", newline="\n").write(
    json.dumps({"metadata": METADATA, "beats": beats}, ensure_ascii=False, indent=2) + "\n")
print("wrote %s with %d bookend beats" % (json_path, len(beats)))
print("excerpt self-test:")
for rel, a, b in [(TRAP, 1, 7), (DRIVER, 73, 76), (HINT, 1, 7), (SURF, 1, 13)]:
    text = excerpt(rel, a, b)
    print("  %-52s %2d-%2d  %d chars, first line: %s"
          % (rel, a, b, len(text), text.split(chr(10))[0][:46]))
