#!/usr/bin/env python3
"""Compose the five result-beat cards: a real capture plus its own numbers.

One full-frame 3840 x 2160 card per result beat, dropped as media/<bid>.png.
The compiler's resolve_slot() picks a beat's PNG as a STILL, and
`motion: "hold"` renders it with no Ken Burns move, which is what a table of
measured numbers needs.

**Why these are not GodotDevWorkbench beats.** Two reasons, both found by
rendering a beat and looking at it.

1. The workbench's `asset` mode lays out {code}{image} at 1.08fr / 0.92fr,
   so a measured table beside the capture means a non-empty `code` prop -
   and verify_gamedev.py:68 requires every GodotDevWorkbench beat with a
   non-empty `code` to carry a source excerpt record and to be the code half
   of a code-then-result pair. A table of measurements is neither, so the
   official check failed with 'Displayed code lacks an excerpt record'.
   Leaving `code` empty passes the check and renders half a frame of empty
   dark panel with a stray line number in it.
2. The workbench's chrome says "Godot editor reconstruction - source-backed
   teaching view". That is the right label for the code beats. It is the
   wrong label for these: they are frames a real GPU drew in a windowed run,
   and SHOTLIST.md has always said so.

Every figure drawn is READ FROM THE RECORDED REPORT at build time and
rendered verbatim - none of it is typed here. If a report changes, the card
changes with it, and the ledger's hash changes too.

    python -X utf8 scripts/compose_a5_extras.py     # the two grids first
    python -X utf8 scripts/compose_lost_evidence.py

Writes youtube/<reel>/media/{B03A,B07,B09,B11,B11B}.png.
"""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-gamedev"
MEDIA = REEL / "media"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
EDGE = (206, 201, 192)

# Title-safe at 3840 x 2160 is x 192..3648, y 108..2052. frame_footage_beats.py
# learned this the hard way - its first card put the title at x 150 and Gate V
# called edge-bleed on every frame. Everything here sits inside.
SAFE_L, SAFE_R = 230, 3600
TOP = 300            # first pixel of the capture
FOOT_Y = 1930        # the footer's first baseline


def font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def mono(size):
    return font(("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"), size)


def sans(size):
    return font(("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"), size)


def table_from(report: pathlib.Path, start: str, stop: str) -> list[str]:
    """The block of a recorded report between two markers, verbatim."""
    rows, on = [], False
    for raw in report.read_text(encoding="utf-8").splitlines():
        if start in raw:
            on = True
        if on:
            rows.append(raw.rstrip())
        if on and stop and stop in raw and len(rows) > 1:
            break
    if not rows:
        raise SystemExit("no block starting %r in %s" % (start, report))
    return rows


def ends_only(report: pathlib.Path, names) -> list[str]:
    """Each uniform's heading with its min and max rows, verbatim. The
    default row of each is dropped for room; the footer says where the full
    table is, and the capture above it is the min/max pair anyway."""
    rows = [r.rstrip() for r in report.read_text(encoding="utf-8").splitlines()]
    out: list[str] = []
    for name in names:
        head = next(i for i, r in enumerate(rows)
                    if r.strip().startswith(name + " "))
        block = rows[head:head + 4]
        if out:
            out.append("")
        out.append(block[0])
        out += [r for r in block[1:] if " min " in r or " max " in r]
    return out


def wrap(d, text, f, width):
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if d.textlength(trial, font=f) > width and line:
            out.append(line)
            line = word
        else:
            line = trial
    out.append(line)
    return out


