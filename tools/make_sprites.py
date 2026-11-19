"""Write the 2D slice's sprites from code, to the colours CHANGE-BRIEF.md fixed.

The brief specified these colours *before* anything was drawn, so that the
hand-computed pixel predictions in its §6 describe the sprite rather than the
other way round. This script is the reason that claim is checkable: the two
named prediction pixels are asserted here, and the script fails loudly if a
future edit moves them.

    python -I tools/make_sprites.py

Palette (from CHANGE-BRIEF.md §6):
    trap base plate   #2A2A33   prediction pixel A at (8, 12)
    trap spike        #8A90A1   prediction pixel B at (8, 3)
    floor tile        #16242B   the background the predictions assume
"""
import pathlib

from PIL import Image

OUT = pathlib.Path(__file__).resolve().parent.parent / "godot" / "assets" / "sprites"

PLATE = (0x2A, 0x2A, 0x33, 255)
PLATE_EDGE = (0x1E, 0x1E, 0x26, 255)
SPIKE = (0x8A, 0x90, 0xA1, 255)
SPIKE_SHADE = (0x5E, 0x64, 0x72, 255)
FLOOR = (0x16, 0x24, 0x2B, 255)
FLOOR_GROUT = (0x11, 0x1C, 0x22, 255)
CLEAR = (0, 0, 0, 0)

# The blade's two greys are the character's own, already in every pose,
# so its steel reads as this character's rather than as something pasted
# on. TUNING.md, 2026-11-18.
# The sword's length, 2026-11-18 (r4). 16 px first; the author played r3 and
# asked for a longer blade, so it is 20. `Blade.offset` in player.tscn is
# (0, -LEN/2) so the HILT sits on the pivot, and `test_swing_clip.gd`'s
# BLADE_PX must equal LEN -- the tip-reach assertions are computed from it.
SWORD_LEN = 20
SWORD_EDGE = 15                   # rows 0..14 are blade; row 15 is the guard
STEEL = (0x9A, 0xA7, 0xBD, 255)
STEEL_DK = (0x5E, 0x64, 0x72, 255)
GRIP = (0x16, 0x23, 0x3D, 255)

# The prediction pixels. Asserted at the end; a failure here means the brief
# and the art have drifted apart, which would quietly invalidate §6.
PREDICTION_PIXELS = {(8, 12): PLATE, (8, 3): SPIKE}


def spike_trap() -> Image.Image:
    """16x16. Rows 8-15 are the base plate, rows 2-7 the three spikes.

    The middle spike is kept flat across columns 7-8 so that pixel (8, 3) is
    exactly SPIKE with no shading blended into it; the outer columns of each
    spike carry the shading instead.
    """
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()

    # Base plate, rows 8-15, with a darker top lip and outer border.
    for y in range(8, 16):
        for x in range(16):
            edge = y == 8 or y == 15 or x == 0 or x == 15
            px[x, y] = PLATE_EDGE if edge else PLATE

    # Three spikes. Each is 4 wide at the base (rows 5-7) and 2 wide at the
    # tip (rows 2-4). left_x is the leftmost column of the 4-wide base.
    for left_x in (1, 6, 11):
        mid = (left_x + 1, left_x + 2)  # the two flat centre columns
        for y in range(5, 8):
            for x in range(left_x, left_x + 4):
                px[x, y] = SPIKE if x in mid else SPIKE_SHADE
        for y in range(2, 5):
            for x in mid:
                px[x, y] = SPIKE

    return img


