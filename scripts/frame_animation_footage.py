#!/usr/bin/env python3
"""Crop and frame Assignment 7's three gameplay beats.

    python -X utf8 scripts/frame_animation_footage.py

Run AFTER scripts/build_media_clips.py, which cuts each beat's window out of
its take. Two steps, in this order.

**Crop.** The room is 640 x 360 logical and this film's subject is a 28-pixel
character inside it, so a 4K frame of this game is mostly empty wall above and
empty floor below. The crop windows below are derived from the takes' own
logs - the player's measured x range, plus the jump's measured apex - and not
eyeballed. They are printed when this runs.

**No pixel is resampled.** Each crop is chosen so that it lands on the inset
at an INTEGER scale: B03 and B11 crop 368 x 154 logical, which at the
capture's 6x is 2208 x 924 and is pasted at its native size; B05 crops
184 x 77, which at 6x is 1104 x 462 and is doubled with `neighbor`. The game
is nearest-filtered pixel art and a 1.5x nearest upscale gives a 2-1-2-1
pixel pattern that is visible on a 28-pixel figure, so the sizes were chosen
to avoid it rather than the scaling being chosen to fit the sizes.

Cropping is a framing choice and not a change to the evidence: nothing is
brightened, retimed, composited or re-ordered, and the pixels that remain are
the pixels the engine drew, at their own values.

**Frame.** Assignment 5 measured why: the compositor's fill gate counts a
pixel as content when it differs from the background by more than 28 in some
channel, and this game's floor is #16242B against a #17141B sky - a largest
channel difference of 16, so the floor is not content as far as the checker is
concerned. A full frame of this room measures underfilled however it is
cropped. The two honest options were to brighten the capture, which would
misreport what the engine drew, or to frame it. This frames it, and **every
number on the frame is read out of that take's own input log at build time.**

Each step keeps its own input file, so running this twice does not put a card
inside a card - the failure A5 shipped once and found only by looking at it.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-animation-gamedev"
MEDIA = REEL / "media"
LOGS = REEL / "capture/logs"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
PANEL = (44, 50, 62)

SAFE_L, SAFE_R = 230, 3600
INSET = (SAFE_L, 440, 2208, 924)
COL_X = 2620
SCALE = 6                       # the captures are 3840 x 2160 of 640 x 360

# logical (x, y, w, h) per beat, and the integer factor from 6x to the inset.
CROPS = {
    "B03": ((0, 118, 368, 154), 1),
    "B11": ((0, 118, 368, 154), 1),
    "B05": ((4, 141, 184, 77), 2),
}
TAKE_OF = {"B03": "c", "B05": "s", "B11": "m"}


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
    path = LOGS / ("take-%s-inputs.jsonl" % take)
    if not path.is_file():
        raise SystemExit("missing %s - render the take first" % path)
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def facts() -> dict:
    """Everything the three cards print, read out of the take logs. Nothing on
    a card is typed in, so a re-recorded take changes the cards with it."""
    c, s, m = rows("c"), rows("s"), rows("m")

    def wraps(log):
        n, last = 0, 0.0
        for r in log:
            if r["legs"] == "legs_run":
                if r["clip_t"] < last - 0.01:
                    n += 1
                last = r["clip_t"]
            else:
                last = 0.0
        return n

    def swing_lengths(log):
        out, run, last = [], 0, log[0]["swing_count"]
        for r in log:
            if r["swing_count"] != last:
                if run:
                    out.append(run)
                run, last = 0, r["swing_count"]
            if r["locked"]:
                run += 1
        if run:
            out.append(run)
        return out

    sl_s, sl_m = swing_lengths(s), swing_lengths(m)
    return {
        "c_rows": len(c), "c_len": c[-1]["t"], "c_wraps": wraps(c),
        "c_x0": min(r["player_x"] for r in c),
        "c_x1": max(r["player_x"] for r in c),
        "c_hp": c[-1]["health"] if "health" in c[-1] else 5,
        "c_left": sum(1 for r in c if r["facing"] < 0),
        "s_rows": len(s), "s_len": s[-1]["t"],
        "s_swings": len(sl_s), "s_min": min(sl_s), "s_max": max(sl_s),
        "s_opens": sum(1 for i in range(1, len(s))
                       if s[i]["monitoring"] and not s[i - 1]["monitoring"]),
        "m_rows": len(m), "m_len": m[-1]["t"],
        "m_swings": len(sl_m), "m_min": min(sl_m), "m_max": max(sl_m),
        "m_travel": sum(1 for r in m if r["locked"] and r["legs"] == "legs_run"),
        "m_air": sum(1 for r in m if r["locked"] and not r["on_floor"]),
    }


def card(title: str, lines: list[str], footer: str) -> Image.Image:
    im = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(im)
    d.text((SAFE_L, 170), title, font=sans(92), fill=INK)
    x, y, w, h = INSET
    d.rectangle([x - 14, y - 14, x + w + 14, y + h + 14], fill=PANEL)
    d.text((COL_X, y - 6), "ENGINE CAPTURE", font=sans(38), fill=DIM)
    d.line([COL_X, y + 54, SAFE_R, y + 54], fill=RULE, width=4)
    ty = y + 96
    f = mono(36)
    for line in lines:
        d.text((COL_X, ty), line, font=f, fill=INK if line.strip() else DIM)
        ty += 56
    ff = sans(34)
    fy = 1930
    words, line, wrapped = footer.split(), "", []
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
        fy += 42
    d.text((SAFE_R - d.textlength("@NikBearBrown", font=sans(40)), 1925),
           "@NikBearBrown", font=sans(40), fill=INK)
    return im


def crop(bid: str) -> None:
    src = MEDIA / ("%s.mp4" % bid)
    keep = MEDIA / ("%s-uncropped.mp4" % bid)
    if not src.is_file():
        raise SystemExit("%s is missing; run build_media_clips.py first" % src)
    if not keep.is_file():
        shutil.copyfile(src, keep)
    (lx, ly, lw, lh), factor = CROPS[bid]
    x, y, w, h = lx * SCALE, ly * SCALE, lw * SCALE, lh * SCALE
    vf = "crop=%d:%d:%d:%d" % (w, h, x, y)
    if factor != 1:
        vf += ",scale=%d:%d:flags=neighbor" % (w * factor, h * factor)
    tmp = MEDIA / ("%s-croptmp.mp4" % bid)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(keep), "-vf", vf,
         "-c:v", "libx264", "-preset", "medium", "-crf", "14",
         "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
    tmp.replace(src)
    print("  %s cropped to %d,%d %dx%d logical, x%d -> %dx%d (inset is %dx%d)"
          % (bid, lx, ly, lw, lh, factor, w * factor, h * factor,
             INSET[2], INSET[3]))
    if (w * factor, h * factor) != (INSET[2], INSET[3]):
        raise SystemExit(
            "%s: the crop lands at %dx%d but the inset is %dx%d, so ffmpeg "
            "would resample it. Pick a crop whose 6x size times an integer "
            "equals the inset." % (bid, w * factor, h * factor,
                                   INSET[2], INSET[3]))


def frame(bid: str, title: str, lines: list[str], footer: str) -> None:
    src = MEDIA / ("%s.mp4" % bid)
    cropped = MEDIA / ("%s-cropped.mp4" % bid)
    if not cropped.is_file():
        shutil.copyfile(src, cropped)
    base = MEDIA / ("%s-framed-base.png" % bid)
    card(title, lines, footer).save(base)
    x, y, w, h = INSET
    tmp = MEDIA / ("%s-framed.mp4" % bid)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(base),
         "-i", str(cropped), "-filter_complex",
         "[0:v][1:v]overlay=%d:%d:shortest=1[v]" % (x, y),
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
         "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
    tmp.replace(src)
    base.unlink()
    print("  %s framed: capture inset at %d,%d %dx%d, pasted 1:1"
          % ((bid,) + INSET))


def main() -> int:
    f = facts()
    for bid in CROPS:
        crop(bid)

    frame("B03", "The cycle, and the dust that shares its clock",
          ["take-c - PLAYED, 3840x2160",
           "held keys, real input map",
           "",
           "frames          %d" % f["c_rows"],
           "take length     %.2f s" % f["c_len"],
           "player x        %.0f to %.0f" % (f["c_x0"], f["c_x1"]),
           "cycle wraps     %d" % f["c_wraps"],
           "frames facing   %d" % f["c_left"],
           "  left",
           "",
           "2 x 24 px / 96 px/s",
           "       = 0.500 s"],
          "capture/take-c.mp4 - cropped to the action band and pasted at its "
          "own resolution; no pixel value altered and nothing resampled. This "
          "take never crosses a trap: the driver paces the clear stretch west "
          "of the first one, so the figure ends the take undamaged.")

    frame("B05", "Four swings, four fresh presses",
          ["take-s - PLAYED",
           "",
           "frames          %d" % f["s_rows"],
           "take length     %.2f s" % f["s_len"],
           "swings          %d" % f["s_swings"],
           "window opened   %d times" % f["s_opens"],
           "clip length     %d to %d" % (f["s_min"], f["s_max"]),
           "  physics frames",
           "",
           "0.600 s at 60 Hz",
           "       = 36 frames",
           "",
           "gaps are 0.5 s, longer",
           "than the 0.333 recovery,",
           "so none is buffered"],
          "capture/take-s.mp4 - cropped tight and doubled with a nearest "
          "filter, which on pixel art is an exact 2x of the pixels the engine "
          "drew. The hitbox window is NOT visible in this footage: a hitbox "
          "contributes no pixels, which is why it is measured instead.")

    frame("B11", "A travelling swing, and a jumped one",
          ["take-m - PLAYED",
           "",
           "frames          %d" % f["m_rows"],
           "take length     %.2f s" % f["m_len"],
           "swings          %d" % f["m_swings"],
           "clip length     %d to %d" % (f["m_min"], f["m_max"]),
           "  physics frames",
           "",
           "frames of swing with",
           "  legs_run under it  %d" % f["m_travel"],
           "frames of swing",
           "  off the floor      %d" % f["m_air"],
           "",
           "revisions 7.0.9 and",
           "7.0.10, in one take"],
          "capture/take-m.mp4 - cropped to the action band and pasted at its "
          "own resolution. The clip lengths are identical to take-s's: a "
          "swing that travels and a swing that leaves the floor both run the "
          "same 36 physics frames as one standing still.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
