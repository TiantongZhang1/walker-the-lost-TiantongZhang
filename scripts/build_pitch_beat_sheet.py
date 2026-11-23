#!/usr/bin/env python3
"""Build Assignment 8's pitch reel beat sheet from pitch/PROJECT-BRIEF.md.

    python -X utf8 scripts/build_pitch_beat_sheet.py      # pass 1, before TTS
    python -X utf8 scripts/build_pitch_beat_sheet.py      # pass 2, after TTS

Run it TWICE and not a third time, for the same reason Assignment 7's builder
says so: cue positions below are written as FRACTIONS of their beat, and the
second pass turns them into seconds against the measured narration. A third
pass after `build_media_clips.py` would rewrite a duration by a hundredth of a
second and the beat would silently lose its Remotion stamp.

**Every excerpt on screen is read out of the brief at build time**, by line
number, and asserted against the ledger's copy. Nothing is typed twice. If the
brief is edited so that a range no longer starts where it did, this script
stops rather than drawing a stale quotation - which is the failure
`tools/build_anim_strips.py` shipped in Assignment 7 and the fifth hard-coded
sentence this repository has had to go back for.

The document is `pitch/PROJECT-BRIEF.md`, not `the-lost-gdd/GDD.md`. The GDD
describes the whole four-floor game; the brief describes the project being
pitched, and the pitch film is a walk through the brief. `SOURCES.md` says so
where a reviewer will look for it.
"""
from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRIEF = ROOT / "pitch/PROJECT-BRIEF.md"
SLUG = "claude-liam-walker-the-lost-pitch-gdd"
REEL = ROOT / "youtube" / SLUG
FPS = 60

# Measured from Assignment 6's finished sheet: 2168 narrated words across
# 613.7 s of measured Kokoro am_onyx. Used only for the first pass's estimates,
# which the second pass replaces with the real thing.
WORDS_PER_SECOND = 3.533

BRAND = "@HumanitariansAI"
VOICE = "am_onyx"


def excerpt(start: int, end: int) -> str:
    lines = BRIEF.read_text(encoding="utf-8").splitlines()
    if not 1 <= start <= end <= len(lines):
        sys.exit("excerpt range %d-%d is outside %s" % (start, end, BRIEF.name))
    return "\n".join(lines[start - 1:end])


def headings() -> list[str]:
    return [ln[3:].strip() for ln in BRIEF.read_text(encoding="utf-8").splitlines()
            if ln.startswith("## ")]


# --------------------------------------------------------------------------
# The excerpt ranges. Line numbers, never text - the text is read above.
# --------------------------------------------------------------------------
EXCERPTS = {
    "B02": (20, 21),
    "B03": (65, 67),
    "B05": (117, 119),
    "B07": (288, 288),
    "B08": (164, 166),
    "B09": (179, 179),
    "B10": (255, 256),
}


def board(title, section, lines, source, status, visual_label, layout, cards, cues):
    """A GodotDesignBoard beat's props. `cues` are FRACTIONS of the beat."""
    return {
        "title": title,
        "section": section,
        "excerpt": excerpt(*lines),
        "source": source,
        "status": status,
        "visualLabel": visual_label,
        "layout": layout,
        "cards": [{"label": a, "text": b} for a, b in cards],
        "cues": [{"at": f, "card": i} for f, i in cues],
        "durationSeconds": 20,
    }


BEATS: list[dict] = []


def add(beat_id, act, role_note, narration, pattern, props,
        design_status=None, shot_extra=None, audio_policy=None,
        lead_silence_s=None):
    beat = {
        "beat_id": beat_id,
        "act": act,
        "role_note": role_note,
        "narration_text": " ".join(narration.split()),
        "voice": VOICE,
        "engine": "kokoro",
        "estimated_duration_s": round(
            len(narration.split()) / WORDS_PER_SECOND, 2),
    }
    if lead_silence_s is not None:
        beat["lead_silence_s"] = lead_silence_s
    if design_status:
        beat["design_status"] = design_status
    shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "card-reveal-with-highlight"}
    if pattern:
        shot["remotion"] = {"props": props, "pattern": pattern}
    if shot_extra:
        shot.update(shot_extra)
    beat["shot"] = shot
    if audio_policy:
        beat["audio_policy"] = audio_policy
    BEATS.append(beat)


