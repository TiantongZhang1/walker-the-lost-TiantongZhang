#!/usr/bin/env python3
"""Crop the two footage beats to the band the action happens in.

Gate V measured B03 and B05 at 47 % of the title-safe area and called it
underfill, correctly: the room is 640 x 360 logical and the traps occupy a
60-pixel band across the middle of it, so a 4K frame of this game is mostly
empty sky above and empty floor below.

Cropping is a framing choice, not a change to the evidence. Nothing is
brightened, retimed, composited or re-ordered; the pixels that remain are the
pixels the engine drew, at their own values. The crop window is fixed for
both beats and is derived from the room, not eyeballed:

    traps at x 208, 320, 432, each sprite 16 px wide
    detection zones span x 175 .. 465
    the player is 16 x 28 and walks the floor at y about 172 .. 200
    the floor's top edge is y = 200

so the band that has to stay is x 175..465, y 170..215. Centred on that and
opened out to 16:9 at the largest size that keeps all three traps clear of
the edge:

    x 107 .. 533   (426 wide)     y 80 .. 320   (240 tall)

which is 1.775:1, within a pixel of 16:9. At the capture's 6x scale that is
(642, 480) + 2556 x 1440, upscaled back to 3840 x 2160 with nearest
neighbour - the game is nearest-filtered pixel art and anything else would
invent detail that was never drawn.

    python -I scripts/crop_footage_beats.py

SHOTLIST.md records that these two beats are cropped and by how much.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEDIA = ROOT / "youtube/claude-liam-walker-the-lost-gamedev/media"
BEATS = ("B03", "B05")

# Logical-pixel crop, and the capture's scale from logical to recorded.
LOGICAL = (107, 80, 426, 240)
SCALE = 6
OUT_W, OUT_H = 3840, 2160


def main() -> int:
    x, y, w, h = (v * SCALE for v in LOGICAL)
    vf = ("crop=%d:%d:%d:%d,scale=%d:%d:flags=neighbor"
          % (w, h, x, y, OUT_W, OUT_H))
    for bid in BEATS:
        src = MEDIA / ("%s.mp4" % bid)
        if not src.is_file():
            raise SystemExit("%s is missing; run build_media_clips.py first" % src)
        keep = MEDIA / ("%s-uncropped.mp4" % bid)
        if not keep.is_file():
            shutil.copyfile(src, keep)
        tmp = MEDIA / ("%s-cropped.mp4" % bid)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(keep),
             "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "14",
             "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
        tmp.replace(src)
        print("  %s  crop %d,%d %dx%d of the logical room, rescaled to %dx%d"
              % (bid, LOGICAL[0], LOGICAL[1], LOGICAL[2], LOGICAL[3], OUT_W, OUT_H))
        print("        uncropped original kept as %s" % keep.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
