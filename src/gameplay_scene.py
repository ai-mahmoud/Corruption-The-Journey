"""The playable-room scene: room + player + optional enemy/hazards + camera.

Room-data-driven so one scene class covers every room instead of a
subclass per beat. `room_data` (see data/rooms.py) opts into extra
behavior purely by including certain optional keys:
  - "enemy_spawn" / "enemy_patrol_bounds": spawns an Enemy if present.
  - "hazards": [(x, y), ...] -- spawns a CorruptedPlant at each point.
  - "attack_beast_spawn": (x, y) -- spawns an AttackBeast. Contact during
    its strike costs a heart (see _apply_beast_hit) -- except the first
    time it would take her last heart, which becomes the absorption-unlock
    beat instead of a death.
  - "exit_zone": (x, y, w, h) -- while the player stands in it: if
    "next_room" is also present, transitions to a fresh GameplayScene for
    it; otherwise shows a placeholder overlay (there's nowhere to go yet).
  - "checkpoint_zone": (x, y, w, h) -- entering it (edge-triggered, not
    every frame she stands in it) heals to full and saves to disk.
  - "reveal_zone": (x, y, w, h) -- unlike exit_zone, this always leaves
    GameplayScene entirely: entering it transitions to CutsceneMasterScene
    (Beat 5's ending), not another room.
  - "log_obstacle" + "tutorial_prompt": shows the prompt text once, the
    first time the player nears the obstacle, then never again once
    she's passed it.
  - "music": which looping background track (see src/audio.py's
    TRACK_PATHS) plays in this room; defaults to "exploration" if absent.

Takes a GameProgress alongside room_data -- hearts, whether absorption is
unlocked, and the checkpoint all outlive any single room, so they're
threaded through every transition (next_room, respawn) rather than living
here.
"""

from __future__ import annotations

import pygame

import audio
import save_system
import settings
from attack_beast import AttackBeast
from camera import Camera
from cutscene_master import CutsceneMasterScene
from enemy import Enemy
from game_progress import GameProgress
from hazard import CorruptedPlant
from input import PlayerInput
from level import Room
from pause_menu import PauseMenuScene
from player import Player
from rooms import ROOM_REGISTRY
from scene import Scene
from sprite_utils import load_sprite