# --------------------------------------------------------------------------
# B00 — the ask
# --------------------------------------------------------------------------
add("B00", "ASK",
    "COLD OPEN. Claude composer, explicitly a reconstruction. The ask is the "
    "real one: turn the project brief into a pitch film. Narration is first "
    "person - this film speaks as Tiantong Zhang, which Assignment 8 requires.",
    """
    I am Tiantong Zhang. This is a pitch, not a build - most of what I describe
    does not exist. I have spent three assignments on one character in one room.
    I asked Claude to read my project brief and build this film.
    """,
    "ClaudeComposerAsk", {
        "topic": "CSYE 7270 · FINAL PROJECT PITCH",
        "segment": "The Lost: Floor One",
        "greeting": "Tiantong Zhang",
        "command": "Please use Walker to convert my game design document about "
                   "The Lost - a 2D side-view dungeon crawler where you cure "
                   "the boss instead of killing them - into a pitch film.",
        "runningText": "reading pitch/PROJECT-BRIEF.md · mapping 9 sections · "
                       "hashing capture evidence...",
        "output": [
            "9 sections found - 9 covered, 0 excluded",
            "7 exact excerpts · 4 evidence files · 2 real captures at b33b06c",
        ],
        "folderLabel": BRAND,
        "modelLabel": "Opus 5",
        "effortLabel": "High",
        "durationSeconds": 20,
    })

# --------------------------------------------------------------------------
# B01 — BLUF, with the working correction
# --------------------------------------------------------------------------
add("B01", "BLUF",
    "EXECUTIVE SUMMARY. BrutalistHesitantWriter with a working single-word "
    "correction: 'finished' -> 'proposed'. The misconception this film has to "
    "kill in ten seconds is that any of the final project is built.",
    """
    Here is the honest shape of it. One room exists, tested to an unusual
    depth. The game around it is proposed. The film labels which is which on
    every card, because a pitch that fabricates progress has already failed.
    """,
    "BrutalistHesitantWriter", {
        # TWO lines, and the length is measured rather than chosen. A frame
        # at 10.5 s of the four-line version was still typing line two: this
        # component writes at about 138 ms per character event here, the
        # correction costs about sixteen events of its own, and the beat is
        # 12.0 s because the narration is. Four lines meant the last two were
        # never shown to anybody. **That is a content fault Gate V cannot see
        # and a single frame can**, which is the fourth time in this
        # repository that looking has caught what checking could not.
        "text": "The Lost is a finished game.\n"
                "One room of it exists.",
        # Two numbers that are layout constraints, not style, and both were
        # measured off a rendered frame rather than guessed.
        #
        # The component sets `whiteSpace: 'pre'` inside a `maxWidth: 86%`
        # box, so a long line does NOT wrap -- it overflows, symmetrically,
        # out of a centred flex column. It also multiplies fontSize by
        # canvas/1920, so 104 renders at 208 px and 38 characters measured
        # 3647 px against a 3456 px safe width. The first fix for this beat
        # raised the type from 84 to clear an underfill MAJOR (43% of safe,
        # floor 55%) and bought an edge-bleed BLOCKER with it; shortening
        # the longest line from 42 characters to 38 was not enough on its
        # own. 96 measures 3366 px wide and 62% of safe: inside both gates
        # with 45 px to spare on each side.
        "triggerWords": "finished",
        "replacementWords": "proposed",
        "fontSize": 96,
        # Gate V samples each beat at 50% and 85% of its length, and a
        # typing animation is half-empty at its own midpoint: at
        # lineSpacing 3.1 the 50% sample measured 46% of the safe area
        # against a 55% floor. `charMs` looks like the fix and is NOT
        # one - 12 and 50 render pixel-identical, so the prop does not
        # reach the component. Taller line spacing does reach it, and
        # it grows the block without widening it, which matters
        # because the width is already near the safe edge.
        "lineSpacing": 4.0,
        # A standing label, present from frame 0. It is what finally
        # cleared the underfill: raising lineSpacing could not, because
        # the 50% sample always shows the same FRACTION of the block
        # however tall the block is, and the arithmetic needs a block
        # taller than the whole safe area to get there. A title is ink
        # that is already on screen while the typing is still half
        # done, and it labels the beat, which the beat wanted anyway.
        "contextTitle": "What exists, and what does not",
        "seed": "walker-the-lost-pitch-2026",
        "ink": "#3D3929",
        "accent": "#D97757",
        "bg": "#FAF9F5",
        "face": "serif",
        "align": "center",
        "brandLabel": BRAND,
        "durationSeconds": 15,
    }, lead_silence_s=0.8)

