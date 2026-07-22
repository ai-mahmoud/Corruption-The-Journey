"""Turns a plain-data room definition (see data/rooms.py) into something
the game can collide with and draw."""

from __future__ import annotations

import pygame

from settings import COLOR_GROUND, COLOR_PLATFORM, PROJECT_ROOT

COLOR_LIGHT_SHAFT = (68, 62, 48)
# Distinct from COLOR_LIGHT_SHAFT on purpose -- warm and out of place
# against the grey-black palette everywhere else, per Beat 5's "the first
# 'different' thing she's encountered."
COLOR_WARM_GLOW = (196, 122, 54)
BACKGROUNDS_DIR = PROJECT_ROOT / "assets" / "backgrounds"


class Room:
    def __init__(self, room_data: dict):
        self.world_width: int = room_data["world_width"]
        self.world_height: int = room_data["world_height"]
        self.player_spawn: tuple[int, int] = room_data["player_spawn"]

        self.solids: list[pygame.Rect] = [pygame.Rect(*p) for p in room_data["platforms"]]
        # The ground is always the first platform in the list by convention;
        # everything else is drawn as a raised platform.
        self._ground = self.solids[0]

        self.light_shaft = (
            pygame.Rect(*room_data["light_shaft"]) if "light_shaft" in room_data else None
        )
        self.warm_glow = (
            pygame.Rect(*room_data["warm_glow"]) if "warm_glow" in room_data else None
        )

        # Generated once by tools/generate_room_backgrounds.py, sized to
        # exactly world_width x window_height -- drawn 1:1 with world space
        # (not parallax-scrolled), so it lines up with the room geometry
        # without any extra scroll-speed math.
        self.background: pygame.Surface | None = None
        if "background" in room_data:
            path = BACKGROUNDS_DIR / f"{room_data['background']}.png"
            self.background = pygame.image.load(str(path)).convert()

    def draw(self, surface: pygame.Surface, camera) -> None:
        if self.background is not None:
            screen_x, screen_y = camera.apply(0, 0)
            surface.blit(self.background, (round(screen_x), round(screen_y)))

        if self.light_shaft is not None:
            pygame.draw.rect(surface, COLOR_LIGHT_SHAFT, camera.apply_rect(self.light_shaft))
        if self.warm_glow is not None:
            pygame.draw.rect(surface, COLOR_WARM_GLOW, camera.apply_rect(self.warm_glow))

        for solid in self.solids:
            color = COLOR_GROUND if solid is self._ground else COLOR_PLATFORM
            pygame.draw.rect(surface, color, camera.apply_rect(solid))
