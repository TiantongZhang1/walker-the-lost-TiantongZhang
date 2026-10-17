#!/usr/bin/env python3
"""Synthesise the four PLACEHOLDER sound effects, deterministically.

These are NOT generated assets. They are written by arithmetic in this file,
so the assignment's "generate art, sound and music" requirement is NOT
satisfied by them -- `ASSET-LOG.md` says so in the same words. They exist for
one reason: the slice has to be audible before the one check that matters can
be run at all.

That check is the masking prediction from CONCEPT revision 1.1 -- *the trap's
15-frame warning is drowned by a 124 bpm bed with pulsing bass, so the hazard
reads as unfair with sound on even though it is fair with sound off.* It is
perceptual, it needs a human ear, and it cannot be run against silence. With
these in place it can be run today and re-run against the generated versions
when they land, which makes the two comparable instead of sequential.

Reproducibility, which the generated versions will not have from Suno and
should have from a seeded model:

    every waveform below is a closed-form function of time plus one noise
    array drawn from numpy's PCG64 at SEED. Re-running this file produces
    byte-identical WAVs.

    The OGGs are NOT byte-identical across runs, and the first version of this
    docstring claimed they were. They are not because an Ogg page header
    carries a stream serial number that ffmpeg picks at random, and ffmpeg
    exposes no flag to pin it. What IS identical is the audio: decoding both
    runs' OGGs to raw PCM and comparing gives a byte-for-byte match on all four
    sounds. That was checked rather than assumed --

        ffmpeg -i sfx-trap.ogg -f s16le -ac 1 -ar 48000 a.raw
        python scripts/synth_placeholder_sfx.py
        ffmpeg -i sfx-trap.ogg -f s16le -ac 1 -ar 48000 b.raw
        cmp a.raw b.raw

    -- so the reproducible artefact is the waveform, and the OGG's hash is a
    fingerprint of one particular encode rather than of the sound.

Usage:
    python scripts/synth_placeholder_sfx.py
"""
import io
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
SEED = 72700_1  # course number, assignment number
OUT = Path(__file__).resolve().parent.parent / "godot" / "assets"
SCRATCH = Path(__file__).resolve().parent.parent / "build" / "sfx"


def env(n, attack, decay, power=2.0):
    """Attack-decay envelope in samples; `power` shapes the decay curve."""
    a = max(1, int(attack * SR))
    d = max(1, n - a)
    return np.concatenate([
        np.linspace(0.0, 1.0, a),
        (1.0 - np.linspace(0.0, 1.0, d)) ** power,
    ])[:n]


def sweep(n, f0, f1, shape="exp"):
    """Phase of a frequency sweep from f0 to f1 across n samples."""
    t = np.arange(n) / SR
    total = n / SR
    if shape == "exp":
        f = f0 * (f1 / f0) ** (t / total)
        # integral of f0*(r)**(t/T) dt
        r = f1 / f0
        phase = 2 * np.pi * f0 * total / np.log(r) * (r ** (t / total) - 1.0)
    else:
        f = f0 + (f1 - f0) * t / total
        phase = 2 * np.pi * (f0 * t + 0.5 * (f1 - f0) * t * t / total)
    return phase, f


def tri(phase):
    """Triangle wave from a phase array -- more bite than a sine at this size."""
    return 2.0 / np.pi * np.arcsin(np.sin(phase))


def onepole_band(x, lo, hi):
    """Crude band-pass: one-pole high-pass then one-pole low-pass. Good enough
    for a 140 ms effect, and it keeps the dependency list at numpy."""
    def lp(sig, fc):
        a = np.exp(-2 * np.pi * fc / SR)
        out = np.empty_like(sig)
        acc = 0.0
        for i in range(len(sig)):
            acc = (1 - a) * sig[i] + a * acc
            out[i] = acc
        return out
    return lp(x - lp(x, lo), hi)


def norm(x, peak=0.85):
    m = float(np.abs(x).max())
    return x * (peak / m) if m > 0 else x


