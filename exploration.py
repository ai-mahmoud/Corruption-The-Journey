import pygame
import sys
import os
import random
from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, scale=None):
        super().__init__()
        self.assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        self.image = self.load_image(image_path, scale)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-10, -10)

    def load_image(self, name, scale=None):
        path = os.path.join(self.assets_dir, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        except Exception as e:
            print(f"Failed to load {name}: {e}")
            surf = pygame.Surface(scale if scale else (40, 40))
            surf.fill(COLOR_RED)
            return surf

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 'spr_hatchling.png', (64, 64))
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 4
        
        self.hitbox = self.rect.inflate(-20, -30)
        self.hitbox.center = self.rect.center
        self.steps_taken = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity.y = self.speed

        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * self.speed
            self.steps_taken += 1

    def update(self, obstacles, map_width, map_height):
        # Move X
        self.hitbox.x += self.velocity.x
        for wall in obstacles:
            if self.hitbox.colliderect(wall.hitbox):
                if self.velocity.x > 0: 
                    self.hitbox.right = wall.hitbox.left
                if self.velocity.x < 0: 
                    self.hitbox.left = wall.hitbox.right
        
        # Move Y
        self.hitbox.y += self.velocity.y
        for wall in obstacles:
            if self.hitbox.colliderect(wall.hitbox):
                if self.velocity.y > 0: 
                    self.hitbox.bottom = wall.hitbox.top
                if self.velocity.y < 0: 
                    self.hitbox.top = wall.hitbox.bottom
        
        # Clamp to Map Bounds
        self.hitbox.clamp_ip(pygame.Rect(0, 0, map_width, map_height))
        
        # Sync rect with hitbox
        self.rect.center = self.hitbox.center
                    
    def draw(self, surface, camera):
        # Shadow
        shadow_rect = pygame.Rect(0, 0, 40, 10)
        shadow_rect.centerx = self.rect.centerx
        shadow_rect.top = self.rect.bottom - 5
        cam_shadow = camera.apply_rect(shadow_rect)
        pygame.draw.ellipse(surface, (0,0,0,100), cam_shadow)
        
        surface.blit(self.image, camera.apply(self))

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        # Calculate target position (centered)
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        
        # Clamp camera to map bounds CORRECTLY
        # Camera needs to stop when it hits the edge of the map
        # min limit: 0 (camera left edge at map 0) -> x cannot be > 0
        # max limit: -(map_width - screen_width) -> x cannot be < this
        
        x = min(0, max(-(self.width - SCREEN_WIDTH), x))
        y = min(0, max(-(self.height - SCREEN_HEIGHT), y))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Obstacle(Entity):
    def __init__(self, x, y, type_name):
        if type_name == 'tree':
            super().__init__(x, y, 'spr_tree.png', (96, 128))
            self.hitbox = pygame.Rect(x + 30, y + 80, 36, 40)
        elif type_name == 'rock':
            super().__init__(x, y, 'spr_rock.png', (64, 64))
            self.hitbox = self.rect.inflate(-10, -20)

class Exploration:
    def __init__(self, screen=None):
        self.screen = screen if screen else pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.map_width = 1600
        self.map_height = 1200
        
        self.player = Player(400, 300)
        self.obstacles = pygame.sprite.Group()
        self.camera = Camera(self.map_width, self.map_height)
        
        self.assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        try:
             self.bg_tile = pygame.image.load(os.path.join(self.assets_dir, 'bg_forest.png')).convert()
        except:
             self.bg_tile = pygame.Surface((128, 128))
             self.bg_tile.fill((30, 20, 40))
        
        self.generate_map()
        
        # Encounter system
        self.encounter_cooldown = 0
        self.trigger_encounter = False
        self.encounter_type = None

    def generate_map(self):
        for i in range(30):
            wx = random.randint(0, self.map_width - 100)
            wy = random.randint(0, self.map_height - 100)
            self.obstacles.add(Obstacle(wx, wy, 'tree'))
            
        for i in range(15):
            rx = random.randint(0, self.map_width - 100)
            ry = random.randint(0, self.map_height - 100)
            self.obstacles.add(Obstacle(rx, ry, 'rock'))
            
        spawn_zone = pygame.Rect(300, 200, 200, 200)
        for obs in self.obstacles:
            if obs.rect.colliderect(spawn_zone):
                obs.kill()

    def update(self):
        self.player.handle_input()
        self.player.update(self.obstacles, self.map_width, self.map_height)
        self.camera.update(self.player)
        
        # --- Encounter Logic ---
        # 1. Random Encounters (Dynamic) relative to Danger Zone (x > 600)
        if self.player.rect.x > 600:
            if self.encounter_cooldown > 0:
                self.encounter_cooldown -= 1
            else:
                # Only check if moving
                if self.player.velocity.length() > 0:
                     # 0.5% chance per frame (~1 encounter per 4-5 sec of walking)
                     if random.random() < 0.005: 
                        self.trigger_encounter = True
                        self.encounter_type = "Corrupted Wolf"
                        self.encounter_cooldown = 300 # 5 seconds immunity

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        
        # 1. Back Layer (Tiled Ground)
        start_x = -(self.camera.camera.x % self.bg_tile.get_width())
        start_y = -(self.camera.camera.y % self.bg_tile.get_height())
        cols = (SCREEN_WIDTH // self.bg_tile.get_width()) + 2
        rows = (SCREEN_HEIGHT // self.bg_tile.get_height()) + 2
        
        for r in range(rows):
            for c in range(cols):
                self.screen.blit(self.bg_tile, (start_x + c * self.bg_tile.get_width(), start_y + r * self.bg_tile.get_height()))

        # 2. Main Layer (Sprites Sorted by Y for depth)
        all_sprites = list(self.obstacles) + [self.player]
        all_sprites.sort(key=lambda s: s.rect.bottom)
        
        for sprite in all_sprites:
            if isinstance(sprite, Player):
                sprite.draw(self.screen, self.camera)
            else:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
