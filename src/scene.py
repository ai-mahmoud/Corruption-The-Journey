"""The minimal interface Game.run() switches between.

A Scene owns everything about what's on screen for a stretch of the game
-- a cutscene, a playable room -- and hands control to the next one by
returning it from update(). Game itself never needs to know what kind of
scene it's showing.
"""

from __future__ import annotations

import pygame


class Scene:
    # Subclasses set `self.quit_requested = True` (e.g. on Esc during
    # gameplay) to end the app; Game.run() checks this after every event.
    quit_requested = False

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> "Scene | None":
        """Return a new Scene to switch to it now, or None to keep running this one."""
        return None

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError
