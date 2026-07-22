"""Generates the hearts-HUD icon. Two frames packed side-by-side: "full"
(a filled red heart) and "empty" (the same silhouette, dim grey -- a lost
heart, not a missing one).

Run once (`python tools/generate_heart_icon.py`) to (re)produce
assets/sprites/heart.{png,json}.
"""

from pixel_art import build_image, save_sprite

WIDTH, HEIGHT = 7, 6

HEART_PIXELS = [
    (1, 0), (2, 0), (4, 0), (5, 0),
    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
    (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
    (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
    (2, 4), (3, 4), (4, 4),
    (3, 5),
]

FULL_COLOR = (206, 58, 66, 255)
EMPTY_COLOR = (58, 56, 60, 255)


def heart_pixels(color):
    return {pos: color for pos in HEART_PIXELS}


sheet_pixels = {}
for frame_index, color in enumerate([FULL_COLOR, EMPTY_COLOR]):
    offset_x = frame_index * WIDTH
    for (col, row), pixel_color in heart_pixels(color).items():
        sheet_pixels[(col + offset_x, row)] = pixel_color

image = build_image(WIDTH * 2, HEIGHT, sheet_pixels)

save_sprite(
    image,
    name="heart",
    scale=4,
    anchor=(0, 0),  # HUD icon -- drawn top-left, not world-anchored
    frames={
        "full": [[0, 0, WIDTH, HEIGHT]],
        "empty": [[WIDTH, 0, WIDTH, HEIGHT]],
    },
)
