"""Generates the cracking-egg sprite for Cutscene 2 (The Hatching). Three
frames packed side-by-side in one PNG: an intact shell (shaded, veined),
a cracked one, and a broken one with a small hand silhouette poking
through the opening.

Run once (`python tools/generate_egg_sprite.py`) to (re)produce
assets/sprites/egg.{png,json}.
"""

from pixel_art import build_image, save_sprite

WIDTH, HEIGHT = 18, 22

# A rounded, slightly bottom-heavy egg silhouette -- per-row width, widest
# around the middle rather than a perfect symmetric oval.
ROW_WIDTHS = [
    4, 6, 8, 10, 12, 13, 14, 15, 16, 16,
    16, 16, 16, 16, 15, 14, 13, 12, 10, 8, 6, 4,
]

# Shifted toward blue-indigo rather than the enemy/undergrowth's warm
# purple family (BODY=(58,40,74), SPINE=(96,66,118)) -- these read as
# near-identical hues at a glance otherwise, and the egg isn't part of
# that corruption-creature palette.
SHELL = (32, 38, 74, 255)
SHELL_HIGHLIGHT = (52, 60, 102, 255)
SHELL_SHADOW = (20, 24, 48, 255)
VEIN = (92, 112, 182, 255)
CRACK = (230, 220, 196, 255)
SKIN = (235, 213, 191, 255)  # matches the Hatchling's skin tone
SKIN_SHADOW = (205, 180, 160, 255)


def shell_pixels() -> dict[tuple[int, int], tuple[int, int, int, int]]:
    """Shaded left-to-right: a highlight strip, a shadow strip, shell between."""
    pixels = {}
    for row, width in enumerate(ROW_WIDTHS):
        start = (WIDTH - width) // 2
        for col in range(start, start + width):
            if col < start + 2:
                pixels[(col, row)] = SHELL_HIGHLIGHT
            elif col >= start + width - 2:
                pixels[(col, row)] = SHELL_SHADOW
            else:
                pixels[(col, row)] = SHELL
    return pixels


def with_veins(pixels):
    pixels = dict(pixels)
    for col, row in [(6, 6), (11, 9), (7, 13), (12, 16), (9, 18)]:
        pixels[(col, row)] = VEIN
    return pixels


def with_crack(pixels):
    pixels = dict(pixels)
    zigzag = [
        (9, 2), (8, 4), (10, 6), (8, 8), (10, 10),
        (8, 12), (10, 14), (8, 16), (9, 18),
    ]
    for col, row in zigzag:
        pixels[(col, row)] = CRACK
        pixels[(col + 1, row)] = CRACK
    return pixels


def with_broken_crown(pixels):
    # A torn opening at the top, with a small hand silhouette in it.
    pixels = dict(pixels)
    for col in range(7, 11):
        for row in range(0, 3):
            pixels.pop((col, row), None)
    # Fingers/hand: a few skin pixels emerging from the gap.
    pixels[(8, 1)] = SKIN
    pixels[(9, 1)] = SKIN
    pixels[(8, 2)] = SKIN_SHADOW
    pixels[(9, 2)] = SKIN
    pixels[(10, 2)] = SKIN_SHADOW
    return pixels


intact_pixels = with_veins(shell_pixels())
cracked_pixels = with_crack(intact_pixels)
broken_pixels = with_broken_crown(cracked_pixels)

# Pack all three frames side-by-side in one image.
sheet_pixels: dict[tuple[int, int], tuple[int, int, int, int]] = {}
for frame_index, frame_pixels in enumerate([intact_pixels, cracked_pixels, broken_pixels]):
    offset_x = frame_index * WIDTH
    for (col, row), color in frame_pixels.items():
        sheet_pixels[(col + offset_x, row)] = color

image = build_image(WIDTH * 3, HEIGHT, sheet_pixels)

save_sprite(
    image,
    name="egg",
    scale=6,
    anchor=(WIDTH // 2, HEIGHT),  # bottom-center
    frames={
        "intact": [[0, 0, WIDTH, HEIGHT]],
        "cracked": [[WIDTH, 0, WIDTH, HEIGHT]],
        "broken": [[WIDTH * 2, 0, WIDTH, HEIGHT]],
    },
)
