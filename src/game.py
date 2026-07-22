"""Owns the window, the clock, and switching between Scenes."""

from __future__ import annotations

import pygame

import audio
import settings
from title_scene import TitleScene


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(settings.WINDOW_TITLE)
        self.fullscreen = False
        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Every scene always draws onto this fixed-size surface; fullscreen
        # only changes how it's scaled/letterboxed onto the real display in
        # _present(), so no scene's draw() needs to know or care. Deliberately
        # not pygame.SCALED (which does this same job via an SDL renderer) --
        # that flag fails outright on repeat set_mode() calls on systems
        # without a hardware renderer (confirmed under the dummy video driver
        # used for headless testing), which would crash fullscreen toggling
        # for real players on similarly limited setups.
        self.game_surface = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = False
        self.scene = TitleScene()

    def run(self) -> None:
        self.running = True
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            dt = min(dt, 1 / 30)  # avoid huge steps if the window was paused/dragged

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                else:
                    self.scene.handle_event(event)

            if self.scene.quit_requested:
                self.running = False

            next_scene = self.scene.update(dt)
            if next_scene is not None:
                self.scene = next_scene
            audio.update()

            self.scene.draw(self.game_surface)
            self._present()

        pygame.quit()

    def _present(self) -> None:
        if not self.fullscreen:
            self.screen.blit(self.game_surface, (0, 0))
            pygame.display.flip()
            return

        target_w, target_h = self.screen.get_size()
        scale = min(target_w / settings.WINDOW_WIDTH, target_h / settings.WINDOW_HEIGHT)
        scaled_size = (round(settings.WINDOW_WIDTH * scale), round(settings.WINDOW_HEIGHT * scale))
        # Nearest-neighbor, matching every other scale in this codebase --
        # crisp pixel edges rather than a blurry smoothscale.
        scaled = pygame.transform.scale(self.game_surface, scaled_size)
        self.screen.fill((0, 0, 0))  # letterbox bars when the aspect ratio doesn't match
        self.screen.blit(scaled, ((target_w - scaled_size[0]) // 2, (target_h - scaled_size[1]) // 2))
        pygame.display.flip()

    def _toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
