"""Generates the corrupted-beast sprite: the patrol enemy in the vertical
slice's sandbox room, and Beat 3's AttackBeast (same sprite, different
behavior wired in src/attack_beast.py).

Deliberately a different silhouette and palette from the Hatchling: low
and wide (quadruped-ish, doglike/insectile) instead of tall and upright,
in dark corrupted purples with a glowing eye and a ridged spine, shaded
top-lit so the low-slung body reads with real volume rather than a flat
silhouette.

Run once (`python tools/generate_enemy_sprite.py`) to (re)produce
assets/sprites/enemy.{png,json}.
"""

from pixel_art import build_image, rect_pixels, save_sprite

WIDTH, HEIGHT = 25, 16

BODY = (58, 40, 74, 255)
BODY_SHADOW = (42, 28, 56, 255)
BODY_HIGHLIGHT = (78, 56, 98, 255)
HEAD = (70, 48, 90, 255)
HEAD_SHADOW = (52, 34, 68, 255)
LEG = (35, 25, 45, 255)
SPINE = (96, 66, 118, 255)
EYE = (224, 44, 96, 255)
EYE_GLOW = (255, 130, 170, 255)

pixels: dict[tuple[int, int], tuple[int, int, int, int]] = {}

# Body: a low, wide mass, rows 4-10.
pixels |= rect_pixels(6, 4, 16, 7, BODY)
pixels |= rect_pixels(6, 9, 16, 2, BODY_SHADOW)  # underside shadow
pixels |= rect_pixels(6, 4, 16, 1, BODY_HIGHLIGHT)  # top-lit ridge line

# Spine ridge: a few raised segments along the back.
for x in (9, 13, 17):
    pixels |= rect_pixels(x, 2, 2, 2, SPINE)

# Head: protrudes forward (left) of the body, rows 1-7.
pixels |= rect_pixels(0, 3, 8, 7, HEAD)
pixels |= rect_pixels(0, 8, 8, 1, HEAD_SHADOW)
pixels |= rect_pixels(0, 3, 8, 1, BODY_HIGHLIGHT)
# A short snout taper.
pixels |= rect_pixels(0, 5, 2, 3, HEAD_SHADOW)

# Eye: a glowing core with a soft halo pixel.
pixels[(3, 5)] = EYE_GLOW
pixels[(4, 5)] = EYE
pixels[(4, 6)] = EYE

# Legs: four stubby columns under the body, uneven length for an
# "arrhythmic" gait read even standing still -- but all four feet still
# reach the same ground row (HEIGHT - 1), varying only how far up each leg
# extends, so nothing floats above the ground plane.
for leg_x, leg_h in ((6, 4), (10, 5), (16, 4), (21, 5)):
    top = HEIGHT - leg_h
    pixels |= rect_pixels(leg_x, top, 3, leg_h, LEG)

image = build_image(WIDTH, HEIGHT, pixels)

save_sprite(
    image,
    name="enemy",
    # scale=2, not 6: at 6x (150x96) this sprite was 2.5x wider/2.7x taller
    # than settings.ENEMY_COLLISION_WIDTH/HEIGHT (60x36) and visibly
    # overhung its actual hitbox. 2x (50x32) sits comfortably inside it.
    scale=2,
    anchor=(WIDTH // 2, HEIGHT),  # bottom-center
)
