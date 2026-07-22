"""Generates a background image for each playable room, replacing the flat
color fill. Low native resolution (world_width/6 x window_height/6, same
6x scale as the sprites) with a blocky/banded gradient sky (not a smooth
per-pixel gradient -- that would clash with the crisp flat-shaded sprite
style) and a few layers of silhouette shapes (roots/trees/rocks) at
different darkness for depth, plus sparse ash specks.

Deterministic: each room seeds its own RNG, so regenerating produces the
same image -- consistent with every other asset in this pipeline.

Run once (`python tools/generate_room_backgrounds.py`) to (re)produce
assets/backgrounds/*.png.
"""

import random

from PIL import Image, ImageDraw

from pixel_art import SPRITES_DIR

BACKGROUNDS_DIR = SPRITES_DIR.parent / "backgrounds"
SCALE = 6  # same nearest-neighbor scale convention as every sprite


def make_sky(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int], bands: int = 7) -> Image.Image:
    """A blocky (not smooth) vertical gradient -- reads as banded light
    rather than a photographic sky, matching the flat-shaded sprite style."""
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    band_height = max(1, height // bands)
    for band in range(bands + 1):
        t = band / bands
        color = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        y0 = band * band_height
        draw.rectangle([0, y0, width, y0 + band_height], fill=color)
    return image


def scatter_specks(image: Image.Image, count: int, color: tuple[int, int, int], rng: random.Random) -> None:
    pixels = image.load()
    for _ in range(count):
        x = rng.randrange(image.width)
        y = rng.randrange(image.height)
        pixels[x, y] = color


def draw_tree(draw: ImageDraw.ImageDraw, x: int, ground_y: int, trunk_h: int, canopy_r: int, color: tuple[int, int, int]) -> None:
    """A simple distorted tree/root silhouette: thin trunk + a ragged
    triangular canopy, asymmetric per the script's "distorted... wrong"
    plant description."""
    trunk_w = max(1, canopy_r // 4)
    draw.rectangle([x - trunk_w // 2, ground_y - trunk_h, x + trunk_w // 2, ground_y], fill=color)
    top_y = ground_y - trunk_h
    draw.polygon(
        [
            (x - canopy_r, top_y + canopy_r // 2),
            (x, top_y - canopy_r),
            (x + canopy_r // 2, top_y),
            (x + canopy_r, top_y + canopy_r // 3),
            (x, top_y + canopy_r),
        ],
        fill=color,
    )


def draw_hanging_root(draw: ImageDraw.ImageDraw, x: int, top_y: int, length: int, width: int, color: tuple[int, int, int]) -> None:
    """A root dangling down from the ceiling -- used for the enclosed hollow."""
    draw.rectangle([x - width // 2, top_y, x + width // 2, top_y + length], fill=color)
    draw.polygon(
        [(x - width, top_y + length), (x + width, top_y + length), (x, top_y + length + width)],
        fill=color,
    )


def generate_hollow_background(native_width: int, native_height: int) -> Image.Image:
    """Waking Hollow: enclosed, roots hanging from the low ceiling, tight
    and dim -- matches the room's low choke-ceiling geometry."""
    rng = random.Random(1)
    image = make_sky(native_width, native_height, (12, 13, 17), (62, 56, 48), bands=5)
    draw = ImageDraw.Draw(image)

    far_root = (32, 30, 26)
    near_root = (11, 11, 10)
    x = 6
    while x < native_width:
        draw_hanging_root(draw, x, 0, rng.randint(10, 22), rng.randint(2, 4), far_root)
        x += rng.randint(14, 24)

    ground_y = native_height - 6
    x = 4
    while x < native_width:
        draw_tree(draw, x, ground_y, rng.randint(8, 14), rng.randint(4, 7), near_root)
        x += rng.randint(16, 26)

    scatter_specks(image, native_width // 4, (58, 56, 52), rng)
    return image


def generate_forest_background(native_width: int, native_height: int) -> Image.Image:
    """The Forest Floor: a corridor of receding, distorted trees -- the
    grey-bled corrupted palette the script describes."""
    rng = random.Random(2)
    image = make_sky(native_width, native_height, (10, 11, 15), (72, 68, 60), bands=6)
    draw = ImageDraw.Draw(image)

    ground_y = native_height - 5
    layers = [
        ((48, 46, 42), 0.55, 10, 16),  # far, dim, shorter
        ((28, 27, 25), 0.75, 14, 22),
        ((13, 13, 14), 1.0, 18, 30),   # near, dark, tallest
    ]
    for color, height_scale, min_r, max_r in layers:
        x = rng.randint(0, 14)
        while x < native_width:
            canopy_r = rng.randint(min_r, max_r)
            draw_tree(draw, x, ground_y, round(canopy_r * height_scale), canopy_r, color)
            x += rng.randint(min_r, max_r) + rng.randint(4, 12)

    scatter_specks(image, native_width // 3, (70, 68, 64), rng)
    return image


def generate_clearing_background(native_width: int, native_height: int) -> Image.Image:
    """The Clearing: "wider sightlines" -- a more open sky, treeline set
    low and further back than the corridor, room to see the beast coming."""
    rng = random.Random(3)
    image = make_sky(native_width, native_height, (14, 15, 21), (78, 74, 64), bands=8)
    draw = ImageDraw.Draw(image)

    ground_y = native_height - 4
    far_color = (38, 36, 32)
    x = rng.randint(0, 16)
    while x < native_width:
        canopy_r = rng.randint(8, 14)
        draw_tree(draw, x, ground_y, round(canopy_r * 0.5), canopy_r, far_color)
        x += rng.randint(18, 30)

    scatter_specks(image, native_width // 3, (66, 64, 60), rng)
    return image


def generate_deeper_forest_background(native_width: int, native_height: int) -> Image.Image:
    """The Pull Toward the Master: denser corruption, and this room finally
    has real verticality (world_height > window height, so the camera
    actually pans vertically for the first time) -- taller tree layers to
    fill that space, plus a cluster of hanging roots concentrated near the
    far end, foreshadowing the "curtain of hanging roots" she pushes
    through for the reveal."""
    rng = random.Random(4)
    image = make_sky(native_width, native_height, (9, 10, 14), (66, 60, 50), bands=9)
    draw = ImageDraw.Draw(image)

    ground_y = native_height - 5
    layers = [
        ((44, 42, 38), 0.6, 12, 20),
        ((24, 23, 21), 0.85, 18, 30),
        ((12, 12, 13), 1.15, 24, 40),  # taller than Forest Floor's -- denser corruption
    ]
    for color, height_scale, min_r, max_r in layers:
        x = rng.randint(0, 14)
        while x < native_width:
            canopy_r = rng.randint(min_r, max_r)
            draw_tree(draw, x, ground_y, round(canopy_r * height_scale), canopy_r, color)
            x += rng.randint(min_r, max_r) + rng.randint(4, 10)

    # Hanging roots, concentrated in the last quarter of the room.
    root_color = (26, 24, 20)
    root_zone_start = round(native_width * 0.75)
    x = root_zone_start
    while x < native_width:
        draw_hanging_root(draw, x, 0, rng.randint(14, 30), rng.randint(2, 5), root_color)
        x += rng.randint(8, 14)

    scatter_specks(image, native_width // 3, (62, 60, 54), rng)
    return image


ROOMS = {
    "waking_hollow": (1100, 540, generate_hollow_background),
    "forest_floor": (1900, 540, generate_forest_background),
    "clearing": (1400, 540, generate_clearing_background),
    "deeper_forest": (1800, 760, generate_deeper_forest_background),
}

if __name__ == "__main__":
    BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)
    for name, (world_width, world_height, generator) in ROOMS.items():
        native_width = world_width // SCALE
        native_height = world_height // SCALE
        image = generator(native_width, native_height)
        # Resize to the room's *exact* world_width/world_height, not
        # native*SCALE -- that floor-divides and loses a few pixels (e.g.
        # 1100 -> 1098), which would leave a thin unrendered edge at max
        # camera scroll.
        scaled = image.resize((world_width, world_height), Image.NEAREST)
        out_path = BACKGROUNDS_DIR / f"{name}.png"
        scaled.save(out_path)
        print(f"wrote {out_path} ({scaled.width}x{scaled.height})")
