"""The Beat 3 attack beast: notices her and strikes, with a generous
telegraph so the encounter is survivable by reacting, not by luck.

Deliberately not an `Enemy` -- contact here should never trigger the
absorption path (`GameplayScene._check_absorption`), since she hasn't
discovered that ability yet in the story. This class has no idea
absorption exists; `GameplayScene` is what decides contact means a hit
reaction, not a kill, by simply never wiring this into that path.
"""

from __future__ import annotations

import random
from enum import Enum, auto

import pygame

import settings
from physics import move_and_collide
from sprite_utils import SpriteSheet


class BeastState(Enum):
    IDLE = auto()
    TELEGRAPH = auto()
    STRIKE = auto()
    RECOVER = auto()
    ABSORBED = auto()


class AttackBeast:
    def __init__(self, sprite: SpriteSheet, spawn_x: float, spawn_y: float):
        self.sprite = sprite
        # Same fixed collision size as Enemy (settings.ENEMY_COLLISION_*) --
        # they share the same base sprite, so they share the same box.
        self.width = settings.ENEMY_COLLISION_WIDTH
        self.height = settings.ENEMY_COLLISION_HEIGHT

        # spawn position is its feet; store the top-left corner for physics.
        self.x = float(spawn_x - self.width / 2)
        self.y = float(spawn_y - self.height)
        self.vy = 0.0

        self.state = BeastState.IDLE
        self.state_timer = 0.0
        self.strike_vx = 0.0
        self._committed_direction = 1
        self.alive = True
        self.absorb_timer = 0.0

        # Small, irregular per-frame draw offset -- "twitchy and
        # arrhythmic" without needing new animation frames.
        self._jitter_offset = (0, 0)
        self._jitter_timer = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    @property
    def is_striking(self) -> bool:
        return self.state is BeastState.STRIKE

    def _start_telegraph(self, player_rect: pygame.Rect) -> None:
        """The strike direction commits here, at the start of the wind-up --
        not when it ends. A telegraph that re-aims itself up to the last
        frame isn't a fair warning; it's just tracking her."""
        self.state = BeastState.TELEGRAPH
        self.state_timer = settings.BEAST_TELEGRAPH_DURATION
        self._committed_direction = 1 if player_rect.centerx >= self.rect.centerx else -1

    def _start_strike(self) -> None:
        self.state = BeastState.STRIKE
        self.state_timer = settings.BEAST_STRIKE_DURATION
        self.strike_vx = settings.BEAST_STRIKE_SPEED * self._committed_direction

    def _start_recover(self) -> None:
        self.state = BeastState.RECOVER
        self.state_timer = settings.BEAST_RECOVER_DURATION

    def begin_absorbed(self) -> None:
        """The Beat 4 unlock moment: mirrors Enemy.begin_absorbed exactly,
        kept in sync with the player's own absorb timer."""
        self.state = BeastState.ABSORBED
        self.absorb_timer = settings.ABSORB_DURATION
        self.strike_vx = 0.0

    def update(self, dt: float, solids: list[pygame.Rect], player_rect: pygame.Rect) -> None:
        if self.state is BeastState.ABSORBED:
            self.absorb_timer -= dt
            if self.absorb_timer <= 0:
                self.alive = False
            return

        self._update_jitter(dt)

        self.vy = min(self.vy + settings.GRAVITY_FALL * dt, settings.MAX_FALL_SPEED)
        dx = self.strike_vx * dt if self.state is BeastState.STRIKE else 0.0
        dy = self.vy * dt
        self.x, self.y, collision = move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, solids
        )
        if collision.touched_bottom:
            self.vy = 0.0

        in_range = abs(player_rect.centerx - self.rect.centerx) < settings.BEAST_AGGRO_RADIUS

        if self.state is BeastState.IDLE:
            if in_range:
                self._start_telegraph(player_rect)
        elif self.state is BeastState.TELEGRAPH:
            if not in_range:
                self.state = BeastState.IDLE  # backing off cancels the wind-up
                return
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._start_strike()
        elif self.state is BeastState.STRIKE:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._start_recover()
        elif self.state is BeastState.RECOVER:
            self.state_timer -= dt
            if self.state_timer <= 0:
                if in_range:
                    self._start_telegraph(player_rect)
                else:
                    self.state = BeastState.IDLE

    def _update_jitter(self, dt: float) -> None:
        self._jitter_timer -= dt
        if self._jitter_timer <= 0:
            jitter = settings.BEAST_IDLE_JITTER_PX
            self._jitter_offset = (random.randint(-jitter, jitter), random.randint(-jitter, jitter))
            self._jitter_timer = random.uniform(0.05, 0.3)

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.alive:
            return

        frame = self.sprite.get("idle")
        if self.state is BeastState.TELEGRAPH:
            # The tell grows more intense as the wind-up nears its end --
            # a fair, escalating warning rather than a single flash.
            progress = 1 - (self.state_timer / settings.BEAST_TELEGRAPH_DURATION)
            alpha = round(160 * progress)
            frame = frame.copy()
            flash = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            flash.fill((220, 60, 60, max(0, alpha)))
            frame.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        elif self.state is BeastState.ABSORBED:
            frame = frame.copy()
            fade = max(0.0, self.absorb_timer / settings.ABSORB_DURATION)
            frame.set_alpha(round(255 * fade))

        jitter_x, jitter_y = self._jitter_offset if self.state is not BeastState.ABSORBED else (0, 0)
        draw_x = self.x - (frame.get_width() - self.width) / 2 + jitter_x
        draw_y = self.y - (frame.get_height() - self.height) + jitter_y
        screen_x, screen_y = camera.apply(draw_x, draw_y)
        surface.blit(frame, (round(screen_x), round(screen_y)))
