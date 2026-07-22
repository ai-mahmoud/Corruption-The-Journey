"""Hardcoded room/level definitions.

Plain data only (no pygame types) so this stays a simple, readable
description of a room's geometry -- `src/level.py` is what turns it into
something the game can collide with and draw. This is a stand-in for a real
tilemap pipeline, which is a later step once there's real content to build.
"""

# Platforms as (x, y, width, height) rectangles in world pixels, top-left
# origin. All values were chosen to fit the movement tuning in
# `src/settings.py`: an 80px vertical gap from the ground to PLATFORM_A's
# top, and another 80px gap up to PLATFORM_B's top, both comfortably within
# a full jump's ~97px apex height. Platforms are kept thin (12px) so their
# underside still clears the player's 60px height with some headroom,
# rather than exactly grazing it, while she's walking underneath on the
# ground below.

GROUND = (0, 660, 2200, 60)
PLATFORM_A = (350, 580, 150, 12)
PLATFORM_B = (600, 500, 150, 12)

TEST_ROOM = {
    "key": "TEST_ROOM",
    "world_width": 2200,
    "world_height": 720,
    "platforms": [GROUND, PLATFORM_A, PLATFORM_B],
    "player_spawn": (100, 660),  # feet position; player.py aligns her feet here
    "enemy_spawn": (1000, 660),
    "enemy_patrol_bounds": (900, 1300),
}

# --- Beat 5: The Pull Toward the Master ------------------------------------
# "Verticality starting to open up" -- the first room where world_height
# differs from the window height (760 vs 540), so the camera's vertical
# follow actually pans for the first time. A 3-jump ascending sequence
# leveling out onto a walkway toward the reveal. One ledge sits ~300px
# above anything reachable -- visible, never explained, never reachable:
# "most paths are still gated shut here," done with geometry alone.
# No enemies/hazards -- this is the calm-before-the-reveal beat.
#
# Each jump is an 80px vertical gap with an 85px horizontal gap. A full
# jump's max horizontal reach at an 80px vertical gain is ~108px (verified
# by simulating the actual physics, same way PLATFORM_A/B's clearance was
# checked) -- 85px leaves real margin rather than sitting at the edge of
# what's reachable. An earlier version of this room used 110px horizontal
# gaps (past that ~108px ceiling) and was actually impossible to clear;
# caught by driving the jump headlessly and checking she landed on the
# platform, not fell through to the ground below it.

DEEPER_GROUND = (0, 700, 1800, 60)
DEEPER_PLATFORM_1 = (300, 620, 140, 12)
DEEPER_PLATFORM_2 = (525, 540, 140, 12)
DEEPER_PLATFORM_3 = (750, 460, 140, 12)
DEEPER_WALKWAY = (950, 460, 830, 12)  # levels out, leads to the reveal
DEEPER_GATED_LEDGE = (850, 180, 220, 12)  # visible, never reachable

DEEPER_FOREST = {
    "key": "DEEPER_FOREST",
    "world_width": 1800,
    "world_height": 760,
    "platforms": [
        DEEPER_GROUND,
        DEEPER_PLATFORM_1,
        DEEPER_PLATFORM_2,
        DEEPER_PLATFORM_3,
        DEEPER_WALKWAY,
        DEEPER_GATED_LEDGE,
    ],
    "player_spawn": (80, 700),
    "warm_glow": (1740, 60, 70, 400),
    "background": "deeper_forest",
    "reveal_zone": (1740, 380, 60, 100),
}

# --- Beat 3: First Threat -------------------------------------------------
# A small clearing, wider sightlines -- open ground, no choke geometry
# (nothing here needs to force contact; the beast comes to her), with room
# to dodge laterally. One AttackBeast; no absorption, no health -- see
# GameplayScene's "attack_beast_spawn" handling for why contact here is a
# hit reaction, never a kill.

CLEARING_GROUND = (0, 480, 1400, 60)
CLEARING_EXIT = (1310, 380, 90, 160)

CLEARING = {
    "key": "CLEARING",
    "world_width": 1400,
    "world_height": 540,
    "platforms": [CLEARING_GROUND],
    "player_spawn": (80, 480),
    "attack_beast_spawn": (700, 480),
    "light_shaft": (1330, 60, 70, 420),
    "background": "clearing",
    "exit_zone": CLEARING_EXIT,
    # Heals/saves regardless of whether absorption's been unlocked yet --
    # reaching this spot is what matters, not how she got here.
    "checkpoint_zone": CLEARING_EXIT,
    "next_room": DEEPER_FOREST,
}

# --- Beat 2: The Forest Floor --------------------------------------------
# A short, mostly linear corridor. One corrupted-undergrowth patch sits at
# a genuine choke point -- a low ceiling section spans only that stretch,
# low enough that a full jump can't clear the patch, so "no way around
# except through" is enforced by geometry, not a scripted block. A second
# patch sits further along in the open, for a player who wants to backtrack
# and confirm touching it wasn't a fluke. No enemy, no text -- the entire
# lesson ("corruption does not hurt me") is taught by the hazards alone.

FOREST_GROUND = (0, 480, 1900, 60)
FOREST_CHOKE_CEILING = (600, 0, 200, 400)  # bottom at y=400: only an 80px gap

FOREST_FLOOR = {
    "key": "FOREST_FLOOR",
    "world_width": 1900,
    "world_height": 540,
    "platforms": [FOREST_GROUND, FOREST_CHOKE_CEILING],
    "player_spawn": (80, 480),
    "hazards": [(700, 480), (1400, 480)],  # (700, ...) sits in the choke point
    "light_shaft": (1830, 60, 70, 420),
    "background": "forest_floor",
    "exit_zone": (1810, 380, 90, 160),
    "next_room": CLEARING,
}

# --- Beat 1: Waking -----------------------------------------------------
# The hatching hollow: small, enclosed by roots (a low ceiling caps how far
# she can jump out of frame), with one fallen log to hop over on the way to
# a sliver of light marking the only way out. No enemy -- that's Beat 3.

HOLLOW_GROUND = (0, 480, 1100, 60)
HOLLOW_CEILING = (0, 0, 1100, 20)
HOLLOW_LOG = (520, 454, 40, 26)

WAKING_HOLLOW = {
    "key": "WAKING_HOLLOW",
    "world_width": 1100,
    "world_height": 540,
    "platforms": [HOLLOW_GROUND, HOLLOW_CEILING, HOLLOW_LOG],
    "player_spawn": (80, 480),
    "light_shaft": (1020, 60, 70, 420),
    "background": "waking_hollow",
    "exit_zone": (1000, 380, 100, 160),
    "log_obstacle": HOLLOW_LOG,
    "tutorial_prompt": "Press Space to jump",
    "next_room": FOREST_FLOOR,
}

# Rooms referenced by their "key" -- used by save/load and by respawn (both
# need to name a room without serializing/duplicating its whole dict).
ROOM_REGISTRY = {
    "TEST_ROOM": TEST_ROOM,
    "WAKING_HOLLOW": WAKING_HOLLOW,
    "FOREST_FLOOR": FOREST_FLOOR,
    "CLEARING": CLEARING,
    "DEEPER_FOREST": DEEPER_FOREST,
}
