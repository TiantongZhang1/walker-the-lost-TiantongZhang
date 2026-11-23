#!/usr/bin/env python3
"""Write gdd-evidence.json for Assignment 8's pitch reel.

    python -X utf8 scripts/build_pitch_ledger.py

`./art godot-gdd --check` is strict in four ways and this file is built to
each of them rather than written by hand and corrected until it passes:

1. **Every `## ` heading in the document is covered or excluded.** Not most of
   them, and the comparison is a set comparison - a heading reworded in the
   brief and not here fails the check rather than silently dropping out of the
   film. The headings are read from the brief at build time.
2. **Every excerpt is an exact line range**, and the text is re-read from the
   document here AND compared against what the beat actually displays. Three
   copies of one quotation is this repository's recurring fault; the checker
   makes it impossible to ship a fourth.
3. **Every evidence file is hashed**, must live inside the reel, and must
   carry both a method and the claim it supports. A file with no stated claim
   is not evidence, it is an attachment.
4. **Every BODY beat carries a design status.** This film's statuses are the
   assignment's honesty rule in machine-readable form: `proposed` is a thing
   that does not exist, `implemented` is a thing that does, `observed` is a
   thing that was measured, `pending` is a question nothing has answered.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRIEF = ROOT / "pitch/PROJECT-BRIEF.md"
REEL = ROOT / "youtube/claude-liam-walker-the-lost-pitch-gdd"

# Section heading -> the beats that cover it. Read against the brief below;
# a heading that is not in this map, or a map entry that is not a heading,
# stops the build.
COVERAGE = {
    "1. What is it?": (
        ["B02"], "The one sentence, the artifact and its form."),
    "2. Why would anyone care?": (
        ["B03"], "Unique value and the one named comparable, Hollow Knight."),
    "3. Who opens it, and what do they do in the first sixty seconds?": (
        ["B04"], "Target role, plus real captured play of what a player "
                 "actually moves in the first minute."),
    "4. What does it prove about me?": (
        ["B05"], "Course skills against the tags that hold their evidence, "
                 "and what the evidence does not prove."),
    "5. What is in, what is out, what comes first?": (
        ["B08"], "In, out and first separated; the first piece's assertion "
                 "named."),
    "6. What could sink it?": (
        ["B09"], "The one concrete risk and the mitigation."),
    "7. Why this project?": (
        ["B10"], "New learning separated from existing skill on show."),
    "§A. Exists today": (
        ["B06", "B07"], "A played capture of the one mechanism this "
                        "assignment's §B is built on (B06), then the list "
                        "itself (B07)."),
    "§B. Will exist": (
        ["B07"], "The unstarted list, shown beside §A so neither can be read "
                 "without the other."),
}

# Beat -> the brief's line range it quotes. The TEXT is never written here.
EXCERPT_LINES = {
    "B02": (20, 21),
    "B03": (65, 67),
    "B05": (117, 119),
    "B07": (288, 288),
    "B08": (164, 166),
    "B09": (179, 179),
    "B10": (255, 256),
}

# Evidence inside the reel. Method and claim are both required by the checker,
# and the claim is the sentence in the film the file is answerable for.
EVIDENCE = [
    ("capture/take-c.mp4",
     "Godot Movie Maker at 3840x2160, driven by godot/tests/capture_animation.gd "
     "at game-source revision b33b06c. PLAYED: keys held through the real "
     "input map, nothing teleported, no state written, no clip seeked. The "
     "take asserts >=5 cycle wraps, both facings and >=12 distinct dust puffs "
     "before a frame of it counts, and exits nonzero otherwise.",
     "B04's claim that the walk on screen is the game as it exists today, and "
     "that a player is moving within seconds without reading anything."),
    ("capture/take-s.mp4",
     "Same driver and revision. PLAYED. The take asserts exactly 4 swings, the "
     "hitbox window opening exactly 4 times, and every clip 34-38 physics "
     "frames.",
     "B06's claim that the committing swing and its 0.133 s window exist, run, "
     "and connect with nothing."),
    ("capture/logs/take-c-inputs.jsonl",
     "Per-physics-frame log written by the capture driver: the held action "
     "set, the player's position, velocity, state and health, one JSON object "
     "per frame.",
     "That take-c is played input rather than a scripted animation - the log "
     "is the input, frame by frame, and can be replayed."),
    ("capture/logs/take-s-inputs.jsonl",
     "Same log for take-s, including the frame on which each swing starts and "
     "the frames on which Hitbox.monitoring is true.",
     "That the four swings in B06 are four real button presses and that the "
     "window opened four times."),
]


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    lines = BRIEF.read_text(encoding="utf-8").splitlines()
    headings = [ln[3:].strip() for ln in lines if ln.startswith("## ")]

    missing = [h for h in headings if h not in COVERAGE]
    extra = [h for h in COVERAGE if h not in headings]
    if missing or extra:
        for h in missing:
            print("  heading with no coverage entry: %r" % h)
        for h in extra:
            print("  coverage entry that is not a heading: %r" % h)
        sys.exit("the brief's headings and this script's map disagree")

    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}

    excerpts = []
    for beat_id, (start, end) in EXCERPT_LINES.items():
        if not 1 <= start <= end <= len(lines):
            sys.exit("%s: line range %d-%d is outside the brief"
                     % (beat_id, start, end))
        text = "\n".join(lines[start - 1:end])
        shown = (beats[beat_id].get("shot", {}).get("remotion", {})
                 .get("props", {}).get("excerpt"))
        if shown != text:
            sys.exit("%s displays an excerpt the brief does not contain at "
                     "lines %d-%d" % (beat_id, start, end))
        excerpts.append({"beat_id": beat_id, "start_line": start,
                         "end_line": end, "text": text})

    evidence = []
    for rel, method, supports in EVIDENCE:
        target = REEL / rel
        if not target.is_file():
            sys.exit("evidence file is missing: %s" % rel)
        evidence.append({"path": rel, "sha256": sha256(target),
                         "method": method, "supports": supports})

    ledger = {
        "schema_version": 1,
        "note": (
            "The document walked through is pitch/PROJECT-BRIEF.md, not "
            "the-lost-gdd/GDD.md. The GDD describes the whole four-floor game; "
            "the brief describes the project being pitched, and a pitch film "
            "is a walk through the brief. The GDD is cited inside the brief "
            "where its cut rule and its renderer row are used, and it is in no "
            "git repository - which the brief's own §A lists as a gap."),
        "document": {
            "path": "pitch/PROJECT-BRIEF.md",
            "sha256": sha256(BRIEF),
            "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "version_note": "Assignment 8 draft of 2026-11-23, after the "
                            "author settled the four open items in the first "
                            "draft (comparable, target role, artifact, first "
                            "piece).",
        },
        "game_source_revision": "b33b06c",
        "sections": [
            {"heading": h,
             "beat_ids": COVERAGE[h][0],
             "coverage": COVERAGE[h][1]}
            for h in headings
        ],
        "excerpts": excerpts,
        "evidence": evidence,
    }
    (REEL / "gdd-evidence.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print("gdd-evidence.json  %d sections, %d excerpts, %d evidence files"
          % (len(headings), len(excerpts), len(evidence)))
    statuses = {}
    for beat in sheet["beats"]:
        if beat.get("design_status"):
            statuses.setdefault(beat["design_status"], []).append(beat["beat_id"])
    for status in sorted(statuses):
        print("  %-12s %s" % (status, " ".join(statuses[status])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
