"""Cutscene 1: "The World" -- mythic narration over a generated ruined-
world backdrop, no player input.

The background (tools/generate_cutscene_backgrounds.py) is placeholder-tier
procedural art, not hand-painted, but it's a real scene (ruined skyline,
faint mana-sigil glints) rather than a flat fill -- swappable for real art
later without touching the timing/advance logic below.
"""

from __future__ import annotations

import pygame

import settings
from cutscene_hatching import CutsceneHatchingScene
from game_progress import GameProgress
from narration import WORLD_NARRATION
from scene import Scene

BACKGROUND_PATH = settings.PROJECT_ROOT / "assets" / "backgrounds" / "cutscene_world.png"
COLOR_LETTERBOX = (0, 0, 0)
COLOR_TEXT = (215, 210, 200)
COLOR_SKIP_HINT = (130, 130, 130)

SKIP_HINT_TEXT = "Press Esc or X to skip cutscene"

LETTERBOX_HEIGHT = 70
TEXT_MARGIN = 100
LINE_SPACING = 8
FADE_IN_DURATION = 0.4
MIN_CARD_DURATION = 2.5
MAX_CARD_DURATION = 7.0
SECONDS_PER_CHARACTER = 0.06


def _card_duration(text: str) -> float:
    return max(MIN_CARD_DURATION, min(MAX_CARD_DURATION, SECONDS_PER_CHARACTER * len(text)))


def _wrap_text(font: pygame.font.Font, text: str, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


class CutsceneWorldScene(Scene):
    def __init__(self, progress: GameProgress):
        self.progress = progress
        self.background = pygame.image.load(str(BACKGROUND_PATH)).convert()
        self.font = pygame.font.Font(None, 30)
        self.hint_font = pygame.font.Font(None, 20)
        self.card_index = 0
        self.card_elapsed = 0.0
        self._advance_requested = False
        self._skip_requested = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_x):
                self._skip_requested = True
            else:
                self._advance_requested = True

    def update(self, dt: float) -> Scene | None:
        if self._skip_requested:
            return CutsceneHatchingScene(self.progress)

        self.card_elapsed += dt
        duration = _card_duration(WORLD_NARRATION[self.card_index])
        if self._advance_requested or self.card_elapsed >= duration:
            self._advance_requested = False
            self.card_index += 1
            self.card_elapsed = 0.0
            if self.card_index >= len(WORLD_NARRATION):
                return CutsceneHatchingScene(self.progress)

        return None

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))

        max_width = settings.WINDOW_WIDTH - 2 * TEXT_MARGIN
        lines = _wrap_text(self.font, WORLD_NARRATION[self.card_index], max_width)
        line_surfaces = [self.font.render(line, True, COLOR_TEXT) for line in lines]

        alpha = round(255 * min(1.0, self.card_elapsed / FADE_IN_DURATION))
        total_height = sum(s.get_height() for s in line_surfaces) + LINE_SPACING * (len(line_surfaces) - 1)
        y = (settings.WINDOW_HEIGHT - total_height) // 2

        # A soft scrim behind the text -- the background is a real scene
        # now, not a flat fill, so legibility needs a little help.
        scrim = pygame.Surface((settings.WINDOW_WIDTH, total_height + 40), pygame.SRCALPHA)
        scrim.fill((0, 0, 0, round(120 * min(1.0, self.card_elapsed / FADE_IN_DURATION))))
        surface.blit(scrim, (0, y - 20))

        for line_surface in line_surfaces:
            line_surface.set_alpha(alpha)
            rect = line_surface.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=y)
            surface.blit(line_surface, rect)
            y += line_surface.get_height() + LINE_SPACING

        pygame.draw.rect(surface, COLOR_LETTERBOX, (0, 0, settings.WINDOW_WIDTH, LETTERBOX_HEIGHT))
        pygame.draw.rect(
            surface,
            COLOR_LETTERBOX,
            (0, settings.WINDOW_HEIGHT - LETTERBOX_HEIGHT, settings.WINDOW_WIDTH, LETTERBOX_HEIGHT),
        )

        hint = self.hint_font.render(SKIP_HINT_TEXT, True, COLOR_SKIP_HINT)
        hint_rect = hint.get_rect(
            centerx=settings.WINDOW_WIDTH // 2, centery=settings.WINDOW_HEIGHT - LETTERBOX_HEIGHT // 2
        )
        surface.blit(hint, hint_rect)
