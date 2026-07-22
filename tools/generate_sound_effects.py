"""Generates every gameplay sound effect as a short procedurally-synthesized
WAV file -- same "scriptable, regeneratable, reviewable as code" pipeline
as the Pillow sprite generators, just synthesis instead of pixels. No
recorded/licensed audio anywhere in here.

Run once (already done, but re-run any time after editing an effect
below):

    python tools/generate_sound_effects.py
"""

from __future__ import annotations

import numpy as np

from audio_synth import (
    chime_tone,
    concat,
    linear_envelope,
    mix,
    normalize,
    save_wav,
    sine_sweep,
    smooth,
    swell_envelope,
    white_noise,
)


def generate_jump() -> None:
    # A short upward pitch flick -- the "hop" of leaving the ground.
    tone = sine_sweep(320, 760, 0.12)
    tone *= linear_envelope(len(tone), attack_frac=0.05, release_frac=0.55)
    save_wav(normalize(tone, 0.5), "jump")


def generate_land() -> None:
    # A low thump (descending sweep) plus a tiny click at the very start
    # for a percussive onset, rather than a pure soft sine.
    thud = sine_sweep(140, 60, 0.09)
    thud *= linear_envelope(len(thud), attack_frac=0.02, release_frac=0.8)
    click = smooth(white_noise(0.015, seed=1), window=2)
    click *= linear_envelope(len(click), attack_frac=0.05, release_frac=0.8)
    save_wav(normalize(mix(thud, click), 0.55), "land")


def generate_dodge() -> None:
    # A smoothed noise "whoosh" shaped by a rise-then-fall swell rather
    # than a percussive decay -- matches settings.DODGE_DURATION (0.18s).
    noise = smooth(white_noise(0.18, seed=2), window=10)
    noise *= swell_envelope(len(noise))
    save_wav(normalize(noise, 0.45), "dodge")


def generate_stumble() -> None:
    # A soft, breathy "whiff" -- quieter and lower than dodge, matching
    # the fact that she's reaching for an attack that doesn't exist yet.
    noise = smooth(white_noise(0.2, seed=3), window=18)
    noise *= linear_envelope(len(noise), attack_frac=0.15, release_frac=0.7)
    groan = sine_sweep(220, 160, 0.2)
    groan *= linear_envelope(len(groan), attack_frac=0.2, release_frac=0.7)
    save_wav(normalize(mix(noise, groan * 0.3), 0.35), "stumble")


def generate_hit() -> None:
    # Harsher and sharper than stumble -- a real impact, not a whiff.
    noise = white_noise(0.16, seed=4)
    noise *= linear_envelope(len(noise), attack_frac=0.01, release_frac=0.85)
    pain = sine_sweep(480, 140, 0.2)
    pain *= linear_envelope(len(pain), attack_frac=0.01, release_frac=0.8)
    save_wav(normalize(mix(noise * 0.5, pain), 0.6), "hit")


def generate_absorb() -> None:
    # A quick 3-note ascending chime -- the everyday contact-absorption
    # sound (Beat 2's enemy, or any later enemy she absorbs).
    notes = [chime_tone(freq, 0.14) for freq in (440.0, 660.0, 880.0)]
    tone = concat(*notes, overlap=0.03)
    save_wav(normalize(tone, 0.55), "absorb")


def generate_unlock() -> None:
    # The one-time absorption-unlock beat: a longer, wider ascending
    # arpeggio over a soft sustained low drone -- a bigger, one-off event,
    # not just a louder "absorb".
    notes = [chime_tone(freq, 0.22) for freq in (330.0, 440.0, 554.37, 660.0, 880.0)]
    arpeggio = concat(*notes, overlap=0.04)
    drone = np.sin(2 * np.pi * 165.0 * np.arange(len(arpeggio)) / 22050)
    drone *= linear_envelope(len(drone), attack_frac=0.1, release_frac=0.6) * 0.25
    save_wav(normalize(mix(arpeggio, drone), 0.7), "unlock")


def generate_checkpoint() -> None:
    # A calm major-chord arpeggio (C5-E5-G5) -- a "rest/save" feeling,
    # deliberately warmer and slower than absorb's more magical chime.
    notes = [chime_tone(freq, 0.22) for freq in (523.25, 659.25, 783.99)]
    tone = concat(*notes, overlap=0.06)
    save_wav(normalize(tone, 0.5), "checkpoint")


def generate_menu_move() -> None:
    save_wav(normalize(chime_tone(600.0, 0.05), 0.3), "menu_move")


def generate_menu_select() -> None:
    tone = concat(chime_tone(520.0, 0.05), chime_tone(760.0, 0.06), overlap=0.01)
    save_wav(normalize(tone, 0.4), "menu_select")


if __name__ == "__main__":
    generate_jump()
    generate_land()
    generate_dodge()
    generate_stumble()
    generate_hit()
    generate_absorb()
    generate_unlock()
    generate_checkpoint()
    generate_menu_move()
    generate_menu_select()
