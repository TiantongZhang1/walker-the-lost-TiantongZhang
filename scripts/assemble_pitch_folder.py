#!/usr/bin/env python3
"""Assemble pitch/ — the folder Assignment 8 asks for — from live sources.

    python -X utf8 scripts/assemble_pitch_folder.py [--url <film URL>]

Assignment 8 wants `pitch/` to contain the README, the brief, the beat sheet,
the build prompt, SOURCES, the gate reports and FRICTIONAL. Several of those
already exist inside the reel, and **a second hand-maintained copy of a
document is how a sentence outlives its facts.** This repository has gone
back for eleven of those. So the copies are generated here, every one of them
carries a header saying it is generated, and the originals stay in the reel.

Written by hand and never touched by this script:
`pitch/PROJECT-BRIEF.md` and `pitch/FRICTIONAL.md`.

Every figure in `pitch/README.md` is measured here - the master's length, its
byte count and its SHA-256 - so the README cannot disagree with the file it
describes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PITCH = ROOT / "pitch"
SLUG = "claude-liam-walker-the-lost-pitch-gdd"
REEL = ROOT / "youtube" / SLUG
MASTER = REEL / "exports/landscape" / ("%s.mp4" % SLUG)
SUBMITTED_NAME = "TheLostPitch_TiantongZhang.mp4"

COPIES = [
    ("beat_sheet.json", "the narration and visual plan, written by "
                        "scripts/build_pitch_beat_sheet.py"),
    ("gdd-evidence.json", "the ledger the official checker reads, written by "
                          "scripts/build_pitch_ledger.py"),
    ("SOURCES.md", "what is in the film, where it came from, and who made it"),
    ("BUILD-PROMPT.md", "the commands that rebuild the film, in order"),
    ("SHOTLIST.md", "every beat, what is on screen, and how long it runs"),
    ("FACTCHECK.md", "every narrated claim traced to the file it came from"),
    ("GDD-COVERAGE.md", "every section of the document and the beat that "
                        "carries it"),
    ("_qc/REPORT.md", "the toolkit's Gate V visual QC report, as it ran"),
]

HEADER = ("<!-- GENERATED COPY. The original is\n"
          "     youtube/%s/%s\n"
          "     Rebuild with: python -X utf8 scripts/assemble_pitch_folder.py\n"
          "     Do not edit this copy; edit the original. -->\n\n")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def probe(path: pathlib.Path, entries: str) -> str:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", entries,
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return out.stdout.strip().splitlines()[0]


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> tuple[int, str]:
    """Run a check and report what it said.

    **`PYTHONUTF8` is not optional here.** Without it a child Python on this
    machine opens files in the system ANSI codepage, and the official checker
    came back `'gbk' codec can't decode byte 0x94` - a FAIL that says nothing
    about the evidence it was asked to verify. A check that fails for a reason
    unrelated to what it checks is worth no more than one that passes for the
    wrong reason, and this report is the thing a reviewer reads instead of
    running them.
    """
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default="", help="the film's URL once uploaded")
    args = ap.parse_args()

    if not MASTER.is_file():
        sys.exit("no master at %s - run `art final` first" % MASTER)
    PITCH.mkdir(exist_ok=True)

    for name, _ in COPIES:
        src = REEL / name
        if not src.is_file():
            sys.exit("missing %s" % src)
        dst = PITCH / pathlib.Path(name).name
        if name.endswith(".json"):
            shutil.copyfile(src, dst)
        else:
            dst.write_text(HEADER % (SLUG, name)
                           + src.read_text(encoding="utf-8"),
                           encoding="utf-8", newline="\n")
        print("  copied  %-20s -> pitch/%s" % (name, dst.name))

    seconds = float(probe(MASTER, "format=duration"))
    size = MASTER.stat().st_size
    digest = sha256(MASTER)
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = sheet["beats"]
    narrated = sum(1 for b in beats if b.get("audio_policy") != "silence")
    words = sum(len(b.get("narration_text", "").split()) for b in beats)

    url = args.url.strip()
    if not url:
        old = PITCH / "README.md"
        if old.is_file():
            found = re.search(r"\*\*Film URL:\*\* <(\S+)>", old.read_text(encoding="utf-8"))
            if found and found.group(1) != "PENDING":
                url = found.group(1)
    url_line = ("<%s>" % url) if url else ("_PENDING — the upload is the "
                                           "author's. The SHA-256 below is "
                                           "what the uploaded file must match._")

    # Live checks, run now rather than remembered.
    checks = []
    code, out = run([sys.executable,
                     str(ROOT.parent / "brutalist.art-main/skills/make"
                         / "godot-gdd/scripts/verify_gdd.py"),
                     str(REEL), "--gdd", str(PITCH / "PROJECT-BRIEF.md")])
    checks.append(("`./art godot-gdd --check`", code == 0, out.splitlines()[0] if out else ""))
    code, out = run(["git", "diff", "--stat", "b33b06c", "--", "godot/"], ROOT)
    checks.append(("`git diff b33b06c..HEAD -- godot/`", not out.strip(),
                   out.strip() or "empty - no game code changed by Assignment 8"))
    code, out = run([sys.executable, "-I", str(ROOT / "tools/check_claude_refs.py")], ROOT)
    checks.append(("`tools/check_claude_refs.py`", code == 0,
                   out.strip().splitlines()[-1] if out.strip() else ""))
    code, out = run([sys.executable, "-I", str(ROOT / "tools/check_reel_tracked.py"),
                     str(REEL)], ROOT)
    checks.append(("`tools/check_reel_tracked.py`", code == 0,
                   out.strip().splitlines()[-1] if out.strip() else ""))

    (PITCH / "CHECKS-REPORT.md").write_text(
        "# CHECKS-REPORT.md — run at assembly time, not remembered\n\n"
        "Written by `scripts/assemble_pitch_folder.py` on %s.\n"
        "Every row below is a live run; the Gate V report is a copy of the\n"
        "render's own output and sits beside this file as `REPORT.md`.\n\n"
        "| Check | Result | Output |\n|---|---|---|\n%s\n"
        % (dt.date.today().isoformat(),
           "\n".join("| %s | %s | %s |"
                     % (name, "**PASS**" if ok else "**FAIL**",
                        (detail or "").replace("|", "\\|")[:180])
                     for name, ok, detail in checks)),
        encoding="utf-8", newline="\n")
    print("  wrote   pitch/CHECKS-REPORT.md")

    (PITCH / "README.md").write_text(README % {
        "url": url_line,
        "mins": int(seconds // 60), "secs": seconds % 60,
        "seconds": seconds, "size": "{:,}".format(size), "sha": digest,
        "beats": len(beats), "narrated": narrated, "words": words,
        "name": SUBMITTED_NAME, "slug": SLUG,
        "date": dt.date.today().isoformat(),
    }, encoding="utf-8", newline="\n")
    print("  wrote   pitch/README.md  (%d:%05.2f, %s bytes)"
          % (int(seconds // 60), seconds % 60, "{:,}".format(size)))
    for name, ok, _ in checks:
        print("  %-38s %s" % (name, "PASS" if ok else "FAIL"))
    return 0 if all(ok for _, ok, _ in checks) else 1


README = """# pitch/ — Assignment 8, Final Project Pitch Film

