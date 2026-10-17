#!/usr/bin/env python3
"""Compose B09's evidence card from the recorded stdout of tests/test_game.gd.

Output is 1529 x 987, the GodotDevWorkbench right-hand image area measured off
a rendered master.

Check names, values and their order are verbatim. The two JSON payloads are
WRAPPED one key per line, because the recorded lines are 91 characters wide and
a 91-character line in this panel renders at 29 px on a 3840-wide frame, which
is not readable. The wrap buys 42 px -- the fitter prints the figure it reached.
Nothing is reworded, reordered, rounded or dropped, and the label on screen
says the payloads are wrapped.

Deterministic: same input text, byte-identical PNG.
"""
import io
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REEL = os.path.join(ROOT, "youtube", "claude-liam-walker-ninja-gamedev")
SRC = os.path.join(REEL, "media", "B09-suite-output.txt")
OUT = os.path.join(REEL, "media", "B09-suite-output.png")
FONT_MONO = os.environ.get("ART_FONT_MONO", os.path.join(
    os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "consola.ttf"))

W, H = 1529, 987
PAD, LEAD = 34, 1.42

CREAM = (0xf7, 0xf4, 0xec)
SHELL = (0x22, 0x2a, 0x38)
INK = (0xe8, 0xe4, 0xdb)
DIM = (0x9a, 0xa7, 0xbd)
PASS = (0x7f, 0xc1, 0x8f)
TOTAL = (0xc8, 0x9a, 0x5a)


def payload(line):
    """Split one recorded JSON line into (key, value) in the order recorded."""
    inner = line.strip().lstrip("{").rstrip("}")
    out = []
    for part in inner.split(", "):
        k, _, v = part.partition(": ")
        out.append((k.strip().strip('"'), v.strip()))
    return out


def relay(recorded):
    lines = []
    for raw in recorded:
        s = raw.rstrip()
        if not s:
            lines.append(("", INK))
        elif s.startswith("Recorded from:"):
            head, _, tail = s[len("Recorded from: "):].partition(" --script ")
            lines.append(("Recorded from: " + head, DIM))
            lines.append((" " * 15 + "--script " + tail, DIM))
        elif s.lstrip().startswith("{"):
            kv = payload(s)
            pad = max(len(k) for k, _ in kv)
            for k, v in kv:
                lines.append(("    " + (k + ":").ljust(pad + 2) + " " + v, INK))
        elif s.startswith("WALKER TESTS:"):
            lines.append((s, TOTAL))
        else:
            lines.append((s, PASS if s.endswith("PASS") else INK))
    return lines


def main():
    recorded = io.open(SRC, encoding="utf-8").read().splitlines()
    lines = relay(recorded)
    widest = max(len(t) for t, _ in lines)
    n = len(lines)
    print(n, "lines, widest", widest, "chars (recorded was",
          len(recorded), "/", max(len(l) for l in recorded), ")")

    size = 10
    while True:
        f = ImageFont.truetype(FONT_MONO, size + 1)
        cw = f.getlength("M" * 10) / 10.0
        if (cw * widest > W - 4 * PAD) or ((size + 1) * LEAD * n > H - 4 * PAD):
            break
        size += 1

    font = ImageFont.truetype(FONT_MONO, size)
    lh = int(size * LEAD)
    cw = font.getlength("M" * 10) / 10.0
    bw = int(cw * widest) + 2 * PAD
    bh = lh * n + 2 * PAD

    canvas = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(canvas)
    bx, by = (W - bw) // 2, (H - bh) // 2
    d.rectangle([bx, by, bx + bw - 1, by + bh - 1], fill=SHELL)
    for i, (t, col) in enumerate(lines):
        if t:
            d.text((bx + PAD, by + PAD + i * lh), t, font=font, fill=col)

    canvas.save(OUT)
    print("wrote", OUT, canvas.size, "font", size, "block", bw, "x", bh,
          "(" + str(bw * 100 // W) + "% w, " + str(bh * 100 // H) + "% h)")


if __name__ == "__main__":
    main()
