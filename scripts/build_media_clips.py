#!/usr/bin/env python3
"""Pre-trim each gameplay beat's media/<beat_id>.mp4 to its exact beat duration.

The compositor's ordinary footage path will centre-cut a long clip and retime a
short one to fit the beat (`compile.py` retimes silently within +/-5%). The
walkthrough contract forbids that for gameplay: each slot's ratio must round to
1.000000, and extra narration time must be taken by a labeled final-frame hold,
never by slowing the action. So the clips are cut here, deliberately, to the
frame.

For each gameplay beat:

    beat duration = ceil(narration_seconds * fps) / fps          (compile.py's rule)
    clip          = capture[window_start : window_start + min(window, duration)]
    hold          = duration - clip, as a cloned final frame

The script writes `actual_duration_s`, `render_duration_s`, `audio_file` and a
`shot.hold_s` back into the beat sheet, and refuses to drop recorded footage
silently: if a window is longer than its beat, it says so and exits, because the
body is supposed to tile the takes exactly once.

    python scripts/build_media_clips.py <reel> [--fps 60]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reel", type=Path)
    parser.add_argument("--fps", type=int, default=60)
    args = parser.parse_args()
    reel = args.reel.resolve()
    fps = args.fps
    sheet_path = reel / "beat_sheet.json"
    sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
    media = reel / "media"
    media.mkdir(exist_ok=True)

    ok = True
    total_clip = total_hold = 0.0
    for beat in sheet["beats"]:
        bid = beat["beat_id"]
        mp3 = reel / "mp3" / ("beat-%s.mp3" % bid)
        if mp3.is_file():
            actual = probe_duration(mp3)
            beat["audio_file"] = "mp3/beat-%s.mp3" % bid
        else:
            # Intentional silence (the outro card) keeps its estimate.
            actual = float(beat.get("estimated_duration_s", 0))
        beat["actual_duration_s"] = round(actual, 3)
        beat["render_duration_s"] = math.ceil(actual * fps - 1e-8) / fps

        shot = beat.get("shot", {})
        capture = shot.get("capture")
        if not capture:
            continue
        duration = beat["render_duration_s"]
        start, stop = (float(v) for v in shot["window_s"])
        window = stop - start
        if window - duration > 1.0 / fps:
            print("%s: window is %.3f s but the beat is %.3f s - %.3f s of recorded "
                  "footage would be dropped. Give it to the next beat of this take."
                  % (bid, window, duration, window - duration))
            ok = False
            continue
        clip = min(window, duration)
        hold = round(duration - clip, 6)
        out = media / ("%s.mp4" % bid)
        # -ss before -i seeks on keyframes, so decode from the start and trim
        # with the filter graph instead; these clips are short and 4K but the
        # accuracy matters more than the seconds.
        vf = "trim=start=%.6f:end=%.6f,setpts=PTS-STARTPTS" % (start, start + clip)
        if hold > 1e-6:
            vf += ",tpad=stop_mode=clone:stop_duration=%.6f" % hold
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(reel / "capture" / ("%s.mp4" % capture)),
            "-vf", vf, "-an", "-r", str(fps), "-t", "%.6f" % duration,
            "-c:v", "libx264", "-preset", "medium", "-crf", "14",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
        got = probe_duration(out)
        shot["hold_s"] = hold
        shot["clip_s"] = round(clip, 3)
        drift = abs(got - duration)
        status = "ok" if drift <= 1.5 / fps else "DURATION DRIFT %.4f s" % drift
        if drift > 1.5 / fps:
            ok = False
        total_clip += clip
        total_hold += hold
        print("%s  %s %7.3f-%7.3f  clip %6.3f + hold %5.3f = %6.3f s  (got %6.3f)  %s"
              % (bid, capture, start, start + clip, clip, hold, duration, got, status))

    sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    film = sum(b["render_duration_s"] for b in sheet["beats"])
    print("\n%.2f s of action + %.2f s of labeled hold; film runs %.2f s at %d fps"
          % (total_clip, total_hold, film, fps))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