# --------------------------------------------------------------------------
# B02 — §1 What is it
# --------------------------------------------------------------------------
add("B02", "MECHANISM",
    "Covers brief §1. The one sentence, then the artifact and its form. "
    "Status: PROPOSED - no part of this artifact exists.",
    """
    What is it. The Lost: Floor One - a playable vertical slice of a two-D
    side-view dungeon crawler in which you do not kill the boss, you cure them.
    The artifact is a Windows desktop export plus the tagged repository. One
    executable, title screen to end screen, under ten minutes, no reading. The
    full design has four floors; this is one of them.
    """,
    "GodotDesignBoard",
    board("What is it", "§1 · pitch/PROJECT-BRIEF.md", EXCERPTS["B02"],
          "Exact excerpt, pitch/PROJECT-BRIEF.md lines 20-21 · brief at commit HEAD",
          "PROPOSED · nothing in this artifact exists today",
          "The artifact, and its form",
          "flow",
          [("One executable", "Windows desktop export. Double-click, play."),
           ("Title to end screen", "Under ten minutes. No menu, no tutorial text."),
           ("One floor, one boss", "The GDD's own cut rule: cut floor count, not floor quality."),
           ("Plus the tagged repo", "The test report a stranger can rerun.")],
          [(0.08, 0), (0.34, 1), (0.60, 2), (0.84, 3)]),
    design_status="proposed")

# --------------------------------------------------------------------------
# B03 — §2 Why anyone would care, and the comparable
# --------------------------------------------------------------------------
add("B03", "MECHANISM",
    "Covers brief §2. The unique value, and the one real comparable - Hollow "
    "Knight, a game the author has played. The difference is stated as a "
    "mechanic, not as a feeling, and no market claim is made.",
    """
    Why would anyone care. The game has two progress bars and only one is in
    the interface. The visible one is floors cleared. The invisible one is how
    many people are standing in the room you come home to. The comparable is
    Hollow Knight, which I have played. Dirtmouth fills with people you rescued
    off the critical path; the bosses are the ones you killed. Two systems that
    never touch. In The Lost the boss IS the resident - one system.
    """,
    "GodotDesignBoard",
    board("Why anyone would care", "§2 · The comparable: Hollow Knight",
          EXCERPTS["B03"],
          "Exact excerpt, pitch/PROJECT-BRIEF.md lines 65-67 · comparable named by the author",
          "PROPOSED · comparison, not a market claim",
          "Two systems, or one",
          "cards",
          [("Hollow Knight · rescue", "Dirtmouth fills with NPCs found OFF the critical path."),
           ("Hollow Knight · bosses", "Killed. The infection is cured once, globally, in an ending."),
           ("The Lost", "The boss IS the resident. One system, not two."),
           ("What that buys", "You cannot run the main line and come home to an empty room.")],
          [(0.22, 0), (0.40, 1), (0.62, 2), (0.84, 3)]),
    design_status="comparison")

