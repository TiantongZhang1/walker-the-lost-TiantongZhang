"""Compose Assignment 7's two frame strips from a Movie Maker capture.

    python -I tools/build_anim_strips.py captures/swing/r0 captures/run/r0

**Nothing here judges anything.** It crops the frames `CHANGE-BRIEF.md` §10
names, labels each with its capture frame AND its table frame, and writes one
PNG per strip. Reading them is the author's job; a strip is a fixture and
every caption says so.

The capture is 1280 x 720 for a 640 x 360 logical viewport, so the scale is
exactly 2 and a logical rectangle is doubled to get the image rectangle. The
crop is derived from the floor line (logical y = 200) and the player's stand
position, not eyeballed.
"""
import pathlib
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCALE = 2                      # 1280 x 720 capture of a 640 x 360 viewport
ZOOM = 3                       # how much the cropped band is blown up

# CHANGE-BRIEF.md §10. Capture frame 10 is the swing's table frame 0, so
# table = capture - 10 for the swing. The cycle is a rig and has no table
# frames, so its strip is labelled by capture frame only.
SWING_FRAMES = [10, 16, 20, 22, 28, 40]
# The captions describe the TABLE, not one revision. r0 said table 10 had
# "the same pixels as table 6", which was true while the swing was frames
# only and false the moment the blade started rotating through it. A
# caption that is true of one capture is a caption that will lie about the
# next one.
SWING_SAYS = {
    10: "table 0  startup, windup",
    16: "table 6  active OPENS, live",
    20: "table 10 active CLOSES - nothing here says so",
    22: "table 12 recovery, back through windup",
    28: "table 18 end, idle, movement returns",
    40: "+0.4 s  unchanged",
}
RUN_FRAMES = [20, 21, 22, 23, 24, 25]

# Logical rectangles, (x0, y0, x1, y1). The floor line is y = 200 and the
# figure is 32 px tall standing on it, so 150..215 covers the character and a
# little floor under the feet.
BAND_SWING = (112, 146, 196, 215)
BAND_RUN = (40, 146, 208, 215)


def font(size):
    for n in ("consola.ttf", "segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def strip(folder: pathlib.Path, frames, band, captions, title, out):
    x0, y0, x1, y1 = (v * SCALE for v in band)
    cells = []
    for f in frames:
        p = folder / ("frame%08d.png" % f)
        if not p.is_file():
            raise SystemExit("missing %s — was the capture run?" % p)
        im = Image.open(p).convert("RGB").crop((x0, y0, x1, y1))
        w, h = im.size
        cells.append(im.resize((w * ZOOM, h * ZOOM), Image.NEAREST))

    cw, ch = cells[0].size
    pad, head, foot = 6, 34, 34
    sheet = Image.new("RGB", (len(cells) * (cw + pad) + pad,
                              ch + head + foot + pad * 2), (18, 15, 18))
    d = ImageDraw.Draw(sheet)
    f_title, f_small = font(20), font(15)
    d.text((pad + 2, 8), title, font=f_title, fill=(240, 232, 220))
    for i, im in enumerate(cells):
        x = pad + i * (cw + pad)
        sheet.paste(im, (x, head + pad))
        d.rectangle([x - 1, head + pad - 1, x + cw, head + pad + ch],
                    outline=(90, 78, 70))
        cap = "frame %d" % frames[i]
        d.text((x + 2, head + pad + ch + 5), cap, font=f_small,
               fill=(255, 212, 120))
        if frames[i] in captions:
            d.text((x + 2, head + pad + ch + 20), captions[frames[i]],
                   font=f_small, fill=(170, 200, 230))
    sheet.save(out)
    print("  wrote %s  (%d frames, logical band %s, %dx zoom)"
          % (out.relative_to(ROOT), len(frames), band, ZOOM))


def changes(folder: pathlib.Path, first: int, last: int, band) -> None:
    """How many pixels change from one captured frame to the next.

    A MEASUREMENT, not a reading. It answers two things the eye is bad at:
    did the clip advance at all, and does it hold between keys the way
    UPDATE_DISCRETE promises. It cannot answer whether the motion is good.

    **What it says about holding is derived, not asserted.** An earlier
    version printed "every other frame is identical to the one before it",
    which was true while the swing was a frame clip and became false the
    moment a continuous rotation track was added. The sentence had not
    noticed. Now the frames are counted.
    """
    x0, y0, x1, y1 = (v * SCALE for v in band)
    prev = None
    rows = []
    for f in range(first, last + 1):
        p = folder / ("frame%08d.png" % f)
        if not p.is_file():
            continue
        im = Image.open(p).convert("RGB").crop((x0, y0, x1, y1))
        if prev is not None:
            diff = ImageChops.difference(im, prev)
            rows.append((f, sum(1 for px in diff.getdata()
                                if px != (0, 0, 0))))
        prev = im

    print("")
    print("  capture  changed px vs the frame before")
    for f, n in rows:
        if n:
            note = "   <- named in section 10" if f in SWING_FRAMES else ""
            print("    %3d      %6d%s" % (f, n, note))

    held = [f for f, n in rows if n == 0]
    moved = [n for _, n in rows if n]
    print("")
    if held:
        print("  %d of %d frames are identical to the one before them, which"
              % (len(held), len(rows)))
        print("  is what UPDATE_DISCRETE means for a frame track.")
    else:
        print("  NO frame is identical to the one before it: something on")
        print("  this clip interpolates. A continuous track moves every")
        print("  frame even where the body cell does not change, and that is")
        print("  the clearest evidence a rig clip is a different mechanism")
        print("  from a frame clip.")
    if moved:
        print("  changes range %d..%d px. The large ones are the body cell"
              % (min(moved), max(moved)))
        print("  stepping; any small ones are a continuous track moving.")
    print("")
    print("  NOTHING in this table is the active window closing. A hitbox")
    print("  is invisible: it contributes zero pixels whether it is open")
    print("  or shut, so no strip can show that boundary at all. Whatever")
    print("  moves on that frame moved for another reason, and")
    print("  test_swing_edges.gd is what actually checks the window.")


def main() -> int:
    swing_dir = ROOT / (sys.argv[1] if len(sys.argv) > 1
                        else "captures/swing/r0")
    run_dir = ROOT / (sys.argv[2] if len(sys.argv) > 2 else "captures/run/r0")
    rev_s = swing_dir.name
    rev_r = run_dir.name
    strip(swing_dir, SWING_FRAMES, BAND_SWING, SWING_SAYS,
          "FIXTURE  swing %s  —  captured at 30 fps, one captured frame is "
          "one table frame" % rev_s,
          swing_dir.parent / ("%s-strip.png" % rev_s))
    strip(run_dir, RUN_FRAMES, BAND_RUN, {},
          "FIXTURE  run %s  —  the cycle is 0.250 s, so these six frames are "
          "0.8 of one cycle" % rev_r,
          run_dir.parent / ("%s-strip.png" % rev_r))
    changes(swing_dir, 8, 32, BAND_SWING)
    print("\n  Both are FIXTURE captures from previews/, not the game.")
    print("  Nothing above is a verdict. TUNING.md is where one goes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
