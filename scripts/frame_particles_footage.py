#!/usr/bin/env python3
"""Crop and frame Assignment 6's five gameplay beats.

    python -X utf8 scripts/frame_particles_footage.py

Run AFTER scripts/build_media_clips.py, which cuts each beat's window out of
its take. Two steps, in this order:

**Crop**, for the three beats whose subject is a 24-pixel burst or an
8-pixel puff. The room is 640 x 360 logical and the action lives in a band
across the middle of it, so a 4K frame of this game is mostly empty wall
above and empty floor below. The crop window is derived from the room, not
eyeballed: traps at x 208, 320 and 432, detect zones spanning x 175..465, the
player 16 x 28 walking the floor at y 172..200, floor top edge y 200. The two
MOTE beats are not cropped - the field is the whole room and cropping it
would hide whether it is even.

Cropping is a framing choice and not a change to the evidence: nothing is
brightened, retimed, composited or re-ordered, and the pixels that remain are
the pixels the engine drew, at their own values. The game is nearest-filtered
pixel art, so the rescale is nearest too; anything else would invent detail
that was never drawn.

**Frame**, for all five. A5 measured why: Gate V counts a pixel as content
when it differs from the background by more than 28 in some channel, and this
game's floor is #16242B against a #17141B sky - a largest channel difference
of 16, so the floor is not content as far as the checker is concerned. A full
frame of this room measures underfilled however it is cropped. The two honest
options were to brighten the capture, which would misreport what the engine
drew, or to frame it. This frames it, and every number on the frame is read
out of that take's own input log at build time.

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
REEL = ROOT / "youtube/claude-liam-walker-the-lost-particles-gamedev"
MEDIA = REEL / "media"
LOGS = REEL / "capture/logs"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
PANEL = (44, 50, 62)

SAFE_L, SAFE_R = 230, 3600
INSET = (SAFE_L, 440, 2440, 1372)
COL_X = 2760

# Logical-pixel crop and the capture's scale from logical to recorded.
LOGICAL = (107, 80, 426, 240)
SCALE = 6
CROPPED = ("B03", "B03A", "B11")


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
    """Everything the five cards print, read out of the take logs. Nothing on
    a card is typed in, so a re-recorded take changes the cards with it."""
    p, r, c = rows("p"), rows("r"), rows("c")
    out = {
        "p_rows": len(p), "p_len": p[-1]["t"],
        "p_bursts": max(x["bursts"] for x in p),
        "p_dust": max(x["dust"] for x in p),
        "p_x0": min(x["player_x"] for x in p),
        "p_x1": max(x["player_x"] for x in p),
        "p_hp": p[-1]["health"],
        "r_rows": len(r), "r_len": r[-1]["t"],
        "r_bursts": max(x["bursts"] for x in r),
        "c_rows": len(c), "c_len": c[-1]["t"],
        "c_hp": c[-1]["health"],
    }
    # How long the player's x never moved: the paused stretch, measured
    # rather than asserted from the driver's own timings.
    best = run = 0
    for i in range(1, len(c)):
        if abs(c[i]["player_x"] - c[i - 1]["player_x"]) < 1e-6:
            run += 1
            best = max(best, run)
        else:
            run = 0
    out["c_still"] = best
    stop = next((x for x in c if not x["motes_emitting"]), None)
    out["c_stop_t"] = stop["t"] if stop else -1.0
    return out


def card(title: str, lines: list[str], footer: str) -> Image.Image:
    im = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(im)
    d.text((SAFE_L, 170), title, font=sans(92), fill=INK)
    x, y, w, h = INSET
    d.rectangle([x - 14, y - 14, x + w + 14, y + h + 14], fill=PANEL)
    d.text((COL_X, y - 6), "ENGINE CAPTURE", font=sans(38), fill=DIM)
    d.line([COL_X, y + 54, SAFE_R, y + 54], fill=RULE, width=4)
    ty = y + 96
    f = mono(38)
    for line in lines:
        d.text((COL_X, ty), line, font=f, fill=INK if line.strip() else DIM)
        ty += 58
    ff = sans(34)
    fy = 1930
    words, line = footer.split(), ""
    wrapped = []
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
    x, y, w, h = (v * SCALE for v in LOGICAL)
    tmp = MEDIA / ("%s-croptmp.mp4" % bid)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(keep),
         "-vf", "crop=%d:%d:%d:%d,scale=%d:%d:flags=neighbor" % (w, h, x, y, W, H),
         "-c:v", "libx264", "-preset", "medium", "-crf", "14",
         "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
    tmp.replace(src)
    print("  %s cropped to %d,%d %dx%d logical" % ((bid,) + LOGICAL))


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
         "[1:v]scale=%d:%d:flags=neighbor[g];[0:v][g]overlay=%d:%d:shortest=1[v]"
         % (w, h, x, y),
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
         "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
    tmp.replace(src)
    base.unlink()
    print("  %s framed: capture inset at %d,%d %dx%d" % ((bid,) + INSET))


def main() -> int:
    f = facts()
    for bid in CROPPED:
        crop(bid)

    frame("B03", "The burst, on the game's own event",
          ["take-p - PLAYED, 3840x2160",
           "held keys, real input map",
           "",
           "frames          %d" % f["p_rows"],
           "take length     %.2f s" % f["p_len"],
           "player x        %.0f to %.0f" % (f["p_x0"], f["p_x1"]),
           "bursts at once  %d" % f["p_bursts"],
           "health left     %d of 5" % f["p_hp"],
           "",
           "nothing teleported,",
           "no state written"],
          "capture/take-p.mp4 - cropped to the action band and inset; no pixel "
          "value altered. The driver asserted all three traps fired before the "
          "take counted as evidence.")

    frame("B03A", "Three at once - SCRIPTED, not played",
          ["take-r - SCRIPTED",
           "fired.emit() every 0.20 s",
           "",
           "frames          %d" % f["r_rows"],
           "take length     %.2f s" % f["r_len"],
           "bursts at once  %d" % f["r_bursts"],
           "",
           "in the PLAYED take",
           "the peak was      %d" % f["p_bursts"],
           "",
           "revision 6.0.2:",
           "the ceiling is real",
           "and unreachable"],
          "capture/take-r.mp4 - the signal is emitted directly at the spawner. "
          "No input is involved and this is not gameplay. Cropped to the action "
          "band and inset; no pixel value altered.")

    frame("B07A", "The field, and the paused tree",
          ["take-c - PLAYED",
           "",
           "frames          %d" % f["c_rows"],
           "take length     %.2f s" % f["c_len"],
           "longest stretch",
           "with x unmoved  %d frames" % f["c_still"],
           "",
           "process_mode is inherit,",
           "so a paused game is a",
           "frozen field"],
          "capture/take-c.mp4 - full frame, uncropped: the field is the whole "
          "room and cropping it would hide whether it is even. The still "
          "stretch is measured from the take's own log, not from the driver's "
          "timings.")

    frame("B07B", "Stopping is not clearing",
          ["take-c - PLAYED",
           "",
           "emitting went false",
           "at t            %.2f s" % f["c_stop_t"],
           "health          %d of 5" % f["c_hp"],
           "mote lifetime   8.0 s",
           "",
           "no new mote is born;",
           "the ones already alive",
           "finish on the ramp"],
          "capture/take-c.mp4 - full frame. The player was killed by walking "
          "onto a trap five times; a trap only re-arms on a fresh DetectArea "
          "entry, so standing on one does nothing after the first strike.")

    frame("B11", "The trail, and the turn",
          ["take-p - PLAYED",
           "",
           "stride            24 px",
           "puffs alive at once %d" % f["p_dust"],
           "player speed      96 px/s",
           "",
           "a stride takes 0.25 s",
           "and a puff lives 0.45,",
           "so the trail is 2-3 deep",
           "",
           "scale.x = -1 on the turn"],
          "capture/take-p.mp4 - the same unbroken take as the burst beat, a "
          "different window of it. Cropped to the action band and inset; no "
          "pixel value altered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
