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
FEET_ROW = 29          # the lowest inked row of every standing pose, measured
LEG_TOP = 20           # rows at or below this are legs, from the row scan
SPLIT_X = 25           # left of this is the trailing leg, right is the planted
HIP = (20, 20)         # the pivot both legs hang from, in cell coordinates

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
        safe = []
        for deg in range(-34, 35):
            big = Image.new("RGBA", (CELL * 3, CELL * 3), CLEAR)
            big.paste(leg, (CELL + CELL - HIP[0], CELL + CELL - HIP[1]))
            big = big.rotate(deg, resample=Image.NEAREST,
                             center=(CELL * 2 - HIP[0] + HIP[0],
                                     CELL * 2 - HIP[1] + HIP[1]))
            lp = big.load()
            rows = [y for y in range(big.height)
                    if any(lp[x, y][3] for x in range(big.width))]
            low = max(rows) - (CELL + CELL - HIP[1]) if rows else -99
            if low <= FEET_ROW:
                safe.append(deg)
        print("  %-14s may rotate %+d .. %+d degrees without the foot "
              "going below row %d" % (leg_name, min(safe), max(safe), FEET_ROW))

if __name__ == "__main__":
    main()
