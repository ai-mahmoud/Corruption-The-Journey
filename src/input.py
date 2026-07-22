"""Per-frame input snapshot fed into Player.update().

Keeping this as a small, plain dataclass -- rather than having Player read
pygame's keyboard state directly -- means the movement code doesn't care
where input comes from. Convenient if a controller, or a scripted test,
needs to drive the player later.
"""

from dataclasses import dataclass


@dataclass
class PlayerInput:
    move_left: bool = False
    move_right: bool = False
    jump_pressed: bool = False  # true only on the frame the key was first pressed
    jump_held: bool = False  # true for as long as the key is held down
    dodge_pressed: bool = False  # true only on the frame the key was first pressed
    attack_pressed: bool = False  # true only on the frame the key was first pressed