def spike_trap_fired() -> Image.Image:
    """16x16, the same trap with the spikes driven out.

    Firing is a texture swap rather than a moving child node, so the trap stays
    ONE Sprite2D with ONE material. CHANGE-BRIEF.md specifies a shader that
    "changes the colour of one object"; splitting the plate and the spikes into
    two sprites would have meant two materials to drive and two places for the
    per-instance rule R6 to go wrong.

    The prediction pixels are NOT asserted on this texture. Section 6's
    captures force warn_amount from code while the trap sits in ARMED, which is
    how the assignment's own capture helper works, so the base texture is the
    one under them.
    """
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    for y in range(8, 16):
        for x in range(16):
            edge = y == 8 or y == 15 or x == 0 or x == 15
            px[x, y] = PLATE_EDGE if edge else PLATE
    # Same three spikes, 7 px higher and longer, so they read as driven out.
    for left_x in (1, 6, 11):
        mid = (left_x + 1, left_x + 2)
        for y in range(5, 11):
            for x in range(left_x, left_x + 4):
                if y < 8 or x in mid:
                    px[x, y] = SPIKE if x in mid else SPIKE_SHADE
        for y in range(0, 5):
            for x in mid:
                px[x, y] = SPIKE
    return img


def floor_tile() -> Image.Image:
    """16x16 flat FLOOR with grout on two edges.

    Flat on purpose: §6's predictions name a background colour, and a noisy
    tile would make the sampled pixel depend on where the trap happens to sit.
    """
    img = Image.new("RGBA", (16, 16), FLOOR)
    px = img.load()
    for i in range(16):
        px[i, 15] = FLOOR_GROUT
        px[15, i] = FLOOR_GROUT
    return img


def player() -> Image.Image:
    """16x28 silhouette. 28 px = 1.75 m at the project's 16 px = 1 m."""
    body = (0x1F, 0x3A, 0x6E, 255)
    trim = (0x9A, 0xA7, 0xBD, 255)
    cloak = (0x7B, 0x4F, 0xD6, 255)
    img = Image.new("RGBA", (16, 28), CLEAR)
    px = img.load()
    for y in range(6, 28):  # torso and legs
        for x in range(4, 12):
            px[x, y] = body
    for y in range(2, 6):  # head
        for x in range(5, 11):
            px[x, y] = trim
    for y in range(8, 18):  # cloak, one shoulder
        for x in range(1, 4):
            px[x, y] = cloak
    for y in range(24, 28):  # a gap between the legs
        px[7, y] = CLEAR
        px[8, y] = CLEAR
    return img


# ---------------------------------------------------------------------------
# Assignment 7: the player sheet and the cutout legs.
#
# **Nothing here draws a character.** The five poses this project carried from
# walker-ninja-TiantongZhang, plus the three it had left behind, are
# generated pixel art with their provenance already in ATTRIBUTION.md. This
# code CUTS them -- crops and composes -- and writes the result. Cutting is
# not redrawing: assert_lossless_cut() below proves the three leg layers
# recombine into the original run pose pixel for pixel.
#
# An earlier revision of this file drew its own silhouette instead. It was
# rejected on sight, in the author's words: too crude beside the art the game
# already had. FRICTIONAL.md records that.
#
# The sheet: 32 x 32 cells, hframes 4 x vframes 2.
#
#   0 run torso   p2-run with the legs removed; only `run` shows it
#   1 idle        p1-idle          4 dead     p8-death
#   2 rising      p3-rising        5 windup   p6-windup   swing startup
#   3 falling     p4-falling       6 live     p7-live     swing active
#                                  7 BLANK, on purpose
#
# Cell 7 is blank so that a mis-slice shows NOTHING rather than wrong art.
# Nothing is easier to see than wrong.

CELL = 32
SHEET_H = 4
SHEET_V = 2
SCAN = 60              # how far the leg-rotation measurement looks
FEET_ROW = 29          # the lowest inked row of every standing pose, measured
LEG_TOP = 20           # rows at or below this are legs, from the row scan
SPLIT_X = 25           # left of this is the trailing leg, right is the planted
# The pivot both legs hang from, in cell coordinates. It is MEASURED from
# the cut surface -- the top row of inked pixels left after the cut --
# because that is where the leg was severed and therefore where it hangs
# from. (20, 20) was assumed, and it is 7 px to the side of the real
# joint, so the leg swung like a pendulum on a bar instead of a leg on a
# hip. Revision 7.0.7. `hip_of()` below reports what it actually is.
HIP = (20, 20)         # the CUT line: everything below row 20 is leg