class GameplayScene(Scene):
    def __init__(self, room_data: dict, progress: GameProgress):
        self.room = Room(room_data)
        self.room_key = room_data["key"]
        self.progress = progress
        self.camera = Camera(self.room.world_width, self.room.world_height)

        audio.play_track(room_data.get("music", "exploration"))

        self.player = Player(load_sprite("hatchling"), *self.room.player_spawn)

        self.enemy: Enemy | None = None
        if "enemy_spawn" in room_data:
            enemy_sprite = load_sprite("enemy")
            self.enemy = Enemy(
                enemy_sprite, *room_data["enemy_spawn"], room_data["enemy_patrol_bounds"]
            )

        self.hazards: list[CorruptedPlant] = []
        if "hazards" in room_data:
            hazard_sprite = load_sprite("undergrowth")
            self.hazards = [
                CorruptedPlant(hazard_sprite, spawn_x, spawn_y)
                for spawn_x, spawn_y in room_data["hazards"]
            ]

        self.attack_beast: AttackBeast | None = None
        if "attack_beast_spawn" in room_data:
            beast_sprite = load_sprite("enemy")
            self.attack_beast = AttackBeast(beast_sprite, *room_data["attack_beast_spawn"])

        self.exit_zone = pygame.Rect(*room_data["exit_zone"]) if "exit_zone" in room_data else None
        self.next_room_data = room_data.get("next_room")

        self.checkpoint_zone = (
            pygame.Rect(*room_data["checkpoint_zone"]) if "checkpoint_zone" in room_data else None
        )
        self._was_in_checkpoint_zone = False

        self.reveal_zone = (
            pygame.Rect(*room_data["reveal_zone"]) if "reveal_zone" in room_data else None
        )

        self.log_obstacle = (
            pygame.Rect(*room_data["log_obstacle"]) if "log_obstacle" in room_data else None
        )
        self.tutorial_prompt = room_data.get("tutorial_prompt")
        self._log_prompt_cleared = False

        self._heart_sprite = load_sprite("heart")

        self._font = pygame.font.Font(None, 22)
        self._banner_font = pygame.font.Font(None, 26)
        self._jump_pressed_this_frame = False
        self._dodge_pressed_this_frame = False
        self._attack_pressed_this_frame = False
        self._pause_requested = False
        self._unlock_banner_timer = 0.0
        self._respawn_requested = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self._jump_pressed_this_frame = True
            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self._dodge_pressed_this_frame = True
            elif event.key == pygame.K_j:
                self._attack_pressed_this_frame = True
            elif event.key == pygame.K_ESCAPE:
                self._pause_requested = True

    def update(self, dt: float) -> Scene | None:
        if self._pause_requested:
            self._pause_requested = False
            return PauseMenuScene(self)

        player_input = self._read_input()
        self._jump_pressed_this_frame = False
        self._dodge_pressed_this_frame = False
        self._attack_pressed_this_frame = False

        # "Time can slow slightly, for weight" -- but only for the specific
        # absorb triggered by this beast (see GameplayScene docstring: no
        # room mixes an Enemy with an AttackBeast, so is_absorbing alone is
        # unambiguous here).
        actor_dt = dt
        if self.attack_beast is not None and self.player.is_absorbing:
            actor_dt = dt * settings.UNLOCK_SLOW_MOTION_FACTOR

        self.player.update(actor_dt, player_input, self.room.solids)
        self._clamp_player_to_world()

        if self.enemy is not None:
            self.enemy.update(dt, self.room.solids)
            self._check_absorption()

        if self.attack_beast is not None:
            self.attack_beast.update(actor_dt, self.room.solids, self.player.rect)
            self._check_beast_strike()

        self._update_hazards(dt)
        self._update_log_prompt()
        self._update_checkpoint()
        if self._unlock_banner_timer > 0:
            self._unlock_banner_timer = max(0.0, self._unlock_banner_timer - dt)

        player_center_x = self.player.x + self.player.width / 2
        player_center_y = self.player.y + self.player.height / 2
        self.camera.update(player_center_x, player_center_y, dt)

        if self._respawn_requested:
            checkpoint_room = ROOM_REGISTRY[self.progress.checkpoint_room_key]
            return GameplayScene(checkpoint_room, self.progress)

        if self.reveal_zone is not None and self.player.rect.colliderect(self.reveal_zone):
            return CutsceneMasterScene(self.progress)

        if (
            self.exit_zone is not None
            and self.next_room_data is not None
            and self.player.rect.colliderect(self.exit_zone)
        ):
            return GameplayScene(self.next_room_data, self.progress)

        return None

    def _read_input(self) -> PlayerInput:
        keys = pygame.key.get_pressed()
        return PlayerInput(
            move_left=keys[pygame.K_LEFT] or keys[pygame.K_a],
            move_right=keys[pygame.K_RIGHT] or keys[pygame.K_d],
            jump_pressed=self._jump_pressed_this_frame,
            jump_held=keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w],
            dodge_pressed=self._dodge_pressed_this_frame,
            attack_pressed=self._attack_pressed_this_frame,
        )

    def _clamp_player_to_world(self) -> None:
        max_x = self.room.world_width - self.player.width
        self.player.x = max(0.0, min(self.player.x, max_x))

    def _check_absorption(self) -> None:
        assert self.enemy is not None
        if self.player.is_locked or not self.enemy.alive or self.enemy.being_absorbed:
            return
        if self.player.rect.colliderect(self.enemy.rect):
            self.player.start_absorb()
            self.enemy.begin_absorbed()
            audio.play_sfx("absorb")

    def _check_beast_strike(self) -> None:
        assert self.attack_beast is not None
        if not self.attack_beast.is_striking or self.player.is_invulnerable:
            return
        if self.player.rect.colliderect(self.attack_beast.rect):
            direction = 1 if self.player.rect.centerx >= self.attack_beast.rect.centerx else -1
            self._apply_beast_hit(direction)

    def _apply_beast_hit(self, direction: int) -> None:
        # The one scripted exception: the first hit that would take her
        # last heart becomes the absorption-unlock beat, not a death.
        if self.progress.current_hearts <= 1 and not self.progress.absorption_unlocked:
            self._trigger_absorption_unlock()
            return

        self.progress.current_hearts -= 1
        self.player.begin_hit_reaction(direction)  # unchanged -- same knockback/flash/i-frames
        if self.progress.current_hearts <= 0:
            self._trigger_death_and_respawn()

    def _trigger_absorption_unlock(self) -> None:
        assert self.attack_beast is not None
        self.progress.absorption_unlocked = True
        self.progress.max_hearts = settings.LEVEL_UP_MAX_HEARTS
        self.progress.current_hearts = settings.LEVEL_UP_CURRENT_HEARTS
        self.player.start_absorb()  # the existing lock/white-flash beat, reused as-is
        self.attack_beast.begin_absorbed()
        self._unlock_banner_timer = settings.UNLOCK_BANNER_DURATION
        audio.play_sfx("unlock")

    def _trigger_death_and_respawn(self) -> None:
        self.progress.current_hearts = self.progress.max_hearts
        self._respawn_requested = True

    def _update_checkpoint(self) -> None:
        if self.checkpoint_zone is None:
            return
        now_in = self.player.rect.colliderect(self.checkpoint_zone)
        if now_in and not self._was_in_checkpoint_zone:
            self.progress.current_hearts = self.progress.max_hearts
            self.progress.checkpoint_room_key = self.room_key
            save_system.save_game(self.progress)
            audio.play_sfx("checkpoint")
        self._was_in_checkpoint_zone = now_in

    def _update_hazards(self, dt: float) -> None:
        for hazard in self.hazards:
            hazard.update(dt, self.player.rect)
            if hazard.alive and not hazard.dying and self.player.rect.colliderect(hazard.rect):
                hazard.begin_dying()

    def _update_log_prompt(self) -> None:
        if self.log_obstacle is None or self._log_prompt_cleared:
            return
        if self.player.rect.left > self.log_obstacle.right:
            self._log_prompt_cleared = True

    def _should_show_log_prompt(self) -> bool:
        if self.log_obstacle is None or self._log_prompt_cleared:
            return False
        near_distance = 150
        return abs(self.player.rect.centerx - self.log_obstacle.centerx) < near_distance

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.COLOR_BACKGROUND)
        self.room.draw(surface, self.camera)
        if self.enemy is not None:
            self.enemy.draw(surface, self.camera)
        if self.attack_beast is not None:
            self.attack_beast.draw(surface, self.camera)
        for hazard in self.hazards:
            hazard.draw(surface, self.camera)
        self.player.draw(surface, self.camera)

        if self._should_show_log_prompt():
            self._draw_prompt_above_player(surface)
        if (
            self.exit_zone is not None
            and self.next_room_data is None
            and self.player.rect.colliderect(self.exit_zone)
        ):
            self._draw_exit_overlay(surface)

        self._draw_hearts_hud(surface)
        if self._unlock_banner_timer > 0:
            self._draw_unlock_banner(surface)

    def _draw_hearts_hud(self, surface: pygame.Surface) -> None:
        for i in range(self.progress.max_hearts):
            frame_name = "full" if i < self.progress.current_hearts else "empty"
            frame = self._heart_sprite.get(frame_name)
            x = settings.HEART_ICON_MARGIN + i * settings.HEART_ICON_SPACING
            y = settings.HEART_ICON_MARGIN
            surface.blit(frame, (x, y))

    def _draw_unlock_banner(self, surface: pygame.Surface) -> None:
        fade_tail = 0.6
        alpha = 255 if self._unlock_banner_timer >= fade_tail else round(
            255 * (self._unlock_banner_timer / fade_tail)
        )
        alpha = max(0, alpha)

        icon_surface = pygame.Surface((26, 26), pygame.SRCALPHA)
        pygame.draw.circle(icon_surface, (235, 225, 190, alpha), (13, 13), 9)
        icon_rect = icon_surface.get_rect(center=(settings.WINDOW_WIDTH // 2, 54))
        surface.blit(icon_surface, icon_rect)

        text_surface = self._banner_font.render("-- absorption unlocked --", True, (235, 230, 210))
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(settings.WINDOW_WIDTH // 2, 88))
        surface.blit(text_surface, text_rect)

    def _draw_prompt_above_player(self, surface: pygame.Surface) -> None:
        text_surface = self._font.render(self.tutorial_prompt, True, (230, 230, 230))
        player_top_x, player_top_y = self.camera.apply(
            self.player.x + self.player.width / 2, self.player.y
        )
        rect = text_surface.get_rect(midbottom=(round(player_top_x), round(player_top_y) - 12))
        surface.blit(text_surface, rect)

    def _draw_exit_overlay(self, surface: pygame.Surface) -> None:
        text_surface = self._font.render("-- end of vertical slice --", True, (230, 230, 230))
        rect = text_surface.get_rect(center=(settings.WINDOW_WIDTH // 2, 60))
        surface.blit(text_surface, rect)