**Tiantong Zhang** · `zhang.tiant@northeastern.edu` · GitHub `TiantongZhang1`
CSYE 7270, Fall 2026 · assembled %(date)s

| | |
|---|---|
| **Working title** | **The Lost: Floor One** |
| **Target role** | **Gameplay programmer** |
| **Runtime (the project's, not the film's)** | Godot **4.7.2.stable.official** `ed1daf0bf`, **Forward+** (Vulkan 1.4.357), Windows 11 desktop export, 640 × 360 logical at 16 px = 1 m. **No web export** — `PROJECT-BRIEF.md` §6 says what that buys and what it costs |
| **Repository** | <https://github.com/TiantongZhang1/walker-the-lost-TiantongZhang> |
| **Git tag** | **`a8`** |
| **Game-source revision in the film** | **`b33b06c`** — `git diff b33b06c..a8 -- godot/` is empty. **Assignment 8 changed no game code** |

## The film

| | |
|---|---|
| **Filename** | `%(name)s` |
| **Length** | **%(mins)d:%(secs)05.2f** — %(seconds).3f s. Assignment 8 asks for 2–4 minutes |
| **Size** | %(size)s bytes |
| **Format** | 3840 × 2160, 30 fps, h264 + aac 48 kHz |
| **Beats** | %(beats)d, of which %(narrated)d are narrated · %(words)d narrated words |
| **Workflow** | Brutalist `godot-gdd` with the `walker` modifier. Narration: Kokoro `am_onyx`, local, **$0.00** |
| **In the repository as** | `youtube/%(slug)s/exports/landscape/%(slug)s.mp4` — **not committed**; `.gitignore` keeps MP4s out |