POSES = pathlib.Path(__file__).resolve().parent.parent / "godot" / "assets" / "poses"
SHEET_ORDER = ["<run torso>", "p1-idle", "p3-rising", "p4-falling",
               "p8-death", "p6-windup", "p7-live", "<blank>"]


def _load(name: str) -> Image.Image:
    return Image.open(POSES / (name + ".png")).convert("RGBA")


def cut_run_pose():
    """p2-run -> (torso with no legs, trailing leg, planted leg).

    The split is by row and then by column, which is all the art needs: below
    LEG_TOP the trailing leg is left of SPLIT_X and the planted leg is right
    of it. Measured from the pose's own row scan, not guessed.
    """
    run = _load("p2-run")
    px = run.load()
    torso = Image.new("RGBA", (CELL, CELL), CLEAR)
    back = Image.new("RGBA", (CELL, CELL), CLEAR)
    front = Image.new("RGBA", (CELL, CELL), CLEAR)
    tp, bp, fp = torso.load(), back.load(), front.load()
    for y in range(CELL):
        for x in range(CELL):
            c = px[x, y]
            if not c[3]:
                continue
            if y < LEG_TOP:
                tp[x, y] = c
            elif x < SPLIT_X:
                bp[x, y] = c
            else:
                fp[x, y] = c
    return run, torso, back, front


def assert_lossless_cut(run, torso, back, front) -> None:
    """The three layers must recombine into the original, pixel for pixel.

    This is what lets the brief say the GPT-6 art is UNCHANGED. A cut that
    dropped or duplicated a pixel would be a redraw with extra steps.
    """
    rebuilt = Image.new("RGBA", (CELL, CELL), CLEAR)
    rebuilt.alpha_composite(back)
    rebuilt.alpha_composite(torso)
    rebuilt.alpha_composite(front)
    if list(rebuilt.getdata()) != list(run.getdata()):
        raise SystemExit("  FAIL the leg cut is not lossless: torso + back + "
                         "front != p2-run")
    print("  the cut is lossless: torso + trailing + planted == p2-run exactly")