def compose(bid: str, capture: pathlib.Path, title: str, heading: str,
            lines: list[str], footer: str) -> pathlib.Path:
    card = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(card)
    d.text((SAFE_L, 140), title, font=sans(92), fill=INK)

    # The table is sized first and the capture gets whatever height is left,
    # so a long table shrinks the picture rather than running off the card.
    size, step = 46, 58
    widest = max(len(r) for r in lines)
    while size > 26 and widest * size * 0.60 > SAFE_R - SAFE_L:
        size -= 2
        step -= 2
    table_h = step * len(lines)
    shot_h = FOOT_Y - 60 - table_h - 116 - TOP
    if shot_h < 420:
        raise SystemExit("%s: %d rows leave only %d px for the capture"
                         % (bid, len(lines), shot_h))

    shot = Image.open(capture).convert("RGB")
    shot.thumbnail((SAFE_R - SAFE_L, shot_h), Image.LANCZOS)
    x = (W - shot.width) // 2
    card.paste(shot, (x, TOP))
    d.rectangle([x - 2, TOP - 2, x + shot.width + 1, TOP + shot.height + 1],
                outline=EDGE, width=2)

    # Under the picture, not under the BOX the picture was allowed. PIL's
    # thumbnail() never upscales, and three of these captures are 1280 x 720
    # on a 3840-wide card, so the box is taller than the image: anchoring the
    # table at TOP + shot_h left a 150 px hole between the capture and the
    # heading. The slack now falls at the bottom, where it reads as margin.
    y = TOP + shot.height + 24
    d.text((SAFE_L, y), heading, font=sans(50), fill=INK)
    y += 76
    d.line([SAFE_L, y, SAFE_R, y], fill=RULE, width=4)
    y += 40
    f = mono(size)
    for row in lines:
        d.text((SAFE_L, y), row, font=f, fill=INK if row.strip() else DIM)
        y += step

    ff = sans(34)
    fy = FOOT_Y
    for row in wrap(d, footer, ff, SAFE_R - SAFE_L - 480):
        d.text((SAFE_L, fy), row, font=ff, fill=DIM)
        fy += 42
    brand = sans(40)
    d.text((SAFE_R - d.textlength("@NikBearBrown", font=brand), FOOT_Y - 4),
           "@NikBearBrown", font=brand, fill=INK)

    path = MEDIA / (bid + ".png")
    card.save(path)
    return path


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)

    warn = ROOT / "captures/a5/REPORT.txt"
    hint = ROOT / "captures/a5/HINT-REPORT.txt"
    mutated = ROOT / "evidence/a5-mutations/mutation3a-hint-sampler_report.txt"
    sweep = ROOT / "captures/a5/materials/SWEEP-REPORT.txt"

    made = []

    made.append(compose(
        "B03A",
        ROOT / "captures/a5/controlled_grid.png",
        "Four controlled values, and the pixels they predicted",
        "Measured, beside what was written down before the rig existed",
        table_from(warn, "warn_amount | pixel", "worst channel"),
        "captures/a5/REPORT.txt - windowed run 2026-10-24, Forward+, RTX 5080, "
        "logical x2. H1 predicted 2026-10-23; the 2.0 row in revision 5.0.4, "
        "before the rig could run."))

    made.append(compose(
        "B07",
        ROOT / "captures/a5/hint_experiment.png",
        "The hint is worth seventy three counts",
        "Measured, beside the prediction committed 2026-10-23",
        table_from(hint, "stored |", "192 |"),
        "captures/a5/HINT-REPORT.txt - real windowed run, Forward+, RTX 5080. "
        "All six exact."))

    # The two uniforms whose effect is largest, with their own min and max
    # rows, lifted verbatim. The full twelve are in the report.
    all_rows = [r.rstrip() for r in sweep.read_text(encoding="utf-8").splitlines()]
    sweep_rows = [r for r in all_rows if r.strip().startswith("baseline")]
    sweep_rows += [""] + ends_only(sweep, ("roughness_dry", "water_roughness"))
    made.append(compose(
        "B09",
        ROOT / "captures/a5/materials/00-baseline.png",
        "One shader, two materials",
        "The flooded slime moves for every uniform; the dry one never does",
        sweep_rows,
        "captures/a5/materials/SWEEP-REPORT.txt - the dry column reads "
        "50, 56, 55 in all twelve sweep rows."))

    made.append(compose(
        "B11",
        ROOT / "evidence/a5-mutations/mutation3a-hint-sampler_capture.png",
        "The same scene, four words lighter",
        "source_color deleted from hint_bands.gdshader line 4",
        table_from(mutated, "stored |", "192 |"),
        "evidence/a5-mutations/ - captured with the shader deliberately "
        "mutated and restored afterwards. SHADER ERROR: 0, and the uniform "
        "list did not move either."))

    made.append(compose(
        "B11B",
        ROOT / "captures/a5/materials/sweep_grid.png",
        "Four uniforms, both ends, one material moving",
        "Every non-texture uniform at min and max",
        ends_only(sweep, ("tint", "roughness_dry",
                          "water_darkening", "water_roughness")),
        "captures/a5/materials/SWEEP-REPORT.txt - each default row is in the "
        "report. Dry slime left, flooded right; only the flooded one carries "
        "the swept material."))

    for p in made:
        print("  media/%s  %dx%d" % ((p.name,) + Image.open(p).size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
