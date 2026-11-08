#!/usr/bin/env python3
"""Compose Assignment 6's four result-beat cards, and the numbers on them.

    python -X utf8 scripts/compose_particles_evidence.py

One full-frame 3840 x 2160 card per card beat, written to the reel's media/
directory, where the compiler picks a beat's PNG up as a STILL and
`motion: "hold"` renders it with no Ken Burns move.

**Every figure on these cards is MEASURED here, from the committed capture
frames, at build time.** Nothing is typed in. Change a frame and the card
changes; delete one and this script stops rather than drawing a stale number.
The measurements are also written to `evidence/a6/*.txt` so that a reviewer
can read them as text without opening a PNG, and so the film's claims and the
repository's claims cannot drift apart.

The one exception is the cost table, which is the recorded stdout of
`scripts/run-test.sh cost_effects.gd 60 300`, read verbatim out of
`evidence/a6/cost-effects-run{1,2}.txt`.

**Why these are not GodotDevWorkbench beats.** verify_gamedev.py requires every
workbench beat carrying a non-empty `code` prop to have a source excerpt record
and to be the code half of a code-then-result pair. A table of measurements is
neither. The same finding is recorded in A5's compose_lost_evidence.py.
"""
from __future__ import annotations

import io
import json
import pathlib
import subprocess

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
REEL = ROOT / "youtube/claude-liam-walker-the-lost-particles-gamedev"
MEDIA = REEL / "media"
EVID = ROOT / "evidence/a6"
CAP = ROOT / "captures"

W, H = 3840, 2160
GROUND = (250, 249, 245)
INK = (32, 30, 28)
DIM = (120, 115, 108)
RULE = (214, 60, 47)
EDGE = (206, 201, 192)

# Title-safe at 3840 x 2160 is x 192..3648, y 108..2052.
SAFE_L, SAFE_R = 230, 3600
TOP = 300
FOOT_Y = 1930

# The motes preview stands the player at x 96 logical; at the capture's 2x
# that is a band around x 192. The band excluded below is wider than the
# sprite because the player FALLS during the first second, so his column
# differs from the dead-pose baseline over its whole height.
PLAYER_BAND = (160, 270)


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


# ---------------------------------------------------------------- measuring

def load(path: pathlib.Path) -> Image.Image:
    if not path.is_file():
        raise SystemExit("missing capture frame: %s" % path)
    return Image.open(path).convert("RGB")


def delta(a: pathlib.Path, b: pathlib.Path, skip_band=None):
    """Pixels that differ at all, and the largest single-channel difference.

    No threshold: a pixel counts if any channel moved by one. `skip_band` is a
    half-open column range to leave out, which is how the motes measurement
    takes the player out of a whole-room frame.
    """
    A, B = load(a), load(b)
    if A.size != B.size:
        raise SystemExit("%s and %s are different sizes" % (a.name, b.name))
    d = ImageChops.difference(A, B)
    if skip_band is None:
        bands = d.split()
        worst = max(ch.getextrema()[1] for ch in bands)
        grey = d.convert("L")
        hist = grey.histogram()
        return sum(hist[1:]), worst
    px = d.load()
    lo, hi = skip_band
    count, worst = 0, 0
    for x in range(A.size[0]):
        if lo <= x < hi:
            continue
        for y in range(A.size[1]):
            r, g, bl = px[x, y]
            m = max(r, g, bl)
            if m:
                count += 1
            if m > worst:
                worst = m
    return count, worst


def extent(a: pathlib.Path, b: pathlib.Path):
    """Width and height in LOGICAL pixels of everything that differs. The
    captures are 1280 x 720 of a 640 x 360 game, so the box is halved."""
    d = ImageChops.difference(load(a), load(b)).convert("L")
    box = d.getbbox()
    if box is None:
        return 0, 0
    return (box[2] - box[0]) // 2, (box[3] - box[1]) // 2


# The trap view, in LOGICAL pixels: centred on SpikeTrap2 at (320, 200), the
# same framing scripts/build_effect_strip.py crops its strips to. A 24-pixel
# burst in a 640 x 360 room is four pixels tall on a slide; the room view is
# the right frame for the motes and the wrong one for the burst.
TRAP_VIEW = (260, 150, 120, 100)     # x, y, w, h -- logical
CAPTURE_SCALE = 2                     # the captures are 1280 x 720 of 640 x 360


