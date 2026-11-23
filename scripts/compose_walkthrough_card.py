#!/usr/bin/env python3
"""Compose the walkthrough's one still: cause and effect, before and after.

    python -X utf8 scripts/compose_walkthrough_card.py

The assignment asks the film to *"explain at least one cause-and-effect
connection between a source change (a key time, a transition setting, a
restart) and what the player sees, before and after."* Everything else in
this film is footage of the current build; this is the only beat that has to
show something that no longer exists.

Both panels are captures of **the same preview fixture at the same table
frame** -- capture frame 16, which is table frame 6, the last frame before
the hitbox opens. One is revision r1 and one is the shipped r4. Nothing is
retinted, composited or retimed; the panels are cropped to the figure and
pasted at an integer scale.

The numbers under them are computed here from the two revisions' own key
tables, which are in `CHANGE-BRIEF.md` revisions 7.0.2 and 7.0.3 -- the tip's
vertical reach is the thing the author's complaint was about, and it is a
range over a function rather than an impression.
"""
from __future__ import annotations

import io
import math
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-walkthrough"
MEDIA = REEL / "media"
CAP = ROOT / "captures/swing"
EVID = ROOT / "evidence/a7"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
EDGE = (206, 201, 192)
SAFE_L, SAFE_R = 230, 3600
STRIP_SCALE = 2                      # the r0-r4 strips are 1280x720 of 640x360

# `swing_preview.tscn` stands the player at logical (150, 150).
PLAYER_X = 150.0
FRAME = 16                           # table frame 6: the last pre-window frame

# The two key tables, from CHANGE-BRIEF.md. **The blade's pivot is at the
# hand and the blade points OUT of it**, so the tip is at
# (pivot + LEN * sin(deg), pivot - LEN * cos(deg)) with y downward.
R1 = {"len": 16.0, "pivot": (3.0, -2.0),
      "keys": [(0, 20), (6, -80), (10, 85), (12, 75), (18, 20)]}
R4 = {"len": 20.0, "pivot": None,    # keyed; positions below
      "keys": [(0, -150), (4, -60), (6, -50), (10, 100), (12, 115), (18, -150)],
      "pos": {0: (0, 2), 4: (2, -4), 6: (3, -5), 10: (13, 1), 12: (12, 3),
              18: (0, 2)}}


def tips(rev):
    out = []
    for frame, deg in rev["keys"]:
        px, py = rev["pivot"] if rev["pivot"] else rev["pos"][frame]
        r = math.radians(deg)
        out.append((frame, deg,
                    px + rev["len"] * math.sin(r),
                    py - rev["len"] * math.cos(r)))
    return out


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


def crop(rev: str, w: int = 92, h: int = 78) -> Image.Image:
    p = CAP / rev / ("frame%08d.png" % FRAME)
    if not p.is_file():
        raise SystemExit("missing %s" % p)
    im = Image.open(p).convert("RGB")
    cx, cy = int(PLAYER_X * STRIP_SCALE), int(174 * STRIP_SCALE)
    pw, ph = w * STRIP_SCALE, h * STRIP_SCALE
    cx = max(pw // 2, min(im.width - pw // 2, cx))
    cy = max(ph // 2, min(im.height - ph // 2, cy))
    return im.crop((cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2))


def main() -> int:
    a, b = crop("r1"), crop("r4")
    factor = 4
    a = a.resize((a.width * factor, a.height * factor), Image.NEAREST)
    b = b.resize((b.width * factor, b.height * factor), Image.NEAREST)

    card = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(card)
    d.text((SAFE_L, 130), "One change, and what the player saw",
           font=sans(92), fill=INK)

    gap = 90
    total = a.width + b.width + gap
    x0 = (W - total) // 2
    y0 = 300
    for im, x, label in ((a, x0, "BEFORE  r1  -  the author: it is spinning in circles above the body"),
                         (b, x0 + a.width + gap, "AFTER  r4  -  the shipped swing")):
        card.paste(im, (x, y0))
        d.rectangle([x - 3, y0 - 3, x + im.width + 2, y0 + im.height + 2],
                    outline=EDGE, width=3)
    d.text((x0, y0 - 54), "BEFORE   r1, capture frame %d" % FRAME,
           font=sans(40), fill=INK)
    d.text((x0 + a.width + gap, y0 - 54),
           "AFTER   r4, the same frame", font=sans(40), fill=INK)

    y = y0 + a.height + 50
    d.text((SAFE_L, y), "the blade tip's vertical reach, from the key tables",
           font=sans(50), fill=INK)
    y += 72
    d.line([SAFE_L, y, SAFE_R, y], fill=RULE, width=4)
    y += 36

    t1, t4 = tips(R1), tips(R4)
    lo1 = max(t[3] for t in t1)      # y is DOWN: the largest y is the lowest
    lo4 = max(t[3] for t in t4)
    rows = ["  rev   frame   deg      tip y        (y is DOWN; the waist is 0)"]
    rows.append("  " + "-" * 64)
    for rev, tt in (("r1", t1), ("r4", t4)):
        for frame, deg, _tx, ty in tt:
            rows.append("  %-5s %4d  %+6.0f   %+7.1f" % (rev, frame, deg, ty))
        rows.append("")
    rows.append("  r1: the tip never gets below y %+.1f in ANY of the 18 frames."
                % lo1)
    rows.append("  r4: it reaches y %+.1f -- past the waist, out of the top half."
                % lo4)

    f = mono(34)
    for row in rows:
        d.text((SAFE_L, y), row, font=f, fill=INK if row.strip() else DIM)
        y += 42

    foot = ("Both panels are the same preview fixture at the same table "
            "frame, cropped to the figure and scaled by an integer factor "
            "with a nearest filter. No pixel value is altered. The table is "
            "computed from CHANGE-BRIEF.md revisions 7.0.2 and 7.0.3, not "
            "typed in.")
    ff = sans(32)
    fy = 1960
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
    d.text((SAFE_R - d.textlength("@NikBearBrown", font=sans(40)), 1955),
           "@NikBearBrown", font=sans(40), fill=INK)

    MEDIA.mkdir(parents=True, exist_ok=True)
    out = MEDIA / "B08.png"
    card.save(out)
    print("wrote %s" % out)

    EVID.mkdir(parents=True, exist_ok=True)
    io.open(EVID / "before-after.txt", "w", encoding="utf-8",
            newline="\n").write("\n".join(rows) + "\n")
    print("  r1 lowest tip y %+.1f, r4 lowest tip y %+.1f" % (lo1, lo4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
