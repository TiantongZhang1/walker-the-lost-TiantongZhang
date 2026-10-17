#!/usr/bin/env python3
"""Build the character-state contact sheet from real captured frames.

Reads evidence/screens/char-shots.json (written by godot/tests/capture_character.gd),
crops each captured frame around the recorded player position, upscales with
nearest-neighbour so individual logical pixels stay visible, and annotates the
18x28 collider.

The collider rectangle is drawn BY THIS SCRIPT as an annotation, from the same
numbers player.gd uses (shape.size 18x28 at offset (0,-14)). The game does not
render it. Everything else in the panels is the engine's own rendered output.

    python3 scripts/build_char_sheet.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LOGICAL_W, LOGICAL_H = 640, 360
CROP_W, CROP_H = 92, 76   # logical px (widened for the 30 px blade)
ZOOM = 9
COLLIDER_W, COLLIDER_H = 18, 28

ROOT = Path(__file__).resolve().parents[1]
SCREENS = ROOT / "evidence" / "screens"
OUT = SCREENS / "char-contact-sheet.png"


def load_font(name, size):
    for path in (f"C:/Windows/Fonts/{name}", f"/usr/share/fonts/truetype/dejavu/{name}"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    meta = json.loads((SCREENS / "char-shots.json").read_text(encoding="utf-8"))
    bold = load_font("arialbd.ttf", 20)
    plain = load_font("arial.ttf", 15)

    panels = []
    for shot in meta["shots"]:
        img = Image.open(SCREENS / f"{shot['label']}.png")
        scale = img.width / LOGICAL_W
        px, py = shot["player"]
        cx, cy = shot["camera"]
        # world -> logical screen -> image pixels
        sx = (px - cx + LOGICAL_W / 2) * scale
        sy = (py - cy + LOGICAL_H / 2) * scale
        left = sx - CROP_W / 2 * scale
        top = sy - (CROP_H - 10) * scale
        crop = img.crop((round(left), round(top),
                         round(left + CROP_W * scale), round(top + CROP_H * scale)))
        crop = crop.resize((CROP_W * ZOOM, CROP_H * ZOOM), Image.NEAREST)

        d = ImageDraw.Draw(crop)
        ox = (sx - left) / scale * ZOOM
        oy = (sy - top) / scale * ZOOM
        d.rectangle([ox - COLLIDER_W / 2 * ZOOM, oy - COLLIDER_H * ZOOM,
                     ox + COLLIDER_W / 2 * ZOOM, oy],
                    outline=(230, 60, 60), width=2)
        d.line([ox - 14 * ZOOM, oy, ox + 14 * ZOOM, oy], fill=(230, 60, 60), width=1)
        # The live swing hitbox, drawn from the endpoints the engine recorded.
        # Like the collider box this is an annotation, not game output -- but
        # unlike the collider it is what actually kills an enemy, so it is
        # drawn so the blade and the hitbox can be compared directly.
        if "hitbox" in shot:
            ax, ay, bx, by = shot["hitbox"]
            d.line([ox + ax * ZOOM, oy + ay * ZOOM, ox + bx * ZOOM, oy + by * ZOOM],
                   fill=(255, 140, 0), width=max(2, round(shot.get("hitbox_thickness", 4) * ZOOM)))
        d.text((6, 4), shot["label"].replace("char-", ""), font=bold, fill=(20, 30, 45))
        d.text((6, crop.height - 24),
               "facing %+d  on_floor=%s  vx=%.0f%s" % (
                   int(shot["facing"]), shot["on_floor"], shot["velocity"][0],
                   "  phase=%d" % shot["attack_phase"] if shot.get("attack_phase") else ""),
               font=plain, fill=(60, 70, 85))
        panels.append(crop)

    pad = 10
    per_row = 6
    rows = [panels[i:i + per_row] for i in range(0, len(panels), per_row)]
    pw = max(p.width for p in panels)
    ph = max(p.height for p in panels)
    width = per_row * pw + pad * (per_row + 1)
    height = len(rows) * (ph + pad) + pad + 26
    sheet = Image.new("RGB", (width, height), (246, 243, 236))
    for r, row in enumerate(rows):
        for c, p in enumerate(row):
            sheet.paste(p, (pad + c * (pw + pad), pad + r * (ph + pad)))
    ImageDraw.Draw(sheet).text(
        (pad, height - 22),
        f"Godot {meta['engine']} - real rendered viewport, cropped and {ZOOM}x "
        f"nearest-neighbour upscaled. RED BOX = the {COLLIDER_W}x{COLLIDER_H} collider, "
        "drawn by scripts/build_char_sheet.py as an annotation; the game does not render it. "
        "ORANGE LINE = the live swing hitbox on that frame, from the endpoints the engine recorded.",
        font=plain, fill=(120, 60, 60))
    sheet.save(OUT)
    print(f"wrote {OUT} {sheet.size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
