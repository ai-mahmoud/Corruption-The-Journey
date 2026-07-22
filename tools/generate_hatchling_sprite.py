"""Generates the Hatchling's sprite sheet: idle, a 2-frame run cycle, jump,
and fall.

Sized to match her collision box exactly (native 12x20 * scale 3 = 36x60,
settings.PLAYER_COLLISION_WIDTH/HEIGHT) -- an earlier, more detailed pass
grew the sprite to ~2.7x her hitbox, which looked fine in isolation but
visibly clipped through ceilings, logs, and other tight gaps she was
actually clearing. Detail comes from shading and silhouette shape at this
size, not from a bigger canvas than the collision box can justify.

Redesigned to read clearly as female: longer hair flowing past the
shoulders, and a tapered waist/hip silhouette instead of a straight
rectangular torso -- both readable at this small a resolution, unlike
finer detail (facial features beyond eyes, fabric folds, etc.) which
isn't.

Run once (`python tools/generate_hatchling_sprite.py`) to (re)produce
assets/sprites/hatchling.{png,json}. The game loads this PNG and scales it
up with nearest-neighbor scaling -- never hand-drawn as a Pygame rect.
"""

from pixel_art import build_image, rect_pixels, save_sprite

WIDTH, HEIGHT = 12, 20

SKIN = (235, 213, 191, 255)
SKIN_SHADOW = (205, 180, 160, 255)
SKIN_HIGHLIGHT = (247, 232, 218, 255)
EYE = (58, 56, 66, 255)

# Warmer and more saturated than SKIN so long hair reads as hair, not more
# face -- the previous palette had the two nearly the same tone.
HAIR = (214, 196, 150, 255)
HAIR_SHADOW = (184, 168, 124, 255)

GARMENT = (196, 201, 214, 255)
GARMENT_SHADOW = (163, 168, 184, 255)
GARMENT_HIGHLIGHT = (216, 220, 230, 255)

LEG = (163, 168, 184, 255)
LEG_SHADOW = (134, 139, 156, 255)
BOOT = (120, 116, 128, 255)


def _torso_row(y: int, start: int, width: int, base, highlight, shadow):
    """One torso row, shaded left-highlight/right-shadow like every other
    body part -- `start`/`width` vary per row to taper the waist and flare
    the hips, which is what reads as a feminine silhouette at this size."""
    pixels = {}
    for x in range(start, start + width):
        if x == start:
            pixels[(x, y)] = highlight
        elif x == start + width - 1:
            pixels[(x, y)] = shadow
        else:
            pixels[(x, y)] = base
    return pixels


