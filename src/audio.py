"""Background music. A thin wrapper over pygame.mixer.music, which is
already a process-wide singleton -- so this mirrors that instead of
threading a MusicManager instance through every Scene constructor.

Scenes/rooms name a track by *role* ("exploration", "threat", "warmth"),
not by filename -- see TRACK_PATHS. pygame.mixer.music can only play one
stream at a time, so a real crossfade isn't possible; instead a track
change fades the outgoing track out, then starts the new one once that
fade finishes, via `update()` -- call that once per frame from Game.run()
regardless of which scene is active.
"""

from __future__ import annotations

import pygame

import settings

AUDIO_DIR = settings.PROJECT_ROOT / "assets" / "audio"

TRACK_PATHS = {
    "exploration": AUDIO_DIR / "exploration.mp3",
    "threat": AUDIO_DIR / "threat.mp3",
    "warmth": AUDIO_DIR / "warmth.mp3",
}

FADE_OUT_MS = 500
FADE_IN_MS = 800

_volume = 0.5
_current_track: str | None = None
_pending_track: str | None = None
_pending_at_ms = 0
_enabled = True  # flipped off if this machine has no usable audio device


def play_track(track: str) -> None:
    """Switch the looping background track. No-op if it's already playing
    or already queued -- e.g. re-entering a room shouldn't restart it."""
    global _pending_track, _pending_at_ms
    if not _enabled or track == _current_track or track == _pending_track:
        return
    if _current_track is None:
        _start(track)
    else:
        pygame.mixer.music.fadeout(FADE_OUT_MS)
        _pending_track = track
        _pending_at_ms = pygame.time.get_ticks() + FADE_OUT_MS


def stop() -> None:
    global _current_track, _pending_track
    if not _enabled:
        return
    pygame.mixer.music.fadeout(FADE_OUT_MS)
    _current_track = None
    _pending_track = None


def update() -> None:
    global _pending_track
    if not _enabled or _pending_track is None:
        return
    if pygame.time.get_ticks() >= _pending_at_ms:
        track, _pending_track = _pending_track, None
        _start(track)


def get_volume() -> float:
    return _volume


def set_volume(volume: float) -> None:
    global _volume
    _volume = max(0.0, min(1.0, volume))
    if _enabled:
        pygame.mixer.music.set_volume(_volume)


def _start(track: str) -> None:
    global _current_track
    try:
        pygame.mixer.music.load(str(TRACK_PATHS[track]))
        pygame.mixer.music.set_volume(_volume)
        pygame.mixer.music.play(loops=-1, fade_ms=FADE_IN_MS)
        _current_track = track
    except pygame.error:
        # No audio device available (e.g. some CI/headless setups) -- the
        # game should keep running silently rather than crash.
        global _enabled
        _enabled = False
