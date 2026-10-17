#!/usr/bin/env python3
"""Render a level map straight from godot/levels/first_steps.json.

Everything drawn here is read from the level data the game actually loads, so
the map cannot drift away from the level. It is a documentation aid, not a
gameplay screenshot - the real rendered frames live in evidence/screens/.

    python3 scripts/build_level_map.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
LEVEL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "godot" / "levels" / "first_steps.json"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "design" / "level-extension-map.png"

SCALE = 1.15
INK = (37, 53, 74)
NEW = (40, 123, 175)
PLANK = (40, 124, 104)
SPIKE = (210, 78, 66)
TRAP = (232, 150, 40)
SLIME = (122, 182, 72)
HORSE = (150, 90, 160)
HILL = (228, 232, 227)
PAPER = (246, 243, 236)
ORIGINAL_WIDTH = 960          # where the starter's level ended


def font(size, bold=False):
    names = (["msyhbd.ttc", "arialbd.ttf"] if bold else ["msyh.ttc", "arial.ttf"])
    for n in names:
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{n}", size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    level = json.loads(LEVEL.read_text(encoding="utf-8"))
    width = float(level["width"])
    img = Image.new("RGB", (int((width + 40) * SCALE), int(500 * SCALE)), PAPER)
    d = ImageDraw.Draw(img)
    fb, fs, ft = font(17, True), font(13), font(11)

    def rect(x, y, w, h, colour):
        d.rectangle([(x + 20) * SCALE, (y + 60) * SCALE,
                     (x + 20 + w) * SCALE, (y + 60 + h) * SCALE], fill=colour)

    for hx in level["hills"]:
        d.polygon([((hx - 90 + 20) * SCALE, (320 + 60) * SCALE),
                   ((hx + 50 + 20) * SCALE, (180 + 60) * SCALE),
                   ((hx + 190 + 20) * SCALE, (320 + 60) * SCALE)], fill=HILL)

    for x, y, w, h in level["solids"]:
        new = x >= ORIGINAL_WIDTH
        rect(x, y, w, h, (PLANK if h <= 8 else (NEW if new else INK)))

    def spikes(sx, sy, sw, sh, colour):
        for i in range(max(1, int(sw / 8))):
            x = sx + i * 8
            d.polygon([((x + 20) * SCALE, (sy + sh + 60) * SCALE),
                       ((x + 24) * SCALE, (sy + 60) * SCALE),
                       ((x + 28) * SCALE, (sy + sh + 60) * SCALE)], fill=colour)

    for sx, sy, sw, sh in level["hazards"]:
        spikes(sx, sy, sw, sh, SPIKE)
    for trap in level["traps"]:
        sx, sy, sw, sh = trap["spike"]
        spikes(sx, sy, sw, sh, TRAP)
        tx = (trap["trigger_x"] + 20) * SCALE
        d.line([tx, (296 + 60) * SCALE, tx, (400 + 60) * SCALE], fill=TRAP, width=2)
        d.line([tx, (400 + 60) * SCALE, (sx + 32) * SCALE, (400 + 60) * SCALE], fill=TRAP, width=1)
        d.text((tx + 4, (404 + 60) * SCALE), f"trigger {trap['trigger_x']}", font=ft, fill=TRAP)

    for enemy in level.get("enemies", []):
        ex, ey = enemy["spawn"]
        kind = enemy.get("kind", "slime")
        if kind == "horse":
            rect(ex - 13, ey - 18, 26, 18, HORSE)
        else:
            rect(ex - 11, ey - 16, 22, 16, SLIME)
        lo, hi = float(enemy["from"]), float(enemy["to"])
        py = (ey + 60 + 6) * SCALE
        tint = HORSE if kind == "horse" else SLIME
        d.line([(lo + 20) * SCALE, py, (hi + 20) * SCALE, py], fill=tint, width=2)
        for bx in (lo, hi):
            d.line([(bx + 20) * SCALE, py - 5, (bx + 20) * SCALE, py + 5], fill=tint, width=2)
        d.text(((lo + 20) * SCALE, py + 8), f"{kind} {int(hi - lo)}px", font=ft, fill=tint)

    fx = float(level["finish"][0])
    rect(fx + 3, 250, 3, 70, INK)
    d.polygon([((fx + 5 + 20) * SCALE, (250 + 60) * SCALE),
               ((fx + 32 + 20) * SCALE, (260 + 60) * SCALE),
               ((fx + 5 + 20) * SCALE, (274 + 60) * SCALE)], fill=PLANK)

    for text_x, text_y, size, text in level["labels"]:
        d.text(((text_x + 20) * SCALE, (text_y + 60) * SCALE - 12), text,
               font=font(int(size)), fill=INK)

    bx = (ORIGINAL_WIDTH + 20) * SCALE
    d.line([bx, 44 * SCALE, bx, 440 * SCALE], fill=(160, 160, 160), width=2)
    d.text((bx - 96 * SCALE, 28 * SCALE), "starter ends 960", font=fs, fill=(120, 120, 120))
    sx = float(level["spawn"][0])
    d.line([(sx + 20) * SCALE, 300 * SCALE, (sx + 20) * SCALE, 396 * SCALE],
           fill=(120, 120, 120), width=1)
    d.text(((sx + 24) * SCALE, 286 * SCALE), "spawn", font=ft, fill=(120, 120, 120))

    d.text((20 * SCALE, 14 * SCALE),
           f"{level['id']} - {level['width']} x {level['fall_y']} - rendered from "
           f"godot/levels/first_steps.json, not drawn by hand",
           font=fb, fill=INK)
    img.save(OUT)
    print(f"wrote {OUT} {img.size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
