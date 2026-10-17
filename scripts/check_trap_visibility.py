#!/usr/bin/env python3
"""Assert that a risen trap is actually DRAWN, not merely lethal.

A playtest found the traps killing the player while still painted underground:
the Area2D moved up, but session.gd only redrew the level once from _ready(),
so the spike never appeared. Sixty-nine state assertions missed it because none
of them looked at the rendered image.

This checks the pixels. evidence/screens/05-trap-buried.png and
06-trap-risen.png are captured by godot/tests/capture_game.gd at the same
camera position, so the only thing that may differ between them is the spike.

    python3 scripts/check_trap_visibility.py     # exit 0 = pass
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCREENS = ROOT / "evidence" / "screens"
LEVEL = ROOT / "godot" / "levels" / "first_steps.json"
LOGICAL_W = 640
SPIKE_RGB = (210, 78, 66)          # Color("d24e42") as drawn
TOLERANCE = 30                     # per-channel, to allow for any blending


def spike_mask(img, rect, camera_x):
    """Pixels inside the spike's screen rect that are the spike colour."""
    arr = np.asarray(img.convert("RGB")).astype(int)
    scale = img.width / LOGICAL_W
    sx, sy, sw, sh = rect
    left = (sx - camera_x + LOGICAL_W / 2) * scale
    top = sy * scale + (img.height / 2 - 180 * scale)
    box = arr[int(top):int(top + sh * scale), int(left):int(left + sw * scale)]
    if box.size == 0:
        raise SystemExit(f"spike rect {rect} is off-screen for camera {camera_x}")
    near = np.abs(box - np.array(SPIKE_RGB)).max(axis=2) <= TOLERANCE
    return int(near.sum()), box.shape[0] * box.shape[1]


def main():
    level = json.loads(LEVEL.read_text(encoding="utf-8"))
    rect = level["traps"][0]["spike"]
    buried = Image.open(SCREENS / "05-trap-buried.png")
    risen = Image.open(SCREENS / "06-trap-risen.png")
    # capture_game.gd prints the camera x it used; both frames share it.
    camera_x = 1117.2

    b_hits, area = spike_mask(buried, rect, camera_x)
    r_hits, _ = spike_mask(risen, rect, camera_x)

    print(f"trap 0 spike rect {rect}, screen area {area} px")
    print(f"  buried frame: {b_hits} spike-coloured pixels")
    print(f"  risen  frame: {r_hits} spike-coloured pixels")

    ok = True
    if b_hits != 0:
        print("  FAIL: the buried trap is visible; it must be hidden by the ground")
        ok = False
    if r_hits < 40:
        print(f"  FAIL: the risen trap is barely drawn ({r_hits} px) — it is lethal "
              "while invisible, which is the defect this check exists for")
        ok = False
    if ok:
        print("  PASS: hidden while buried, drawn while risen")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
