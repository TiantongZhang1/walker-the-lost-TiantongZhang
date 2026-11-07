#!/usr/bin/env python3
"""Lay a revision's kept frames out as one strip.

    python scripts/build_effect_strip.py captures/hit_burst/r1 \
        --out captures/hit_burst/r1-strip.png

Every strip in captures/ is built by this script so that two revisions of the
same effect are laid out identically and can be compared by eye. The crop is
fixed in the game's LOGICAL coordinates and is centred on the trap at
x 320, y 200 -- see CROP below -- so the panel shows the same stretch of room
whatever the capture resolution is.

These are FIXTURE captures, from godot/previews/, not from play. TUNING.md and
TEST-REPORT.md label them as such wherever they appear.
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

# Logical half-extents of the crop, centred on the trap at (320, 200).
# godot/project.godot:19 -- the logical viewport is 640 x 360.
CROP_CX, CROP_CY = 320.0, 200.0
CROP_HALF_W, CROP_HALF_H = 160.0, 110.0
LOGICAL_W = 640.0

PANEL_W, PANEL_H = 480, 330
LABEL_H = 30
GAP = 8
COLS = 3
BG = (245, 241, 232)
INK = (26, 24, 22)

# CHANGE-BRIEF.md section 1.5. Frame -> what the brief calls that moment.
CAPTIONS = {
    10: "trigger",
    12: "+0.07 s",
    15: "+0.17 s",
    20: "+0.33 s",
    30: "+0.67 s",
    50: "+1.33 s",
    11: "+0.03 s",
    40: "+1.00 s",
    100: "+3.00 s",
    130: "+4.00 s",
    340: "+11.00 s",
}


def _font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("seguisb.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _panel(path: pathlib.Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = im.width / LOGICAL_W          # 1280-wide capture of a 640-wide game
    box = (
        round((CROP_CX - CROP_HALF_W) * scale),
        round((CROP_CY - CROP_HALF_H) * scale),
        round((CROP_CX + CROP_HALF_W) * scale),
        round((CROP_CY + CROP_HALF_H) * scale),
    )
    return im.crop(box).resize((PANEL_W, PANEL_H), Image.NEAREST)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("revision_dir")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = pathlib.Path(args.revision_dir)
    frames = sorted(
        (int(p.stem.replace("frame", "")), p) for p in src.glob("frame*.png")
    )
    if not frames:
        print("no frame*.png in %s" % src, file=sys.stderr)
        return 1

    rows = (len(frames) + COLS - 1) // COLS
    cell_h = LABEL_H + PANEL_H
    sheet = Image.new(
        "RGB",
        (GAP + COLS * (PANEL_W + GAP), GAP + rows * (cell_h + GAP)),
        BG,
    )
    draw = ImageDraw.Draw(sheet)
    bold = _font(19)

    for i, (number, path) in enumerate(frames):
        col, row = i % COLS, i // COLS
        x = GAP + col * (PANEL_W + GAP)
        y = GAP + row * (cell_h + GAP)
        draw.text((x + 2, y + 4), "frame %d" % number, font=bold, fill=INK)
        caption = CAPTIONS.get(number, "")
        if caption:
            draw.text((x + 108, y + 4), caption, font=bold, fill=INK)
        sheet.paste(_panel(path), (x, y + LABEL_H))

    out = pathlib.Path(args.out)
    sheet.save(out)
    print("%s  %d frames  %dx%d" % (out, len(frames), sheet.width, sheet.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
