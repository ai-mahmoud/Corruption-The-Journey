"""Music and sound effects. Music is a thin wrapper over pygame.mixer.music
(already a process-wide singleton, so this mirrors that instead of
threading a MusicManager instance through every Scene constructor); SFX
are short pygame.mixer.Sound one-shots played on their own channels, so
they can overlap the music (and each other) freely.

Scenes/rooms name a music track by *role* ("exploration", "threat",
"warmth"), not by filename -- see TRACK_PATHS. pygame.mixer.music can
only play one stream at a time, so a real crossfade isn't possible;
instead a track change fades the outgoing track out, then starts the new
one once that fade finishes, via `update()` -- call that once per frame
from Game.run() regardless of which scene is active.

SFX files (assets/audio/sfx/*.wav) are procedurally synthesized by
tools/generate_sound_effects.py -- not recorded/licensed audio, so unlike
the three music tracks they're covered by this repo's own license.
"""

from __future__ import annotations

import pygame

import settings

AUDIO_DIR = settings.PROJECT_ROOT / "assets" / "audio"
SFX_DIR = AUDIO_DIR / "sfx"

TRACK_PATHS = {
    "exploration": AUDIO_DIR / "exploration.mp3",
    "threat": AUDIO_DIR / "threat.mp3",
    "warmth": AUDIO_DIR / "warmth.mp3",
}

SFX_NAMES = (
    "jump",
    "land",
    "dodge",
    "stumble",
    "hit",
    "absorb",
    "unlock",
    "checkpoint",
    "menu_move",
    "menu_select",
)
SFX_PATHS = {name: SFX_DIR / f"{name}.wav" for name in SFX_NAMES}
SFX_VOLUME = 0.7  # fixed -- independent of the music volume slider in Settings

FADE_OUT_MS = 500
FADE_IN_MS = 800

_volume = 0.5
_current_track: str | None = None
_pending_track: str | None = None
_pending_at_ms = 0
_enabled = True  # flipped off if this machine has no usable audio device
_sfx_cache: dict[str, pygame.mixer.Sound] = {}


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


def play_sfx(name: str) -> None:
    """Play a one-shot sound effect. Cached after first load (lazy, not
    eager, since most SFX only ever get used in some of the game's rooms)."""
    global _enabled
    if not _enabled:
        return
    sound = _sfx_cache.get(name)
    if sound is None:
        try:
            sound = pygame.mixer.Sound(str(SFX_PATHS[name]))
            sound.set_volume(SFX_VOLUME)
            _sfx_cache[name] = sound
        except pygame.error:
            _enabled = False
            return
    sound.play()


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
