#!/usr/bin/env python3
"""Compose the three result-beat images: a real capture plus its own numbers.

The workbench's `asset` mode renders one image and a short label, so a table
of measurements has to be part of the picture. Every figure drawn below is
READ FROM THE RECORDED REPORT at build time and rendered verbatim - none of
it is typed here. If a report changes, the composite changes with it, and the
ledger's hash changes too.

    python -I scripts/compose_lost_evidence.py

Writes youtube/<reel>/media/B07,B09,B11-evidence.png.
"""
from __future__ import annotations

import pathlib
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-gamedev"
MEDIA = REEL / "media"

W, H = 1920, 1080
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)


def mono(size: int) -> ImageFont.FreeTypeFont:
    for name in ("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sans(size: int) -> ImageFont.FreeTypeFont:
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


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


def compose(out: str, capture: pathlib.Path, heading: str, lines: list[str],
            footer: str) -> pathlib.Path:
    card = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(card)

    shot = Image.open(capture).convert("RGB")
    box_w, box_h = W - 120, 540
    shot.thumbnail((box_w, box_h), Image.LANCZOS)
    x = (W - shot.width) // 2
    card.paste(shot, (x, 60))
    d.rectangle([x - 1, 59, x + shot.width, 60 + shot.height], outline=(206, 201, 192))

    y = 60 + shot.height + 40
    d.text((60, y), heading, font=sans(34), fill=INK)
    y += 54
    d.line([60, y, W - 60, y], fill=RULE, width=3)
    y += 24

    # Fit or fail. An earlier version drew the rows and let them run over the
    # footer, which looks like a layout bug and reads like a hidden one.
    size, step = 30, 40
    floor_y = H - 96
    while size > 18 and y + step * len(lines) > floor_y:
        size -= 2
        step -= 3
    if y + step * len(lines) > floor_y:
        raise SystemExit("%s: %d rows do not fit; trim the selection"
                         % (out, len(lines)))
    f = mono(size)
    for row in lines:
        d.text((60, y), row, font=f, fill=INK if row.strip() else DIM)
        y += step

    d.text((60, H - 64), footer, font=sans(25), fill=DIM)
    path = MEDIA / out
    card.save(path)
    return path


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)

    hint = ROOT / "captures/a5/HINT-REPORT.txt"
    mutated = ROOT / "evidence/a5-mutations/mutation3a-hint-sampler_report.txt"
    sweep = ROOT / "captures/a5/materials/SWEEP-REPORT.txt"

    made = []

    made.append(compose(
        "B07-evidence.png",
        ROOT / "captures/a5/hint_experiment.png",
        "Measured, beside the prediction committed 2026-10-23",
        table_from(hint, "stored |", "192 |"),
        "captures/a5/HINT-REPORT.txt - real windowed run, Forward+, RTX 5080. "
        "All six exact."))

    # The two uniforms whose effect is largest, with their own min and max
    # rows, lifted verbatim. The full twelve are in the report.
    all_rows = [r.rstrip() for r in sweep.read_text(encoding="utf-8").splitlines()]
    sweep_rows = [r for r in all_rows if r.strip().startswith("baseline")]
    for name in ("roughness_dry", "water_roughness"):
        head = next(i for i, r in enumerate(all_rows)
                    if r.strip().startswith(name + " "))
        block = all_rows[head:head + 4]
        sweep_rows += [""] + [block[0]] + [r for r in block[1:]
                                           if " min " in r or " max " in r]
    made.append(compose(
        "B09-evidence.png",
        ROOT / "captures/a5/materials/00-baseline.png",
        "One shader, two materials - and the dry slime never moves",
        sweep_rows,
        "captures/a5/materials/SWEEP-REPORT.txt - the dry column reads "
        "50, 56, 55 in all twelve sweep rows."))

    made.append(compose(
        "B11-evidence.png",
        ROOT / "evidence/a5-mutations/mutation3a-hint-sampler_capture.png",
        "The same scene with source_color deleted from line 4",
        table_from(mutated, "stored |", "192 |"),
        "evidence/a5-mutations/ - 0 SHADER ERROR lines, uniform list "
        "unchanged, both quads now identical."))

    for p in made:
        im = Image.open(p)
        print("  %-22s %s  %.0f KB" % (p.name, im.size, p.stat().st_size / 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
