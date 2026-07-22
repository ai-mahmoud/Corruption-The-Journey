"""The corrupted-undergrowth hazard: not the absorption ability.

Stationary, has no effect on the player, and reacts to her presence rather
than her deliberate action: it withers (reversibly) if she lingers nearby,
and recoils and quietly dies if she touches it -- no lock, no flash, no
sound. Kept separate from Enemy since none of that behavior overlaps.
"""

from __future__ import annotations

import pygame

import settings
from sprite_utils import SpriteSheet


class CorruptedPlant:
    def __init__(self, sprite: SpriteSheet, spawn_x: float, spawn_y: float):
        self.sprite = sprite
        # Collision size is fixed (settings.HAZARD_COLLISION_*), independent
        # of the sprite's actual pixel size -- see settings.py.
        self.width = settings.HAZARD_COLLISION_WIDTH
        self.height = settings.HAZARD_COLLISION_HEIGHT

        # spawn position is its base; store the top-left corner for drawing.
        self.x = float(spawn_x - self.width / 2)
        self.y = float(spawn_y - self.height)

        self.alive = True
        self.is_withered = False
        self.dying = False
        self.death_timer = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def begin_dying(self) -> None:
        """Contact: recoil and quietly fade, with no effect on the player."""
        self.dying = True
        self.death_timer = settings.HAZARD_DEATH_FADE_DURATION

    def update(self, dt: float, player_rect: pygame.Rect) -> None:
        if not self.alive:
            return

        if self.dying:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.alive = False
            return

        distance = abs(player_rect.centerx - self.rect.centerx)
        self.is_withered = distance < settings.HAZARD_WITHER_RADIUS

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.alive:
            return

        frame_name = "withered" if (self.is_withered or self.dying) else "intact"
        frame = self.sprite.get(frame_name)
        if self.dying:
            frame = frame.copy()
            fade = max(0.0, self.death_timer / settings.HAZARD_DEATH_FADE_DURATION)
            frame.set_alpha(round(255 * fade))

        draw_x = self.x - (frame.get_width() - self.width) / 2
        draw_y = self.y - (frame.get_height() - self.height)
        screen_x, screen_y = camera.apply(draw_x, draw_y)
        surface.blit(frame, (round(screen_x), round(screen_y)))
