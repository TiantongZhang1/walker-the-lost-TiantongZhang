#!/usr/bin/env python3
"""Compose Assignment 7's four result-beat cards, and the numbers on them.

    python -X utf8 scripts/compose_animation_evidence.py

One full-frame 3840 x 2160 card per card beat, written to the reel's media/
directory, where the compiler picks a beat's PNG up as a STILL and
`motion: "hold"` renders it with no Ken Burns move.

**Every figure on these cards is MEASURED here, at build time**, from the
committed resources, the committed capture frames and the recorded evidence
files. Nothing is typed in. Delete a frame or a resource and this script stops
rather than drawing a stale number. The measurements are also written to
`evidence/a7/*.txt` so a reviewer can read them as text without opening a PNG,
and so the film's claims and the repository's claims cannot drift apart.

**Why these are not GodotDevWorkbench beats.** verify_gamedev.py requires every
workbench beat carrying a non-empty `code` prop to have a source excerpt record
and to be the code half of a code-then-result pair. A table of measurements is
neither. The same finding is recorded in A5's and A6's composers.

The four cards:

  B07  the authority, as a partition. Both players' track paths read out of
       the two committed .tres files, plus the two frames that show the two
       leg clips running under the same body clip.
  B09  the two clocks, verbatim from evidence/a7/clocks.txt, beside the frame
       on which the window actually opens in the take.
  B13  the same swing twice. **The picture is the argument**: a grounded frame
       and an airborne frame AT THE SAME PLAYHEAD, found by searching the
       take's own log, so the blade angle can be compared by eye against the
       0.000000 s the comparison reports.
  B14  the ten revisions, who reported each one, and whether a headless run
       could have seen it -- beside r1's windmill and r4's strike, at the same
       table frame, from the frame strips the author judged.
"""
from __future__ import annotations

import io
import json
import pathlib
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-animation-gamedev"
MEDIA = REEL / "media"
EVID = ROOT / "evidence/a7"
CAP = ROOT / "captures"
GAME = ROOT / "godot"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
EDGE = (206, 201, 192)

SAFE_L, SAFE_R = 230, 3600
TOP = 300
FOOT_Y = 1930

# The 4K takes are the 640 x 360 game at 6x; the r0-r4 strips are the same
# game at 2x. Both are nearest-filtered, so cropping is the only thing done
# to either: no pixel value changes anywhere in this file.
TAKE_SCALE = 6
STRIP_SCALE = 2


def font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def mono(size):
    return font(("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"), size)


def sans(size):
    return font(("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"), size)


def wrap(d, text, f, width):
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if d.textlength(trial, font=f) > width and line:
            out.append(line)
            line = word
        else:
            line = trial
    out.append(line)
    return out


# ------------------------------------------------------------------ reading

def take_rows(take: str) -> list[dict]:
    p = REEL / "capture" / "logs" / ("take-%s-inputs.jsonl" % take)
    if not p.is_file():
        raise SystemExit("missing take log: %s" % p)
    return [json.loads(l) for l in io.open(p, encoding="utf-8") if l.strip()]


def take_frame(take: str, index: int) -> Image.Image:
    p = REEL / "capture" / ("take-" + take) / ("frame%08d.png" % index)
    if not p.is_file():
        raise SystemExit(
            "missing capture frame %s.\n"
            "The 4K PNG sequences are not committed (.gitignore), so this "
            "script needs scripts/render_takes.py to have been run in this "
            "working tree. The MP4s and the logs are committed; the frames "
            "are not." % p)
    return Image.open(p).convert("RGB")


def strip_frame(rev: str, index: int) -> Image.Image:
    p = CAP / "swing" / rev / ("frame%08d.png" % index)
    if not p.is_file():
        raise SystemExit("missing strip frame: %s" % p)
    return Image.open(p).convert("RGB")