def _upper_body_pixels():
    """Hair, face, and the tapered torso -- identical across every frame;
    only the legs (and slightly, the arms) change between poses."""
    pixels = {}

    # Hair: rounded top, then flows down past the sides of the face and
    # the neck (shoulder-length), rather than a short cropped cap.
    pixels |= rect_pixels(4, 0, 4, 1, HAIR)
    pixels |= rect_pixels(3, 1, 6, 1, HAIR)
    pixels[(3, 2)] = HAIR
    pixels[(8, 2)] = HAIR_SHADOW
    pixels |= rect_pixels(2, 3, 2, 4, HAIR)  # left flowing lock, rows 3-6
    pixels |= rect_pixels(8, 3, 2, 4, HAIR_SHADOW)  # right flowing lock, rows 3-6

    # Face.
    pixels |= rect_pixels(4, 2, 4, 4, SKIN)
    pixels[(4, 2)] = SKIN_HIGHLIGHT
    pixels[(7, 5)] = SKIN_SHADOW
    pixels[(4, 4)] = EYE
    pixels[(6, 4)] = EYE  # a 1px gap (nose) at col 5 keeps these two eyes, not one bar

    # Neck (hair still flowing alongside it).
    pixels |= rect_pixels(5, 6, 2, 1, SKIN)

    # Torso: wide shoulders -> tapered waist -> flared hip, an hourglass
    # silhouette rather than a straight rectangle.
    pixels |= _torso_row(7, 3, 6, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(8, 3, 6, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(9, 4, 4, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(10, 4, 4, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(11, 3, 6, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)
    pixels |= _torso_row(12, 3, 6, GARMENT, GARMENT_HIGHLIGHT, GARMENT_SHADOW)

    return pixels


def _arm_pixels(left_offset: int, right_offset: int):
    pixels = {}
    pixels |= rect_pixels(1 + left_offset, 7, 2, 5, SKIN)
    pixels |= rect_pixels(9 + right_offset, 7, 2, 5, SKIN_SHADOW)
    return pixels


def _leg_pixels(left_x: int, right_x: int, top: int, height: int, spread: int = 2):
    """A symmetric standing stance -- both legs planted, same height."""
    pixels = {}
    pixels |= rect_pixels(left_x, top, spread, height, LEG)
    pixels |= rect_pixels(right_x, top, spread, height, LEG_SHADOW)
    boot_top = top + height
    pixels |= rect_pixels(left_x - 1, boot_top, spread + 2, 1, BOOT)
    pixels |= rect_pixels(right_x - 1, boot_top, spread + 2, 1, BOOT)
    return pixels


def _walking_legs(front_side: str, top: int, height: int):
    """A real stride: the front leg is shifted forward and bent/raised
    (mid-step), the back leg is planted normally. Color is keyed to
    physical left/right position (matching every other pose's fixed
    left-highlight/right-shadow lighting), not to which leg is "forward"
    -- otherwise the run cycle flickers the lighting every stepping leg."""
    pixels = {}
    raised = 1  # how much shorter/higher the front (stepping) leg reads
    if front_side == "right":
        back_x, front_x = 3, 7
    else:
        back_x, front_x = 7, 3

    back_color = LEG if back_x < front_x else LEG_SHADOW
    pixels |= rect_pixels(back_x, top, 2, height, back_color)
    pixels |= rect_pixels(back_x - 1, top + height, 4, 1, BOOT)

    front_color = LEG if front_x < back_x else LEG_SHADOW
    pixels |= rect_pixels(front_x, top, 2, height - raised, front_color)
    pixels |= rect_pixels(front_x - 1, top + height - raised, 4, 1, BOOT)
    return pixels


def build_frame(pose: str):
    pixels = _upper_body_pixels()
    # Torso's last row is 12 -- legs start at 13, flush, or a gap reads as
    # floating/disconnected legs (a bug caught in an earlier pass).
    if pose == "idle":
        pixels |= _arm_pixels(0, 0)
        pixels |= _leg_pixels(3, 7, 13, 6)
    elif pose == "run_a":  # right leg steps forward, left arm swings forward
        pixels |= _arm_pixels(1, -1)
        pixels |= _walking_legs("right", 13, 6)
    elif pose == "run_b":  # left leg steps forward, right arm swings forward
        pixels |= _arm_pixels(-1, 1)
        pixels |= _walking_legs("left", 13, 6)
    elif pose == "jump":  # legs tucked up beneath her
        pixels |= _arm_pixels(0, 0)
        pixels |= _leg_pixels(4, 6, 13, 2, spread=2)
    elif pose == "fall":  # legs apart, dangling
        pixels |= _arm_pixels(0, 0)
        pixels |= _leg_pixels(1, 8, 13, 6, spread=2)
    else:
        raise ValueError(pose)
    return pixels


POSES = ["idle", "run_a", "run_b", "jump", "fall"]

sheet_pixels: dict[tuple[int, int], tuple[int, int, int, int]] = {}
for frame_index, pose in enumerate(POSES):
    offset_x = frame_index * WIDTH
    for (col, row), color in build_frame(pose).items():
        sheet_pixels[(col + offset_x, row)] = color

image = build_image(WIDTH * len(POSES), HEIGHT, sheet_pixels)

save_sprite(
    image,
    name="hatchling",
    scale=3,
    anchor=(WIDTH // 2, HEIGHT),  # bottom-center, i.e. her feet
    frames={
        "idle": [[0, 0, WIDTH, HEIGHT]],
        "run_a": [[WIDTH, 0, WIDTH, HEIGHT]],
        "run_b": [[WIDTH * 2, 0, WIDTH, HEIGHT]],
        "jump": [[WIDTH * 3, 0, WIDTH, HEIGHT]],
        "fall": [[WIDTH * 4, 0, WIDTH, HEIGHT]],
    },
)
