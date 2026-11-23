# CHECKS-REPORT.md — run at assembly time, not remembered

Written by `scripts/assemble_pitch_folder.py` on 2026-11-23.
Every row below is a live run; the Gate V report is a copy of the
render's own output and sits beside this file as `REPORT.md`.

| Check | Result | Output |
|---|---|---|
| `./art godot-gdd --check` | **PASS** | GDD evidence check PASS: {"sections": 9, "excerpts": 7, "evidence_files": 4} |
| `git diff b33b06c..HEAD -- godot/` | **PASS** | empty - no game code changed by Assignment 8 |
| `tools/check_claude_refs.py` | **PASS** | 61 assertions (26 by line, 35 by name), 0 problem(s) |
| `tools/check_reel_tracked.py` | **PASS** | OK |