# --------------------------------------------------------------------------
# B04 — §3 Who opens it. REAL CAPTURED PLAY.
# --------------------------------------------------------------------------
add("B04", "EVIDENCE",
    "Covers brief §3. take-c, PLAYED: held keys through the real input map at "
    "game-source revision b33b06c, nothing teleported, no state written. This "
    "is what a player is actually moving in the first sixty seconds.",
    """
    The target role is gameplay programmer. This is the game today - real
    captured play at revision b three three b zero six c. Held keys, real
    input map, nothing staged.
    """,
    None, None,
    design_status="implemented",
    shot_extra={
        "type": "FOOTAGE", "class": "SHOW", "source": "capture",
        "motion": "gameplay",
        "capture": "take-c",
        "evidence_media": "capture/take-c.mp4",
        "window_s": [0.0, 9.0],
        "show": [
            {"at": "0.05", "event": "the walk, facing right - real input, not a tween"},
            {"at": "0.45", "event": "step dust under the planted foot"},
            {"at": "0.75", "event": "the turn - the same gait, mirrored"},
        ],
    })

# --------------------------------------------------------------------------
# B05 — §4 What it proves
# --------------------------------------------------------------------------
add("B05", "MECHANISM",
    "Covers brief §4. Course skills tied to tags that exist. The honest half "
    "is the second one: what a reviewer could NOT conclude from any of it.",
    """
    What it proves. Four course skills, each with a tag behind it. Shaders at
    a five, particles and their measured cost at a six, animation and state at
    a seven - two clips on one timeline, two animation players asserted as a
    partition in both directions. Underneath it, two hundred and eighty checks
    and seven mutations. What it does not prove matters more: none of it says
    I can write an enemy or ship a build.
    """,
    "GodotDesignBoard",
    board("What it proves", "§4 · evidence that exists today",
          EXCERPTS["B05"],
          "Exact excerpt, pitch/PROJECT-BRIEF.md lines 117-119 · each tag is in this repository",
          "OBSERVED · every row below is at a tag you can clone",
          "Course skills, and the tag behind each",
          "cards",
          [("a5 · shaders", "3 hand-written shaders · 99 checks · 4 deliberate breakages"),
           ("a6 · particles", "3 effects · 249 checks / 301 results · a measured cost table"),
           ("a7 · animation and state", "2 clips, one timeline · 280 checks · 7 mutations"),
           ("What it does NOT prove", "No enemy. No boss. No export. The hitbox has hit nothing.")],
          [(0.18, 0), (0.33, 1), (0.48, 2), (0.80, 3)]),
    design_status="observed")

# --------------------------------------------------------------------------
# B06 — §A Exists today. REAL CAPTURED PLAY of the swing.
# --------------------------------------------------------------------------
add("B06", "EVIDENCE",
    "Covers brief §A. take-s, PLAYED at b33b06c: four swings, the hitbox "
    "window opening four times, every clip exactly 36 physics frames. The "
    "window is real and it is empty - that is the point of showing it.",
    """
    The committing swing, played, four times. Inside it a hitbox window, open
    a hundred and thirty-three milliseconds. Watch what it hits.
    """,
    None, None,
    design_status="implemented",
    shot_extra={
        "type": "FOOTAGE", "class": "SHOW", "source": "capture",
        "motion": "gameplay",
        "capture": "take-s",
        "evidence_media": "capture/take-s.mp4",
        "window_s": [0.0, 5.5],
        "show": [
            {"at": "0.10", "event": "first swing - wind-up, strike, recovery"},
            {"at": "0.50", "event": "the arc passes through empty air"},
            {"at": "0.80", "event": "four swings, every one 36 physics frames"},
        ],
    })