def player_sheet(torso: Image.Image) -> Image.Image:
    sheet = Image.new("RGBA", (CELL * SHEET_H, CELL * SHEET_V), CLEAR)
    cells = [torso]
    for name in SHEET_ORDER[1:-1]:
        cells.append(_load(name))
    cells.append(Image.new("RGBA", (CELL, CELL), CLEAR))     # 7, blank
    for i, cell in enumerate(cells):
        sheet.paste(cell, ((i % SHEET_H) * CELL, (i // SHEET_H) * CELL))
    return sheet



def sword() -> Image.Image:
    """The blade, 3 x 20, hilt at the BOTTOM so the pivot sits in the hand.

    Added back on 2026-11-18. The original brief had it; revision 7.0.1
    deleted it believing the poses already carried a weapon. They do not --
    `walker-ninja`'s character fought unarmed, and `p6-windup` and `p7-live`
    are a raised arm and an extended arm. TUNING.md's 2026-11-18 entry has
    the author's words and the pixel counts.

    **Drawn in the character's own palette**, the two greys that are already
    in every pose, so the steel reads as this character's rather than as
    something pasted on. No pose file is touched: the blade is a separate
    sprite on a separate node, which is what a cutout rig is for.
    """
    LEN, EDGE = SWORD_LEN, SWORD_EDGE
    img = Image.new("RGBA", (3, LEN), CLEAR)
    px = img.load()
    for y in range(0, EDGE):          # blade, lit on its left edge
        px[0, y] = STEEL
        px[1, y] = STEEL
        px[2, y] = STEEL_DK
    px[1, 0] = STEEL_DK               # a blunted tip reads better than a point
    for x in range(3):                # crossguard
        px[x, EDGE] = STEEL_DK
    for y in range(EDGE + 1, LEN):    # grip
        px[1, y] = GRIP
    assert img.size == (3, LEN), img.size
    return img

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = {
        "spike_trap.png": spike_trap(),
        "spike_trap_fired.png": spike_trap_fired(),
        "floor_tile.png": floor_tile(),
        "player.png": player(),
    }
    run, torso, back, front = cut_run_pose()
    assert_lossless_cut(run, torso, back, front)
    images["player_sheet.png"] = player_sheet(torso)
    images["leg_front.png"] = front
    images["leg_back.png"] = back
    images["sword.png"] = sword()
    for name, img in images.items():
        img.save(OUT / name)
        print(f"  wrote {name:<16} {img.size[0]}x{img.size[1]}")

    trap = images["spike_trap.png"].load()
    print("\n  prediction pixels asserted against CHANGE-BRIEF.md §6:")
    for (x, y), want in PREDICTION_PIXELS.items():
        got = trap[x, y]
        hexs = "#%02X%02X%02X" % got[:3]
        if got != want:
            raise SystemExit(
                f"  FAIL ({x},{y}) is {hexs}, brief says #%02X%02X%02X" % want[:3]
            )
        print(f"    OK  ({x:>2},{y:>2}) = {hexs}")
    print("\n  all prediction pixels match the brief")

    # Assignment 7. The sheet's claims, asserted here so that the read-back
    # test, the brief and the file on disk cannot disagree.
    sheet = images["player_sheet.png"]
    want = (CELL * SHEET_H, CELL * SHEET_V)
    if sheet.size != want:
        raise SystemExit("  FAIL sheet is %s, brief says %s" % (sheet.size, want))
    print("\n  sheet: %dx%d, %d x %d cells of %d px"
          % (*sheet.size, SHEET_H, SHEET_V, CELL))

    sp = sheet.load()
    problems = []
    n_cells = SHEET_H * SHEET_V
    for i in range(n_cells):
        ox, oy = (i % SHEET_H) * CELL, (i // SHEET_H) * CELL
        rows = [y for y in range(CELL)
                if any(sp[ox + x, oy + y][3] for x in range(CELL))]
        if SHEET_ORDER[i] == "<blank>":
            if rows:
                problems.append("cell %d must be blank, has ink on %s" % (i, rows))
            continue
        if not rows:
            problems.append("cell %d (%s) is empty" % (i, SHEET_ORDER[i]))
            continue
        # Registration. Every standing pose ends on FEET_ROW; the death pose
        # lies down and still ends there, which is the point of checking it.
        # The run torso has had its legs removed, so it ends higher by
        # construction and is excluded by name rather than by a loose rule.
        if SHEET_ORDER[i] != "<run torso>" and max(rows) != FEET_ROW:
            problems.append("cell %d (%s): lowest ink row %d, FEET_ROW is %d"
                            % (i, SHEET_ORDER[i], max(rows), FEET_ROW))
    if problems:
        raise SystemExit("  FAIL  " + "\n  FAIL  ".join(problems))
    print("  cells: " + ", ".join("%d %s" % (i, n)
                                  for i, n in enumerate(SHEET_ORDER)))
    print("  every pose cell ends on row %d; the blank cell is blank" % FEET_ROW)

    # The legs, and the rotation range the clip is allowed to key. The planted
    # leg's foot is ON the floor at 0 degrees, so one direction pushes it
    # through the floor and the other lifts it. This is measured by rendering,
    # not derived on paper -- the paper version had the sign backwards.
    for leg_name in ("leg_front.png", "leg_back.png"):
        leg = images[leg_name]
        lp0 = leg.load()
        ink = [(x, y) for y in range(CELL) for x in range(CELL)
               if lp0[x, y][3]]
        top = min(y for _, y in ink)
        cols = [x for x, y in ink if y <= top + 1]
        hip = ((min(cols) + max(cols)) / 2.0, float(top))
        foot_row = max(y for _, y in ink)
        print("  %-14s %d inked px, cut surface row %d cols %d..%d"
              % (leg_name, len(ink), top, min(cols), max(cols)))
        print("  %-14s HIP JOINT is texture (%.1f, %.0f); lowest row %d"
              % ("", hip[0], hip[1], foot_row))
        if foot_row < FEET_ROW:
            print("  %-14s ** this cut NEVER REACHES THE FLOOR (%d px short)."
                  % ("", FEET_ROW - foot_row))
            print("  %-14s ** It cannot plant, so it cannot take a step. The"
                  % "")
            print("  %-14s ** scene does not use it; player.tscn gives BOTH"
                  % "")
            print("  %-14s ** legs leg_front.png. Revision 7.0.7."
                  % "")
        safe = []
        # +/-60, not +/-34. Revision 7.0.7's cycle swings to -52, and a
        # scan that stops at -34 would report a band that merely ends
        # where the SCAN ends -- a limit of the instrument read as a
        # limit of the leg.
        for deg in range(-SCAN, SCAN + 1):
            big = Image.new("RGBA", (CELL * 3, CELL * 3), CLEAR)
            # about the leg's OWN measured hip joint, not the cut line
            hx, hy = int(round(hip[0])), int(round(hip[1]))
            big.paste(leg, (CELL + CELL - hx, CELL + CELL - hy))
            # **MINUS deg.** PIL's rotate() turns the opposite way from
            # Godot's rotation_degrees -- verified pixel for pixel, the two
            # lowest-row tables are exact mirror images. Without this the
            # band below is reported in the WRONG SIGN, which is how the
            # shipped cycle came to drive the planted foot 3.3 px through
            # the floor while test_player_clips.gd called every key legal.
            big = big.rotate(-deg, resample=Image.NEAREST,
                             center=(CELL * 2, CELL * 2))
            lp = big.load()
            rows = [y for y in range(big.height)
                    if any(lp[x, y][3] for x in range(big.width))]
            low = max(rows) - (CELL + CELL - hy) if rows else -99
            # **FEET_ROW + 1, not FEET_ROW.** "never below row 29" is
            # "never touches the floor", which is the wrong rule for a
            # PLANTED foot: the whole point of contact is that the foot is
            # ON row 29, and nearest-neighbour rotation puts its lowest
            # inked pixel one row either side of that. One pixel into the
            # floor lip is contact; more is sinking. Revision 7.0.7.
            if low <= FEET_ROW + 1:
                safe.append(deg)
        # **The CONTIGUOUS band around 0, not min/max of the whole set.**
        # A short leg lifts its foot again past 60 degrees, so min/max of a
        # scattered set reports a band that contains angles which are not
        # safe. Same shape as every other bad measurement in this file's
        # history: computed correctly, answering the wrong question.
        lo = hi = 0
        while lo - 1 in safe:
            lo -= 1
        while hi + 1 in safe:
            hi += 1
        print("  %-14s contact band %+d .. %+d degrees (GODOT's sign): the "
              "foot" % (leg_name, lo, hi))
        print("  %-14s rests ON row %d and never sinks past row %d."
              % ("", FEET_ROW, FEET_ROW + 1))
        if lo <= -SCAN and hi >= SCAN:
            print("  %-14s ** that is the whole SCAN, so it is a weak check."
                  % "")
            print("  %-14s ** This leg is 8.6 px long with its foot almost"
                  % "")
            print("  %-14s ** under the hip, so rotating it barely moves the"
                  % "")
            print("  %-14s ** foot: %+d..%+d degrees shifts it about 10 px"
                  % ("", -SCAN, SCAN))
            print("  %-14s ** against a 24 px step. The cycle ALTERNATES; it"
                  % "")
            print("  %-14s ** cannot STRIDE. CHANGE-BRIEF.md revision 7.0.7."
                  % "")

if __name__ == "__main__":
    main()
