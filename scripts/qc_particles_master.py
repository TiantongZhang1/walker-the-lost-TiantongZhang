#!/usr/bin/env python3
"""Pull one frame per beat out of the rendered master and lay them on a sheet.

    python -X utf8 scripts/qc_particles_master.py

Writes `_qc/contact-sheet.png` and `_qc/REPORT.md` into the reel.

**This is not a check, it is a way of looking.** Every automatic gate in this
chain — the evidence checker, the configuration suites, the compiler's own
slot count — was green through four faults in this film: a take that recorded
the wrong thing, a card captioned over an empty room, two note panels clipped
mid-word, and a narrated claim that was simply false. Not one of them is
visible to a hash or a line number. All four were found by pulling a frame
out and reading it.

The frame per beat is taken at the beat's own MIDPOINT, computed from the
measured narration lengths in `beat_sheet.json` rather than from a guess, so
a beat that is frozen or blank in its second half still shows up here. The
sheet is evidence that the master was looked at; it is not evidence that the
master is right. Only reading it is that.
"""
from __future__ import annotations

import io
import json
import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-particles-gamedev"
MASTER = REEL / "exports/landscape/claude-liam-walker-the-lost-particles-gamedev.mp4"
QC = REEL / "_qc"

CELL_W = 640
COLS = 4
LABEL_H = 34


def font(size):
    for n in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def probe_seconds(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main() -> int:
    if not MASTER.is_file():
        raise SystemExit("no master at %s - run `art final` first" % MASTER)
    QC.mkdir(parents=True, exist_ok=True)
    sheet = json.load(io.open(REEL / "beat_sheet.json", encoding="utf-8"))
    beats = sheet["beats"]

    # Beat boundaries from the measured narration, which is the film's clock.
    marks, t = [], 0.0
    for b in beats:
        length = float(b.get("render_duration_s")
                       or b.get("actual_duration_s")
                       or b["estimated_duration_s"])
        marks.append((b["beat_id"], t, length, t + length * 0.5))
        t += length

    total = probe_seconds(MASTER)
    drift = abs(total - t)
    rows: list[str] = []
    frames: list[Image.Image] = []
    for bid, start, length, mid in marks:
        out = QC / ("frame-%s.png" % bid)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % mid,
                        "-i", str(MASTER), "-frames:v", "1",
                        "-vf", "scale=%d:-1" % CELL_W, str(out)], check=True)
        im = Image.open(out).convert("RGB")
        frames.append(im)
        rows.append("| %s | %6.1f | %5.1f | %6.1f | `_qc/frame-%s.png` |"
                    % (bid, start, length, mid, bid))

    cell_h = frames[0].height
    rows_n = (len(frames) + COLS - 1) // COLS
    board = Image.new("RGB", (CELL_W * COLS, (cell_h + LABEL_H) * rows_n),
                      (250, 249, 245))
    d = ImageDraw.Draw(board)
    f = font(22)
    for i, (im, mark) in enumerate(zip(frames, marks)):
        x, y = (i % COLS) * CELL_W, (i // COLS) * (cell_h + LABEL_H)
        board.paste(im, (x, y))
        d.text((x + 8, y + cell_h + 6), "%s   %.1f s" % (mark[0], mark[3]),
               font=f, fill=(32, 30, 28))
    board.save(QC / "contact-sheet.png")

    io.open(QC / "REPORT.md", "w", encoding="utf-8", newline="\n").write(
        "\n".join([
            "# _qc — the master, one frame per beat",
            "",
            "`contact-sheet.png`, written by `scripts/qc_particles_master.py`.",
            "",
            "| | |",
            "|---|---|",
            "| Master | `exports/landscape/%s` |" % MASTER.name,
            "| Measured length | **%.2f s** (%d:%05.2f) |" % (total, total // 60, total % 60),
            "| Beat sheet total | %.2f s |" % t,
            "| Drift | %.3f s |" % drift,
            "| Beats | %d |" % len(beats),
            "",
            "Each frame is taken at its beat's **midpoint**, computed from the",
            "measured narration length rather than guessed, so a beat that is",
            "frozen or blank in its second half still appears here.",
            "",
            "| beat | starts | length | frame at | file |",
            "|---|---|---|---|---|",
        ] + rows + [
            "",
            "## What this sheet is, and is not",
            "",
            "It is evidence that the master was looked at. It is **not**",
            "evidence that the master is right; only reading it is that.",
            "",
            "Every automatic gate in this chain was green through four faults",
            "in this film — a take that recorded the wrong thing, a card",
            "captioned over an empty room, two note panels clipped mid-word,",
            "and a narrated claim that was false. None is visible to a hash or",
            "a line number, and all four were found by pulling a frame out and",
            "reading it. `../../TEST-REPORT.md` records each one.",
            "",
        ]))

    print("wrote %s" % (QC / "contact-sheet.png"))
    print("  %d beats, master %.2f s, beat sheet %.2f s, drift %.3f s"
          % (len(beats), total, t, drift))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