# --------------------------------------------------------------------------
# B07 — §A and §B, the two lists
# --------------------------------------------------------------------------
add("B07", "DESIGN-TELL",
    "Covers brief §A and §B. The exists/will-exist split is the honesty "
    "mechanism of the whole brief, so it gets a beat of its own rather than "
    "being implied by the status labels on the others.",
    """
    Nothing, because there is no enemy in this project and there never has
    been. Which brings me to the two lists the brief ends with - the only
    thing stopping this film from lying. Ten things can be cloned at a tag and
    run, and the eleventh - the design document itself - is in no repository at
    all. Everything the final project adds is unstarted: not the enemy, not the
    boss, not the shrine, not a title screen, no export of any kind. The game
    has never left the editor.
    """,
    "GodotDesignBoard",
    board("Exists today · will exist", "§B · Will exist",
          EXCERPTS["B07"],
          "Exact excerpt, pitch/PROJECT-BRIEF.md line 288 · §A lists 11 rows, each at a tag",
          "PROPOSED · nothing in the right-hand column is started",
          "What the final project adds",
          "cards",
          [("Combat that connects", "Enemy · enemy behaviour · the roll and its i-frames"),
           ("The floor", "Boss in two forms · purification · the key · a chest"),
           ("The frame around it", "Shrine · four outlines · title screen · end screen · transitions"),
           ("And a build", "No export_presets.cfg exists. The game has never left the editor.")],
          [(0.25, 0), (0.45, 1), (0.62, 2), (0.82, 3)]),
    design_status="proposed")

# --------------------------------------------------------------------------
# B08 — §5 In, out, first
# --------------------------------------------------------------------------
add("B08", "DESIGN-TELL",
    "Covers brief §5. In / out / first, separated. The first piece and the "
    "assertion that says it ran are both named, and the assertion is an "
    "existing measurement rather than a new one.",
    """
    What is in, out, and first. Out, deliberately: one level only, no save
    system. First is one thing - an enemy the existing hitbox can hit. And
    here is how anyone knows it ran without watching. Measure clocks already
    pins the frame that window opens on: the one whose playhead reads nought
    point two thousand. The first test asserts the enemy's area entered signal
    fires on that frame. Same number, same file, now with something on the
    other side of it.
    """,
    "GodotDesignBoard",
    board("In · out · first", "§5 · the first piece", EXCERPTS["B08"],
          "Exact excerpt, pitch/PROJECT-BRIEF.md lines 164-166 · the window is measured in evidence/a7/clocks.txt",
          "PROPOSED first piece · OBSERVED measurement it is asserted against",
          "The first thing to make run, and its test",
          "flow",
          [("IN", "One floor · one enemy · the roll · a boss in two forms · the key"),
           ("OUT, deliberately", "One level only. No save system. No web export."),
           ("FIRST", "An enemy the hitbox can hit. Smallest change that is not cosmetic."),
           ("How you know it ran", "area_entered fires on the frame whose playhead reads 0.2000")],
          [(0.10, 0), (0.22, 1), (0.40, 2), (0.66, 3)]),
    design_status="proposed")

