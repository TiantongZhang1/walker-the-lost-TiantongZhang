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
# Assignment 7: the player sheet.
#
# One sheet, 32 x 32 cells, hframes 6 x vframes 2. CHANGE-BRIEF.md section 3
# fixes the grid and the cell order; this file is the editable source, because
# the sheet is written rather than downloaded.
#
# **Why 32 x 32 and not the 16 x 28 `player()` draws.** pose_driver.gd recorded
# the arithmetic that has to survive: the feet sit on ROW 30 of a 32 x 32 cell,
# the body box is 10 x 28 centred on the origin so its underside is y = +14,
# and a centred 32 px sprite spans y -16..+16 -- which puts row 30 at exactly
# y = +14, with no offset to maintain. Every cell below is drawn to that rule
# and FEET_ROW asserts it.
#
# **Registration is by construction.** Every cell comes from one figure
# function at one origin, so the character cannot drift inside its cell. That
# is an argument; the frame strip in CHANGE-BRIEF.md section 10 is the check.

CELL = 32
FEET_ROW = 30          # the row the soles touch, in cell coordinates
HIP_Y = 21
SHOULDER_Y = 12
HEAD_TOP = 4
CLOAK_MAX = 6          # keeps the cloak clear of the cell edge

SKIN = (0x9A, 0xA7, 0xBD, 255)
BODY = (0x1F, 0x3A, 0x6E, 255)
BODY_DK = (0x15, 0x28, 0x4D, 255)
CLOAK = (0x7B, 0x4F, 0xD6, 255)
STEEL = (0xC8, 0xCC, 0xD6, 255)
STEEL_DK = (0x5E, 0x64, 0x72, 255)


def _line(px, x0, y0, x1, y1, colour, width=2):
    """Integer line, `width` px thick horizontally. Pixel art, not geometry."""
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        for w in range(width):
            xx = x + w - width // 2
            if 0 <= xx < CELL and 0 <= y < CELL:
                px[xx, y] = colour


def _box(px, x0, y0, x1, y1, colour):
    for y in range(max(0, y0), min(CELL, y1 + 1)):
        for x in range(max(0, x0), min(CELL, x1 + 1)):
            px[x, y] = colour


def figure(front_foot_dx, back_foot_dx, bob, front_arm_dx, back_arm_dx,
           *, lean=0, cloak_dx=0, dead=False, blade_arm=None):
    """One 32 x 32 cell. All offsets are in pixels from a standing pose.

    Revision r1, 2026-11-16. The first version drew a 9 px torso with the
    arms inside it and a cloak that never moved, and the six run cells came
    out nearly identical -- a silhouette that stood still while its feet
    twitched. What makes a run read at this size is not the legs: it is the
    SILHOUETTE changing, so the torso is narrow enough for the arms to swing
    outside it, the cloak trails by `cloak_dx`, and `bob` is two pixels.
    """
    img = Image.new("RGBA", (CELL, CELL), CLEAR)
    px = img.load()
    cx = CELL // 2

    if dead:
        _box(px, cx - 9, FEET_ROW - 4, cx + 7, FEET_ROW, BODY)
        _box(px, cx - 13, FEET_ROW - 6, cx - 9, FEET_ROW - 1, CLOAK)
        _box(px, cx - 7, FEET_ROW - 7, cx - 2, FEET_ROW - 4, SKIN)
        _box(px, cx - 9, FEET_ROW, cx + 7, FEET_ROW, BODY_DK)
        return img

    hip = HIP_Y + bob
    shoulder = SHOULDER_Y + bob
    head_top = HEAD_TOP + bob

    # 1. the cloak, behind everything, trailing BACKWARD by an amount the
    #    caller varies per frame. A cloak that does not move is a wall --
    #    and one that reaches the cell edge is a registration failure, so
    #    the reach is capped at CLOAK_MAX and asserted in main().
    for i, y in enumerate(range(shoulder + 1, hip + 3)):
        reach = 2 + (i * (2 + cloak_dx)) // 9
        reach = min(reach, CLOAK_MAX)
        _box(px, cx - 4 - reach, y, cx - 4, y, CLOAK)

    # 2. back leg, then back arm -- both darker, both behind the torso
    _line(px, cx, hip, cx + back_foot_dx, FEET_ROW, BODY_DK, 3)
    _line(px, cx - 1, shoulder + 1, cx - 1 + back_arm_dx, shoulder + 7,
          BODY_DK, 2)

    # 3. torso: six pixels wide, so an arm at +-5 clears it
    _box(px, cx - 3 + lean, shoulder, cx + 2 + lean, hip, BODY)

    # 4. head, with a one-pixel hood brim so it is not a plain box
    _box(px, cx - 3 + lean, head_top, cx + 2 + lean, shoulder - 1, SKIN)
    _box(px, cx - 4 + lean, head_top + 1, cx - 4 + lean, head_top + 2, CLOAK)

    # 5. front leg and front arm, over the torso, in the lighter body colour
    _line(px, cx, hip, cx + front_foot_dx, FEET_ROW, BODY, 3)
    _line(px, cx + 1 + lean, shoulder + 1, cx + 1 + front_arm_dx + lean,
          shoulder + 7, SKIN, 2)

    if blade_arm is not None:
        hx, hy = blade_arm
        _line(px, cx + 1 + lean, shoulder + 1, cx + hx, shoulder + hy, SKIN, 2)
    return img


