"""The pause menu: Resume / Settings / Hints / Exit.

Opened from GameplayScene on Esc. Wraps whatever scene was paused and
draws it frozen (no update() calls reach it while paused) behind a dim
overlay, so "Resume" is just handing that same instance back unchanged.
"""

from __future__ import annotations

import pygame

import settings
from scene import Scene

COLOR_DIM_OVERLAY = (0, 0, 0, 160)
COLOR_MENU_TEXT = (215, 210, 200)
COLOR_MENU_SELECTED = (255, 220, 140)
COLOR_MENU_BODY_TEXT = (190, 190, 190)

MAIN_ITEMS = ["Resume", "Settings", "Hints", "Exit"]

HINTS_LINES = [
    "Arrow Keys / WASD -- move",
    "Space / Up / W -- jump (tap for a short hop, hold for a full jump)",
    "Shift -- dodge (briefly invulnerable)",
    "Walk into an enemy -- absorb it",
    "Esc -- pause",
]

SETTINGS_LINES = [
    "-- no settings yet --",
]


class PauseMenuScene(Scene):
    def __init__(self, paused_scene: Scene):
        self.paused_scene = paused_scene
        self.view = "main"  # "main" | "settings" | "hints"
        self.selected_index = 0
        self._resume_requested = False

        self._title_font = pygame.font.Font(None, 40)
        self._item_font = pygame.font.Font(None, 30)
        self._body_font = pygame.font.Font(None, 24)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if self.view != "main":
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_x):
                self.view = "main"
            return

        if event.key == pygame.K_ESCAPE:
            self._resume_requested = True
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (self.selected_index - 1) % len(MAIN_ITEMS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (self.selected_index + 1) % len(MAIN_ITEMS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._select_current_item()

    def _select_current_item(self) -> None:
        item = MAIN_ITEMS[self.selected_index]
        if item == "Resume":
            self._resume_requested = True
        elif item == "Settings":
            self.view = "settings"
        elif item == "Hints":
            self.view = "hints"
        elif item == "Exit":
            self.quit_requested = True

    def update(self, dt: float) -> Scene | None:
        if self._resume_requested:
            return self.paused_scene
        return None

    def draw(self, surface: pygame.Surface) -> None:
        self.paused_scene.draw(surface)

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(COLOR_DIM_OVERLAY)
        surface.blit(overlay, (0, 0))

        if self.view == "main":
            self._draw_main_menu(surface)
        elif self.view == "settings":
            self._draw_body("Settings", SETTINGS_LINES, surface)
        elif self.view == "hints":
            self._draw_body("Hints", HINTS_LINES, surface)

    def _draw_main_menu(self, surface: pygame.Surface) -> None:
        title = self._title_font.render("Paused", True, COLOR_MENU_TEXT)
        title_rect = title.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=140)
        surface.blit(title, title_rect)

        y = title_rect.bottom + 40
        for index, item in enumerate(MAIN_ITEMS):
            color = COLOR_MENU_SELECTED if index == self.selected_index else COLOR_MENU_TEXT
            label = f"> {item}" if index == self.selected_index else item
            text = self._item_font.render(label, True, color)
            rect = text.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=y)
            surface.blit(text, rect)
            y += text.get_height() + 16

    def _draw_body(self, title: str, lines: list[str], surface: pygame.Surface) -> None:
        title_surface = self._title_font.render(title, True, COLOR_MENU_TEXT)
        title_rect = title_surface.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=140)
        surface.blit(title_surface, title_rect)

        y = title_rect.bottom + 30
        for line in lines:
            text = self._body_font.render(line, True, COLOR_MENU_BODY_TEXT)
            rect = text.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=y)
            surface.blit(text, rect)
            y += text.get_height() + 10

        hint = self._body_font.render("Esc / Enter -- back", True, COLOR_MENU_BODY_TEXT)
        hint_rect = hint.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=y + 20)
        surface.blit(hint, hint_rect)
