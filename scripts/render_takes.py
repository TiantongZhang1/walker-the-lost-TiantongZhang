#!/usr/bin/env python3
"""Render walkthrough takes as native 3840x2160 frame sequences.

Godot's Movie Maker fixes its output size from the window size at engine
startup - before `--resolution` is applied and before any script runs - so the
size has to come from project settings. Setting it permanently in
project.godot would change the game's own window for normal play, so this
script writes a temporary `godot/override.cfg`, renders, and removes it again.
Verified: without the override the same command silently records 1280x720 and
prints "recording movie in 1280x720", which is how the first take of this film
was produced.

    python scripts/render_takes.py a b c d --out <dir>
    python scripts/render_takes.py p t --out <dir>         --driver res://tests/capture_gamedev.gd

Each take writes <dir>/take-<letter>/frame########.png plus frame.wav, and its
input log to <dir>/logs/take-<letter>-inputs.jsonl. The driver asserts its own
expected outcome and exits nonzero if the take did not happen, so a completed
render is not by itself the claim - the take's CAPTURE OK line is.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

PROJECT = Path(__file__).resolve().parent.parent
GODOT_DIR = PROJECT / "godot"
OVERRIDE = GODOT_DIR / "override.cfg"
WIDTH, HEIGHT = 3840, 2160

OVERRIDE_TEXT = """; Temporary, written by scripts/render_takes.py for 4K walkthrough renders.
; Movie Maker fixes its output size from the window size at startup, before
; --resolution or any script runs. Removed again when the render finishes.
[display]

window/size/window_width_override={w}
window/size/window_height_override={h}
""".format(w=WIDTH, h=HEIGHT)

# Generous per-take frame bounds. The driver quits itself on success; these are
# only the safety net --quit-after provides, so they sit well above the
# measured tick counts (a 484, b 1389, c 705, d 1618).
QUIT_AFTER = {"a": 600, "b": 1500, "c": 900, "d": 1800, "p": 600, "t": 900}

# Assignment 2's film uses a second driver. The default stays Assignment 1's,
# so that film remains reproducible from this script unchanged.
DEFAULT_DRIVER = "res://tests/capture_walkthrough.gd"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    return struct.unpack(">II", header[16:24])


def render(godot: str, take: str, out_root: Path, driver: str = DEFAULT_DRIVER) -> bool:
    out = out_root / ("take-" + take)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    logs = out_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, WALKER_TAKE=take, WALKER_LOG_DIR=str(logs))
    command = [
        godot, "--path", str(GODOT_DIR),
        "--script", driver,
        "--write-movie", str(out / "frame.png"),
        "--fixed-fps", "60", "--disable-vsync",
        "--quit-after", str(QUIT_AFTER.get(take, 1800)),
    ]
    print("--- take %s ---" % take, flush=True)
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    combined = (result.stdout or "") + (result.stderr or "")
    for line in combined.splitlines():
        if any(k in line for k in ("CAPTURE", "Movie Maker", "Parse Error", "SCRIPT ERROR")):
            print("  " + line.strip(), flush=True)
    if result.returncode != 0 or "CAPTURE OK" not in combined:
        print("  FAILED: take %s did not complete (exit %d)" % (take, result.returncode))
        return False
    frames = sorted(out.glob("frame*.png"))
    if not frames:
        print("  FAILED: no frames written")
        return False
    bad = [f.name for f in (frames[0], frames[len(frames) // 2], frames[-1])
           if png_size(f) != (WIDTH, HEIGHT)]
    if bad:
        print("  FAILED: frames are not %dx%d: %s" % (WIDTH, HEIGHT, bad))
        return False
    wav = out / "frame.wav"
    size_mb = sum(f.stat().st_size for f in frames) / (1024 * 1024)
    print("  %d frames at %dx%d, %.1f MB, audio %s" % (
        len(frames), WIDTH, HEIGHT, size_mb,
        "%.2f MB" % (wav.stat().st_size / (1024 * 1024)) if wav.is_file() else "MISSING"))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("takes", nargs="+", help="take letters, e.g. a b c d")
    parser.add_argument("--out", required=True, type=Path, help="output root directory")
    parser.add_argument("--godot", default=os.environ.get("GODOT", "godot"),
                        help="Godot executable (or set $GODOT)")
    parser.add_argument("--driver", default=DEFAULT_DRIVER,
                        help="res:// path of the capture driver "
                             "(default: Assignment 1's walkthrough driver)")
    args = parser.parse_args()
    if OVERRIDE.exists():
        print("refusing to run: %s already exists; remove it first" % OVERRIDE)
        return 2
    OVERRIDE.write_text(OVERRIDE_TEXT, encoding="utf-8")
    try:
        ok = True
        for take in args.takes:
            ok = render(args.godot, take, args.out.resolve(), args.driver) and ok
    finally:
        OVERRIDE.unlink(missing_ok=True)
        print("removed %s" % OVERRIDE.name)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
