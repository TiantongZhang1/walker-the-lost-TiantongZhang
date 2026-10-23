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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = {
        "spike_trap.png": spike_trap(),
        "spike_trap_fired.png": spike_trap_fired(),
        "floor_tile.png": floor_tile(),
        "player.png": player(),
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


if __name__ == "__main__":
    main()
