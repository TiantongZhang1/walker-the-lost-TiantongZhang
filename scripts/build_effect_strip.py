#!/usr/bin/env python3
"""Lay a revision's kept frames out as one strip.

    python scripts/build_effect_strip.py captures/hit_burst/r1 \
        --out captures/hit_burst/r1-strip.png

Every strip in captures/ is built by this script so that two revisions of the
same effect are laid out identically and can be compared by eye. The crop is
fixed in the game's LOGICAL coordinates -- see VIEWS below -- so the panel
shows the same stretch of room whatever the capture resolution is.

Two views, because the two effects are different sizes. `--view trap` (the
default) crops to the trap at x 320, y 200, which is where Effect A happens
and where a 24 px burst would be invisible in a whole-room panel. `--view
room` is the whole 640 x 360 viewport, which is the only honest frame for
Effect B: the motes ARE the room, and a crop would hide whether the field is
even.

These are FIXTURE captures, from godot/previews/, not from play. TUNING.md and
TEST-REPORT.md label them as such wherever they appear.
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

# Logical crops: name -> (centre x, centre y, half width, half height,
# panel width, panel height). godot/project.godot:19 -- the logical viewport
# is 640 x 360, so "room" is the whole of it.
VIEWS = {
    "trap": (320.0, 200.0, 160.0, 110.0, 480, 330),
    "room": (320.0, 180.0, 320.0, 180.0, 480, 270),
    # Effect C happens at the floor line on the left half of the room, and a
    # puff is a few pixels tall: the room view would hide it entirely.
    "feet": (120.0, 180.0, 120.0, 90.0, 480, 360),
}
LOGICAL_W = 640.0
LABEL_H = 30
GAP = 8
COLS = 3
BG = (245, 241, 232)
INK = (26, 24, 22)

# CHANGE-BRIEF.md section 1.5. Frame -> what the brief calls that moment.
CAPTIONS = {
    1: "first drawn frame",
    10: "trigger",
    12: "+0.07 s",
    15: "+0.17 s",
    20: "+0.33 s",
    30: "+0.67 s",
    50: "+1.33 s",
}

## Effect B reads a different clock: section 2.5's frames are about the
## condition, not about a trigger.
CAPTIONS_FEET = {
    20: "running right",
    26: "mid-stride",
    32: "next stride",
    50: "just after the turn",
    70: "running left",
    95: "after the stop",
}

CAPTIONS_ROOM = {
    1: "first drawn frame",
    10: "condition running",
    11: "one frame later",
    40: "steady state",
    100: "last frame alive",
    130: "1 s after death",
    340: "8 s after death",
}


def _font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("seguisb.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _panel(path: pathlib.Path, view: tuple) -> Image.Image:
    cx, cy, hw, hh, pw, ph = view
    im = Image.open(path).convert("RGB")
    scale = im.width / LOGICAL_W          # 1280-wide capture of a 640-wide game
    box = (
        round((cx - hw) * scale),
        round((cy - hh) * scale),
        round((cx + hw) * scale),
        round((cy + hh) * scale),
    )
    return im.crop(box).resize((pw, ph), Image.NEAREST)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("revision_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--view", choices=sorted(VIEWS), default="trap")
    args = ap.parse_args()

    view = VIEWS[args.view]
    panel_w, panel_h = view[4], view[5]
    captions = CAPTIONS
    if args.view == "room":
        captions = CAPTIONS_ROOM
    elif args.view == "feet":
        captions = CAPTIONS_FEET

    src = pathlib.Path(args.revision_dir)
    frames = sorted(
        (int(p.stem.replace("frame", "")), p) for p in src.glob("frame*.png")
    )
    if not frames:
        print("no frame*.png in %s" % src, file=sys.stderr)
        return 1

    rows = (len(frames) + COLS - 1) // COLS
    cell_h = LABEL_H + panel_h
    sheet = Image.new(
        "RGB",
        (GAP + COLS * (panel_w + GAP), GAP + rows * (cell_h + GAP)),
        BG,
    )
    draw = ImageDraw.Draw(sheet)
    bold = _font(19)

    for i, (number, path) in enumerate(frames):
        col, row = i % COLS, i // COLS
        x = GAP + col * (panel_w + GAP)
        y = GAP + row * (cell_h + GAP)
        draw.text((x + 2, y + 4), "frame %d" % number, font=bold, fill=INK)
        caption = captions.get(number, "")
        if caption:
            draw.text((x + 108, y + 4), caption, font=bold, fill=INK)
        sheet.paste(_panel(path, view), (x, y + LABEL_H))

    out = pathlib.Path(args.out)
    sheet.save(out)
    print("%s  %d frames  %dx%d" % (out, len(frames), sheet.width, sheet.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
