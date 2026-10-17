#!/usr/bin/env python3
"""Write SOURCE-SNAPSHOT.json for a reel and print its build_id.

`coverage.json` needs a `build_id` that is "a content hash of the source
snapshot" (skills/make/godot-waikthrough/references/capture-and-coverage.md).
This builds that snapshot from the files that can change what a capture shows,
and derives the id from the snapshot's own canonical bytes, so the id is
reproducible from the repository and changes if any of those files change.

Included: project.godot, every .gd and .tscn under godot/, godot/levels/*.json,
and godot/assets/* (the death reaction's image and audio are loaded at runtime
and are part of what the film shows). The capture driver is included on
purpose: it decides which inputs the footage contains, so a change to it should
invalidate the captures it produced.

Excluded: .godot/ (engine cache, not source and not committed), *.uid (editor
bookkeeping), and everything outside godot/ except project.godot itself.

    python scripts/build_source_snapshot.py <reel-dir>
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parent.parent
GODOT_DIR = PROJECT / "godot"
SKIP_DIRS = {".godot"}
SKIP_SUFFIXES = {".uid"}
INCLUDE_SUFFIXES = {".gd", ".tscn", ".json", ".godot", ".png", ".ogg"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect() -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(GODOT_DIR.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(GODOT_DIR).parts):
            continue
        if path.suffix in SKIP_SUFFIXES or path.suffix not in INCLUDE_SUFFIXES:
            continue
        files[path.relative_to(PROJECT).as_posix()] = sha256_file(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reel", type=Path)
    args = parser.parse_args()
    files = collect()
    if not files:
        print("no source files found under %s" % GODOT_DIR, file=sys.stderr)
        return 1
    snapshot = {
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project": "walker-jumpman-TiantongZhang",
        "engine": "Godot 4.7.2.stable.official.ed1daf0bf",
        "hash_method": "sha256 of each file; build_id = sha256 of this object's "
                       "`files` map serialized as canonical JSON "
                       "(sort_keys=True, separators=(',', ':'), UTF-8)",
        "files": files,
    }
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    snapshot["build_id"] = hashlib.sha256(canonical).hexdigest()
    reel = args.reel.resolve()
    reel.mkdir(parents=True, exist_ok=True)
    (reel / "SOURCE-SNAPSHOT.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print("%d files" % len(files))
    print(snapshot["build_id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
