#!/usr/bin/env python3
"""Make every code beat FIT the panel it renders in.

The B02 pilot clipped: a 17-line excerpt showed 14 lines, so 132-134 were off
the bottom while the beat's last cue pointed at 134 and the narration claimed
`idle is what is left`. The third note was cut mid-word too.

Measured from that render: the code panel holds about 14 lines at the schema's
minimum 23 px font, and the notes column holds 2 cards. So the excerpts come
down to the panel rather than the panel being stretched to the excerpts - the
skill says to extend a shared component only for a real missing teaching need,
and "my excerpt was too long" is not one.
"""
import io, json, os

ROOT = r"D:\Graduate\2026Fall\7270\walker-ninja-TiantongZhang"
os.chdir(ROOT)
GAME, REEL = "godot", "youtube/claude-liam-walker-ninja-gamedev"
BS = os.path.join(REEL, "beat_sheet.json")
doc = json.load(io.open(BS, encoding="utf-8"))
by = {b["beat_id"]: b for b in doc["beats"]}


def excerpt(rel, a, b):
    lines = io.open(os.path.join(GAME, rel), encoding="utf-8", newline="").read().split("\n")
    return "\n".join(lines[a - 1:b])


# path, start, end, cues(line, label), notes(label, value), narration, show-fractions
FIT = {
    "B02": {
        "range": ("features/player/player.gd", 118, 131),
        "cues": [(119, "death first"), (124, "the swing outranks both"),
                 (128, "dash outranks the air"), (130, "rise or fall by the sign")],
        "notes": [
            ("Why a string and not a texture",
             "A string can be asserted without a renderer. The check drives the game "
             "through all eight states and reads the key back."),
            ("Why death is tested first",
             "A disabled body keeps whatever is_on_floor() last returned, so a pose "
             "read off movement would differ by cause of death.")],
        "narration":
            "Eight generated sprites, one per state. The function that picks one "
            "returns a string, not a texture - and that is the whole reason the "
            "mapping can be tested. Death is checked first, because on death the body "
            "is disabled and is on floor keeps whatever it last returned; a pose read "
            "off movement would depend on how you died. Then the swing, then the dash, "
            "and then the sign of vertical velocity for rising or falling.",
        "show": [(0.05, "the excerpt is already readable"),
                 (0.10, "line 119 highlights - death_pose"),
                 (0.33, "line 124 highlights - the live window"),
                 (0.55, "line 128 highlights - dash_ticks_left"),
                 (0.76, "line 130 highlights - not is_on_floor()")],
    },
    "B04": {
        "range": ("features/player/player.gd", 313, 326),
        "cues": [(318, "grown one way only"), (313, "x is forward, so it mirrors"),
                 (322, "polygons translate, not expand")],
        "notes": [
            ("The arithmetic",
             "A rim on four sides costs a part 2 px of width. A 3 px arm keeps 1 px of "
             "armour, and the limbs rendered as grey pipes."),
            ("Measured on the generated sprite",
             "Reading at 3:1 or better against the wall: 6.3% without the rim, 24.2% "
             "with it. The code-drawn character measures 9.1%.")],
        "narration": None,
        "show": [(0.04, "the excerpt and its notes are framed"),
                 (0.14, "line 318 highlights - the one-way growth"),
                 (0.48, "line 313 highlights - x is forward"),
                 (0.74, "line 322 highlights - the polygon case")],
    },
    "B06": {
        "range": ("game/session.gd", 276, 288),
        "cues": [(276, "the trigger gate"), (284, "the tick trap_risen leaves 0"),
                 (288, "the spike moves by its rise offset")],
        "notes": [
            ("Why not on the damage",
             "Hung off the contact it is a death sound, arriving after the information "
             "is useless - and it would still pass a test that only asked whether a "
             "sound played when the trap killed you."),
            ("Recorded",
             "Warning at tick 24, player at x 1064.6, trigger at 1064. Death at tick "
             "59. A 35-tick lead against a 15-tick rise.")],
        "narration": None,
        "show": [(0.05, "the excerpt is framed with its notes"),
                 (0.14, "line 276 highlights - the trigger comparison"),
                 (0.44, "line 284 highlights - trap_risen[i] == 0"),
                 (0.76, "line 288 highlights - the rise offset")],
    },
    "B08": {
        "range": ("game/session.gd", 601, 611),
        "cues": [(604, "guarded, not unconditional"),
                 (605, "playing OR stream_paused"),
                 (611, "play() only on a cold start")],
        "notes": [
            ("The bug inside the fix",
             "AudioStreamPlayer.playing reports FALSE while stream_paused is true. So "
             "testing playing alone was right for an ordinary death and wrong for "
             "pause-then-retry, where the track jumped to bar 1."),
            ("How it was found",
             "By printing what the engine reports in each state before writing the "
             "assertion. The code reads correctly.")],
        "narration": None,
        "show": [(0.05, "the excerpt is framed with its notes"),
                 (0.18, "line 604 highlights - the guard"),
                 (0.46, "line 605 highlights - playing or stream_paused"),
                 (0.76, "line 611 highlights - the cold start")],
    },
    "B10": {
        "range": ("features/player/player.gd", 678, 690),
        "cues": [(678, "the pivot the hitbox uses"),
                 (680, "the wedge only while it can kill"),
                 (689, "the blade itself")],
        "notes": [
            ("Three numbers, two consumers",
             "ATTACK_PIVOT, attack_angle() and attack_reach drive both this drawing "
             "and the kill hitbox. The poses were prompted 'empty hand, NO weapon'."),
            ("What baking it in would cost",
             "Both hitbox checks would still pass, because they measure the hitbox "
             "against the numbers and not against the picture. Worst endpoint error: "
             "3.8e-6 px.")],
        "narration": None,
        "show": [(0.05, "the excerpt is framed with its notes"),
                 (0.18, "line 678 highlights - ATTACK_PIVOT"),
                 (0.45, "line 680 highlights - phase >= 2"),
                 (0.74, "line 689 highlights - the bar from a to b")],
    },
}

timings = json.load(io.open(os.path.join(REEL, "mp3/timings.json"), encoding="utf-8"))

for bid, spec in FIT.items():
    b = by[bid]
    rel, a, e = spec["range"]
    n = e - a + 1
    if n > 14:
        raise SystemExit("%s: %d lines will clip" % (bid, n))
    props = b["shot"]["remotion"]["props"]
    props["code"] = excerpt(rel, a, e)
    props["startLine"] = a
    props["path"] = "godot/%s  lines %d-%d" % (rel, a, e)
    props["source"] = "godot/%s" % rel
    props["notes"] = [{"label": l, "value": v} for l, v in spec["notes"]]
    dur = timings[bid]
    props["cues"] = [{"at": round(f * dur, 2), "line": ln, "label": lb}
                     for (ln, lb), (f, _) in zip(spec["cues"], spec["show"][1:])]
    b["shot"]["show"] = [{"at": "%.2f" % f, "event": ev} for f, ev in spec["show"]]
    if spec["narration"]:
        b["narration_text"] = spec["narration"]
    print("  %s  %-34s %2d lines, %d cues, %d notes" % (
        bid, "%s %d-%d" % (rel.split("/")[-1], a, e), n, len(props["cues"]), len(props["notes"])))

doc["beats"] = [by[b["beat_id"]] for b in doc["beats"]]
io.open(BS, "w", encoding="utf-8", newline="\n").write(
    json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print("every code beat is now <= 14 lines and <= 2 notes")
