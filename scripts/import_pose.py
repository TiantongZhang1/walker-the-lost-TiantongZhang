#!/usr/bin/env python3
"""Turn a generated pose image into a game-ready sprite, and check it.

    python scripts/import_pose.py design/character/CHAR-P1.png --id p1-idle

What it does, in order:

  1. finds the character in the generated image (alpha, or the background
     colour sampled from the corners)
  2. scales it so it occupies the right number of logical pixels
  3. places it in a 32 x 32 cell with the feet on the anchor at (20, 30)
  4. snaps every pixel to the eight-colour palette
  5. runs the acceptance checks of CHARACTER-SHEET.md section 6 and prints what
     each one found

It does NOT decide anything. It tells you which rule a frame breaks, and it
writes the silhouette and the on-background previews so the two checks that
need an eye can actually be looked at. `--write` is what finally puts the
sprite in godot/assets/poses/.

The anchor, the cell, the palette and the contrast thresholds all come from
CHARACTER-SHEET.md. If this file and that one disagree, that one wins.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent

# --- from CHARACTER-SHEET.md section 2 ---
CELL = 32
ANCHOR = (20, 30)          # the point the engine places at `position`, from top-left
STAND_H = 28               # the collider's height: a standing pose fills it
PRONE_W = 26               # P8 is laid out across instead (CONCEPT revision 1.4)

# --- from CHARACTER-SHEET.md sections 3 / 3b / 3c ---
PALETTE = {
    "plate":      "#1f3a6e",
    "shade":      "#16233d",
    "visor":      "#7fe3ff",
    "glint":      "#d8f7ff",
    "scarf":      "#8a5cf0",
    "scarf_tip":  "#6a3fbf",
    "steel":      "#4a5468",
    "steel_edge": "#9aa7bd",
}
RIM = "steel_edge"
WALL = "#1b1620"           # the dungeon backdrop the character stands against
LIT_EDGE = "#c89a5a"       # the torchlit platform top edge it stands on


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(c):
    l = lin(np.asarray(c, dtype=np.float64))
    return 0.2126 * l[..., 0] + 0.7152 * l[..., 1] + 0.0722 * l[..., 2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = np.maximum(la, lb), np.minimum(la, lb)
    return (hi + 0.05) / (lo + 0.05)


PAL_NAMES = list(PALETTE)
PAL_RGB = np.array([rgb(PALETTE[n]) for n in PAL_NAMES])


def extract(img):
    """Return (rgb array, opaque mask) with the background removed."""
    img = img.convert("RGBA")
    a = np.array(img)
    col, alpha = a[..., :3].astype(np.float64), a[..., 3]
    if (alpha < 250).mean() > 0.02:
        return col, alpha > 128
    # No usable alpha: take the background from the four corners. If they
    # disagree the image has no plain background and the crop is a guess, so
    # say so rather than silently producing a bad sprite.
    h, w = alpha.shape
    corners = np.array([col[0, 0], col[0, w - 1], col[h - 1, 0], col[h - 1, w - 1]])
    spread = float(np.abs(corners - corners.mean(axis=0)).max())
    if spread > 24:
        print("  ! the four corners differ by %.0f/255 -- this image has no plain"
              " background, so the cut-out below is unreliable" % spread)
    bg = corners.mean(axis=0)
    dist = np.sqrt(((col - bg) ** 2).sum(axis=2))
    return col, dist > 40


def snap(col, mask):
    """Nearest palette colour per pixel, plus how far each had to move."""
    flat = col[mask]
    d = np.sqrt(((flat[:, None, :] - PAL_RGB[None, :, :]) ** 2).sum(axis=2))
    idx = d.argmin(axis=1)
    out = np.zeros_like(col)
    out[mask] = PAL_RGB[idx]
    names = np.full(mask.shape, -1, dtype=int)
    names[mask] = idx
    return out, names, d.min(axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--id", required=True, help="e.g. p1-idle")
    ap.add_argument("--prone", action="store_true",
                    help="lay the figure out across the cell instead of up it (P8)")
    ap.add_argument("--write", action="store_true",
                    help="actually write godot/assets/poses/<id>.png")
    ap.add_argument("--no-rim", action="store_true",
                    help="do NOT add the directional rim (CHARACTER-SHEET 3c makes it"
                         " mandatory, so this is only for comparing against)")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        print("no such file:", src)
        return 2
    print("source: %s" % src)

    col, mask = extract(Image.open(src))
    if not mask.any():
        print("  FAIL  nothing left after background removal")
        return 1

    # Which source pixels are the visor, decided BEFORE anything is scaled.
    #
    # The slit is 1-2 px tall once the figure is 28 px high, and an area
    # resample averages it into the navy helm around it -- the result snaps to
    # `plate` and the visor disappears completely. Measured on the first eight
    # imported poses: 0 visor pixels in seven of them, 1 in the eighth.
    #
    # That is not a cosmetic loss. CHARACTER-SHEET section 3b has the visor at
    # 12.12:1 against the dungeon wall, the strongest colour on the character,
    # and section 5 makes it the reason facing is readable from the head alone.
    _, src_names, _ = snap(col, mask)
    vis_i = PAL_NAMES.index("visor")
    gl_i = PAL_NAMES.index("glint")
    src_visor = (src_names == vis_i) | (src_names == gl_i)
    # Only the biggest blob. A bright highlight on a steel boot also snaps to
    # `glint`, and restoring those put stray cyan pixels at the feet of P1 and
    # P6 -- which reads as a rendering bug rather than as armour. Taking the
    # largest connected component keeps the slit and drops the specks, and
    # unlike a "top 45% of the figure" rule it still works for the prone pose,
    # where the head is at the RIGHT rather than the top.
    if src_visor.any():
        lab, n = ndimage.label(src_visor)
        if n > 1:
            sizes = ndimage.sum(src_visor, lab, range(1, n + 1))
            src_visor = lab == (int(np.argmax(sizes)) + 1)
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    print("  found the figure at %dx%d px in the source" % (x1 - x0, y1 - y0))

    # Scale so the figure occupies the logical size the collider implies.
    target = PRONE_W / (x1 - x0) if args.prone else STAND_H / (y1 - y0)
    nw, nh = max(1, round((x1 - x0) * target)), max(1, round((y1 - y0) * target))
    crop = Image.fromarray(
        np.dstack([col.astype(np.uint8), (mask * 255).astype(np.uint8)])[y0:y1, x0:x1]
    ).resize((nw, nh), Image.LANCZOS)

    # The visor mask is resampled with BOX (area coverage) and thresholded low,
    # so a target pixel that covers even a sliver of slit stays a slit. Nearest
    # would drop it and LANCZOS would blur it back into the helm.
    vcrop = Image.fromarray((src_visor[y0:y1, x0:x1] * 255).astype(np.uint8)).resize(
        (nw, nh), Image.BOX)
    vcell = Image.new("L", (CELL, CELL), 0)
    vcell.paste(vcrop, (ANCHOR[0] - nw // 2, ANCHOR[1] - nh))
    visor_mask = np.array(vcell) > 38          # ~15% of the target pixel's area

    cell = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    cell.paste(crop, (ANCHOR[0] - nw // 2, ANCHOR[1] - nh), crop)
    a = np.array(cell)
    col, mask = a[..., :3].astype(np.float64), a[..., 3] > 128
    if not mask.any():
        print("  FAIL  the figure landed outside the cell")
        return 1

    snapped, names, dist = snap(col, mask)

    # Stamp the visor back on. Like the rim below, this is an EDIT to a
    # generated asset rather than something the model produced at this size,
    # and it belongs in ASSET-LOG's "Edits" column. What the model produced is
    # the slit in the source image; what is restored here is its survival
    # through the downscale.
    visor_mask = visor_mask & mask
    restored = int(visor_mask.sum())
    if restored:
        snapped[visor_mask] = PAL_RGB[vis_i]
        names[visor_mask] = vis_i
    print("  visor: %d px restored through the downscale (CHARACTER-SHEET 3b)"
          % restored)

    # The directional rim, added here rather than asked of the generator.
    #
    # CHARACTER-SHEET section 3c makes it mandatory and specifies it exactly:
    # 1 px toward the character's back and 1 px up, in steel_edge, because the
    # dungeon's light is a torch above and behind. A model cannot be relied on
    # to place a one-pixel light edge correctly at a 28 px figure height -- the
    # reference came back with a near-black outline instead, which snaps to
    # `shade` at 1.14:1 against the wall and so does nothing at all.
    #
    # Doing it here is deterministic, identical for every pose, and derived
    # from the same rule the code-drawn character uses. It IS an edit to a
    # generated asset and belongs in ASSET-LOG's "Edits" column.
    rim_added = 0
    if not args.no_rim:
        right = np.zeros_like(mask)
        right[:, :-1] = mask[:, 1:]      # an opaque pixel immediately to the RIGHT
        below = np.zeros_like(mask)
        below[:-1, :] = mask[1:, :]      # an opaque pixel immediately BELOW
        # The sprite is generated facing right, so "the back" is -x: the rim
        # lands on the left and top boundary of the silhouette.
        edge = (~mask) & (right | below)
        rim_i = PAL_NAMES.index(RIM)
        snapped[edge] = PAL_RGB[rim_i]
        names[edge] = rim_i
        mask = mask | edge
        rim_added = int(edge.sum())
        print("  rim: added %d px of %s along the back and top edges"
              " (CHARACTER-SHEET 3c)" % (rim_added, RIM))

    print("\nacceptance checks -- CHARACTER-SHEET.md section 6")

    # 4. palette
    worst, far = float(dist.max()), float((dist > 60).mean())
    print("  [palette ] worst snap distance %.0f/255, %.1f%% of pixels moved more than 60"
          % (worst, 100 * far))
    print("             %s" % ("ok -- the image was already close to the eight"
                               if far < 0.10 else
                               "WARN -- a lot of colour was invented; prompt the palette harder"))

    # 5. anchor
    ys2 = np.where(mask.any(axis=1))[0]
    feet, head = int(ys2.max()) + 1, int(ys2.min())
    print("  [anchor  ] feet row %d (want %d), head row %d, height %d px"
          % (feet, ANCHOR[1], head, feet - head))
    print("             %s" % ("ok" if abs(feet - ANCHOR[1]) <= 1 else
                               "WARN -- the character will float or sink"))

    # 3. contrast. The question is NOT "how much of the body is dark" -- the
    # body is SUPPOSED to be dark, it is navy armour on a dungeon wall at
    # 1.60:1. The question is whether enough high-contrast material exists to
    # carry the silhouette. The shipped code-drawn character measures 9.1% of
    # its pixels at 3:1 or better against the wall, and that is the rim, the
    # visor and the scarf doing exactly their job; 6% is the floor below which
    # there is nothing holding the figure up.
    used = snapped[mask]
    uniq, counts = np.unique(used.reshape(-1, 3), axis=0, return_counts=True)
    cw = contrast(uniq, rgb(WALL))
    carry = float(counts[cw >= 3.0].sum()) / counts.sum()
    dark = float(counts[cw < 2.0].sum()) / counts.sum()
    print("  [contrast] against the wall %s: %.1f%% of the figure reads at 3:1 or"
          " better, %.1f%% is under 2:1" % (WALL, 100 * carry, 100 * dark))
    print("             (the shipped code-drawn character measures 9.1%)")
    print("             %s" % ("ok -- the rim, visor and scarf are carrying it"
                               if carry >= 0.06 else
                               "WARN -- almost nothing reads against the wall. A dark"
                               " body is fine; a dark body with no rim is not"))

    # 3c. the rim has to be on the back and the top, and nowhere else matters
    rim_idx = PAL_NAMES.index(RIM)
    has_rim = names == rim_idx
    if has_rim.any():
        rx = np.where(has_rim.any(axis=0))[0]
        ry = np.where(has_rim.any(axis=1))[0]
        body_x = np.where(mask.any(axis=0))[0]
        back_third = rx.min() <= body_x.min() + max(1, (body_x.max() - body_x.min()) // 3)
        print("  [rim     ] %d px of %s (%d added by this script), columns %d-%d,"
              " rows %d-%d"
              % (has_rim.sum(), RIM, rim_added, rx.min(), rx.max(), ry.min(), ry.max()))
        print("             %s" % ("ok -- it reaches the back edge" if back_third else
                                   "WARN -- no rim on the back edge; it is facing right,"
                                   " so the light is on the LEFT"))
    else:
        print("  [rim     ] FAIL -- no %s pixels at all. The figure has no rim light,"
              % RIM)
        print("             and at 1.60:1 the body alone does not read against the wall.")

    # 1. silhouette, and 2. scale -- written out, because both need an eye
    out_dir = ROOT / "build" / "poses"
    out_dir.mkdir(parents=True, exist_ok=True)
    previews = []
    for label, bg in (("wall", WALL), ("edge", LIT_EDGE)):
        for solid in (False, True):
            im = Image.new("RGB", (CELL, CELL), tuple(rgb(bg).astype(int)))
            body = np.array(im).astype(np.float64)
            body[mask] = 0.0 if solid else snapped[mask]
            previews.append(Image.fromarray(body.astype(np.uint8)))
    strip = Image.new("RGB", (CELL * 4 + 15, CELL), (24, 22, 30))
    for i, p in enumerate(previews):
        strip.paste(p, (i * (CELL + 5), 0))
    strip.resize((strip.width * 8, strip.height * 8), Image.NEAREST).save(
        out_dir / ("%s-checks.png" % args.id))
    print("\n  previews: build/poses/%s-checks.png" % args.id)
    print("            on wall | silhouette on wall | on lit edge | silhouette on edge")
    print("            [silhouette] and [scale] are YOUR call -- look at it at 1x too")

    final = np.dstack([snapped.astype(np.uint8), (mask * 255).astype(np.uint8)])
    if args.write:
        dest = ROOT / "godot" / "assets" / "poses" / ("%s.png" % args.id)
        dest.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(final).save(dest)
        print("\n  WROTE %s" % dest.relative_to(ROOT))
    else:
        tmp = out_dir / ("%s.png" % args.id)
        Image.fromarray(final).save(tmp)
        print("\n  dry run -- sprite written to build/poses/%s.png" % args.id)
        print("  pass --write once the checks above are acceptable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