# --------------------------------------------------------------------------
# B09 — §6 The risk
# --------------------------------------------------------------------------
add("B09", "DESIGN-TELL",
    "Covers brief §6. One concrete risk specific to this project, with what "
    "would be done about it. The risk is derived from this repository's own "
    "revision history rather than from a generic list.",
    """
    What could sink it. The swing commits - thirty-six physics frames, no
    cancel, no restart, no turn. Every piece of evidence that this feels
    acceptable was gathered in a room with nothing in it. The lock has narrowed
    three times, each time because I played it and said it felt bad with no
    opponent there. Put something in that room that walks behind you, and the
    commitment is either the best thing in the game or the reason nobody
    finishes the fight. The fix would not be a tuning value - sixty checks are
    the sixty-check suite that is my best evidence has that rule written
    through it. So the enemy comes first, while one suite depends on it.
    """,
    "GodotDesignBoard",
    board("What could sink it", "§6 · the risk", EXCERPTS["B09"],
          "Exact excerpt, pitch/PROJECT-BRIEF.md line 179 · revisions 7.0.6, 7.0.9, 7.0.10 in CHANGE-BRIEF.md",
          "PENDING · no evidence either way exists, and none can be gathered in an empty room",
          "Why the risk is real, and what is done about it",
          "cards",
          [("The rule", "swing is 0.600 s, 36 physics frames. No cancel, no restart, no turn."),
           ("Why it is untested", "Every verdict on it was given in a room with no opponent."),
           ("What it costs if wrong", "A state machine change. A 60-check suite has 'cannot turn' written through it."),
           ("The mitigation", "Build the enemy FIRST - judge it while one suite depends on the rule.")],
          [(0.12, 0), (0.33, 1), (0.60, 2), (0.84, 3)]),
    design_status="pending")

# --------------------------------------------------------------------------
# B10 — §7 Why this project
# --------------------------------------------------------------------------
add("B10", "MECHANISM",
    "Covers brief §7. New learning separated from existing skill on show, and "
    "the existing half is backed by tags rather than by assertion.",
    """
    Why this project. A mix, and the halves are not close. Showing off:
    shaders, particles, a state machine, a headless harness - all at a tag,
    all of it repeating what I can already do. Learning: every new thing
    involves a second thing being in the room. And I do not know whether the
    purification beat reads as a reward or an anticlimax. No test can tell me.
    I find out by playing it and writing down what I said.
    """,
    "GodotDesignBoard",
    board("Why this project", "§7 · new learning vs existing skill",
          EXCERPTS["B10"],
          "Exact excerpt, pitch/PROJECT-BRIEF.md lines 255-256",
          "OBSERVED left column · PROPOSED right column · one row is genuinely unknown",
          "Have, learning, and do not know yet",
          "cards",
          [("Have · evidence at a tag", "Shaders a5 · particles a6 · animation and state a7 · the harness"),
           ("Learning · nothing to point at", "Enemy behaviour · a boss · combat that connects · transitions · an export"),
           ("Do not know yet", "Whether purification reads as a reward or as an anticlimax."),
           ("How I will find out", "Build the beat early, play it, write down what I said. No test can do it.")],
          [(0.12, 0), (0.40, 1), (0.68, 2), (0.86, 3)]),
    design_status="proposed")

# --------------------------------------------------------------------------
# B11 — Verdict
# --------------------------------------------------------------------------
add("B11", "VERDICT",
    "Verdict. Recapitulation only - no claim appears here that has not already "
    "been made and labelled. AI organised the sections and ran the checks; the "
    "scope, the comparable and whether this is worth playing are the author's.",
    """
    The verdict on my own pitch. One room exists, tested further than it needs
    to be. One floor is proposed. The risk is a rule I have never tested
    against anything that moves. Claude mapped the sections and ran the checks;
    the scope, and whether it is worth playing, stayed mine.
    """,
    "ClaudeVerdictArtifact", {
        "artifactTitle": "The Lost: Floor One - pitch verdict",
        "artifactHeading": "What is built, what is proposed, and who decided",
        "brandLabel": BRAND,
        "artifactLines": [
            "EXISTS: one room, two clips, a measured hitbox window, 280 checks at a tag",
            "PROPOSED: one floor, one boss, the shrine, a title and end screen, an export",
            "FIRST: an enemy the hitbox can hit, asserted on the frame reading 0.2000",
            "RISK: a 36-frame commitment never tested against anything that moves",
            "Claude mapped sections and ran checks; scope and worth stayed the author's",
        ],
        "durationSeconds": 18,
    })

