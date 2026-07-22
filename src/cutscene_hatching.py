"""Cutscene 2: "The Hatching" -- diegetic only, no text, no player input.

A close, static shot on the egg: it sits, trembles, cracks, and a hand
pushes through, then a hard cut to black leads into Beat 1 (Waking). The
background (tools/generate_cutscene_backgrounds.py) is a real generated
scene -- roots framing the hollow, kept simpler/darker than the playable
rooms' backgrounds since this is a close, intimate shot, not a space to
explore.
"""

from __future__ import annotations

import random

import pygame

import settings
from game_progress import GameProgress
from gameplay_scene import GameplayScene
from rooms import WAKING_HOLLOW
from scene import Scene
from sprite_utils import load_sprite

BACKGROUND_PATH = settings.PROJECT_ROOT / "assets" / "backgrounds" / "cutscene_hatching_hollow.png"
COLOR_SKIP_HINT = (110, 112, 105)

SKIP_HINT_TEXT = "Press Esc or X to skip cutscene"

SIT_DURATION = 1.0
TREMBLE_DURATION = 1.5
CRACK_DURATION = 1.0
BROKEN_DURATION = 1.0
BLACK_DURATION = 0.6
TOTAL_DURATION = SIT_DURATION + TREMBLE_DURATION + CRACK_DURATION + BROKEN_DURATION + BLACK_DURATION

TREMBLE_JITTER_PX = 2

# The egg's stored sprite scale is tuned for in-game world space, where she'd
# stand next to it -- far too small for this "camera close and intimate"
# shot. Blow it up further, just for this scene, keeping nearest-neighbor
# crispness. (Tuned against the egg's current native 18x22 size -- if that
# changes again, re-check this against the window height, not just carried
# over unchanged.)
CLOSEUP_ZOOM = 2

EGG_ANCHOR_SCREEN = (settings.WINDOW_WIDTH // 2, round(settings.WINDOW_HEIGHT * 0.72))


class CutsceneHatchingScene(Scene):
    def __init__(self, progress: GameProgress):
        self.progress = progress
        self.background = pygame.image.load(str(BACKGROUND_PATH)).convert()
        egg_sprite = load_sprite("egg")
        self._frames = {
            name: pygame.transform.scale(
                surface, (surface.get_width() * CLOSEUP_ZOOM, surface.get_height() * CLOSEUP_ZOOM)
            )
            for name, surface in egg_sprite.frames.items()
        }
        anchor_x, anchor_y = egg_sprite.anchor
        self._anchor = (anchor_x * CLOSEUP_ZOOM, anchor_y * CLOSEUP_ZOOM)

        self.hint_font = pygame.font.Font(None, 20)
        self.elapsed = 0.0
        self._skip_requested = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_x):
            self._skip_requested = True

    def update(self, dt: float) -> Scene | None:
        if self._skip_requested or self.elapsed >= TOTAL_DURATION:
            return GameplayScene(WAKING_HOLLOW, self.progress)
        self.elapsed += dt
        return None

    def _current_frame_and_jitter(self) -> tuple[str | None, int]:
        t = self.elapsed
        if t < SIT_DURATION:
            return "intact", 0
        t -= SIT_DURATION
        if t < TREMBLE_DURATION:
            return "intact", TREMBLE_JITTER_PX
        t -= TREMBLE_DURATION
        if t < CRACK_DURATION:
            return "cracked", TREMBLE_JITTER_PX // 2
        t -= CRACK_DURATION
        if t < BROKEN_DURATION:
            return "broken", 0
        return None, 0  # hard cut to black

    def draw(self, surface: pygame.Surface) -> None:
        frame_name, jitter = self._current_frame_and_jitter()

        if frame_name is None:
            surface.fill((0, 0, 0))
            return

        surface.blit(self.background, (0, 0))

        frame = self._frames[frame_name]
        offset_x = random.randint(-jitter, jitter) * CLOSEUP_ZOOM if jitter else 0
        anchor_x, anchor_y = self._anchor
        top_left = (
            EGG_ANCHOR_SCREEN[0] - anchor_x + offset_x,
            EGG_ANCHOR_SCREEN[1] - anchor_y,
        )
        surface.blit(frame, top_left)

        hint = self.hint_font.render(SKIP_HINT_TEXT, True, COLOR_SKIP_HINT)
        hint_rect = hint.get_rect(centerx=settings.WINDOW_WIDTH // 2, bottom=settings.WINDOW_HEIGHT - 16)
        surface.blit(hint, hint_rect)
