#!/usr/bin/env python3
"""Assert enemies are DRAWN where they currently are, not where they spawned.

CHANGE-BRIEF revision 0.6.0 P16. Enemies move every physics frame, so a missed
repaint leaves them lethal at a position they are no longer drawn at. Revision
0.5.1 shipped exactly that defect for the pop-up traps and a playtest caught
it; no state assertion could, because the state was correct all along.

This looks at the pixels. For each captured enemy it checks that the enemy's
body colour appears inside its live collider box, and that the patrol has
actually carried it away from its spawn x, so a frozen render would fail.

    python3 scripts/check_enemy_visibility.py     # exit 0 = pass
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCREENS = ROOT / "evidence" / "screens"
LOGICAL_W, LOGICAL_H = 640, 360
BODY_RGB = {"slime": (122, 182, 72), "horse": (150, 90, 160)}
TOLERANCE = 40
MIN_MOVED = 6.0     # px the patrol must have carried the enemy from its spawn
MIN_HITS = 25       # body pixels expected inside the live box


def colour_hits(img, rgb, box_px):
    left, top, right, bottom = box_px
    arr = np.asarray(img.convert("RGB")).astype(int)
    left = max(0, int(left)); top = max(0, int(top))
    right = min(arr.shape[1], int(right)); bottom = min(arr.shape[0], int(bottom))
    if right <= left or bottom <= top:
        return -1
    patch = arr[top:bottom, left:right]
    near = np.abs(patch - np.array(rgb)).max(axis=2) <= TOLERANCE
    return int(near.sum())


def main():
    meta = json.loads((SCREENS / "enemy-shots.json").read_text(encoding="utf-8"))
    ok = True
    for shot in meta["shots"]:
        img = Image.open(SCREENS / f"{shot['label']}.png")
        scale = img.width / LOGICAL_W
        cam_x, cam_y = shot["camera"]
        print(f"{shot['label']}  camera x={cam_x:.1f}")
        for enemy in shot["enemies"]:
            w, h = enemy["size"]
            # live collider box -> logical screen -> image pixels
            sx = (enemy["x"] - cam_x + LOGICAL_W / 2) * scale
            sy = (enemy["y"] - cam_y + LOGICAL_H / 2) * scale
            box = (sx - w / 2 * scale, sy - h * scale, sx + w / 2 * scale, sy)
            hits = colour_hits(img, BODY_RGB[enemy["kind"]], box)
            moved = abs(enemy["x"] - enemy["spawn_x"])
            verdict = []
            if moved < MIN_MOVED:
                verdict.append(f"patrol only moved {moved:.1f} px - a frozen render could pass")
            if hits < MIN_HITS:
                verdict.append(f"only {hits} body pixels in the live box - drawn elsewhere?")
            status = "PASS" if not verdict else "FAIL"
            if verdict:
                ok = False
            print(f"  {status}  {enemy['kind']:5} #{enemy['index']}  x={enemy['x']:7.1f} "
                  f"(spawn {enemy['spawn_x']:.0f}, moved {moved:5.1f})  body px in live box: {hits}")
            for v in verdict:
                print(f"        {v}")
    print("PASS: every captured enemy is drawn at its live position"
          if ok else "FAIL: see above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