# CHANGE-BRIEF.md section 3's frame order. Six run cells, then the four poses
# the state machine holds, then the braced cell the swing's body shows, then
# one deliberately blank cell so a mis-slice shows NOTHING rather than wrong
# art -- nothing is easier to see than wrong.
#
# The run is read as contact / down / pass, twice, with the legs swapped the
# second time. `bob` is 0 at contact and 1 at down, so the body drops on the
# plant -- which is the frame a step-dust puff spawns on.
RUN_CELLS = [
    #  front  back  bob  fArm  bArm  cloak
    (    8,    -7,   0,   -5,    5,     4),   # 0 contact, right foot forward
    (    4,    -4,   2,   -3,    3,     2),   # 1 down, weight low
    (   -4,     5,   1,    4,   -4,     0),   # 2 pass, legs crossing
    (   -7,     8,   0,    5,   -5,     4),   # 3 contact, left foot forward
    (   -4,     4,   2,    3,   -3,     2),   # 4 down
    (    5,    -4,   1,   -4,    4,     0),   # 5 pass
]


def player_sheet() -> Image.Image:
    sheet = Image.new("RGBA", (CELL * 6, CELL * 2), CLEAR)
    cells = []
    for f, b, bob, fa, ba, ck in RUN_CELLS:
        cells.append(figure(f, b, bob, fa, ba, lean=1, cloak_dx=ck))
    cells.append(figure(1, -2, 0, -1, 1, cloak_dx=0))          # 6  idle
    cells.append(figure(-4, 6, 0, -6, 4, lean=1, cloak_dx=6))  # 7  rising
    cells.append(figure(6, -4, 2, 6, -4, lean=0, cloak_dx=5))  # 8  falling
    cells.append(figure(0, 0, 0, 0, 0, dead=True))             # 9  dead
    cells.append(figure(8, -7, 2, -3, 6, lean=2, cloak_dx=5,
                        blade_arm=(9, 1)))                     # 10 braced
    cells.append(Image.new("RGBA", (CELL, CELL), CLEAR))       # 11 BLANK
    for i, cell in enumerate(cells):
        sheet.paste(cell, ((i % 6) * CELL, (i // 6) * CELL))
    return sheet


def sword() -> Image.Image:
    """3 x 14 blade, hilt at the BOTTOM so the pivot sits in the hand."""
    img = Image.new("RGBA", (3, 14), CLEAR)
    px = img.load()
    for y in range(0, 10):          # blade
        px[1, y] = STEEL
        px[0, y] = STEEL_DK
        px[2, y] = STEEL_DK
    for x in range(3):              # crossguard
        px[x, 10] = STEEL_DK
    for y in range(11, 14):         # grip
        px[1, y] = (0x4A, 0x32, 0x1E, 255)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = {
        "spike_trap.png": spike_trap(),
        "spike_trap_fired.png": spike_trap_fired(),
        "floor_tile.png": floor_tile(),
        "player.png": player(),
        "player_sheet.png": player_sheet(),
        "sword.png": sword(),
    }
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

    # Assignment 7. The sheet's claims, asserted here so the read-back test
    # and the brief cannot disagree with the file.
    sheet = images["player_sheet.png"]
    if sheet.size != (CELL * 6, CELL * 2):
        raise SystemExit(f"  FAIL sheet is {sheet.size}, brief says 192x64")
    print("\n  sheet: %dx%d, 6 x 2 cells of %d px" % (*sheet.size, CELL))

    sp = sheet.load()
    problems = []
    for i in range(12):
        ox, oy = (i % 6) * CELL, (i // 6) * CELL
        rows = [y for y in range(CELL)
                if any(sp[ox + x, oy + y][3] for x in range(CELL))]
        if i == 11:
            if rows:
                problems.append("cell 11 must be blank, has ink on %s" % rows)
            continue
        if not rows:
            problems.append("cell %d is empty" % i)
            continue
        # Registration: every cell's lowest ink is the feet row. The dead
        # cell lies down and still ends there, which is the point.
        if max(rows) != FEET_ROW:
            problems.append("cell %d: lowest ink row %d, FEET_ROW is %d"
                            % (i, max(rows), FEET_ROW))
        # Containment. Ink in column 0 or 31 means the figure was CLIPPED by
        # the cell, which is a registration failure the eye reads as the
        # character changing shape. r1's cloak did exactly this in cells 0
        # and 3 before CLOAK_MAX existed.
        edge = [x for x in (0, CELL - 1)
                if any(sp[ox + x, oy + y][3] for y in range(CELL))]
        if edge:
            problems.append("cell %d: ink touches cell column(s) %s"
                            % (i, edge))
    if problems:
        raise SystemExit("  FAIL  " + "\n  FAIL  ".join(problems))
    print("  every cell 0-10 has ink, ends on row %d, and cell 11 is blank"
          % FEET_ROW)
    print("  registration is by construction: one figure function, one origin")


if __name__ == "__main__":
    main()
