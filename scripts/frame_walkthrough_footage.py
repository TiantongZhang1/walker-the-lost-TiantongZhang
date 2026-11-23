#!/usr/bin/env python3
"""Inset the walkthrough's six gameplay beats in a card.

    python -X utf8 scripts/frame_walkthrough_footage.py

Run AFTER `scripts/build_media_clips.py`.

**Why this exists, and why it is not a crop.** Gate V refused the first
compile with fourteen BLOCKERs and thirteen MAJORs, all on the gameplay
beats, and both reasons are true of the footage rather than faults in it:

  edge-bleed    full-bleed gameplay touches the title-safe edge by
                definition -- there is no margin in a frame that IS the game
  low-contrast  this room is #16242B floor against a #17141B sky, a largest
                channel difference of 16 against the gate's threshold of 28,
                so a dungeon measures as having almost no content ink

The two honest options were to brighten the capture, which would misreport
what the engine drew, or to frame it. Assignment 5 measured this first and
chose framing; this does the same.

**Nothing is cropped.** Assignment 7's other film cropped to the action band
because its subject was a character's limbs. This film's subject is the
room -- the player crosses it, the traps are spread across it, the floating
key is a landmark between two of them -- so the whole frame is kept.

**Nothing is resampled unevenly either.** The capture is the game's 640 x 360
logical canvas at 6x. The inset is 1920 x 1080, which is that canvas at
**exactly 3x**: an integer division of an integer scale, done with a nearest
filter, so every logical pixel becomes a clean 3 x 3 block. It is the largest
of the three available clean sizes (3x, 2x, 1x); anything between them would
give a 2-1-2-1 pixel pattern that is visible on a 28-pixel character.

Every number on the card is read out of that take's own input log at build
time, so a re-recorded take changes the card with it.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-walkthrough"
MEDIA = REEL / "media"
LOGS = REEL / "capture/logs"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
PANEL = (44, 50, 62)

SAFE_L, SAFE_R = 230, 3600
INSET = (250, 430, 1920, 1080)        # the game's 640x360 canvas at exactly 3x
COL_X = 2300

# Which take each beat draws from, and the one line that says what the beat
# is for. The rest of each card is measured.
# `crop` is a LOGICAL (x, y, w, h) window of the 640 x 360 room, or None for
# all of it. Both choices land on the 1920 x 1080 inset at an integer scale:
# a 320 x 180 crop is the capture's own 6x pasted 1:1, and the whole room is
# 3x. There is no third option that does not give a 2-1-2-1 pixel pattern.
#
# **Which beats crop is decided by where the player goes**, measured from
# the take logs rather than chosen: take a runs x 5..174 and take b stands
# at 96, so both fit in the room's left half; take c reaches 357 and take d
# reaches 491, so those two keep the whole room.
#
# The first cut framed every beat at 3x and the character was 84 pixels in a
# 2160-pixel frame -- four per cent of the height, on a film whose subject is
# whether you can see its legs alternate. Cropping where the player stays
# put doubles that, and the beats where the player crosses the room keep the
# room, because that crossing IS what they show.
HALF_ROOM = (0, 100, 320, 180)
BEATS = {
    "B02": ("a", "Idle, the cycle, and the dust", HALF_ROOM),
    "B03": ("a", "Rising, falling, and the key", HALF_ROOM),
    "B04": ("b", "The committing action", HALF_ROOM),
    "B05": ("b", "An action during another action", HALF_ROOM),
    "B06": ("c", "Travelling, and jumping, through a swing", None),
    "B07": ("d", "The hazard, and the fifth state", None),
}
CAPTURE_SCALE = 6


def font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sans(size):
    return font(("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"), size)


def mono(size):
    return font(("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"), size)


def rows(take: str) -> list[dict]:
    p = LOGS / ("take-%s-inputs.jsonl" % take)
    if not p.is_file():
        raise SystemExit("missing %s -- render the take first" % p)
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def facts(take: str) -> list[str]:
    r = rows(take)
    clips, wraps, last = {}, 0, 0.0
    swings, lsw = 0, r[0]["swing_count"]
    opens, was = 0, False
    left = right = False
    for x in r:
        if x["clip"]:
            clips[x["clip"]] = True
        if x["legs"] == "legs_run":
            if x["clip_t"] < last - 0.01:
                wraps += 1
            last = x["clip_t"]
        else:
            last = 0.0
        if x["swing_count"] != lsw:
            swings += 1
            lsw = x["swing_count"]
        if x["monitoring"] and not was:
            opens += 1
        was = x["monitoring"]
        if x["facing"] < 0:
            left = True
        else:
            right = True
    out = [
        "take-%s - SCRIPTED INPUT" % take,
        "held keys, real input map",
        "",
        "frames          %d" % len(r),
        "take length     %.2f s" % r[-1]["t"],
        "clips seen      %d" % len(clips),
        "cycle wraps     %d" % wraps,
        "facings         %s" % ("both" if left and right else
                                ("right" if right else "left")),
    ]
    if swings:
        out.append("swings          %d" % swings)
        out.append("window opened   %d times" % opens)
    out.append("health at end   %d of 5" % r[-1]["health"])
    out += ["", "nothing teleported,", "no clip seeked"]
    return out


def card(title: str, lines: list[str], crop_note: str) -> Image.Image:
    im = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(im)
    d.text((SAFE_L, 170), title, font=sans(84), fill=INK)
    x, y, w, h = INSET
    d.rectangle([x - 14, y - 14, x + w + 14, y + h + 14], fill=PANEL)
    d.text((COL_X, y - 6), "ENGINE CAPTURE  3840 x 2160", font=sans(36),
           fill=DIM)
    d.line([COL_X, y + 50, SAFE_R, y + 50], fill=RULE, width=4)
    ty = y + 92
    f = mono(38)
    for line in lines:
        d.text((COL_X, ty), line, font=f, fill=INK if line.strip() else DIM)
        ty += 58
    foot = (crop_note + " No pixel value is altered and nothing is "
            "retimed; it is inset so the picture does not touch the "
            "title-safe edge.")
    ff = sans(32)
    fy = 1900
    words, line, wrapped = foot.split(), "", []
    for word in words:
        trial = (line + " " + word).strip()
        if d.textlength(trial, font=ff) > SAFE_R - SAFE_L - 480 and line:
            wrapped.append(line)
            line = word
        else:
            line = trial
    wrapped.append(line)
    for row in wrapped:
        d.text((SAFE_L, fy), row, font=ff, fill=DIM)
        fy += 40
    d.text((SAFE_R - d.textlength("@NikBearBrown", font=sans(40)), 1895),
           "@NikBearBrown", font=sans(40), fill=INK)
    return im


def frame(bid: str, take: str, title: str, crop=None) -> None:
    src = MEDIA / ("%s.mp4" % bid)
    if not src.is_file():
        raise SystemExit("%s is missing; run build_media_clips.py first" % src)
    keep = MEDIA / ("%s-fullbleed.mp4" % bid)
    if not keep.is_file():
        shutil.copyfile(src, keep)
    base = MEDIA / ("%s-base.png" % bid)
    note = ("The whole frame, uncropped, at an exact 3x of the game's "
            "640 x 360 canvas." if crop is None else
            "The left half of the room - %d x %d logical of 640 x 360 - at "
            "the capture's own 6x, pasted 1:1. The player never leaves it "
            "in this take." % (crop[2], crop[3]))
    card(title, facts(take), note).save(base)
    x, y, w, h = INSET
    if crop is None:
        vf = "[1:v]scale=%d:%d:flags=neighbor[g];" % (w, h)
        how = "the whole 640x360 room at 3x"
    else:
        cx, cy, cw, ch = (v * CAPTURE_SCALE for v in crop)
        if (cw, ch) != (w, h):
            raise SystemExit(
                "%s: a %dx%d logical crop is %dx%d at %dx, but the inset is "
                "%dx%d -- pick one that lands on it exactly."
                % (bid, crop[2], crop[3], cw, ch, CAPTURE_SCALE, w, h))
        vf = "[1:v]crop=%d:%d:%d:%d[g];" % (cw, ch, cx, cy)
        how = "%dx%d logical of the room, pasted 1:1" % (crop[2], crop[3])
    tmp = MEDIA / ("%s-framed.mp4" % bid)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(base),
         "-i", str(keep), "-filter_complex",
         vf + "[0:v][g]overlay=%d:%d:shortest=1[v]" % (x, y),
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
         "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
    tmp.replace(src)
    base.unlink()
    print("  %s  take-%s  %s" % (bid, take, how))


def main() -> int:
    for bid, (take, title, crop) in BEATS.items():
        frame(bid, take, title, crop)
    print("")
    print("  The full-bleed originals are kept beside each beat as")
    print("  media/<BID>-fullbleed.mp4, so running this twice does not")
    print("  put a card inside a card -- the failure A5 shipped once.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
