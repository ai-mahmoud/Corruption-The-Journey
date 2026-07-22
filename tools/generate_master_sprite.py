"""Generates the Master's sprite for Beat 5's reveal cutscene: a single
held mid-strike pose (front arm extended with a small ember at the fist,
back arm cocked, wide fighting stance), two frames for a simple ember
flicker.

Cutscene-only -- unlike the Hatchling/enemy/hazard, this sprite has no
settings.*_COLLISION_* constant to match, since he's never a physics
entity, only ever drawn in src/cutscene_master.py.

Deliberately a different build and palette from the Hatchling: broader
shoulders, short dark hair, warm tanned skin, dark warm-toned clothing --
not her pale palette, and not the corruption-purple family either ("he
doesn't look corrupted. Not yet.").

Run once (`python tools/generate_master_sprite.py`) to (re)produce
assets/sprites/master.{png,json}.
"""

from pixel_art import build_image, rect_pixels, save_sprite

WIDTH, HEIGHT = 14, 22

SKIN = (196, 148, 108, 255)
SKIN_SHADOW = (166, 120, 84, 255)
SKIN_HIGHLIGHT = (214, 168, 128, 255)
EYE = (44, 36, 30, 255)

HAIR = (58, 44, 36, 255)
HAIR_SHADOW = (40, 30, 24, 255)

GARMENT = (92, 58, 40, 255)
GARMENT_SHADOW = (70, 42, 28, 255)
GARMENT_HIGHLIGHT = (112, 74, 52, 255)

BOOT = (54, 40, 30, 255)

EMBER_SMALL = (255, 150, 40, 255)
EMBER_BIG = (255, 190, 80, 255)


def _torso_row(y: int, start: int, width: int, base, highlight, shadow):
    pixels = {}
    for x in range(start, start + width):
        if x == start:
            pixels[(x, y)] = highlight
        elif x == start + width - 1:
            pixels[(x, y)] = shadow
        else:
            pixels[(x, y)] = base
    return pixels


def _base_pixels():
    """Everything except the ember accent -- identical across both frames."""
    pixels = {}

    # Hair: short, compact -- reads as adult/male, contrast to the
    # Hatchling's long flowing hair.
    pixels |= rect_pixels(6, 0, 3, 1, HAIR)
    pixels |= rect_pixels(5, 1, 5, 1, HAIR)
    pixels[(5, 2)] = HAIR
    pixels[(9, 2)] = HAIR_SHADOW

    # Face.
    pixels |= rect_pixels(6, 2, 3, 4, SKIN)
    pixels[(6, 2)] = SKIN_HIGHLIGHT
    pixels[(8, 5)] = SKIN_SHADOW
    pixels[(6, 4)] = EYE
    pixels[(8, 4)] = EYE

    pixels |= rect_pixels(7, 6, 2, 1, SKIN)  # neck

    # Torso: broad shoulders, a straight-ish V-taper (not an hourglass) --
    # a masculine silhouette distinct from the Hatchling's.
    pixels |= _torso_row(7, 3, 9, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(8, 3, 9, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(9, 4, 7, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(10, 4, 7, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(11, 5, 5, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(12, 5, 5, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(13, 5, 5, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)

    # Back arm: cocked in close to the body.
    pixels |= rect_pixels(1, 7, 2, 4, SKIN)

    # Front arm: extended outward mid-strike (horizontal, not a hanging
    # limb) -- the ember goes at its tip, added per-frame separately.
    pixels |= rect_pixels(10, 8, 4, 2, SKIN_SHADOW)

    # Legs: a wide fighting stance.
    pixels |= rect_pixels(4, 14, 2, 6, GARMENT_SHADOW)
    pixels |= rect_pixels(8, 14, 2, 6, GARMENT)
    pixels |= rect_pixels(3, 20, 4, 2, BOOT)
    pixels |= rect_pixels(7, 20, 4, 2, BOOT)

    return pixels


def build_frame(ember_color) -> dict[tuple[int, int], tuple[int, int, int, int]]:
    pixels = dict(_base_pixels())
    pixels[(12, 8)] = ember_color
    if ember_color is EMBER_BIG:
        pixels[(13, 8)] = ember_color
        pixels[(12, 9)] = ember_color
        pixels[(13, 9)] = ember_color
    return pixels


FRAMES = {"ember_small": EMBER_SMALL, "ember_big": EMBER_BIG}

sheet_pixels: dict[tuple[int, int], tuple[int, int, int, int]] = {}
for frame_index, (frame_name, ember_color) in enumerate(FRAMES.items()):
    offset_x = frame_index * WIDTH
    for (col, row), color in build_frame(ember_color).items():
        sheet_pixels[(col + offset_x, row)] = color

image = build_image(WIDTH * len(FRAMES), HEIGHT, sheet_pixels)

save_sprite(
    image,
    name="master",
    scale=6,
    anchor=(WIDTH // 2, HEIGHT),  # bottom-center
    frames={
        name: [[index * WIDTH, 0, WIDTH, HEIGHT]] for index, name in enumerate(FRAMES)
    },
)
