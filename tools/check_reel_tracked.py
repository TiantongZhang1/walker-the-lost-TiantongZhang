#!/usr/bin/env python3
"""Assert that every file a reel's ledger HASHES is actually tracked by git.

    python -I tools/check_reel_tracked.py <reel-dir> [...]

**Why this exists.** Three times now, a file that `gamedev-evidence.json`
hashes has been excluded by `.gitignore` while everything looked right: the
file is on disk, `git status` is clean, the ledger builder hashes it happily,
and the course checker passes — *here*. A reviewer who clones the tag gets
`Missing or escaping source` and can verify nothing.

  2026-10-28  `capture/take-w.mp4`, Assignment 5. Found by cloning the tag.
  2026-11-21  `capture/take-{s,m}.mp4`, Assignment 7. Found by running
              `git check-ignore` by hand before the first commit of the reel.
  2026-11-21  `media/B13.png` and `media/B14.png`, Assignment 7. **Found by
              cloning the tag, because the hand check above covered the takes
              and not the cards.**

The third one is the reason this is a script. A hand check is a thing you
remember to point at some of the files; `.gitignore`'s `youtube/*/media/*`
rule with one `!` line per hashed still is exactly the shape that rewards
forgetting, and B07 and B09 survived **by luck** — Assignment 5's film has
stills with the same two names.

This reads the ledger, collects every path it references, and asks git. It
exits nonzero and names each file, which is what a check is for.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def referenced(ledger: dict, sheet: dict) -> list[str]:
    """Every reel-relative media path the ledger hashes OR the sheet needs.

    The ledger only hashes the result half of a code->result pair. **That is
    not the whole set a clone needs** -- Assignment 7's `media/B14.png` is a
    STILL that is not in any pair, so a check built on the ledger alone
    reported it tracked when it was not, and a clone could not recompile the
    film. The beat sheet's `evidence_media` is the authority for what the
    compiler will open.
    """
    out = []
    for pair in ledger.get("code_result_pairs", []):
        media = pair.get("media", {}).get("path")
        if media:
            out.append(media)
    for beat in sheet.get("beats", []):
        media = beat.get("shot", {}).get("evidence_media")
        if media:
            out.append(media)
    return sorted(set(out))


def coverage_media(cov: dict) -> list[str]:
    """Every capture a walkthrough reel's coverage.json hashes, plus its
    input log. A `godot-waikthrough` reel has no gamedev-evidence.json; its
    evidence file is coverage.json and its media are the takes."""
    out = []
    for cap in cov.get("captures", {}).values():
        if cap.get("path"):
            out.append(cap["path"])
        if cap.get("input_log"):
            out.append(cap["input_log"])
    return out


def check(reel: pathlib.Path) -> int:
    led = reel / "gamedev-evidence.json"
    cov = reel / "coverage.json"
    if not led.is_file() and not cov.is_file():
        print("  no gamedev-evidence.json or coverage.json in %s" % reel.name)
        return 1
    ledger = json.load(led.open(encoding="utf-8")) if led.is_file() else {}
    sheet_path = reel / "beat_sheet.json"
    if not sheet_path.is_file():
        print("  no beat_sheet.json in %s" % reel.name)
        return 1
    sheet = json.load(sheet_path.open(encoding="utf-8"))
    paths = referenced(ledger, sheet)
    if cov.is_file():
        paths += coverage_media(json.load(cov.open(encoding="utf-8")))
        paths = sorted(set(paths))
    if not paths:
        print("  %s: the ledger references no media at all" % reel.name)
        return 1

    # The ledger itself, the beat sheet and the take logs are evidence too: a
    # reviewer needs all of them. Checking only what is hashed would have let
    # the input logs through, and every number on three cards is computed
    # from those.
    extra = ["beat_sheet.json"]
    for name in ("gamedev-evidence.json", "coverage.json",
                 "SOURCE-SNAPSHOT.json"):
        if (reel / name).is_file():
            extra.append(name)
    extra += [p.relative_to(reel).as_posix()
              for p in sorted((reel / "capture" / "logs").glob("*.jsonl"))]

    bad, missing = [], []
    for rel in paths + extra:
        f = reel / rel
        if not f.is_file():
            missing.append(rel)
            continue
        r = subprocess.run(["git", "check-ignore", "-q",
                            str(f.relative_to(ROOT).as_posix())],
                           cwd=ROOT)
        if r.returncode == 0:
            bad.append(rel)

    print("  %s: %d referenced + %d supporting file(s)"
          % (reel.name, len(paths), len(extra)))
    for rel in missing:
        print("    MISSING   %s" % rel)
    for rel in bad:
        print("    IGNORED   %s   <-- the ledger needs it; a clone will not have it"
              % rel)
    if not bad and not missing:
        print("    all tracked")
    return 1 if (bad or missing) else 0


def main(argv: list[str]) -> int:
    reels = [pathlib.Path(a) for a in argv[1:]]
    if not reels:
        reels = sorted(p for p in (ROOT / "youtube").iterdir() if p.is_dir())
    rc = 0
    for reel in reels:
        rc |= check(reel if reel.is_absolute() else (ROOT / reel))
    print("\n%s" % ("OK" if rc == 0 else
                    "FAILED -- add a `!` line to .gitignore for each file above"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
