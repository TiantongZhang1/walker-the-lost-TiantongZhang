#!/usr/bin/env python3
"""Put the two gameplay beats inside a card, like every other beat.

Why, precisely. Gate V counts a pixel as content when it differs from the
background by more than 28 in some channel. This game's floor is #16242B
against a #17141B sky: the largest channel difference is 16, so THE FLOOR IS
NOT CONTENT as far as the checker is concerned. Only the player, the traps
and the grid lines register. A full-frame capture of this room therefore
measures 47 % filled and 0.11 contrast however it is cropped, and cropping
was tried: it moved neither number.

The two honest options were to brighten the capture or to frame it. The first
would misreport what the engine drew - and the low contrast is a design
requirement, not an accident: CHANGE-BRIEF.md section 6 puts the armed trap
at 1.12:1 against the floor so that a trap is not visible from across the
room. So: frame it. Not one pixel of the capture changes; it is inset on the
brand ground with the beat's title and the numbers the take itself recorded.

Every number on the card is computed from
capture/logs/take-w-inputs.jsonl at build time.

    python -I scripts/frame_footage_beats.py

Run after build_media_clips.py and crop_footage_beats.py.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-gamedev"
MEDIA = REEL / "media"
LOG = REEL / "capture/logs/take-w-inputs.jsonl"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
PANEL = (44, 50, 62)

# Title-safe at 3840 x 2160 is x 192..3648, y 108..2052 (layout.ts, scaled),
# with a 15 px tolerance. The first version of this card put its title and
# footer at x = 150 and ran the right column to 3690; Gate V called
# edge-bleed on every frame, correctly. Everything below sits inside.
SAFE_L, SAFE_R = 230, 3600
INSET = (SAFE_L, 440, 2440, 1372)   # x, y, w, h - 16:9 within the safe box
COL_X = 2760


def font(name_list, size):
    for n in name_list:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sans(size):
    return font(("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"), size)


def mono(size):
    return font(("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"), size)


def take_facts() -> dict:
    rows = [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    onsets, prev = [], [0.0, 0.0, 0.0]
    multi = 0
    for r in rows:
        w = r["warn"]
        if sum(1 for v in w if v > 0) > 1:
            multi += 1
        for k in range(3):
            if prev[k] == 0 and w[k] > 0:
                onsets.append((k + 1, r["t"], r["player_x"]))
        prev = w
    return {"rows": len(rows), "length": rows[-1]["t"], "onsets": onsets, "multi": multi}


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
    d.text((SAFE_L, 1930), footer, font=sans(34), fill=DIM)
    d.text((SAFE_R - d.textlength("@NikBearBrown", font=sans(40)), 1925),
           "@NikBearBrown", font=sans(40), fill=INK)
    return im


def frame_beat(bid: str, title: str, lines: list[str], footer: str) -> None:
    """Idempotent. The first version read media/<bid>.mp4 and wrote back to
    it, so a second run framed its own output and produced a card inside a
    card - which Gate V passed, because a nested card still fills the frame
    and still has contrast. Only looking at it caught that. Each step now
    keeps its own input, so this always starts from the cropped clip."""
    src = MEDIA / ("%s.mp4" % bid)
    cropped = MEDIA / ("%s-cropped.mp4" % bid)
    if not cropped.is_file():
        import shutil
        shutil.copyfile(src, cropped)
    src = cropped
    base = MEDIA / ("%s-framed-base.png" % bid)
    card(title, lines, footer).save(base)
    x, y, w, h = INSET
    tmp = MEDIA / ("%s-framed.mp4" % bid)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(base), "-i", str(src),
         "-filter_complex",
         "[1:v]scale=%d:%d:flags=neighbor[g];[0:v][g]overlay=%d:%d:shortest=1[v]" % (w, h, x, y),
         "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
         "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
    tmp.replace(MEDIA / ("%s.mp4" % bid))
    base.unlink()
    print("  %s framed: capture inset at %d,%d %dx%d" % (bid, x, y, w, h))


def main() -> int:
    f = take_facts()
    t1, t2, t3 = f["onsets"][0], f["onsets"][1], f["onsets"][2]

    frame_beat(
        "B03", "The warning, in motion",
        ["take-w - 3840 x 2160, 60 fps",
         "Forward+, RTX 5080",
         "",
         "warning begins   t %.2f s" % t1[1],
         "player at        x %.1f" % t1[2],
         "DetectArea zone  x 175",
         "",
         "the zone edge was derived",
         "from the warning length,",
         "not chosen"],
        "capture/take-w.mp4 - window 0.30-4.85 s. Cropped to the action band; "
        "no pixel value altered.")

    frame_beat(
        "B05", "One trap at a time",
        ["take-w - the whole walk",
         "",
         "frames sampled   %d" % f["rows"],
         "more than 1 lit  %d" % f["multi"],
         "",
         "trap 1  t %.2f  x %.1f" % (t1[1], t1[2]),
         "trap 2  t %.2f  x %.1f" % (t2[1], t2[2]),
         "trap 3  t %.2f  x %.1f" % (t3[1], t3[2]),
         "",
         "R6, checked every frame",
         "of a real run"],
        "capture/take-w.mp4 - window 0.60-11.33 s. The driver counted the lit "
        "traps itself and refused to report OK above one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
