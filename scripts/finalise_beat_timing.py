#!/usr/bin/env python3
"""Final pass on the beat sheet: windows, cues bound to measured audio, holds.

Three things happen here that could not happen earlier:

  1. The footage windows are set against the re-rendered take-p (8.37 s now,
     with a second swing) instead of the 4.33 s first cut.
  2. Every code beat's cues are placed at the fraction of its ACTUAL measured
     narration that its own `show` entry claims, instead of the estimates I
     wrote before any audio existed.
  3. hold_s is computed from the measured narration minus the clip, so the
     freeze is a derived number rather than a guess.
"""
import io, json, os, subprocess

ROOT = r"D:\Graduate\2026Fall\7270\walker-ninja-TiantongZhang"
os.chdir(ROOT)
REEL = "youtube/claude-liam-walker-ninja-gamedev"
BS = os.path.join(REEL, "beat_sheet.json")
doc = json.load(io.open(BS, encoding="utf-8"))
by = {b["beat_id"]: b for b in doc["beats"]}
timings = json.load(io.open(os.path.join(REEL, "mp3/timings.json"), encoding="utf-8"))

# -- 1. the windows, against the re-rendered take-p ------------------------
by["B03"]["shot"]["window_s"] = [0.15, 7.20]
by["B11"]["shot"]["window_s"] = [6.90, 8.36]
by["B11"]["narration_text"] = (
    "Wind-up, then the live window with the bright arc. Nine active ticks, both "
    "facings, and the blade sits where the hitbox is to within four millionths of a "
    "pixel.")
by["B11"]["shot"]["show"] = [
    {"at": "0.10", "event": "landing, then idle - no sword in the sprite"},
    {"at": "0.42", "event": "windup - the arm goes up and back"},
    {"at": "0.62", "event": "the live window - the arc wedge appears"},
    {"at": "0.86", "event": "the blade sweeps down and forward"}]

# -- 2. cues bound to the measured narration -------------------------------
# cue i takes the fraction from show[i+1]: show[0] is always "the excerpt is
# framed", which is not a highlight.
for bid in ("B02", "B04", "B06", "B08", "B10"):
    b = by[bid]
    dur = timings[bid]
    cues = b["shot"]["remotion"]["props"]["cues"]
    fracs = [float(s["at"]) for s in b["shot"]["show"][1:]]
    if len(fracs) != len(cues):
        raise SystemExit("%s: %d cues but %d show fractions" % (bid, len(cues), len(fracs)))
    for cue, f in zip(cues, fracs):
        cue["at"] = round(f * dur, 2)
    b["shot"]["remotion"]["props"]["durationSeconds"] = round(dur, 3)

# every non-footage beat's durationSeconds follows its own measured audio
for bid, b in by.items():
    if "remotion" not in b["shot"]:
        continue
    if bid in timings:
        b["shot"]["remotion"]["props"].setdefault("durationSeconds", 0)
        if "durationSeconds" in b["shot"]["remotion"]["props"]:
            b["shot"]["remotion"]["props"]["durationSeconds"] = round(timings[bid], 3)

# -- 3. holds, derived ------------------------------------------------------
for bid in ("B03", "B07", "B11"):
    b = by[bid]
    w = b["shot"]["window_s"]
    clip = round(w[1] - w[0], 3)
    narr = timings[bid]
    hold = round(max(0.0, narr - clip), 3)
    b["shot"]["clip_s"] = clip
    b["shot"]["hold_s"] = hold
    b["shot"]["hold_note"] = (
        "The last frame is held for %.2f s. The clip is %.2f s of real play and the "
        "measured narration is %.2f s; nothing is retimed and no action is repeated."
        % (hold, clip, narr))

for bid, b in by.items():
    if bid in timings:
        b["actual_duration_s"] = round(timings[bid], 3)
        b["audio_file"] = "mp3/beat-%s.mp3" % bid

doc["beats"] = [by[b["beat_id"]] for b in doc["beats"]]
io.open(BS, "w", encoding="utf-8", newline="\n").write(
    json.dumps(doc, indent=1, ensure_ascii=False) + "\n")

total = sum(by[b["beat_id"]].get("actual_duration_s",
            b["estimated_duration_s"]) for b in doc["beats"])
print("beat_sheet.json finalised - %d beats, %d:%04.1f measured" % (
    len(doc["beats"]), int(total // 60), total % 60))
for b in doc["beats"]:
    sh = b["shot"]
    d = b.get("actual_duration_s", b["estimated_duration_s"])
    if "capture" in sh:
        tail = "FOOTAGE %s  clip %.2fs hold %.2fs" % (sh["capture"], sh["clip_s"], sh["hold_s"])
    else:
        n = len(sh["remotion"]["props"].get("cues", []))
        tail = "%s%s" % (sh["remotion"]["pattern"], "  %d cues" % n if n else "")
    print("  %-4s %-8s %6.2fs  %s" % (b["beat_id"], b["act"], d, tail))
