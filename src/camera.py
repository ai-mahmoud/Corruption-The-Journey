"""A smooth-follow camera: eases toward its target instead of snapping."""

from __future__ import annotations

import pygame

from settings import CAMERA_LERP_SPEED, WINDOW_HEIGHT, WINDOW_WIDTH


class Camera:
    def __init__(self, world_width: int, world_height: int):
        self.world_width = world_width
        self.world_height = world_height
        # (x, y) of the camera's top-left corner, in world space.
        self.x = 0.0
        self.y = 0.0

    def update(self, target_x: float, target_y: float, dt: float) -> None:
        """Ease the camera toward centering on (target_x, target_y)."""
        desired_x = target_x - WINDOW_WIDTH / 2
        desired_y = target_y - WINDOW_HEIGHT / 2

        # Frame-rate-independent lerp: higher CAMERA_LERP_SPEED closes more
        # of the remaining distance per second.
        t = 1 - pow(2.718281828, -CAMERA_LERP_SPEED * dt)
        self.x += (desired_x - self.x) * t
        self.y += (desired_y - self.y) * t

        self._clamp_to_world()

    def _clamp_to_world(self) -> None:
        max_x = max(0, self.world_width - WINDOW_WIDTH)
        max_y = max(0, self.world_height - WINDOW_HEIGHT)
        self.x = min(max(self.x, 0), max_x)
        self.y = min(max(self.y, 0), max_y)

    def apply(self, world_x: float, world_y: float) -> tuple[float, float]:
        """Convert a world-space point to screen-space."""
        return world_x - self.x, world_y - self.y

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        screen_x, screen_y = self.apply(rect.x, rect.y)
        return pygame.Rect(round(screen_x), round(screen_y), rect.width, rect.height)