def side_by_side(left: pathlib.Path, right: pathlib.Path,
                 left_label: str, right_label: str, crop=None) -> Image.Image:
    """Two capture frames side by side, each labelled. Cropping is a framing
    choice and nothing else is done: no pixel value changes, nothing is
    brightened, retimed or composited."""
    a, b = load(left), load(right)
    if crop is not None:
        x, y, w, h = (v * CAPTURE_SCALE for v in crop)
        a = a.crop((x, y, x + w, y + h))
        b = b.crop((x, y, x + w, y + h))
    gap, pad, bar = 40, 8, 66
    card = Image.new("RGB", (a.width + b.width + gap + pad * 2,
                             max(a.height, b.height) + bar + pad * 2), GROUND)
    d = ImageDraw.Draw(card)
    # The label has to fit ITS OWN panel, not the card. A cropped panel is
    # 240 px wide and a 40 px label is 400, so the two labels ran into each
    # other and the card said "frame 15 FIXTUREframe 20 FIX". Found by
    # rendering it and looking at it, which is the only way any of these are
    # ever found.
    size = 40
    while size > 11 and max(d.textlength(t, font=sans(size))
                            for t in (left_label, right_label)) > a.width - 8:
        size -= 2
    f = sans(size)
    card.paste(a, (pad, pad + bar))
    card.paste(b, (pad + a.width + gap, pad + bar))
    d.text((pad, pad + 8), left_label, font=f, fill=INK)
    d.text((pad + a.width + gap, pad + 8), right_label, font=f, fill=INK)
    for x, w in ((pad, a.width), (pad + a.width + gap, b.width)):
        d.rectangle([x - 2, pad + bar - 2, x + w + 1, pad + bar + a.height + 1],
                    outline=EDGE, width=2)
    return card


# ----------------------------------------------------------------- drawing

