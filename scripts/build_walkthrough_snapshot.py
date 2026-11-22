#!/usr/bin/env python3
"""Write the walkthrough reel's SOURCE-SNAPSHOT.json and its `build_id`.

    python -X utf8 scripts/build_walkthrough_snapshot.py

`godot-waikthrough`'s coverage contract wants a content hash of the source
snapshot as `build_id`, and every capture carries the same one. That makes
the claim "this footage is of this source" checkable: re-run this script and
the id either matches or the game moved.

**The hash is of the FILES MAP, not of a commit.** A commit SHA would be the
easier thing to use and it would be the wrong one: it changes when a
document changes, and the film's claim is about the game. This hashes the
bytes under `godot/`, so a commit that only adds film documentation leaves
the id alone — which is exactly the property the assignment asks for when it
says "verify that the final commit does not change the demonstrated game
source".

Same exclusions as the gamedev ledger: `.godot/` (an engine cache) and the
generated `.uid` files. `.import` sidecars are IN, because they carry
authored import settings.
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
GAME = ROOT / "godot"
REEL = ROOT / "youtube/claude-liam-walker-the-lost-walkthrough"
SKIP_DIRS = {".godot", ".import"}

HASH_METHOD = ("sha256 of each file; build_id = sha256 of this object's "
               "`files` map serialized as canonical JSON "
               "(sort_keys=True, separators=(',', ':'), UTF-8)")


def files_map() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted(GAME.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(GAME)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.as_posix().endswith(".uid"):
            continue
        out[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main() -> int:
    stray = GAME / "override.cfg"
    if stray.is_file():
        raise SystemExit(
            "godot/override.cfg exists -- that is render_takes.py's temporary "
            "4K override. Hashing it would put a file in the snapshot that no "
            "clone has.")

    REEL.mkdir(parents=True, exist_ok=True)
    fm = files_map()
    canonical = json.dumps(fm, sort_keys=True, separators=(",", ":"))
    build_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "godot"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()

    snap = {
        "captured_at": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "project": "walker-the-lost-TiantongZhang",
        "engine": "Godot 4.7.2.stable.official.ed1daf0bf",
        "git_revision": rev,
        "git_godot_clean": dirty == "",
        "hash_method": HASH_METHOD,
        "files": fm,
        "build_id": build_id,
    }
    out = REEL / "SOURCE-SNAPSHOT.json"
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(snap, ensure_ascii=False, indent=2) + "\n")
    print("wrote %s" % out)
    print("  %d files under godot/" % len(fm))
    print("  git revision   %s%s" % (rev[:7], "" if dirty == "" else "  DIRTY"))
    print("  build_id       %s" % build_id)
    if dirty:
        print("  WARNING: godot/ has uncommitted changes. The snapshot")
        print("  describes the working tree, not the revision above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
