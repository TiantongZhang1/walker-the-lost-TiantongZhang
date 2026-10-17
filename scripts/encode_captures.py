#!/usr/bin/env python3
"""Encode rendered take frames into the reel's capture/*.mp4 evidence files.

Input is what `scripts/render_takes.py` produced: a numbered lossless PNG
sequence per take plus Movie Maker's `frame.wav`. Output is one MP4 per take in
`<reel>/capture/`, alongside that take's input log, which is what `coverage.json`
hashes and what `verify_walkthrough.py` probes.

The engine audio is carried into the MP4 so the capture stays faithful to what
the run produced. It is NOT how the laugh reaches the finished film - see the
audio decision in CAPTURE.md.

    python scripts/encode_captures.py --frames <render-root> --reel <reel-dir>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

# Assignment 1's four walkthrough takes, then Assignment 2's two gamedev takes.
# Both films' captures encode with the same settings, so a frame from either is
# the same kind of evidence.
TAKES = ("a", "b", "c", "d", "p", "t")
FPS = 60
WIDTH, HEIGHT = 3840, 2160


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def encode(frames_dir: Path, wav: Path, out: Path) -> None:
    command = [
        "ffmpeg", "-y", "-v", "error",
        "-framerate", str(FPS), "-i", str(frames_dir / "frame%08d.png"),
    ]
    if wav.is_file():
        command += ["-i", str(wav)]
    # crf 14 on flat vector-drawn colour is visually lossless and keeps the
    # file small enough to work with; yuv420p for players that need it.
    command += ["-c:v", "libx264", "-preset", "medium", "-crf", "14",
                "-pix_fmt", "yuv420p", "-r", str(FPS)]
    if wav.is_file():
        command += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    command += ["-movflags", "+faststart", str(out)]
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", required=True, type=Path)
    parser.add_argument("--reel", required=True, type=Path)
    args = parser.parse_args()
    frames_root = args.frames.resolve()
    capture = (args.reel.resolve() / "capture")
    capture.mkdir(parents=True, exist_ok=True)

    ok = True
    for letter in TAKES:
        src = frames_root / ("take-%s" % letter)
        pngs = sorted(src.glob("frame*.png"))
        if not pngs:
            print("take %s: no frames in %s" % (letter, src))
            ok = False
            continue
        out = capture / ("take-%s.mp4" % letter)
        encode(src, src / "frame.wav", out)
        info = probe(out)
        video = [s for s in info["streams"] if s["codec_type"] == "video"]
        audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
        width, height = int(video[0]["width"]), int(video[0]["height"])
        duration = float(info["format"]["duration"])
        expected = len(pngs) / FPS
        status = "ok"
        if (width, height) != (WIDTH, HEIGHT):
            status = "WRONG SIZE"
            ok = False
        if abs(duration - expected) > 0.05:
            status = "DURATION DRIFT (expected %.3f)" % expected
            ok = False
        print("take-%s.mp4  %dx%d  %6.2f s  %d frames  %5.1f MB  %d audio stream(s)  %s" % (
            letter, width, height, duration, len(pngs),
            out.stat().st_size / (1024 * 1024), len(audio), status))
        log_src = frames_root / "logs" / ("take-%s-inputs.jsonl" % letter)
        if log_src.is_file():
            shutil.copy2(log_src, capture / log_src.name)
        else:
            print("  WARNING: no input log at %s" % log_src)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
