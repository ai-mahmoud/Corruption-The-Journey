"""Generates the corrupted-undergrowth hazard sprite for Beat 2 (The Forest
Floor). Two frames packed side-by-side: "intact" (spiky, upright, shaded
for volume) and "withered" (spikes shortened and dimmed, drooping) -- the
latter doubles as both the proximity-wither visual and the "recoils and
dies quietly" pose during its death fade.

Run once (`python tools/generate_undergrowth_sprite.py`) to (re)produce
assets/sprites/undergrowth.{png,json}.
"""

from pixel_art import build_image, rect_pixels, save_sprite

WIDTH, HEIGHT = 22, 30
BASE_TOP = 20  # where the base clump starts; spikes root here and grow up

BASE = (28, 34, 26, 255)
BASE_HIGHLIGHT = (40, 48, 37, 255)
BASE_SHADOW = (18, 22, 17, 255)
SPIKE = (54, 44, 68, 255)
SPIKE_HIGHLIGHT = (72, 60, 88, 255)
VEIN = (154, 62, 112, 255)

BASE_WITHERED = (20, 24, 19, 255)
SPIKE_WITHERED = (40, 34, 48, 255)

# (x, width, height) for each spike, intact heights -- asymmetric and
# irregular, "distorted... might lash out."
SPIKES = [
    (2, 2, 14),
    (5, 1, 9),
    (8, 2, 17),
    (11, 1, 7),
    (13, 2, 11),
    (16, 1, 5),
    (18, 2, 8),
]


def base_pixels(base_color, highlight, shadow):
    pixels = {}
    pixels |= rect_pixels(1, BASE_TOP, 20, 10, base_color)
    pixels |= rect_pixels(1, BASE_TOP, 20, 1, highlight)
    pixels |= rect_pixels(1, BASE_TOP + 8, 20, 2, shadow)
    return pixels


def intact_pixels():
    pixels = base_pixels(BASE, BASE_HIGHLIGHT, BASE_SHADOW)
    for x, width, height in SPIKES:
        top = BASE_TOP - height
        pixels |= rect_pixels(x, top, width, height, SPIKE)
        pixels |= rect_pixels(x, top, width, 1, SPIKE_HIGHLIGHT)
    for x, _, height in SPIKES[::2]:
        pixels[(x, BASE_TOP - height // 2)] = VEIN
    return pixels


def withered_pixels():
    # Same rooted base, spikes shortened to ~1/3 height and dimmed -- reads
    # as drooping, not a different plant.
    pixels = base_pixels(BASE_WITHERED, BASE_WITHERED, BASE_WITHERED)
    for x, width, height in SPIKES:
        shrunk = max(2, height // 3)
        top = BASE_TOP - shrunk
        pixels |= rect_pixels(x, top, width, shrunk, SPIKE_WITHERED)
    return pixels


sheet_pixels: dict[tuple[int, int], tuple[int, int, int, int]] = {}
for frame_index, frame_pixels in enumerate([intact_pixels(), withered_pixels()]):
    offset_x = frame_index * WIDTH
    for (col, row), color in frame_pixels.items():
        sheet_pixels[(col + offset_x, row)] = color

image = build_image(WIDTH * 2, HEIGHT, sheet_pixels)

save_sprite(
    image,
    name="undergrowth",
    # scale=3, not 6: at 6x (132x180) this sprite was over 2x
    # settings.HAZARD_COLLISION_WIDTH/HEIGHT (60x84) in both dimensions and
    # visibly towered above/through the choke-point ceiling it sits under.
    # 3x (66x90) is a close match with only a slight, tasteful spike overhang.
    scale=3,
    anchor=(WIDTH // 2, HEIGHT),  # bottom-center
    frames={
        "intact": [[0, 0, WIDTH, HEIGHT]],
        "withered": [[WIDTH, 0, WIDTH, HEIGHT]],
    },
)