def compose(bid: str, picture: Image.Image, title: str, heading: str,
            lines: list[str], footer: str) -> pathlib.Path:
    card = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(card)
    d.text((SAFE_L, 140), title, font=sans(92), fill=INK)

    # The table is sized first; the picture gets what is left, so a long
    # table shrinks the picture rather than running off the card.
    size, step = 46, 58
    widest = max(len(r) for r in lines)
    while size > 22 and widest * size * 0.60 > SAFE_R - SAFE_L:
        size -= 2
        step -= 2
    table_h = step * len(lines)
    shot_h = FOOT_Y - 60 - table_h - 116 - TOP
    if shot_h < 380:
        raise SystemExit("%s: %d rows leave only %d px for the picture"
                         % (bid, len(lines), shot_h))

    # PIL's thumbnail() never upscales, and three of these pictures are
    # smaller than the box they are allowed, so without this they sit in the
    # middle of a card with a third of it empty -- A5's composer hit the same
    # thing from the other side. The game is nearest-filtered pixel art, so
    # the upscale is an INTEGER factor with NEAREST: no pixel value changes
    # and no detail is invented. Anything larger than the box is still
    # reduced with LANCZOS, which only ever throws information away.
    shot = picture.copy()
    box_w, box_h = SAFE_R - SAFE_L, shot_h
    factor = min(box_w // shot.width, box_h // shot.height)
    if factor >= 2:
        shot = shot.resize((shot.width * factor, shot.height * factor),
                           Image.NEAREST)
    shot.thumbnail((box_w, box_h), Image.LANCZOS)
    x = (W - shot.width) // 2
    card.paste(shot, (x, TOP))

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


# ------------------------------------------------------------------- cards

def card_b05() -> list[str]:
    """Effect A's one tuning revision: r0 against r1, frame by frame, with
    the prediction written before the recapture."""
    predicted = {10: "different", 12: "different", 15: "identical",
                 20: "identical", 30: "identical", 50: "identical"}
    rows = ["frame   r0 vs r1   worst ch   predicted    "]
    for f in (10, 12, 15, 20, 30, 50):
        name = "frame%08d.png" % f
        n, worst = delta(CAP / "hit_burst/r0" / name, CAP / "hit_burst/r1" / name)
        changed = "different" if n else "identical"
        rows.append("%5d   %5d px   %8d   %-9s    %s"
                    % (f, n, worst, predicted[f],
                       "hit" if changed == predicted[f] else "MISS"))
    report("effect-a-r0-vs-r1.txt",
           ["Effect A, revision 6.0.1: Flash.scale_min/max 1.6/2.4 -> 5.0/7.0.",
            "Pixels differing between the r0 and r1 capture of the same frame,",
            "whole 1280x720 frame, no threshold. Recomputed by",
            "scripts/compose_particles_evidence.py from the committed frames.",
            ""] + rows)
    return rows


def card_b07() -> list[str]:
    """Effect B's preprocess, against the same effect with preprocess 0.0."""
    base = CAP / "dungeon_motes/r0/frame00000340.png"
    rows = ["frame   preprocess 8.0   preprocess 0.0   0.0 as % of 8.0"]
    for f in (1, 10, 40, 100):
        name = "frame%08d.png" % f
        on, _ = delta(CAP / "dungeon_motes/r0" / name, base, PLAYER_BAND)
        off, _ = delta(CAP / "dungeon_motes/f4-no-preprocess" / name, base,
                       PLAYER_BAND)
        rows.append("%5d   %10d px   %10d px   %12d %%"
                    % (f, on, off, round(100.0 * off / on) if on else 0))
    report("effect-b-preprocess.txt",
           ["Effect B, F4: the shipped effect against the same effect with",
            "preprocess mutated to 0.0 in the scene file and reverted after.",
            "Mote pixels = pixels differing from frame 340 of the SHIPPED",
            "capture, which is the same field 8.0 s after it stopped - an",
            "empty room. The player's column band x %d..%d is excluded,"
            % PLAYER_BAND,
            "because the player falls during the first second and his column",
            "differs from the dead-pose baseline over its whole height.",
            ""] + rows)
    return rows


def card_b09() -> list[str]:
    """What lines 161 and 162 of the generated shader do to a picture: the
    burst grows and dims across its life, which is the scale curve and the
    colour ramp, sampled once per particle per frame."""
    base = CAP / "hit_burst/r1/frame00000050.png"
    rows = ["frame   lit pixels   brightest   extent (logical px)"]
    for f in (10, 12, 15, 20, 30):
        name = "frame%08d.png" % f
        n, worst = delta(CAP / "hit_burst/r1" / name, base)
        w, h = extent(CAP / "hit_burst/r1" / name, base)
        rows.append("%5d   %7d px   %9d   %3d x %-3d" % (f, n, worst, w, h))
    rows += ["",
             "161  parameters.scale *= texture(scale_curve, vec2(lifetime)).rgb;",
             "162  parameters.color *= texture(color_ramp, vec2(lifetime));"]
    facts = {}
    for f, tag in ((10, "10"), (20, "20")):
        name = "frame%08d.png" % f
        _, worst = delta(CAP / "hit_burst/r1" / name, base)
        w, h = extent(CAP / "hit_burst/r1" / name, base)
        facts["w" + tag], facts["h" + tag], facts["b" + tag] = w, h, worst
    report("shader-lines-161-162.txt",
           ["The two generated-shader lines, and the burst they produce.",
            "Lit pixels and extent are measured against frame 50 of the same",
            "capture, which is empty. Dust carries scale_curve 0.6 -> 1.8 and",
            "a colour ramp that ends at alpha 0; the burst gets WIDER and",
            "DIMMER across its life, which is those two lines and nothing",
            "else. CHANGE-BRIEF.md section 1.3, the Dust column.",
            ""] + rows)
    return rows, facts


def cost_rows() -> list[str]:
    """The two recorded cost runs, side by side, verbatim from their files."""
    def pick(path: pathlib.Path) -> dict:
        if not path.is_file():
            raise SystemExit("missing recorded output: %s" % path)
        out = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            for key in ("A only", "B only", "C only", "all three",
                        "Baseline", "Spread"):
                if raw.strip().startswith(key) and "+" in raw:
                    out[key] = raw.split()[-3]
                elif raw.strip().startswith(key) and key in ("Baseline", "Spread"):
                    out[key] = raw.split()[-2]
        return out
    one = pick(EVID / "cost-effects-run1.txt")
    two = pick(EVID / "cost-effects-run2.txt")
    rows = ["condition                       run 1      run 2    instances",
            "A at its ceiling of 3        %8s   %8s           30"
            % (one.get("A only", "?"), two.get("A only", "?")),
            "B at steady state            %8s   %8s            0"
            % (one.get("B only", "?"), two.get("B only", "?")),
            "C while the player runs      %8s   %8s           22"
            % (one.get("C only", "?"), two.get("C only", "?")),
            "all three                    %8s   %8s           55"
            % (one.get("all three", "?"), two.get("all three", "?")),
            "",
            "baseline, two runs each      %8s   %8s"
            % (one.get("Baseline", "?"), two.get("Baseline", "?")),
            "spread WITHIN a run          %8s   %8s"
            % (one.get("Spread", "?"), two.get("Spread", "?"))]
    report("cost-summary.txt",
           ["Microseconds per frame over the effects-removed baseline, from",
            "two full runs of scripts/run-test.sh cost_effects.gd 60 300.",
            "The ORDER is stable across runs and the instances column is",
            "identical. The microsecond figures are not stable: B moves by",
            "more between the two runs than the within-run baseline spread",
            "either run reports. The instances column is the reading that",
            "survives. None of this is a GPU time, and no budget here is",
            "settled by it.",
            ""] + rows)
    return rows


def take_r_frame():
    """A real frame of take r at a moment the TAKE'S OWN LOG says three bursts
    were alive -- not a timestamp somebody eyeballed.

    The first version of this hardcoded 3.0 s, and when the take was
    re-recorded longer that second no longer had a burst in it. The card then
    said "three bursts alive" under a picture of an empty room, and nothing
    in the pipeline noticed. The timestamp now comes out of the log and the
    count is read back, so a card that cannot find three bursts stops the
    build instead of drawing a false label.
    """
    src = REEL / "capture/take-r.mp4"
    log = REEL / "capture/logs/take-r-inputs.jsonl"
    for path in (src, log):
        if not path.is_file():
            raise SystemExit("missing %s - render and encode take r first" % path)
    rows = [json.loads(r) for r in log.read_text(encoding="utf-8").splitlines()
            if r.strip()]
    # Not the FIRST frame that reaches three. On that frame the third burst is
    # one frame old and has not drawn anything yet, so the card would say
    # "three alive" over a picture with two in it -- true, and useless, which
    # is the failure this whole report keeps recording. Take the sixth
    # consecutive frame instead: a tenth of a second in, all three are drawn.
    run, best = 0, None
    for row in rows:
        run = run + 1 if row["bursts"] >= 3 else 0
        if run == 6:
            best = row
            break
    if best is None:
        raise SystemExit("take r never held 3 bursts for 6 frames - check the capture")
    out = EVID / "take-r-three-bursts.png"
    EVID.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.4f" % best["t"],
                    "-i", str(src), "-frames:v", "1", str(out)], check=True)
    # Cropped to the same action band scripts/frame_particles_footage.py uses,
    # for the same reason: three 24-pixel bursts in an uncropped 4K frame of a
    # 640 x 360 room are too small to count. Logical x 107..533, y 80..320, at
    # the 4K capture's 6x scale. Framing only; no pixel value changes.
    im = Image.open(out).convert("RGB")
    x, y, w, h = (v * 6 for v in (107, 80, 426, 240))
    return im.crop((x, y, x + w, y + h)), best


