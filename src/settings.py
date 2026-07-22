"""All tunable constants for the vertical slice, in one place.

Nothing here runs; it's just numbers and paths so tuning "feel" never means
hunting for magic numbers scattered through game code.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPRITES_DIR = PROJECT_ROOT / "assets" / "sprites"

# --- Window ---------------------------------------------------------------

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FPS = 60
WINDOW_TITLE = "Corruption: The Journey -- Chapter 0 Demo"

# --- Colors (placeholder palette, nodding to the corrupted-forest tone) ---

COLOR_BACKGROUND = (30, 32, 40)
COLOR_GROUND = (74, 68, 63)
COLOR_PLATFORM = (90, 83, 76)

# --- Collision box sizes -------------------------------------------------------
# Deliberately decoupled from sprite pixel size: every room (choke-point
# ceilings, log heights, exit-zone sizes, jump-clearance math) was tuned
# against these exact numbers. A sprite can get bigger/more detailed in an
# art pass without silently retuning every room's geometry -- draw() centers
# the (possibly larger) sprite over this (fixed) box instead.

PLAYER_COLLISION_WIDTH = 36
PLAYER_COLLISION_HEIGHT = 60
ENEMY_COLLISION_WIDTH = 60
ENEMY_COLLISION_HEIGHT = 36
HAZARD_COLLISION_WIDTH = 60
HAZARD_COLLISION_HEIGHT = 84

# --- Player physics ---------------------------------------------------------
# Tuned for a snappy, deliberate metroidvania feel rather than a floaty one:
# faster deceleration than acceleration (crisp stops), asymmetric gravity
# (falling pulls harder than rising), and a jump that can be cut short for
# variable height. All values are in pixels/second (or /second^2 for accel).

MOVE_ACCEL = 3000.0
MOVE_DECEL = 3600.0
AIR_ACCEL = 2200.0
MAX_RUN_SPEED = 260.0

GRAVITY_RISE = 2000.0
GRAVITY_FALL = 3200.0
MAX_FALL_SPEED = 1000.0

JUMP_VELOCITY = -640.0
JUMP_CUT_MULTIPLIER = 0.45  # applied to upward velocity if jump is released early

COYOTE_TIME = 0.10  # seconds after leaving a ledge that a jump still works
JUMP_BUFFER_TIME = 0.12  # seconds a jump press is remembered before landing

RUN_FRAME_DURATION = 0.12  # how long each run-cycle pose (run_a/run_b) holds

# --- Absorption -------------------------------------------------------------

ABSORB_DURATION = 0.45  # seconds the "deliberate action" beat locks movement

# --- Enemy -------------------------------------------------------------------

ENEMY_PATROL_SPEED = 60.0

# --- Corrupted-plant hazard ---------------------------------------------------
# Not the absorption ability -- a quiet, no-consequence reaction. Withering is
# reversible (walking away un-withers it); death on contact is not.

HAZARD_WITHER_RADIUS = 90.0
HAZARD_DEATH_FADE_DURATION = 0.3

# --- Dodge --------------------------------------------------------------------
# A real cooldown, not just feel-tuning: Beat 4 needs a moment where dodging
# genuinely isn't an option, so unlimited dodging isn't just "too easy," it's
# the wrong foundation.

DODGE_SPEED = 620.0
DODGE_DURATION = 0.18
DODGE_COOLDOWN = 0.6

# --- Stumble (failed attack attempt) -------------------------------------------
# She has no attack yet -- pressing the key does nothing but leave her briefly
# vulnerable, unlike DODGE which is invulnerable.

STUMBLE_DURATION = 0.35

# --- Hit reaction (beast strike lands) -----------------------------------------
# No health value anywhere -- the "unseen safety net" from the script is simply
# that nothing here tracks lethal consequence, so a hit can never end anything.

HIT_DURATION = 0.35
HIT_KNOCKBACK_SPEED = 260.0

# --- Attack beast ---------------------------------------------------------------

BEAST_AGGRO_RADIUS = 260.0
BEAST_TELEGRAPH_DURATION = 1.3  # long and generous -- teach through survival
BEAST_STRIKE_DURATION = 0.25
BEAST_STRIKE_SPEED = 480.0
BEAST_RECOVER_DURATION = 1.0
BEAST_IDLE_JITTER_PX = 3

# --- Camera ------------------------------------------------------------------

CAMERA_LERP_SPEED = 4.5  # higher = camera catches up to the player faster

# --- Hearts / progress ---------------------------------------------------------
# Real death exists from the moment this system is introduced -- running out of
# hearts respawns her at the last checkpoint. The one deliberate exception is
# the very first time it would happen: that's the absorption-unlock beat
# (GameplayScene._trigger_absorption_unlock), not a death.

STARTING_MAX_HEARTS = 2
LEVEL_UP_MAX_HEARTS = 3  # after the unlock beat
LEVEL_UP_CURRENT_HEARTS = 2  # she ends hurt, not full -- a scripted outcome, not a formula

UNLOCK_SLOW_MOTION_FACTOR = 0.4  # "time can slow slightly, for weight"
UNLOCK_BANNER_DURATION = 2.5  # cosmetic only -- doesn't extend any movement lock

# --- Hearts HUD ------------------------------------------------------------------
# (icon scale itself lives in the generated sprite's JSON, like every other
# sprite -- these are screen-layout numbers only.)

HEART_ICON_MARGIN = 16
HEART_ICON_SPACING = 32  # icon is 7px * scale=4 = 28px wide; must exceed that or icons overlap
