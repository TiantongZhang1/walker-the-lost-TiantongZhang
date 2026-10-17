#!/usr/bin/env python3
"""Mix the game's death laugh under one beat's narration, at the right frame.

Why this exists rather than muxing the capture's `frame.wav`: the compositor
encodes every ordinary footage slot with `-an`, and `build_master_audio()`
assembles exactly one track per beat - the beat's narration mp3, declared
silence, or a source report's embedded audio. There is no supported path that
lays gameplay audio under narration. Pre-mixing into the narration track is
supported, checkable, and keeps compile.py's `require_audible()` and its
+/-0.15 s duration agreement in force.

The delay is not guessed. It is the death's timestamp in the take's own input
log, minus the beat's window start, so the laugh begins on the frame the
character actually dies in the clip the viewer is watching.

    python scripts/mix_death_laugh.py <reel> --beat B02 --gain 0.35
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

PROJECT = Path(__file__).resolve().parent.parent
LAUGH = PROJECT / "godot" / "assets" / "death-laugh.ogg"


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reel", type=Path)
    parser.add_argument("--beat", default="B02")
    parser.add_argument("--gain", type=float, default=0.35,
                        help="laugh level under the voice (1.0 = as recorded)")
    args = parser.parse_args()
    reel = args.reel.resolve()

    sheet = json.loads((reel / "beat_sheet.json").read_text(encoding="utf-8"))
    beat = next((b for b in sheet["beats"] if b["beat_id"] == args.beat), None)
    if beat is None or not beat.get("shot", {}).get("capture"):
        print("%s is not a gameplay beat" % args.beat, file=sys.stderr)
        return 1
    capture = beat["shot"]["capture"]
    window_start = float(beat["shot"]["window_s"][0])

    log = reel / "capture" / ("%s-inputs.jsonl" % capture)
    deaths = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
              if line.strip() and json.loads(line)["action"] == "DIED"]
    inside = [d for d in deaths
              if window_start <= d["t_s"] < window_start + float(beat["shot"]["clip_s"])]
    if len(inside) != 1:
        print("%s: expected exactly one death inside the clip, found %d"
              % (args.beat, len(inside)), file=sys.stderr)
        return 1
    delay_s = inside[0]["t_s"] - window_start

    mp3 = reel / "mp3" / ("beat-%s.mp3" % args.beat)
    backup = reel / "mp3" / ("beat-%s.narration-only.mp3" % args.beat)
    if not backup.is_file():
        shutil.copy2(mp3, backup)
    before = probe_duration(backup)

    tmp = mp3.with_suffix(".mixed.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(backup), "-i", str(LAUGH),
        "-filter_complex",
        "[1:a]adelay=%d|%d,volume=%.3f[laugh];"
        "[0:a][laugh]amix=inputs=2:duration=first:normalize=0[out]"
        % (round(delay_s * 1000), round(delay_s * 1000), args.gain),
        "-map", "[out]", "-t", "%.6f" % before,
        "-c:a", "libmp3lame", "-b:a", "192k", str(tmp)], check=True)
    after = probe_duration(tmp)
    if abs(after - before) > 0.05:
        print("duration moved %.3f -> %.3f s; refusing to replace the narration"
              % (before, after), file=sys.stderr)
        tmp.unlink(missing_ok=True)
        return 1
    tmp.replace(mp3)
    print("%s: laugh from %s mixed at %.3f s (death at %.3f s in %s, window starts %.3f), "
          "gain %.2f, duration %.3f -> %.3f s"
          % (args.beat, LAUGH.name, delay_s, inside[0]["t_s"], capture, window_start,
             args.gain, before, after))
    print("narration-only original kept at mp3/%s" % backup.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
