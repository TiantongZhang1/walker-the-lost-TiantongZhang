#!/usr/bin/env python3
"""Compose the two grids the film needs from captures that already exist.

Nothing here measures anything or alters a pixel value. Each tile is a crop
of a committed PNG, rescaled with nearest neighbour, with the controlled
input printed above it. The numbers those captures produced stay where they
were recorded - captures/a5/REPORT.txt and
captures/a5/materials/SWEEP-REPORT.txt - and the beat sheet reads them from
there verbatim.

    python -X utf8 scripts/compose_a5_extras.py

Two outputs:

  captures/a5/controlled_grid.png        four controlled values of warn_amount
  captures/a5/materials/sweep_grid.png   four uniforms at min and max

Why grids at all. The assignment asks the film to show the controlled-value
captures and an interface sweep of the non-texture uniforms. Four separate
beats for four values would be four beats of the same trap, and the point of
a controlled series is that you see it side by side.
"""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
EDGE = (206, 201, 192)

# Trap 1 sits at logical (208, 200); the capture is the 1280 x 720 window, so
# logical x2. A 200 x 84 logical box around it holds the trap, the floor line
# under it and enough sky to judge the red against, and makes each tile wide
# enough that a 2 x 2 grid is close to 2:1 - the shape that fills the
# evidence card without leaving white gutters down both sides.
TRAP_LOGICAL = (208, 200)
TRAP_BOX = (200, 84)
TRAP_SCALE = 2          # window pixels per logical pixel
TRAP_ZOOM = 6           # nearest-neighbour magnification of the crop

# The two slimes in the 1280 x 720 material captures. Both are in frame on
# purpose: the dry one must not move while the flooded one is swept.
SLIME_CROP = (170, 330, 1100, 720)
SLIME_W = 620


def font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def mono(size):
    return font(("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"), size)


def grid(tiles, cols, label_h, pad=24):
    """tiles: [(label, PIL.Image)], all the same size."""
    tw, th = tiles[0][1].size
    rows = (len(tiles) + cols - 1) // cols
    w = tw * cols + pad * (cols + 1)
    h = (th + label_h) * rows + pad * (rows + 1)
    card = Image.new("RGB", (w, h), GROUND)
    d = ImageDraw.Draw(card)
    f = mono(int(label_h * 0.74))
    for i, (label, tile) in enumerate(tiles):
        cx = pad + (i % cols) * (tw + pad)
        cy = pad + (i // cols) * (th + label_h + pad)
        d.text((cx, cy), label, font=f, fill=INK)
        card.paste(tile, (cx, cy + label_h))
        d.rectangle([cx - 1, cy + label_h - 1, cx + tw, cy + label_h + th],
                    outline=EDGE)
    return card


def controlled_grid() -> pathlib.Path:
    src = ROOT / "captures/a5"
    cw, ch = TRAP_BOX
    x = (TRAP_LOGICAL[0] - cw // 2) * TRAP_SCALE
    y = (TRAP_LOGICAL[1] - ch // 2) * TRAP_SCALE
    tiles = []
    for label, name in (("0.0", "warn_0_0.png"), ("0.5", "warn_0_5.png"),
                        ("1.0", "warn_1_0.png"), ("2.0", "warn_2_0.png")):
        im = Image.open(src / name).convert("RGB")
        crop = im.crop((x, y, x + cw * TRAP_SCALE, y + ch * TRAP_SCALE))
        tiles.append(("warn_amount = " + label,
                      crop.resize((cw * TRAP_ZOOM, ch * TRAP_ZOOM), Image.NEAREST)))
    out = src / "controlled_grid.png"
    grid(tiles, 2, 46).save(out)
    return out


def sweep_grid() -> pathlib.Path:
    src = ROOT / "captures/a5/materials"
    x0, y0, x1, y1 = SLIME_CROP
    h = round(SLIME_W * (y1 - y0) / (x1 - x0))
    tiles = []
    for end in ("min", "max"):
        for uni in ("tint", "roughness_dry", "water_darkening", "water_roughness"):
            im = Image.open(src / ("sweep-%s-%s.png" % (uni, end))).convert("RGB")
            tiles.append(("%s  %s" % (uni, end),
                          im.crop(SLIME_CROP).resize((SLIME_W, h), Image.LANCZOS)))
    out = src / "sweep_grid.png"
    # Four columns, two rows. The grid sits above its table on a card whose
    # aspect is the workbench's image panel, so it has to be wide and short;
    # a 2 x 4 grid of these frames came out nearly square and shrank to a
    # third of the width.
    grid(tiles, 4, 36).save(out)
    return out


def main() -> int:
    for f in (controlled_grid(), sweep_grid()):
        print("  %s  %dx%d" % (f.relative_to(ROOT).as_posix(),
                               *Image.open(f).size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