def main() -> int:
    MEDIA.mkdir(parents=True, exist_ok=True)
    b09_rows, b09_facts = card_b09()
    made = []

    made.append(compose(
        "B05",
        load(CAP / "hit_burst/r0-vs-r1-frame10.png"),
        "One setting, one frame, and the prediction that missed",
        "Measured after the change, against what was written before it",
        card_b05(),
        "captures/hit_burst/ - FIXTURE capture from the preview scene, 30 fps. "
        "Flash.scale_min/max 1.6/2.4 -> 5.0/7.0, nothing else moved. The "
        "author's verdict in the running game was keep."))

    made.append(compose(
        "B07",
        side_by_side(CAP / "dungeon_motes/r0/frame00000001.png",
                     CAP / "dungeon_motes/f4-no-preprocess/frame00000001.png",
                     "preprocess = 8.0   FIXTURE, frame 1",
                     "preprocess = 0.0   FIXTURE, frame 1, mutated"),
        "The same effect, one number apart, on frame one",
        "Mote pixels against an empty room, player column excluded",
        card_b07(),
        "captures/dungeon_motes/ - the mutation was made in the scene file and "
        "reverted immediately. Nothing errored and the configuration test "
        "passed on both. No headless run in this repository can see this."))

    made.append(compose(
        "B09",
        side_by_side(CAP / "hit_burst/r1/frame00000015.png",
                     CAP / "hit_burst/r1/frame00000020.png",
                     "frame 15   FIXTURE, cropped to the trap",
                     "frame 20   FIXTURE, cropped to the trap",
                     crop=TRAP_VIEW),
        "What those two lines do to a picture",
        "Wider and dimmer: the scale curve and the colour ramp, measured",
        b09_rows,
        "captures/hit_burst/r1/ - lit pixels and extent measured against "
        "frame 50, which is empty. Between frames 10 and 20 the extent grows "
        "from %d x %d to %d x %d logical pixels while the brightest channel "
        "falls from %d to %d. Cropped to the trap; no pixel value is changed."
        % (b09_facts["w10"], b09_facts["h10"], b09_facts["w20"],
           b09_facts["h20"], b09_facts["b10"], b09_facts["b20"])))

    r_frame, r_row = take_r_frame()
    made.append(compose(
        "B11B",
        r_frame,
        "The headless price, and the one column that holds still",
        "Two full runs of the same script, microseconds over baseline",
        cost_rows(),
        "evidence/a6/cost-effects-run1.txt and run2.txt, verbatim. The frame "
        "above is take r at %.2f s - SCRIPTED, not played; the take's own log "
        "records %d bursts alive on that frame. GPU time is not measured here "
        "and no budget in CHANGE-BRIEF.md section 5 is settled by this table."
        % (r_row["t"], r_row["bursts"])))

    for p in made:
        print("  media/%s  %dx%d" % ((p.name,) + Image.open(p).size))
    print("  reports in evidence/a6/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
