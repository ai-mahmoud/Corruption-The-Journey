"""Beat 5's ending: the reveal. No player input, no text during the
reveal itself -- the chapter's near-total silence holds to the very end;
this is a visual/diegetic beat, not a narrated one.

Three phases: REVEAL (the Master training, warm background, ember
flickering) -> BLACK_CUT (a hard cut, matching the style already
established going into Beat 1) -> END_CARD, an honest stopping point.
The script says "Chapter 1 begins here," but only Chapter 0 was ever in
scope -- this does not fabricate content that doesn't exist, same spirit
as every other placeholder already in this codebase.
"""

from __future__ import annotations

import pygame

import settings
from game_progress import GameProgress
from scene import Scene
from sprite_utils import load_sprite

BACKGROUND_PATH = settings.PROJECT_ROOT / "assets" / "backgrounds" / "master_reveal.png"

COLOR_POST = (46, 28, 18)
COLOR_POST_SCORCH = (20, 14, 12)
COLOR_END_CARD_BACKGROUND = (14, 15, 18)
COLOR_TEXT = (225, 218, 205)

REVEAL_DURATION = 3.0
BLACK_DURATION = 0.6
EMBER_FLICKER_INTERVAL = 0.25

CLOSEUP_ZOOM = 4  # a medium shot -- less extreme than the egg's close-up

MASTER_ANCHOR_SCREEN = (settings.WINDOW_WIDTH // 2 - 40, round(settings.WINDOW_HEIGHT * 0.75))
POST_RECT = (
    settings.WINDOW_WIDTH // 2 + 90,
    round(settings.WINDOW_HEIGHT * 0.75) - 140,
    18,
    140,
)


class CutsceneMasterScene(Scene):
    def __init__(self, progress: GameProgress):
        self.progress = progress

        master_sprite = load_sprite("master")
        self._frames = {
            name: pygame.transform.scale(
                surface, (surface.get_width() * CLOSEUP_ZOOM, surface.get_height() * CLOSEUP_ZOOM)
            )
            for name, surface in master_sprite.frames.items()
        }
        anchor_x, anchor_y = master_sprite.anchor
        self._anchor = (anchor_x * CLOSEUP_ZOOM, anchor_y * CLOSEUP_ZOOM)

        self.background = pygame.image.load(str(BACKGROUND_PATH)).convert()

        self._title_font = pygame.font.Font(None, 34)
        self._elapsed = 0.0
        self._ember_timer = 0.0
        self._ember_frame_is_small = True
        self._skip_requested = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_x):
            if self._elapsed >= REVEAL_DURATION + BLACK_DURATION:
                # Already at the end card -- nothing left to skip to.
                self.quit_requested = True
            else:
                self._skip_requested = True

    def update(self, dt: float) -> Scene | None:
        if self._skip_requested:
            self._skip_requested = False
            self._elapsed = REVEAL_DURATION + BLACK_DURATION
            return None

        self._elapsed += dt

        if self._elapsed < REVEAL_DURATION:
            self._ember_timer += dt
            if self._ember_timer >= EMBER_FLICKER_INTERVAL:
                self._ember_timer -= EMBER_FLICKER_INTERVAL
                self._ember_frame_is_small = not self._ember_frame_is_small

        return None

    def draw(self, surface: pygame.Surface) -> None:
        if self._elapsed < REVEAL_DURATION:
            self._draw_reveal(surface)
        elif self._elapsed < REVEAL_DURATION + BLACK_DURATION:
            surface.fill((0, 0, 0))
        else:
            self._draw_end_card(surface)

    def _draw_reveal(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))

        pygame.draw.rect(surface, COLOR_POST, POST_RECT)
        pygame.draw.rect(surface, COLOR_POST_SCORCH, (POST_RECT[0], POST_RECT[1], POST_RECT[2], 30))

        frame_name = "ember_small" if self._ember_frame_is_small else "ember_big"
        frame = self._frames[frame_name]
        anchor_x, anchor_y = self._anchor
        top_left = (MASTER_ANCHOR_SCREEN[0] - anchor_x, MASTER_ANCHOR_SCREEN[1] - anchor_y)
        surface.blit(frame, top_left)

    def _draw_end_card(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_END_CARD_BACKGROUND)
        text = self._title_font.render("-- End of Chapter 0 --", True, COLOR_TEXT)
        rect = text.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2))
        surface.blit(text, rect)