# --------------------------------------------------------------------------
# B12 — Your turn
# --------------------------------------------------------------------------
add("B12", "YOUR-TURN",
    "HANDOFF. A bounded prompt that revises one design hypothesis and names "
    "its test - which is exactly the gap this film's own §6 is about.",
    """
    Your turn, and it is my own question. Take one rule in your game you
    believe feels good, and paste this: find the design rule I have the most
    evidence for, tell me what conditions that evidence was gathered under,
    and name one it has never been tested in.
    """,
    "ClaudeComposerAsk", {
        "topic": "CSYE 7270 · FINAL PROJECT PITCH",
        "segment": "Your Turn",
        "greeting": "Your turn.",
        "command": "Find the design rule I have the most evidence for. Tell me "
                   "what conditions that evidence was gathered under, and name "
                   "one condition it has never been tested in.",
        "runningText": "reading the brief · reading the suites · listing conditions...",
        "output": [
            "most-asserted rule: the swing cannot turn - in a 60-check suite",
            "every check ran in a room with no opponent",
        ],
        "folderLabel": BRAND,
        "modelLabel": "Opus 5",
        "effortLabel": "High",
        "durationSeconds": 18,
    })

# --------------------------------------------------------------------------
# B13 — the locked outro
# --------------------------------------------------------------------------
add("B13", "OUTRO",
    "OUTRO LAW. ClaudeTitleOutro, locked per OUTRO-LOCK.md: exact title, the "
    "hardcoded handle, no narration over the card. SOURCES.md records that the "
    "handle is a toolkit lock and not a credit claimed by this submission.",
    "",
    "ClaudeTitleOutro", {
        "title": "The Lost: Floor One",
        "slug": SLUG,
        "durationSeconds": 8.0,
    }, audio_policy="silence")