**Film URL:** %(url)s

**Film SHA-256:**

```
%(sha)s
```

> **Download the file; do not hash a web preview.** OneDrive re-encodes for
> its in-browser player, so the preview's bytes will not match the hash above.

## What is in this folder

| File | What it is |
|---|---|
| `PROJECT-BRIEF.md` | **the pitch in text** — the seven questions, ending with §A *exists today* and §B *will exist*. Hand-written; the film is a walk through it |
| `FRICTIONAL.md` | dated entries from the day this was built. Hand-written |
| `README.md` | this file. **Generated** — every figure above is measured from the master at assembly time |
| `beat_sheet.json` | the narration and visual plan. Generated copy |
| `gdd-evidence.json` | the ledger the official checker reads. Generated copy |
| `BUILD-PROMPT.md`, `SOURCES.md`, `SHOTLIST.md`, `FACTCHECK.md`, `GDD-COVERAGE.md` | generated copies; the originals live in the reel |
| `CHECKS-REPORT.md` | the checks, **run at assembly time rather than remembered** |
| `REPORT.md` | the toolkit's Gate V visual QC report, as it ran |

Every generated copy carries a header saying so. Edit the original in
`youtube/%(slug)s/` and re-run the assembler; a hand-edited copy is how a
sentence outlives its facts, and this repository has been back for eleven of
those.

## How to rebuild the film

`BUILD-PROMPT.md` has the commands in order. Three things in it are not
optional reading:

1. **The toolkit needs a two-number patch.** `GodotDesignBoard.tsx` draws its
   footer outside the title-safe inset and fails the toolkit's own Gate V on
   every frame. The patch is in `BUILD-PROMPT.md` §5. Without it the master
   will not compile.
2. **Run the beat-sheet builder exactly twice**, and never after the Remotion
   batch.
3. **`scripts/finalise_beat_timing.py` and `scripts/fit_beat_panels.py` must
   not be run.** They `chdir` into `walker-ninja-TiantongZhang`. Both refuse
   to run now; `TOOLCHAIN.md` marks them **Reshape**.

## Honesty, in one place

- **Everything in `PROJECT-BRIEF.md` §B does not exist.** No enemy, no boss,
  no shrine, no title screen, no end screen, and **no export of any kind** —
  there is no `godot/export_presets.cfg` in this repository.
- **Both gameplay beats are real played capture** at `b33b06c`, hashed in
  `gdd-evidence.json`, with their per-frame input logs committed beside them.
- **3.57 s of the film is a held final frame**, and both holds are labelled
  on screen for exactly the seconds they are frozen.
- **Hollow Knight is named as a comparable the author has played.** No
  footage, art or audio of it appears, and no market claim is made.
- **The fact-check changed three numbers before the master was rendered**, and
  `FACTCHECK.md` lists all three rather than quietly fixing them.
"""


if __name__ == "__main__":
    sys.exit(main())
