"""Shared helpers for the sprite-generation scripts in this folder.

These tools run once, offline, to produce the tiny pixel-grid PNGs (and their
JSON metadata) that the game loads at runtime. Nothing in here is imported by
game code (`src/`) -- Pillow/numpy stay confined to asset generation.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

RGBA = tuple[int, int, int, int]

SPRITES_DIR = Path(__file__).resolve().parent.parent / "assets" / "sprites"


def build_image(width: int, height: int, pixels: dict[tuple[int, int], RGBA]) -> Image.Image:
    """Build an RGBA image of exactly `width` x `height` pixels.

    `pixels` maps (col, row) -> RGBA color for every pixel that should be
    opaque (or partially so); any coordinate not present is left fully
    transparent. Rows/cols outside the given size are rejected so typos in a
    sprite layout fail loudly instead of silently drawing off-canvas.
    """
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for (col, row), color in pixels.items():
        if not (0 <= col < width and 0 <= row < height):
            raise ValueError(f"pixel ({col}, {row}) is outside the {width}x{height} canvas")
        image.putpixel((col, row), color)
    return image


def rect_pixels(x: int, y: int, w: int, h: int, color: RGBA) -> dict[tuple[int, int], RGBA]:
    """Return the pixel dict for a filled w x h rectangle at (x, y)."""
    return {(x + dx, y + dy): color for dy in range(h) for dx in range(w)}


def save_sprite(
    image: Image.Image,
    *,
    name: str,
    scale: int,
    anchor: tuple[int, int],
    frames: dict[str, list[list[int]]] | None = None,
) -> None:
    """Save `image` as PNG plus a metadata JSON, both named after `name`.

    `anchor` is the (x, y) point in *native* pixel coordinates -- typically
    bottom-center of the feet -- that the game aligns to an entity's world
    position. `frames` maps an animation name to a list of [x, y, w, h] boxes
    in native pixel coordinates; if omitted, a single "idle" frame spanning
    the whole image is written so the loader always has at least one frame
    to work with. Extra frames can be added later purely by editing the JSON.
    """
    SPRITES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = SPRITES_DIR / f"{name}.png"
    json_path = SPRITES_DIR / f"{name}.json"

    image.save(png_path)

    if frames is None:
        frames = {"idle": [[0, 0, image.width, image.height]]}

    metadata = {
        "image": png_path.name,
        "pixel_width": image.width,
        "pixel_height": image.height,
        "scale": scale,
        "anchor": list(anchor),
        "frames": frames,
    }
    json_path.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"wrote {png_path} ({image.width}x{image.height}) and {json_path}")
