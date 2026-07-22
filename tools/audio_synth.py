"""Shared helpers for the sound-effect generation script in this folder.

Same spirit as pixel_art.py's sprite helpers: these run once, offline, to
produce short WAV files -- nothing here is imported by game code (`src/`),
which only ever loads the finished .wav files. WAV (not mp3) because it
needs no external decoder, so pygame.mixer.Sound can always load it, in a
packaged build or otherwise.

Every generator is deterministic (fixed RNG seeds for the noise-based
effects) so re-running the script reproduces byte-identical output --
"regeneratable, reviewable as code," same as the sprite pipeline.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SFX_DIR = Path(__file__).resolve().parent.parent / "assets" / "audio" / "sfx"

SAMPLE_RATE = 22050


def sine(freq_hz: float, duration: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    n = round(duration * sample_rate)
    t = np.arange(n) / sample_rate
    return np.sin(2 * np.pi * freq_hz * t)


def sine_sweep(freq_start: float, freq_end: float, duration: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """A sine wave whose frequency moves linearly from freq_start to
    freq_end -- the pitch sweep behind jump/land/hit. Uses the cumulative
    sum of instantaneous frequency (not just a linspace-in-time formula)
    so the phase stays continuous and the sweep doesn't click."""
    n = round(duration * sample_rate)
    freq_t = np.linspace(freq_start, freq_end, n)
    phase = 2 * np.pi * np.cumsum(freq_t) / sample_rate
    return np.sin(phase)


def chime_tone(freq_hz: float, duration: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """A single bell-like pluck: fundamental plus two quiet overtones
    (a flat sine reads as a dull beep, not a chime), with a fast attack
    and an exponential decay -- every "collect/save" sound is built from
    this same building block."""
    n = round(duration * sample_rate)
    t = np.arange(n) / sample_rate
    tone = np.sin(2 * np.pi * freq_hz * t)
    tone += 0.35 * np.sin(2 * np.pi * freq_hz * 2 * t)
    tone += 0.15 * np.sin(2 * np.pi * freq_hz * 3 * t)
    decay = np.exp(-t * (4.0 / duration))
    attack = min(1.0, 0.01 / duration)
    attack_n = max(1, round(n * attack))
    envelope = decay.copy()
    envelope[:attack_n] *= np.linspace(0, 1, attack_n)
    return tone * envelope


def white_noise(duration: float, seed: int, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    n = round(duration * sample_rate)
    rng = np.random.default_rng(seed)
    return rng.uniform(-1.0, 1.0, n)


def smooth(signal: np.ndarray, window: int) -> np.ndarray:
    """A short moving-average low-pass -- turns harsh white noise into a
    softer whoosh/thud texture without needing a real filter design."""
    if window <= 1:
        return signal
    kernel = np.ones(window) / window
    return np.convolve(signal, kernel, mode="same")


def linear_envelope(n: int, attack_frac: float, release_frac: float) -> np.ndarray:
    env = np.ones(n)
    a = max(1, round(n * attack_frac))
    r = max(1, round(n * release_frac))
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.minimum(env[-r:], np.linspace(1, 0, r))
    return env


def swell_envelope(n: int) -> np.ndarray:
    """A smooth rise-then-fall over the whole clip (half a sine lobe) --
    the "whoosh" shape for dodge, as opposed to a percussive attack/decay."""
    t = np.linspace(0, np.pi, n)
    return np.sin(t)


def concat(*signals: np.ndarray, overlap: float = 0.0, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Concatenate signals back-to-back, optionally crossfading `overlap`
    seconds between each pair so an arpeggio doesn't click at the seams."""
    overlap_n = round(overlap * sample_rate)
    if overlap_n <= 0:
        return np.concatenate(signals)

    result = signals[0].copy()
    for next_signal in signals[1:]:
        overlap_n = min(overlap_n, len(result), len(next_signal))
        fade_out = np.linspace(1, 0, overlap_n)
        fade_in = np.linspace(0, 1, overlap_n)
        head = result[:-overlap_n] if overlap_n else result
        blended = result[-overlap_n:] * fade_out + next_signal[:overlap_n] * fade_in
        result = np.concatenate([head, blended, next_signal[overlap_n:]])
    return result


def mix(*signals: np.ndarray) -> np.ndarray:
    """Sum signals of different lengths, zero-padding the shorter ones."""
    length = max(len(s) for s in signals)
    total = np.zeros(length)
    for signal in signals:
        total[: len(signal)] += signal
    return total


def normalize(signal: np.ndarray, peak: float = 0.9) -> np.ndarray:
    max_abs = np.max(np.abs(signal))
    if max_abs == 0:
        return signal
    return signal * (peak / max_abs)


def save_wav(signal: np.ndarray, name: str, sample_rate: int = SAMPLE_RATE) -> None:
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    path = SFX_DIR / f"{name}.wav"
    pcm = np.clip(signal, -1.0, 1.0)
    pcm = (pcm * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(pcm.tobytes())
    print(f"wrote {path} ({len(signal) / sample_rate:.2f}s)")
