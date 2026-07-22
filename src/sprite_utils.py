"""Loads generated sprite PNG + JSON pairs and scales them for the game.

This is the only place that touches the raw asset files -- entities ask for
a sprite by name and get back ready-to-blit surfaces. Adding animation
frames later means editing the JSON's "frames" table, not this loader.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pygame

from settings import SPRITES_DIR


@dataclass(frozen=True)
class SpriteSheet:
    """A loaded, pre-scaled sprite ready for drawing.

    `frames` maps a frame name (e.g. "idle") to an already up-scaled
    `pygame.Surface`. `anchor` is the (x, y) offset, in *scaled* pixels from
    the surface's top-left, of the point that should align with an entity's
    world position (typically bottom-center / feet).
    """

    frames: dict[str, pygame.Surface]
    anchor: tuple[int, int]
    scale: int

    def get(self, frame_name: str = "idle") -> pygame.Surface:
        return self.frames[frame_name]


def load_sprite(name: str) -> SpriteSheet:
    """Load `assets/sprites/{name}.png` + `{name}.json` into a SpriteSheet.

    Scaling uses `pygame.transform.scale` (a plain nearest-neighbor-style
    blow-up, not `smoothscale`) so pixel edges stay crisp.
    """
    json_path = SPRITES_DIR / f"{name}.json"
    metadata = json.loads(json_path.read_text())

    image_path = SPRITES_DIR / metadata["image"]
    native = pygame.image.load(str(image_path)).convert_alpha()

    scale = metadata["scale"]
    anchor_x, anchor_y = metadata["anchor"]

    frames: dict[str, pygame.Surface] = {}
    for frame_name, boxes in metadata["frames"].items():
        # A frame can be made of multiple boxes composited together, but for
        # now every sprite has exactly one box per frame.
        x, y, w, h = boxes[0]
        frame_native = native.subsurface(pygame.Rect(x, y, w, h)).copy()
        scaled_size = (w * scale, h * scale)
        frames[frame_name] = pygame.transform.scale(frame_native, scaled_size)

    return SpriteSheet(
        frames=frames,
        anchor=(anchor_x * scale, anchor_y * scale),
        scale=scale,
    )
