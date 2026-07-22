"""The Hatchling: run/jump movement feel, plus the absorption interaction.

Frame order in update() matters for coyote time and jump buffering to work
correctly:
  1. Timers (coyote/jump-buffer) tick down.
  2. A buffered jump is consumed the instant both timers allow it.
  3. Horizontal accel/decel is applied.
  4. Gravity (with jump-cut for variable height) is applied.
  5. The move is resolved against solids.
  6. Ground state and timers are refreshed from the collision result.
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

import settings
from input import PlayerInput
from physics import move_and_collide
from sprite_utils import SpriteSheet


class PlayerState(Enum):
    IDLE = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()
    ABSORBING = auto()
    DODGE = auto()
    STUMBLE = auto()
    HIT = auto()


_LOCKED_STATES = (PlayerState.ABSORBING, PlayerState.DODGE, PlayerState.STUMBLE, PlayerState.HIT)


class Player:
    def __init__(self, sprite: SpriteSheet, spawn_x: float, spawn_y: float):
        self.sprite = sprite
        # Collision size is fixed (settings.PLAYER_COLLISION_*), independent
        # of the sprite's actual pixel size -- see settings.py.
        self.width = settings.PLAYER_COLLISION_WIDTH
        self.height = settings.PLAYER_COLLISION_HEIGHT

        # spawn position is her feet; store the top-left corner for physics.
        self.x = float(spawn_x - self.width / 2)
        self.y = float(spawn_y - self.height)

        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1

        self.on_ground = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.dodge_cooldown_timer = 0.0

        self.state = PlayerState.IDLE
        self.absorb_timer = 0.0
        self.dodge_timer = 0.0
        self.stumble_timer = 0.0
        self.hit_timer = 0.0

        self._run_anim_timer = 0.0
        self._run_frame_is_a = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    @property
    def is_absorbing(self) -> bool:
        return self.state is PlayerState.ABSORBING

    @property
    def is_locked(self) -> bool:
        """True while she's mid-absorption/dodge/stumble/hit-reaction --
        states with their own physics that normal control shouldn't touch."""
        return self.state in _LOCKED_STATES

    @property
    def is_invulnerable(self) -> bool:
        return self.state in (PlayerState.DODGE, PlayerState.HIT)

    def start_absorb(self) -> None:
        """Begin the brief, movement-locking absorption beat."""
        self.state = PlayerState.ABSORBING
        self.absorb_timer = settings.ABSORB_DURATION
        self.vx = 0.0

    def _start_dodge(self) -> None:
        self.state = PlayerState.DODGE
        self.dodge_timer = settings.DODGE_DURATION
        self.vx = settings.DODGE_SPEED * self.facing
        self.vy = 0.0

    def begin_stumble(self) -> None:
        """She has no attack yet -- reaching for one anyway leaves her
        briefly locked and, unlike DODGE, vulnerable."""
        self.state = PlayerState.STUMBLE
        self.stumble_timer = settings.STUMBLE_DURATION
        self.vx = 0.0

    def begin_hit_reaction(self, direction: int) -> None:
        """A beast's strike connected: knockback away from it, then a brief
        i-frame window so the same strike can't hit her again while reeling."""
        self.state = PlayerState.HIT
        self.hit_timer = settings.HIT_DURATION
        self.vx = settings.HIT_KNOCKBACK_SPEED * direction

    def update(self, dt: float, input_state: PlayerInput, solids: list[pygame.Rect]) -> None:
        self.dodge_cooldown_timer = max(0.0, self.dodge_cooldown_timer - dt)

        if self.state is PlayerState.ABSORBING:
            self._update_absorbing(dt, solids)
            return
        if self.state is PlayerState.DODGE:
            self._update_dodge(dt, solids)
            return
        if self.state is PlayerState.HIT:
            self._update_hit(dt, solids)
            return
        if self.state is PlayerState.STUMBLE:
            self._update_stumble(dt, solids)
            return

        if input_state.dodge_pressed and self.dodge_cooldown_timer <= 0:
            self._start_dodge()
            return
        if input_state.attack_pressed:
            self.begin_stumble()
            return

        self._update_jump_timers(dt, input_state)
        self._update_horizontal(dt, input_state)
        self._update_vertical(dt, input_state)

        dx = self.vx * dt
        dy = self.vy * dt
        self.x, self.y, collision = move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, solids
        )

        if collision.touched_top and self.vy < 0:
            self.vy = 0.0

        self.on_ground = collision.touched_bottom
        if self.on_ground:
            self.vy = 0.0
            self.coyote_timer = settings.COYOTE_TIME

        self._update_animation_state()
        self._update_run_animation(dt)

    def _update_run_animation(self, dt: float) -> None:
        if self.state is not PlayerState.RUN:
            self._run_anim_timer = 0.0
            self._run_frame_is_a = True
            return
        self._run_anim_timer += dt
        if self._run_anim_timer >= settings.RUN_FRAME_DURATION:
            self._run_anim_timer -= settings.RUN_FRAME_DURATION
            self._run_frame_is_a = not self._run_frame_is_a

    def _update_jump_timers(self, dt: float, input_state: PlayerInput) -> None:
        self.coyote_timer = max(0.0, self.coyote_timer - dt)
        self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        if input_state.jump_pressed:
            self.jump_buffer_timer = settings.JUMP_BUFFER_TIME

        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            self.vy = settings.JUMP_VELOCITY
            self.jump_buffer_timer = 0.0
            self.coyote_timer = 0.0
            self.on_ground = False

    def _update_horizontal(self, dt: float, input_state: PlayerInput) -> None:
        direction = 0
        if input_state.move_left:
            direction -= 1
        if input_state.move_right:
            direction += 1

        accel = settings.MOVE_ACCEL if self.on_ground else settings.AIR_ACCEL
        decel = settings.MOVE_DECEL if self.on_ground else settings.AIR_ACCEL

        if direction != 0:
            self.vx += direction * accel * dt
            self.vx = max(-settings.MAX_RUN_SPEED, min(settings.MAX_RUN_SPEED, self.vx))
            self.facing = direction
        elif self.vx > 0:
            self.vx = max(0.0, self.vx - decel * dt)
        elif self.vx < 0:
            self.vx = min(0.0, self.vx + decel * dt)

    def _update_vertical(self, dt: float, input_state: PlayerInput) -> None:
        # Variable jump height: while still ascending, releasing the jump
        # key rapidly damps the upward velocity instead of waiting for
        # gravity alone, so a tap yields a short hop and a hold a full jump.
        if self.vy < 0 and not input_state.jump_held:
            self.vy *= settings.JUMP_CUT_MULTIPLIER

        gravity = settings.GRAVITY_RISE if self.vy < 0 else settings.GRAVITY_FALL
        self.vy = min(self.vy + gravity * dt, settings.MAX_FALL_SPEED)

    def _update_animation_state(self) -> None:
        if not self.on_ground:
            self.state = PlayerState.JUMP if self.vy < 0 else PlayerState.FALL
        elif abs(self.vx) > 1.0:
            self.state = PlayerState.RUN
        else:
            self.state = PlayerState.IDLE

    def _update_absorbing(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.absorb_timer -= dt

        # Gravity keeps applying so she settles naturally rather than
        # hovering, but horizontal input is ignored -- this is the "lock".
        self.vy = min(self.vy + settings.GRAVITY_FALL * dt, settings.MAX_FALL_SPEED)
        dy = self.vy * dt
        self.x, self.y, collision = move_and_collide(
            self.x, self.y, self.width, self.height, 0.0, dy, solids
        )
        if collision.touched_bottom:
            self.vy = 0.0
            self.on_ground = True

        if self.absorb_timer <= 0:
            self.state = PlayerState.IDLE

    def _update_dodge(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.dodge_timer -= dt

        # Gravity is suspended for a clean flat burst rather than an arc.
        dx = self.vx * dt
        self.x, self.y, collision = move_and_collide(
            self.x, self.y, self.width, self.height, dx, 0.0, solids
        )
        if collision.touched_left or collision.touched_right:
            self.vx = 0.0  # bonked a wall mid-dodge

        if self.dodge_timer <= 0:
            self.vx = 0.0
            self.dodge_cooldown_timer = settings.DODGE_COOLDOWN
            self.state = PlayerState.IDLE

    def _update_stumble(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.stumble_timer -= dt

        # Same shape as _update_absorbing: gravity continues, horizontal
        # input is ignored -- she's just standing there, exposed.
        self.vy = min(self.vy + settings.GRAVITY_FALL * dt, settings.MAX_FALL_SPEED)
        dy = self.vy * dt
        self.x, self.y, collision = move_and_collide(
            self.x, self.y, self.width, self.height, 0.0, dy, solids
        )
        if collision.touched_bottom:
            self.vy = 0.0
            self.on_ground = True

        if self.stumble_timer <= 0:
            self.state = PlayerState.IDLE

    def _update_hit(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.hit_timer -= dt

        self.vy = min(self.vy + settings.GRAVITY_FALL * dt, settings.MAX_FALL_SPEED)
        # Let the knockback decay so she doesn't slide forever.
        if self.vx > 0:
            self.vx = max(0.0, self.vx - settings.MOVE_DECEL * dt)
        elif self.vx < 0:
            self.vx = min(0.0, self.vx + settings.MOVE_DECEL * dt)

        dx = self.vx * dt
        dy = self.vy * dt
        self.x, self.y, collision = move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, solids
        )
        if collision.touched_bottom:
            self.vy = 0.0
            self.on_ground = True

        if self.hit_timer <= 0:
            self.state = PlayerState.IDLE

    @staticmethod
    def _tinted(frame: pygame.Surface, color: tuple[int, int, int], alpha: float) -> pygame.Surface:
        """A copy of `frame` with a flat color additively flashed over it,
        fading as `alpha` drops -- used for every brief reaction beat below."""
        frame = frame.copy()
        flash = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        flash.fill((*color, max(0, round(alpha))))
        frame.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return frame

    def _pose_frame_name(self) -> str:
        """Which sprite-sheet frame matches her current motion. The locked
        reaction states (absorbing/dodge/stumble/hit) all read from "idle"
        as their base pose -- only the tint/alpha in draw() distinguishes
        them, matching how those states already behaved before real
        animation frames existed."""
        if self.state is PlayerState.JUMP:
            return "jump"
        if self.state is PlayerState.FALL:
            return "fall"
        if self.state is PlayerState.RUN:
            return "run_a" if self._run_frame_is_a else "run_b"
        return "idle"

    def draw(self, surface: pygame.Surface, camera) -> None:
        frame = self.sprite.get(self._pose_frame_name())
        if self.is_absorbing:
            # A brief fading white flash so the beat reads as a deliberate
            # event rather than a silent, instant deletion.
            frame = self._tinted(frame, (255, 255, 255), 160 * (self.absorb_timer / settings.ABSORB_DURATION))
        elif self.state is PlayerState.STUMBLE:
            # Dim/washed-out -- reaching for a tool she doesn't have.
            frame = self._tinted(frame, (150, 150, 150), 130 * (self.stumble_timer / settings.STUMBLE_DURATION))
        elif self.state is PlayerState.HIT:
            frame = self._tinted(frame, (220, 60, 60), 170 * (self.hit_timer / settings.HIT_DURATION))
        elif self.state is PlayerState.DODGE:
            # A translucent "ghost" reads as briefly intangible.
            frame = frame.copy()
            frame.set_alpha(140)

        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)

        # Center the sprite horizontally over the (fixed-size) collision
        # box and align their bottoms (feet), since the sprite's own pixel
        # size no longer has to match the collision box.
        draw_x = self.x - (frame.get_width() - self.width) / 2
        draw_y = self.y - (frame.get_height() - self.height)
        screen_x, screen_y = camera.apply(draw_x, draw_y)
        surface.blit(frame, (round(screen_x), round(screen_y)))
