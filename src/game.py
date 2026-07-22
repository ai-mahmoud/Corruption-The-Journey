"""Owns the window, the clock, and switching between Scenes."""

from __future__ import annotations

import pygame

import save_system
import settings
from cutscene_world import CutsceneWorldScene
from game_progress import GameProgress
from gameplay_scene import GameplayScene
from rooms import ROOM_REGISTRY


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(settings.WINDOW_TITLE)
        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = False

        saved = save_system.load_game()
        if saved is not None:
            # Resuming: skip both cutscenes, open directly on the checkpoint.
            progress = GameProgress(**saved)
            checkpoint_room = ROOM_REGISTRY[progress.checkpoint_room_key]
            self.scene = GameplayScene(checkpoint_room, progress)
        else:
            self.scene = CutsceneWorldScene(GameProgress())

    def run(self) -> None:
        self.running = True
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            dt = min(dt, 1 / 30)  # avoid huge steps if the window was paused/dragged

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)

            if self.scene.quit_requested:
                self.running = False

            next_scene = self.scene.update(dt)
            if next_scene is not None:
                self.scene = next_scene

            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
