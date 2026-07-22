"""The title screen: New Game / Continue / Exit -- the game's front door,
and the only place a genuinely fresh save gets started. Reuses Cutscene
1's establishing-shot background rather than a new asset.

"New Game" while a save already exists needs a confirm step (the `view`
state machine below, same pattern as PauseMenuScene's sub-views) since
it's destructive -- silently overwriting a friend's saved progress on a
single keypress would be a bad surprise.
"""

from __future__ import annotations

import pygame

import audio
import save_system
import settings
from cutscene_world import CutsceneWorldScene
from game_progress import GameProgress
from gameplay_scene import GameplayScene
from rooms import ROOM_REGISTRY
from scene import Scene

BACKGROUND_PATH = settings.PROJECT_ROOT / "assets" / "backgrounds" / "cutscene_world.png"

COLOR_TITLE = (225, 218, 205)
COLOR_SUBTITLE = (170, 165, 155)
COLOR_MENU_TEXT = (215, 210, 200)
COLOR_MENU_SELECTED = (255, 220, 140)
COLOR_MENU_BODY_TEXT = (190, 190, 190)
COLOR_SCRIM = (10, 10, 14, 150)

TITLE_TEXT = "Corruption: The Journey"
SUBTITLE_TEXT = "Chapter 0 Demo"

CONFIRM_LINES = [
    "Starting a new game erases your saved progress.",
    "",
    "Enter -- confirm      Esc -- cancel",
]


class TitleScene(Scene):
    def __init__(self):
        self.background = pygame.image.load(str(BACKGROUND_PATH)).convert()
        self._has_save = save_system.load_game() is not None

        self._title_font = pygame.font.Font(None, 52)
        self._subtitle_font = pygame.font.Font(None, 26)
        self._item_font = pygame.font.Font(None, 34)
        self._body_font = pygame.font.Font(None, 24)

        self.view = "main"  # "main" | "confirm_new_game"
        self.selected_index = 0
        self._new_game_requested = False
        self._continue_requested = False

        audio.play_track("exploration")

    @property
    def _items(self) -> list[str]:
        return ["Continue", "New Game", "Exit"] if self._has_save else ["New Game", "Exit"]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if self.view == "confirm_new_game":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                audio.play_sfx("menu_select")
                self._new_game_requested = True
            elif event.key == pygame.K_ESCAPE:
                self.view = "main"
            return

        if event.key == pygame.K_ESCAPE:
            self.quit_requested = True
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (self.selected_index - 1) % len(self._items)
            audio.play_sfx("menu_move")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (self.selected_index + 1) % len(self._items)
            audio.play_sfx("menu_move")
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            audio.play_sfx("menu_select")
            self._select_current_item()

    def _select_current_item(self) -> None:
        item = self._items[self.selected_index]
        if item == "Continue":
            self._continue_requested = True
        elif item == "New Game":
            if self._has_save:
                self.view = "confirm_new_game"
            else:
                self._new_game_requested = True
        elif item == "Exit":
            self.quit_requested = True

    def update(self, dt: float) -> Scene | None:
        if self._continue_requested:
            saved = save_system.load_game()
            progress = GameProgress(**saved)
            checkpoint_room = ROOM_REGISTRY[progress.checkpoint_room_key]
            return GameplayScene(checkpoint_room, progress)  # sets its own room music

        if self._new_game_requested:
            if save_system.SAVE_PATH.exists():
                save_system.SAVE_PATH.unlink()
            audio.stop()  # the opening cutscenes are deliberately silent
            return CutsceneWorldScene(GameProgress())

        return None

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))

        scrim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        scrim.fill(COLOR_SCRIM)
        surface.blit(scrim, (0, 0))

        title_surface = self._title_font.render(TITLE_TEXT, True, COLOR_TITLE)
        title_rect = title_surface.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=110)
        surface.blit(title_surface, title_rect)

        subtitle_surface = self._subtitle_font.render(SUBTITLE_TEXT, True, COLOR_SUBTITLE)
        subtitle_rect = subtitle_surface.get_rect(
            centerx=settings.WINDOW_WIDTH // 2, top=title_rect.bottom + 12
        )
        surface.blit(subtitle_surface, subtitle_rect)

        if self.view == "confirm_new_game":
            self._draw_lines(surface, CONFIRM_LINES, self._body_font, subtitle_rect.bottom + 80)
        else:
            self._draw_menu(surface, subtitle_rect.bottom + 80)

    def _draw_menu(self, surface: pygame.Surface, top: int) -> None:
        y = top
        for index, item in enumerate(self._items):
            color = COLOR_MENU_SELECTED if index == self.selected_index else COLOR_MENU_TEXT
            label = f"> {item}" if index == self.selected_index else item
            text = self._item_font.render(label, True, color)
            rect = text.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=y)
            surface.blit(text, rect)
            y += text.get_height() + 18

    def _draw_lines(self, surface: pygame.Surface, lines: list[str], font: pygame.font.Font, top: int) -> None:
        y = top
        for line in lines:
            text = font.render(line, True, COLOR_MENU_BODY_TEXT)
            rect = text.get_rect(centerx=settings.WINDOW_WIDTH // 2, top=y)
            surface.blit(text, rect)
            y += text.get_height() + 10
