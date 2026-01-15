import pygame
import os
import random
from settings import *

class Cutscene:
    def __init__(self, screen):
        self.screen = screen
        self.finished = False
        self.start_time = pygame.time.get_ticks()
        
        # Load Assets
        self.assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        
        # Helper to load and scale
        def load_image(name, scale=None):
            path = os.path.join(self.assets_dir, name)
            try:
                img = pygame.image.load(path).convert_alpha()
                if scale:
                    img = pygame.transform.scale(img, scale)
                return img
            except Exception as e:
                print(f"Warning: Could not load {name}. Using placeholder. Error: {e}")
                # Fallback placeholder
                surf = pygame.Surface(scale if scale else (64, 64))
                surf.fill(COLOR_RED)
                return surf

        self.bg = load_image('bg_forest.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.egg_img = load_image('spr_egg.png', (128, 128))
        self.hatchling_img = load_image('spr_hatchling.png', (64, 64))
        
        # Animation State
        self.stage = 0 
        # 0: Wait/Silence
        # 1: Egg appears/Shake
        # 2: Crack sounds/Visuals
        # 3: Hatch/Flash
        # 4: Fade out/End

        self.shake_offset = (0, 0)
        self.particles = []

    def spawn_particles(self, x, y, count=5, color=(200, 200, 200)):
         for _ in range(count):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-5, -1),
                'life': random.randint(20, 50),
                'color': color
            })

    def update(self):
        current_time = pygame.time.get_ticks() - self.start_time
        
        # Update particles
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2 # Gravity
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]

        # Timing Sequence
        if current_time < 2000:
            self.stage = 0
            self.shake_offset = (0, 0)
        elif current_time < 5000:
            self.stage = 1
            # Simple shake effect
            if (current_time // 100) % 2 == 0:
                self.shake_offset = (2, 0)
            else:
                self.shake_offset = (-2, 0)
        elif current_time < 7000:
            self.stage = 2
            # More intense shake
            if (current_time // 50) % 2 == 0:
                self.shake_offset = (random.randint(-5, 5), random.randint(-5, 5))
            else:
                self.shake_offset = (0, 0)
                
            # Random particle burst
            if random.random() < 0.1:
                cx = SCREEN_WIDTH // 2
                cy = SCREEN_HEIGHT // 2
                self.spawn_particles(cx, cy, 2, (100, 50, 100)) # Purple chips

        elif current_time < 9000:
            if self.stage != 3:
                # One time burst
                cx = SCREEN_WIDTH // 2
                cy = SCREEN_HEIGHT // 2
                self.spawn_particles(cx, cy, 30, (255, 255, 255))
                
            self.stage = 3
            self.shake_offset = (0,0)
        else:
            self.stage = 4
            self.finished = True

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        
        if self.stage >= 0:
            # Draw Background (dimmed)
            self.screen.blit(self.bg, (0, 0))
            
            # Dark Overlay for atmosphere
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

        # Center coordinates
        cx = SCREEN_WIDTH // 2 - 64 # Half of egg width (128/2)
        cy = SCREEN_HEIGHT // 2 - 64

        if self.stage in [1, 2]:
            # Draw Egg with offset
            draw_pos = (cx + self.shake_offset[0], cy + self.shake_offset[1])
            self.screen.blit(self.egg_img, draw_pos)

        elif self.stage == 3:
            # Draw Hatchling
            hx = SCREEN_WIDTH // 2 - 32 # Half of hatchling width (64/2)
            hy = SCREEN_HEIGHT // 2 - 32
            
            # Draw shell fragments (simulated) at bottom
            # pygame.draw.circle(self.screen, (100, 80, 120), (cx + 20, cy + 100), 10)
            
            self.screen.blit(self.hatchling_img, (hx, hy))
            
            # Flash white fade out
            flash_time = pygame.time.get_ticks() - (self.start_time + 7000)
            alpha = max(0, 255 - flash_time // 2)
            if alpha > 0:
                flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash.fill(COLOR_WHITE)
                flash.set_alpha(alpha)
                self.screen.blit(flash, (0,0))

        # Particles
        for p in self.particles:
             pygame.draw.circle(self.screen, p['color'], (int(p['x']), int(p['y'])), 2)

        # Text overlay
        if self.stage == 0:
             font = get_font(40)
             text = font.render("", True, COLOR_WHITE) 
             # Keeping it silent for atmosphere as per "Corruption" feel
             # or minimal text
             text = font.render("A new cycle begins...", True, (200, 200, 200))
             self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        # Test loop
        clock = pygame.time.Clock()
        while not self.finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
            
            self.update()
            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    cutscene = Cutscene(screen)
    cutscene.run()
    pygame.quit()
