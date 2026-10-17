#!/usr/bin/env python3
"""Compose B05's evidence strip: the eight committed poses on three backgrounds.

Output is 1529 x 987, which is the GodotDevWorkbench right-hand image area
measured off a rendered master. An earlier version was composed to no
particular aspect and rendered with 59 % of that area's width unused.

Three bands, one per background, each holding the eight poses 2 wide x 4 tall.
Sprites are nearest-neighbour at an integer 7x, so the pixels stay pixels.
Deterministic: same inputs, byte-identical PNG.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REEL = os.path.join(ROOT, "youtube", "claude-liam-walker-ninja-gamedev")
SRC = os.path.join(ROOT, "godot", "assets", "poses")
OUT = os.path.join(REEL, "media", "B05-poses.png")
FONT_UI = os.environ.get("ART_FONT_UI", os.path.join(
    os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "seguisb.ttf"))

POSES = ["p1-idle", "p2-run", "p3-rising", "p4-falling",
         "p5-dash", "p6-windup", "p7-live", "p8-death"]

W, H = 1529, 987
S = 7                     # integer sprite scale -> 224 px cell
CELL = 32 * S
PAD = 14
GAP = 22
LABEL = 38
MARGIN = 12               # keeps a reaching arm off the band edge

WALL = (0x1b, 0x16, 0x20)
LEDGE = (0xc8, 0x9a, 0x5a)
CREAM = (0xf7, 0xf4, 0xec)
INK = (0x1a, 0x1a, 0x1a)


def silhouette(sp: Image.Image) -> Image.Image:
    out = Image.new("RGBA", sp.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", sp.size, (0, 0, 0, 255)), (0, 0), sp.getchannel("A"))
    return out


def main() -> None:
    font = ImageFont.truetype(FONT_UI, 27)
    big = [Image.open(os.path.join(SRC, p + ".png")).convert("RGBA")
           .resize((CELL, CELL), Image.NEAREST) for p in POSES]

    bands = [
        ("on the dungeon wall", WALL, big),
        ("as solid silhouettes", WALL, [silhouette(s) for s in big]),
        ("on the torchlit edge", LEDGE, big),
    ]

    bw = 2 * CELL + 2 * MARGIN
    bh = 4 * CELL + 2 * MARGIN
    total_w = 3 * bw + 2 * GAP
    total_h = bh + LABEL
    assert total_w + 2 * PAD <= W, (total_w, W)
    assert total_h + 2 * PAD <= H, (total_h, H)

    canvas = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(canvas)
    x0 = (W - total_w) // 2
    y0 = (H - total_h) // 2

    for i, (label, bg, imgs) in enumerate(bands):
        bx = x0 + i * (bw + GAP)
        d.rectangle([bx, y0 + LABEL, bx + bw - 1, y0 + LABEL + bh - 1], fill=bg)
        for k, im in enumerate(imgs):
            canvas.paste(im, (bx + MARGIN + (k % 2) * CELL,
                              y0 + LABEL + MARGIN + (k // 2) * CELL), im)
        d.text((bx, y0 + 4), label, font=font, fill=INK)

    canvas.save(OUT)
    print("wrote", OUT, canvas.size, "aspect", round(W / H, 4),
          "sprite scale", str(S) + "x",
          "fill", str(total_w * 100 // W) + "% w", str(total_h * 100 // H) + "% h")


if __name__ == "__main__":
    main()
