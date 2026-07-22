"""The placeholder corrupted beast: a simple back-and-forth patrol whose
only real job is to exist as something the Hatchling can absorb."""

from __future__ import annotations

import pygame

import settings
from physics import move_and_collide
from sprite_utils import SpriteSheet


class Enemy:
    def __init__(
        self,
        sprite: SpriteSheet,
        spawn_x: float,
        spawn_y: float,
        patrol_bounds: tuple[int, int],
    ):
        self.sprite = sprite
        # Collision size is fixed (settings.ENEMY_COLLISION_*), independent
        # of the sprite's actual pixel size -- see settings.py.
        self.width = settings.ENEMY_COLLISION_WIDTH
        self.height = settings.ENEMY_COLLISION_HEIGHT

        # spawn position is its feet; store the top-left corner for physics.
        self.x = float(spawn_x - self.width / 2)
        self.y = float(spawn_y - self.height)
        self.vx = settings.ENEMY_PATROL_SPEED
        self.vy = 0.0

        self.patrol_min, self.patrol_max = patrol_bounds

        self.alive = True
        self.being_absorbed = False
        self.absorb_timer = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def begin_absorbed(self) -> None:
        """Start the same-length fade-out beat that mirrors the player's lock."""
        self.being_absorbed = True
        self.absorb_timer = settings.ABSORB_DURATION
        self.vx = 0.0

    def update(self, dt: float, solids: list[pygame.Rect]) -> None:
        if not self.alive:
            return

        if self.being_absorbed:
            self.absorb_timer -= dt
            if self.absorb_timer <= 0:
                self.alive = False
                self.being_absorbed = False
            return

        if self.x <= self.patrol_min:
            self.vx = abs(self.vx)
        elif self.x + self.width >= self.patrol_max:
            self.vx = -abs(self.vx)

        self.vy = min(self.vy + settings.GRAVITY_FALL * dt, settings.MAX_FALL_SPEED)

        dx = self.vx * dt
        dy = self.vy * dt
        self.x, self.y, collision = move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, solids
        )
        if collision.touched_bottom:
            self.vy = 0.0

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.alive:
            return

        frame = self.sprite.get("idle")
        if self.being_absorbed:
            frame = frame.copy()
            fade = max(0.0, self.absorb_timer / settings.ABSORB_DURATION)
            frame.set_alpha(round(255 * fade))

        draw_x = self.x - (frame.get_width() - self.width) / 2
        draw_y = self.y - (frame.get_height() - self.height)
        screen_x, screen_y = camera.apply(draw_x, draw_y)
        surface.blit(frame, (round(screen_x), round(screen_y)))
