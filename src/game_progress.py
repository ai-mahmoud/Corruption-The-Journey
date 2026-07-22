"""State that outlives any single room: hearts, whether absorption has been
unlocked yet, and where she last checkpointed.

Everything else (Player, GameplayScene, the beast, hazards) gets rebuilt
fresh on every room transition and every respawn. This is the one thing
that doesn't -- constructed once in Game.__init__ (fresh, or loaded from
disk) and threaded through every scene constructor from there on.
"""

from __future__ import annotations

from dataclasses import dataclass

import settings


@dataclass
class GameProgress:
    max_hearts: int = settings.STARTING_MAX_HEARTS
    current_hearts: int = settings.STARTING_MAX_HEARTS
    absorption_unlocked: bool = False
    checkpoint_room_key: str = "WAKING_HOLLOW"