def sfx_jump(rng):
    """A short upward blip. Rising pitch = leaving the ground."""
    n = int(0.110 * SR)
    phase, _ = sweep(n, 240.0, 560.0)
    body = tri(phase) * env(n, 0.004, 0.106, 2.4)
    click = rng.standard_normal(n) * env(n, 0.0005, 0.012, 6.0) * 0.25
    return norm(body * 0.9 + click)


def sfx_slash(rng):
    """Band-passed noise with a falling centre. Air, not metal: the blade is
    already a visible arc, so the sound carries the direction of travel."""
    n = int(0.140 * SR)
    noise = rng.standard_normal(n)
    band = onepole_band(noise, 1400.0, 5200.0)
    # A second, lower layer sweeping down gives the stroke a direction.
    phase, _ = sweep(n, 900.0, 320.0)
    tone = np.sin(phase) * 0.35
    return norm((band * 1.0 + tone) * env(n, 0.002, 0.138, 2.0))


def sfx_trap(rng):
    """The one that has a job to do: a RISING INHARMONIC METALLIC SWEEP.

    CONCEPT revision 1.1 predicted that a 124 bpm bed with pulsing bass and
    tight percussion would mask a warning that competes on volume, and
    specified the answer in advance -- something with a MOVING PITCH, which
    percussion does not have, so it is distinguishable by motion rather than
    by level. The partials below are deliberately inharmonic (1, 1.41, 1.93,
    2.57) so it reads as struck metal rather than as a musical note that the
    score could swallow.

    260 ms, which is 15.6 frames at 60 Hz: the sound lasts the warning.
    """
    n = int(0.260 * SR)
    out = np.zeros(n)
    for ratio, gain in ((1.0, 1.0), (1.41, 0.55), (1.93, 0.38), (2.57, 0.22)):
        phase, _ = sweep(n, 420.0 * ratio, 2100.0 * ratio)
        out += np.sin(phase) * gain
    # Amplitude rises with the spike: the warning gets more urgent, it does not
    # decay away while the hazard is still arriving.
    rise = np.linspace(0.25, 1.0, n) ** 1.5
    scrape = onepole_band(rng.standard_normal(n), 2000.0, 7000.0) * 0.18
    return norm((out * rise + scrape * rise) * env(n, 0.006, 0.254, 0.8))


def sfx_death(rng):
    """Low thud, a short burst, and a descending minor third. The only one of
    the four that is allowed to be long, because the retry is 0.55 s."""
    n = int(0.450 * SR)
    thud_phase, _ = sweep(n, 110.0, 52.0)
    thud = np.sin(thud_phase) * env(n, 0.003, 0.447, 1.6)
    burst = onepole_band(rng.standard_normal(n), 300.0, 2600.0) * env(n, 0.001, 0.09, 4.0) * 0.5
    # 392 Hz -> 311 Hz is a descending minor third: down, and unresolved.
    tone_phase, _ = sweep(n, 392.0, 311.0, shape="lin")
    tone = tri(tone_phase) * env(n, 0.012, 0.438, 2.2) * 0.30
    return norm(thud * 1.0 + burst + tone)


SOUNDS = {
    "sfx-jump": sfx_jump,
    "sfx-slash": sfx_slash,
    "sfx-trap": sfx_trap,
    "sfx-death": sfx_death,
}


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    import wave
    import hashlib
    for name, fn in SOUNDS.items():
        rng = np.random.default_rng(SEED)  # same seed per sound: each is reproducible alone
        x = fn(rng)
        pcm = np.clip(x, -1.0, 1.0)
        pcm = (pcm * 32767.0).astype("<i2")
        wav = SCRATCH / (name + ".wav")
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        ogg = OUT / (name + ".ogg")
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(wav),
             "-c:a", "libvorbis", "-q:a", "4", str(ogg)],
            check=True,
        )
        digest = hashlib.sha256(ogg.read_bytes()).hexdigest()
        print("%-10s  %6.3f s  wav %7d B  ogg %6d B  sha256 %s"
              % (name, len(x) / SR, wav.stat().st_size, ogg.stat().st_size, digest[:16]))
    print("seed %d -- re-running this file reproduces the WAVs byte for byte" % SEED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