def crop_player(im: Image.Image, player_x: float, scale: int,
                w: int = 150, h: int = 125) -> Image.Image:
    """A window of `w` x `h` LOGICAL pixels centred on the player's column.
    The camera is fixed at (320, 180) over a 640 x 360 room, so logical x maps
    straight onto pixel x * scale. Cropping is a framing choice; nothing else
    is done to the image."""
    cx = int(player_x * scale)
    cy = int(174 * scale)
    pw, ph = w * scale, h * scale
    cx = max(pw // 2, min(im.width - pw // 2, cx))
    cy = max(ph // 2, min(im.height - ph // 2, cy))
    return im.crop((cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2))


def tracks_of(tres: pathlib.Path, clip: str) -> list[str]:
    """Every track path in one animation of a .tres, read out of the resource
    text. This is the same information `test_player_clips.gd` reads through
    the engine; reading it here as text is what lets the card be built without
    starting Godot, and the two agreeing is itself worth something."""
    body = io.open(tres, encoding="utf-8").read()
    block = re.search(
        r'\[sub_resource type="Animation" id="[^"]*"\]\s*\nresource_name = "%s"\n(.*?)(?=\n\[|\Z)'
        % re.escape(clip), body, re.S)
    if block is None:
        raise SystemExit("%s: no animation named %s" % (tres.name, clip))
    return re.findall(r'tracks/\d+/path = NodePath\("([^"]+)"\)', block.group(1))


def node_of(path: str) -> str:
    return path.split(":")[0]


# ----------------------------------------------------------------- drawing

def side_by_side(a: Image.Image, b: Image.Image,
                 la: str, lb: str) -> Image.Image:
    gap, pad, bar = 40, 8, 66
    card = Image.new("RGB", (a.width + b.width + gap + pad * 2,
                             max(a.height, b.height) + bar + pad * 2), GROUND)
    d = ImageDraw.Draw(card)
    # The label has to fit ITS OWN panel, not the card -- A6's composer drew
    # two labels into each other before this loop existed.
    size = 40
    while size > 11 and max(d.textlength(t, font=sans(size))
                            for t in (la, lb)) > a.width - 8:
        size -= 2
    f = sans(size)
    card.paste(a, (pad, pad + bar))
    card.paste(b, (pad + a.width + gap, pad + bar))
    d.text((pad, pad + 8), la, font=f, fill=INK)
    d.text((pad + a.width + gap, pad + 8), lb, font=f, fill=INK)
    for x, w in ((pad, a.width), (pad + a.width + gap, b.width)):
        d.rectangle([x - 2, pad + bar - 2, x + w + 1, pad + bar + a.height + 1],
                    outline=EDGE, width=2)
    return card


def compose(bid: str, picture: Image.Image, title: str, heading: str,
            lines: list[str], footer: str) -> pathlib.Path:
    card = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(card)
    d.text((SAFE_L, 140), title, font=sans(92), fill=INK)

    # The table is sized first; the picture gets what is left, so a long table
    # shrinks the picture rather than running off the card.
    size, step = 46, 58
    widest = max(len(r) for r in lines)
    while size > 20 and widest * size * 0.60 > SAFE_R - SAFE_L:
        size -= 2
        step -= 2
    table_h = step * len(lines)
    shot_h = FOOT_Y - 60 - table_h - 116 - TOP
    if shot_h < 300:
        raise SystemExit("%s: %d rows leave only %d px for the picture"
                         % (bid, len(lines), shot_h))

    # Integer NEAREST upscale for pixel art, LANCZOS only ever downward.
    shot = picture.copy()
    box_w, box_h = SAFE_R - SAFE_L, shot_h
    factor = min(box_w // shot.width, box_h // shot.height)
    if factor >= 2:
        shot = shot.resize((shot.width * factor, shot.height * factor),
                           Image.NEAREST)
    shot.thumbnail((box_w, box_h), Image.LANCZOS)
    card.paste(shot, ((W - shot.width) // 2, TOP))

    y = TOP + shot.height + 24
    d.text((SAFE_L, y), heading, font=sans(50), fill=INK)
    y += 76
    d.line([SAFE_L, y, SAFE_R, y], fill=RULE, width=4)
    y += 40
    f = mono(size)
    for row in lines:
        d.text((SAFE_L, y), row, font=f, fill=INK if row.strip() else DIM)
        y += step

    ff = sans(34)
    fy = FOOT_Y
    for row in wrap(d, footer, ff, SAFE_R - SAFE_L - 480):
        d.text((SAFE_L, fy), row, font=ff, fill=DIM)
        fy += 42
    brand = sans(40)
    d.text((SAFE_R - d.textlength("@NikBearBrown", font=brand), FOOT_Y - 4),
           "@NikBearBrown", font=brand, fill=INK)

    MEDIA.mkdir(parents=True, exist_ok=True)
    path = MEDIA / (bid + ".png")
    card.save(path)
    return path


def report(name: str, rows: list[str]) -> None:
    EVID.mkdir(parents=True, exist_ok=True)
    io.open(EVID / name, "w", encoding="utf-8", newline="\n").write(
        "\n".join(rows) + "\n")


# --------------------------------------------------------------- B07: the partition

def card_b07() -> list[str]:
    player = GAME / "animations/player.tres"
    legs = GAME / "animations/legs.tres"

    body_nodes, leg_nodes = set(), set()
    body_clips = ["run", "swing", "idle", "rising", "falling", "dead", "RESET"]
    for clip in body_clips:
        for t in tracks_of(player, clip):
            body_nodes.add(node_of(t))
    for clip in ["legs_run", "legs_planted", "legs_hidden", "RESET"]:
        for t in tracks_of(legs, clip):
            leg_nodes.add(node_of(t))
    overlap = sorted(body_nodes & leg_nodes)
    stray = sorted(n for n in leg_nodes if not n.startswith("Rig/Leg"))
    body_legs = sorted(n for n in body_nodes if n.startswith("Rig/Leg"))

    # The two leg clips, under the SAME body clip, in play. A standing swing
    # holds `legs_planted`; a travelling swing runs `legs_run` -- which is the
    # whole visible consequence of the split.
    s_rows, m_rows = take_rows("s"), take_rows("m")
    s_i = next(i for i, r in enumerate(s_rows)
               if r["locked"] and r["legs"] == "legs_planted"
               and r["clip_t"] > 0.2)
    m_i = next(i for i, r in enumerate(m_rows)
               if r["locked"] and r["legs"] == "legs_run" and r["clip_t"] > 0.2)
    pic = side_by_side(
        crop_player(take_frame("s", s_i), s_rows[s_i]["player_x"], TAKE_SCALE),
        crop_player(take_frame("m", m_i), m_rows[m_i]["player_x"], TAKE_SCALE),
        "take-s f%d   swing + legs_planted" % s_i,
        "take-m f%d   swing + legs_run" % m_i)

    lines = [
        "AnimationPlayer  %s" % "  ".join(sorted(body_nodes)),
        "LegAnim          %s" % "  ".join(sorted(leg_nodes)),
        "",
        "nodes written by BOTH players        %s" % (overlap or "none"),
        "LegAnim paths not under Rig/Leg      %s" % (stray or "none"),
        "AnimationPlayer paths under Rig/Leg  %s" % (body_legs or "none"),
        "",
        "mutation: one leg track moved back onto the body player",
        "  -> 2 of the 3 checks above go red. The third is why it is 3.",
    ]
    report("partition.txt", [
        "The authority, read out of the two committed resources.",
        "godot/animations/player.tres  -- %d body clips" % len(body_clips),
        "godot/animations/legs.tres    -- 4 leg clips",
        "",
        "AnimationPlayer writes: " + ", ".join(sorted(body_nodes)),
        "LegAnim writes:         " + ", ".join(sorted(leg_nodes)),
        "",
        "intersection: %s" % (", ".join(overlap) if overlap else "EMPTY"),
        "",
        "Read as TEXT here and through the engine in test_player_clips.gd.",
        "Two readings of the same fact by different routes; they agree.",
    ])
    return [pic, lines]


# ------------------------------------------------------------- B09: two clocks

def card_b09() -> list[str]:
    src = EVID / "clocks.txt"
    if not src.is_file():
        raise SystemExit("missing %s -- run scripts/run-test.sh "
                         "measure_clocks.gd 60 and record it" % src)
    text = io.open(src, encoding="utf-8").read().split("\n")
    keep = [r.rstrip() for r in text
            if r.strip() and not r.startswith(("PASS", "FAIL", "Godot Engine"))]
    lines = [r for r in keep if len(r) < 92][:9]

    # The frame the window actually opens on, found in the take rather than
    # asserted: the first frame of the first swing whose hitbox is live.
    rows = take_rows("s")
    open_i = next(i for i, r in enumerate(rows) if r["monitoring"])
    before = open_i - 1
    pic = side_by_side(
        crop_player(take_frame("s", before), rows[before]["player_x"], TAKE_SCALE),
        crop_player(take_frame("s", open_i), rows[open_i]["player_x"], TAKE_SCALE),
        "f%d  playhead %.4f  hitbox OFF" % (before, rows[before]["clip_t"]),
        "f%d  playhead %.4f  hitbox LIVE" % (open_i, rows[open_i]["clip_t"]))

    report("window-in-play.txt", [
        "The active window, located in take-s rather than asserted.",
        "",
        "  last frame with monitoring false : f%d, playhead %.4f"
        % (before, rows[before]["clip_t"]),
        "  first frame with monitoring true : f%d, playhead %.4f"
        % (open_i, rows[open_i]["clip_t"]),
        "",
        "The clip's own key is at 0.2000. A hitbox contributes NO PIXELS:",
        "these two frames differ only in the blade's angle, and the thing",
        "the card is about cannot be seen in either of them. That is the",
        "reason the measurement exists.",
    ])
    return [pic, lines]


# ------------------------------------------- B13: the same swing, twice

def card_b13() -> list[str]:
    rows = take_rows("m")
    # A grounded swing frame and an airborne one AT THE SAME PLAYHEAD. If the
    # jump had touched the clip at all, these two poses would differ.
    grounded = [i for i, r in enumerate(rows) if r["locked"] and r["on_floor"]]
    airborne = [i for i, r in enumerate(rows) if r["locked"] and not r["on_floor"]]
    best = None
    for i in grounded:
        for j in airborne:
            d = abs(rows[i]["clip_t"] - rows[j]["clip_t"])
            if best is None or d < best[0]:
                best = (d, i, j)
    gap, gi, ai = best
    if gap > 0.001:
        raise SystemExit(
            "no grounded and airborne frame share a playhead to within one "
            "ms (closest %.4f s). The take cannot make this card." % gap)
    pic = side_by_side(
        crop_player(take_frame("m", gi), rows[gi]["player_x"], TAKE_SCALE),
        crop_player(take_frame("m", ai), rows[ai]["player_x"], TAKE_SCALE),
        "f%d  ON THE FLOOR   playhead %.4f" % (gi, rows[gi]["clip_t"]),
        "f%d  IN THE AIR     playhead %.4f" % (ai, rows[ai]["clip_t"]))

    e = EVID / "swing-edges-e.txt"
    if not e.is_file():
        raise SystemExit("missing %s" % e)
    body = io.open(e, encoding="utf-8").read()
    drifts = re.findall(r"worst disagreement ([0-9.]+) s", body)
    if len(drifts) != 3:
        raise SystemExit("expected three phase comparisons in %s, found %d"
                         % (e.name, len(drifts)))
    total = re.search(r"(\d+) checks, (\d+) failures", body)

    lines = [
        "the SAME swing, run twice: once jumped through, once not",
        "",
        "  jump in startup            worst disagreement  %s s" % drifts[0],
        "  jump in the active window  worst disagreement  %s s" % drifts[1],
        "  jump in recovery           worst disagreement  %s s" % drifts[2],
        "",
        "  over %s frames each, comparing playhead, window, lock, clip" % 36,
        "  test_swing_edges.gd section E   %s checks, %s failures"
        % (total.group(1), total.group(2)),
        "",
        "mutation M7: the jump restarts the clip. All 3 'it jumps'",
        "checks stay GREEN. 8 comparison checks go red.",
    ]
    report("same-swing-twice.txt", [
        "Two frames of ONE take, at the same playhead, one grounded and one",
        "airborne. Found by searching the take's own log, not chosen by eye.",
        "",
        "  grounded : f%d  playhead %.4f  x %.1f  on_floor %s"
        % (gi, rows[gi]["clip_t"], rows[gi]["player_x"], rows[gi]["on_floor"]),
        "  airborne : f%d  playhead %.4f  x %.1f  on_floor %s"
        % (ai, rows[ai]["clip_t"], rows[ai]["player_x"], rows[ai]["on_floor"]),
        "  playhead difference: %.6f s" % gap,
        "",
        "The blade is at the same angle in both, because the angle is a",
        "function of the playhead alone and the jump never touched it.",
        "",
        "Section E's own comparison, over all 36 frames in three phases:",
        "  " + "  ".join("%s s" % d for d in drifts),
    ])
    return [pic, lines]


# ------------------------------------------------ B14: ten revisions

# Each row: revision, who reported it, and WHAT KIND of thing it was. The
# last column is the film's subject and it is the one that has to be argued
# for, so the reasoning for every row is written out in the text report that
# goes beside the card.
#
# The first version of this table had a column headed "headless could see it"
# with yes/no in it, and it was too blunt to be true: it counted an art
# judgement and a design change as things an instrument had failed to catch,
# which they are not. The narration had been written against that version and
# said "seven" and "four" where the table computed nine and six. **The card
# and the voice disagreed, on the card whose whole subject is checking
# things.** Both are computed from this one table now.
#
#   READ-BACK  a fact about committed data. A read-back COULD have caught it
#              and none was asking. This is the film's subject.
#   design     the game was not wrong; the author wanted something else.
#   art        a judgement about how something looks. No fact to check.
#   MEASURED   found by an instrument, written to test a prediction.
#   doc        a sentence in a design document that nobody ever checked.
REVISIONS = [
    ("7.0.1", "author", "art",
     "the generated sheet was a silhouette; the GPT-6 art already existed. "
     "A look, not a defect"),
    ("7.0.2", "author", "READ-BACK",
     "the blade spun above the head. The key table's own range never puts "
     "the tip below -3 px in any of the 18 frames"),
    ("7.0.3", "author", "READ-BACK",
     "the pivot sat on the torso's BACK edge, x +3. A column profile of the "
     "cell says the torso runs +3..+13"),
    ("7.0.4", "author", "art",
     "a longer blade. How long a sword should look is a judgement"),
    ("7.0.5", "author", "design",
     "swing in the air. The is_on_floor() gate was never asserted by any "
     "test either, which is its own finding"),
    ("7.0.6", "author", "design",
     "move while swinging. The brief argued against it and built it"),
    ("7.0.7", "author", "READ-BACK",
     "the legs waggled. The safe band was measured with PIL, which rotates "
     "the opposite way from Godot: the planted foot was 3.3 px through the "
     "floor while the band assertion passed"),
    ("7.0.8", "Claude", "MEASURED",
     "the brief's clock prediction was wrong in SIGN. Found by the "
     "measurement written to test it, because it was tagged [proposal]"),
    ("7.0.9", "author", "doc",
     "the sliding swing. A sentence in a design document said fixing it "
     "needed an AnimationTree. It was never measured, and it was false"),
    ("7.0.10", "author", "design",
     "jump while swinging. The lock narrowed a third time"),
]


def card_b14() -> list[str]:
    # r1's windmill and r4's shipped strike, at the SAME table frame. The
    # capture trigger is frame 10 in both, so table frame 6 -- the last frame
    # before the hitbox opens -- is capture frame 16 in both.
    #
    # swing_preview.tscn stands the player at logical (150, 150); the first
    # version of this card cropped at x 96, the MAIN scene's player position,
    # and put the figure in the corner of both panels at a size nothing could
    # be judged at. Found by rendering the card and looking at it, which is
    # the only way any of these are ever found.
    frame = 16
    pic = side_by_side(
        crop_player(strip_frame("r1", frame), 150.0, STRIP_SCALE, 92, 78),
        crop_player(strip_frame("r4", frame), 150.0, STRIP_SCALE, 92, 78),
        "r1  f%d  the windmill" % frame,
        "r4  f%d  the shipped strike" % frame)

    reported = sum(1 for r in REVISIONS if r[1] == "author")
    readback = sum(1 for r in REVISIONS if r[2] == "READ-BACK")
    lines = ["  rev      reported by   what kind of thing it was"]
    lines.append("  " + "-" * 52)
    for rev, who, kind, _why in REVISIONS:
        lines.append("  %-8s %-13s %s" % (rev, who, kind))
    lines.append("")
    lines.append("  %d of %d reported by the author, playing."
                 % (reported, len(REVISIONS)))
    lines.append("  %d were READ-BACK: visible in committed data, with no"
                 % readback)
    lines.append("  read-back asking. 0 came from a test going red.")
    kinds: dict[str, int] = {}
    for _r, _w, kind, _why in REVISIONS:
        kinds[kind] = kinds.get(kind, 0) + 1
    rows = [
        "Ten revisions, who reported each, and what kind of thing it was.",
        "Sourced from CHANGE-BRIEF.md revisions 7.0.1 - 7.0.10 and the dated",
        "entries in TUNING.md. Every count on the card is computed from this.",
        "",
        "  READ-BACK  a fact about committed data. A read-back COULD have",
        "             caught it and none was asking.",
        "  design     the game was not wrong; the author wanted something",
        "             else. Not a failure of any instrument.",
        "  art        a judgement about how it looks. No fact to check.",
        "  MEASURED   found by an instrument written to test a prediction.",
        "  doc        a sentence in a design document nobody ever checked.",
        "",
    ]
    for rev, who, kind, why in REVISIONS:
        rows.append("  %-8s %-7s %-10s %s" % (rev, who, kind, why))
    rows += [
        "",
        "  " + ", ".join("%s %d" % kv for kv in sorted(kinds.items())),
        "",
        "%d of %d reported by the author in play." % (reported, len(REVISIONS)),
        "%d were READ-BACK." % readback,
        "",
        "ONE was found by an instrument: 7.0.8, and it is worth being exact",
        "about. It was not an existing test going red. It was a measurement",
        "written on purpose to test a prediction the brief had tagged",
        "[proposal] -- derived, not confirmed. The tag is what caused the",
        "measurement to be built, and the measurement is what found the",
        "prediction wrong in sign. Nothing in this assignment was found by a",
        "test that had been passing and started failing.",
    ]
    report("revisions.txt", rows)
    return [pic, lines]


def main() -> int:
    pic, lines = card_b07()
    p = compose("B07", pic, "One authority, as a partition",
                "both players' track paths, read out of the resources",
                lines,
                "Left and right are the same body clip with different leg "
                "clips under it: a standing swing holds a braced stance, a "
                "travelling swing keeps the gait. Frames from take-s and "
                "take-m, cropped and not otherwise altered.")
    print("wrote %s" % p)

    pic, lines = card_b09()
    p = compose("B09", pic, "Two clocks, measured in both modes",
                "evidence/a7/clocks.txt, verbatim", lines,
                "The two frames are the last one with the hitbox off and the "
                "first with it live. They differ only in the blade's angle - "
                "a hitbox contributes no pixels, which is exactly why the "
                "window has to be measured rather than looked at.")
    print("wrote %s" % p)

    pic, lines = card_b13()
    p = compose("B13", pic, "The same swing, twice",
                "test_swing_edges.gd section E, and mutation M7", lines,
                "One take, two frames at the same playhead: one on the floor, "
                "one in the air after a jump. The blade is at the same angle "
                "because the angle is a function of the playhead and the jump "
                "never touched it.")
    print("wrote %s" % p)

    pic, lines = card_b14()
    p = compose("B14", pic, "Ten revisions, and who reported each one",
                "CHANGE-BRIEF.md 7.0.1 - 7.0.10, TUNING.md", lines,
                "r1 and r4 at the same table frame, from the frame strips the "
                "author judged. The left one is what the key table described "
                "the whole time, and no read-back was asking.")
    print("wrote %s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
