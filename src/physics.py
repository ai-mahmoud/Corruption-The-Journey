"""Simple AABB collision resolution against a list of static solid rects.

Movement is resolved one axis at a time (horizontal, then vertical) so
sliding along a wall or landing on a floor/platform falls out naturally,
without special-casing each direction.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class CollisionResult:
    touched_left: bool = False
    touched_right: bool = False
    touched_top: bool = False
    touched_bottom: bool = False


def move_and_collide(
    x: float,
    y: float,
    width: int,
    height: int,
    dx: float,
    dy: float,
    solids: list[pygame.Rect],
) -> tuple[float, float, CollisionResult]:
    """Move a `width`x`height` box from (x, y) by (dx, dy), resolving overlaps.

    Returns the new (possibly clamped) position and which sides made contact,
    which callers use for things like "am I grounded" or "did I hit a wall".
    """
    result = CollisionResult()

    x += dx
    rect = pygame.Rect(round(x), round(y), width, height)
    for solid in solids:
        if rect.colliderect(solid):
            if dx > 0:
                rect.right = solid.left
                result.touched_right = True
            elif dx < 0:
                rect.left = solid.right
                result.touched_left = True
            x = rect.x

    y += dy
    rect = pygame.Rect(round(x), round(y), width, height)
    for solid in solids:
        if rect.colliderect(solid):
            if dy > 0:
                rect.bottom = solid.top
                result.touched_bottom = True
            elif dy < 0:
                rect.top = solid.bottom
                result.touched_top = True
            y = rect.y

    return x, y, result
