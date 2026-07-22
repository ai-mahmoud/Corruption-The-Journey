"""Generates background art for the game's three cutscenes, replacing their
flat fills. Same low-native-resolution + nearest-neighbor-scale-up
convention as the room backgrounds (tools/generate_room_backgrounds.py) --
crisp blocky shading, not smooth gradients, to match the rest of the
game's pixel style.

Run once (`python tools/generate_cutscene_backgrounds.py`) to (re)produce
assets/backgrounds/cutscene_world.png, cutscene_hatching_hollow.png, and
master_reveal.png.
"""

import random

from PIL import Image, ImageDraw

from generate_room_backgrounds import SCALE, draw_tree, make_sky, scatter_specks
from pixel_art import SPRITES_DIR

BACKGROUNDS_DIR = SPRITES_DIR.parent / "backgrounds"
WINDOW_WIDTH, WINDOW_HEIGHT = 960, 540


def generate_world_background(native_width: int, native_height: int) -> Image.Image:
    """Cutscene 1 (The World): ruined cities reclaimed by nature, faint
    mana-sigil glints in the stonework -- placeholder-tier per the script's
    scope decision, but a real scene rather than a flat fill."""
    rng = random.Random(10)
    sky_top, sky_bottom = (8, 9, 14), (58, 52, 48)
    image = make_sky(native_width, native_height, sky_top, sky_bottom, bands=8)
    draw = ImageDraw.Draw(image)

    ground_y = native_height - 6
    far_color = (44, 41, 42)
    near_color = (14, 13, 15)

    # Far ruin skyline.
    x = rng.randint(0, 10)
    while x < native_width:
        w = rng.randint(6, 12)
        h = rng.randint(10, 22)
        draw.rectangle([x, ground_y - h, x + w, ground_y], fill=far_color)
        # Broken roofline: redraw a couple of notches back to sky color.
        for _ in range(rng.randint(1, 3)):
            nw = rng.randint(1, max(2, w // 3))
            nx = x + rng.randint(0, max(1, w - nw))
            nh = rng.randint(2, 5)
            draw.rectangle([nx, ground_y - h, nx + nw, ground_y - h + nh], fill=sky_top)
        x += w + rng.randint(2, 6)

    # Near ruin silhouettes, taller and darker.
    x = rng.randint(0, 14)
    while x < native_width:
        w = rng.randint(8, 16)
        h = rng.randint(18, 34)
        draw.rectangle([x, ground_y - h, x + w, ground_y], fill=near_color)
        for _ in range(rng.randint(1, 3)):
            nw = rng.randint(2, max(2, w // 3))
            nx = x + rng.randint(0, max(1, w - nw))
            nh = rng.randint(2, 6)
            draw.rectangle([nx, ground_y - h, nx + nw, ground_y - h + nh], fill=far_color)
        x += w + rng.randint(4, 10)

    # Faint mana-sigil glints in the stonework -- a few tiny bright accents.
    sigil_color = (150, 170, 210)
    for _ in range(6):
        sx = rng.randint(0, native_width - 1)
        sy = rng.randint(ground_y - 30, ground_y - 4)
        image.putpixel((sx, sy), sigil_color)

    scatter_specks(image, native_width // 5, (60, 58, 60), rng)
    return image


def generate_hatching_hollow_background(native_width: int, native_height: int) -> Image.Image:
    """Cutscene 2 (The Hatching): the corrupted-forest hollow around the
    egg -- roots, dead logs, still air. Framed for a close, intimate shot,
    so this stays simpler/darker than the playable rooms' backgrounds."""
    rng = random.Random(11)
    # Widened a little from its first pass, but deliberately kept dimmer
    # than the playable rooms' backgrounds -- this is a close, intimate
    # shot where the egg is the focus, not the environment.
    image = make_sky(native_width, native_height, (9, 10, 8), (44, 42, 34), bands=5)
    draw = ImageDraw.Draw(image)

    ground_y = native_height - 5
    root_color = (16, 17, 14)
    far_root_color = (28, 28, 22)

    # A ring of fallen logs/roots framing the hollow, denser at the edges
    # so the center (where the egg sits) stays visually open.
    for x in range(0, native_width, rng.randint(6, 9)):
        distance_from_center = abs(x - native_width / 2) / (native_width / 2)
        if distance_from_center < 0.25:
            continue  # keep the center clear for the egg
        height = round(rng.randint(6, 14) * (0.5 + distance_from_center))
        width = rng.randint(3, 6)
        color = root_color if distance_from_center > 0.6 else far_root_color
        draw.rectangle([x, ground_y - height, x + width, ground_y], fill=color)

    scatter_specks(image, native_width // 6, (44, 42, 36), rng)
    return image


def generate_master_reveal_background(native_width: int, native_height: int) -> Image.Image:
    """Beat 5's reveal: the one deliberate palette break in the whole game.
    Every other background (rooms and the first two cutscenes) is grey-
    black/corrupted; this is warm amber/orange -- "the tonal pivot from
    grey/dead to orange/warm... is the emotional hook" (Design Notes).
    Same blocky-gradient + silhouette technique as everything else, so
    it's stylistically consistent while being tonally the opposite of
    everything before it."""
    rng = random.Random(12)
    image = make_sky(native_width, native_height, (36, 20, 14), (168, 96, 46), bands=7)
    draw = ImageDraw.Draw(image)

    ground_y = native_height - 5
    far_color = (70, 42, 26)
    near_color = (30, 18, 12)

    for color, height_scale, min_r, max_r in [(far_color, 0.6, 8, 14), (near_color, 0.9, 10, 18)]:
        x = rng.randint(0, 12)
        while x < native_width:
            canopy_r = rng.randint(min_r, max_r)
            draw_tree(draw, x, ground_y, round(canopy_r * height_scale), canopy_r, color)
            x += rng.randint(min_r, max_r) + rng.randint(6, 14)

    # Warm embers drifting in the air instead of grey ash.
    scatter_specks(image, native_width // 4, (230, 150, 70), rng)
    return image


if __name__ == "__main__":
    BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)

    native_w, native_h = WINDOW_WIDTH // SCALE, WINDOW_HEIGHT // SCALE

    for filename, generator in [
        ("cutscene_world.png", generate_world_background),
        ("cutscene_hatching_hollow.png", generate_hatching_hollow_background),
        ("master_reveal.png", generate_master_reveal_background),
    ]:
        image = generator(native_w, native_h)
        image = image.resize((native_w * SCALE, native_h * SCALE), Image.NEAREST)
        out_path = BACKGROUNDS_DIR / filename
        image.save(out_path)
        print(f"wrote {out_path} ({image.width}x{image.height})")