# --------------------------------------------------------------------------
# Passes
# --------------------------------------------------------------------------
def probe(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main() -> int:
    heads = headings()
    if len(heads) != 9:
        sys.exit("expected 9 '## ' sections in the brief, found %d" % len(heads))

    mp3s = {b["beat_id"]: REEL / "mp3" / ("beat-%s.mp3" % b["beat_id"])
            for b in BEATS}
    second = all(p.is_file() for bid, p in mp3s.items()
                 if BEATS[[b["beat_id"] for b in BEATS].index(bid)]
                 .get("audio_policy") != "silence")
    print("pass %d  (%s)" % (2 if second else 1,
                             "measured narration" if second else "estimates"))

    # A rebuilt sheet is a fresh sheet, so every beat loses the
    # `shot.remotion.rendered` stamp the batch wrote and the whole film
    # re-renders. For a two-word correction in two beats that is fifteen
    # minutes of GPU for thirteen identical files. So: carry the stamp over
    # for any beat whose props and narration are byte-identical to the ones
    # that were rendered, and drop it for the rest. A beat that changed
    # CANNOT keep its stamp - that would ship a card that does not match its
    # own sheet, which is the whole failure this film is about.
    old = {}
    sheet_path = REEL / "beat_sheet.json"
    if sheet_path.is_file():
        for beat in json.loads(sheet_path.read_text(encoding="utf-8"))["beats"]:
            old[beat["beat_id"]] = beat

    kept: list[str] = []
    stale: list[str] = []
    total = 0.0
    for beat in BEATS:
        bid = beat["beat_id"]
        if beat.get("audio_policy") == "silence":
            seconds = float(beat["estimated_duration_s"]) or 8.0
            beat["estimated_duration_s"] = seconds
        elif second:
            seconds = probe(mp3s[bid])
            beat["actual_duration_s"] = round(seconds, 3)
            beat["audio_file"] = "mp3/beat-%s.mp3" % bid
        else:
            seconds = float(beat["estimated_duration_s"])
        render = math.ceil(seconds * FPS - 1e-8) / FPS
        beat["render_duration_s"] = render
        total += render

        remotion = beat["shot"].get("remotion")
        if remotion:
            props = remotion["props"]
            props["durationSeconds"] = round(render, 2)
            # Fractions -> seconds, once, on whichever pass is current.
            if "cues" in props:
                props["cues"] = [
                    {"at": round(c["at"] * render, 2) if c["at"] <= 1.0 else c["at"],
                     "card": c["card"]}
                    for c in props["cues"]]
            was = (old.get(bid, {}).get("shot", {}).get("remotion") or {})
            same = (was.get("props") == props
                    and old[bid].get("narration_text") == beat["narration_text"]
                    if bid in old else False)
            if same and was.get("rendered") and (REEL / "media" / ("%s.mp4" % bid)).is_file():
                remotion["rendered"] = was["rendered"]
                kept.append(bid)
            elif was.get("rendered"):
                stale.append(bid)

        window = beat["shot"].get("window_s")
        if window:
            start, stop = (float(v) for v in window)
            take = REEL / "capture" / ("%s.mp4" % beat["shot"]["capture"])
            available = probe(take) - start
            want = min(render, available)
            hold = render - want
            beat["shot"]["window_s"] = [round(start, 3), round(start + want, 3)]
            verdict = ("fits" if hold <= 1.0 / FPS
                       else "HOLD %.2f s - shorten the narration" % hold)
            print("  %s  %s window %.3f-%.3f  beat %.3f s  %s"
                  % (bid, beat["shot"]["capture"], start, start + want,
                     render, verdict))

    sheet = {
        "metadata": {
            "title": "The Lost: Floor One",
            "slug": SLUG,
            "topic": "CSYE 7270 · FINAL PROJECT PITCH",
            "kind": "gdd",
            "playlist": "CSYE 7270",
            "brand": "claude-liam",
            "audience": "a lead engineer, a hiring manager, or a player",
            "register": "Teardown",
            "engine": "kokoro",
            "voice": VOICE,
            "voice_kokoro": VOICE,
            "palette": "claude",
            "style_preset": "claude",
            "ground": "#FAF9F5",
            "aspect_ratio": "16:9",
            "fit": "contain",
            "captions": False,
            "channel_title": BRAND,
            "channel": BRAND,
            "folderLabel": BRAND,
            "persona": "Tiantong Zhang",
            "presenter": "Tiantong Zhang",
            "in_for_bear": False,
            "episode_id": "csye7270-a8-pitch",
            "document": "pitch/PROJECT-BRIEF.md",
            "game_source_revision": "b33b06c",
            "note": (
                "Assignment 8 pitch film. The document walked through is "
                "pitch/PROJECT-BRIEF.md, not the-lost-gdd/GDD.md: the GDD "
                "describes the whole four-floor game, the brief describes the "
                "project being pitched. Narration is first person and speaks "
                "as Tiantong Zhang, per the assignment. The outro card is the "
                "locked ClaudeTitleOutro with its hardcoded handle per "
                "OUTRO-LOCK.md; SOURCES.md records that it is a toolkit lock "
                "and not a credit this submission claims. Captures take-c and "
                "take-s are real played captures at game-source revision "
                "b33b06c, re-used from Assignment 7's reel with their input "
                "logs. No paid API, no upload, no game change."),
            "tags": ["CSYE 7270", "final project", "pitch", "Godot 4",
                     "The Lost", "vertical slice", "Kokoro", "Remotion"],
        },
        "beats": BEATS,
    }
    REEL.mkdir(parents=True, exist_ok=True)
    (REEL / "beat_sheet.json").write_text(
        json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if kept:
        print("  kept render stamps: %s" % " ".join(kept))
    if stale:
        print("  CHANGED, must re-render with --force: %s" % " ".join(stale))
    words = sum(len(b["narration_text"].split()) for b in BEATS)
    print("\n%d beats · %d narrated words · film runs %.2f s (%d:%05.2f)"
          % (len(BEATS), words, total, int(total // 60), total % 60))
    if not 120 <= total <= 240:
        print("WARNING: Assignment 8 asks for 2-4 minutes and this is %.1f s"
              % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
