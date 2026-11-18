"""Where is the character's torso inside its 32 x 32 cell, measured?

`test_swing_clip.gd` holds three numbers that decide whether the sword reads
as swung or as spun: the torso's back edge, its front edge, and where the
hilt has to be on the last active frame. They were guessed once and the
author caught it twice in play -- the pivot sat on the character's BACK and
the blade turned about it like a clock hand.

So they are measured here instead, from the committed sheet, and this script
asserts that the constants in the test still match what the art says. Run it
like the other generators:

    python tools/check_sword_reach.py

**A column profile, not a bounding box.** The bounding box is useless for
this: the scarf streams out behind the figure and drags the box's left edge
to x = -11, which is why a pivot at x = +3 looked like "the middle" on paper
and sat on the scarf in the game. What matters is where the SOLID mass is,
so each column is counted and the dense run is the torso.
"""
import io
import pathlib
import re
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHEET = ROOT / "godot" / "assets" / "sprites" / "player_sheet.png"
TEST = ROOT / "godot" / "tests" / "test_swing_clip.gd"

CELL = 32
LIVE = 6               # CHANGE-BRIEF.md revision 7.0.1 section 3: p7-live
DENSE = 20             # a column with this many solid pixels is torso


def scarf(px):
    """The scarf is the purple ramp; everything else inked is body or limb."""
    r, g, b, a = px
    return a > 0 and b > r and b > g and r > g and (b - g) > 40


def main() -> int:
    im = Image.open(SHEET).convert("RGBA")
    c = im.crop(((LIVE % 4) * CELL, (LIVE // 4) * CELL,
                 (LIVE % 4) * CELL + CELL, (LIVE // 4) * CELL + CELL)).load()

    solid = {}
    for x in range(CELL):
        n = 0
        for y in range(CELL):
            p = c[x, y]
            if p[3] > 0 and not scarf(p):
                n += 1
        solid[x - CELL // 2] = n

    print("sheet cell %d ('live'), column profile in CENTRED cell coords" % LIVE)
    print("  x    solid px")
    for x in sorted(solid):
        if solid[x]:
            print("%+4d   %-3d %s" % (x, solid[x], "#" * solid[x]))

    dense = [x for x in sorted(solid) if solid[x] >= DENSE]
    back, front = dense[0], dense[-1]
    print("")
    print("  columns with >= %d solid px run %+d .. %+d" % (DENSE, back, front))
    print("  so the torso's BACK edge is x = %+d and its FRONT edge x = %+d"
          % (back, front))
    print("  (the ink bounding box starts at x = -11; that is the SCARF, and")
    print("   trusting it is what put the pivot on the character's back.)")

    src = io.open(TEST, encoding="utf-8").read()

    def const(name):
        m = re.search(r"const %s := ([-\d.]+)" % name, src)
        return None if m is None else float(m.group(1))

    bad = 0
    for name, want in (("TORSO_BACK", back), ("TORSO_FRONT", front)):
        got = const(name)
        ok = got is not None and abs(got - want) < 0.5
        bad += 0 if ok else 1
        print("  %-12s test says %s, the sheet says %+d   %s"
              % (name, got, want, "OK" if ok else "MISMATCH"))

    print("")
    print("  %d mismatch(es). This script measures; test_swing_clip.gd is "
          "where" % bad)
    print("  the numbers are USED, and TUNING.md is where a verdict goes.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
