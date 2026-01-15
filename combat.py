import pygame
import sys
import os
import random
from settings import *

# States
STATE_INTRO = 'INTRO'
STATE_PLAYER_TURN = 'PLAYER_TURN'
STATE_PLAYER_ACTION = 'PLAYER_ACTION'
STATE_ENEMY_TURN = 'ENEMY_TURN'
STATE_ENEMY_ACTION = 'ENEMY_ACTION'
STATE_VICTORY_MENU = 'VICTORY_MENU' 
STATE_WIN = 'WIN'
STATE_LOSE = 'LOSE'

class CombatSystem:
    def __init__(self, screen=None):
        self.screen = screen if screen else pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.active = False
        self.font = get_font(24)
        self.big_font = get_font(40)
        self.assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        
        # --- Robust Asset Loader V2 (Rolled Back) ---
        def load(name, scale=None, flip=False):
            path = os.path.join(self.assets_dir, name)
            try:
                img = pygame.image.load(path)
                
                # Check for existing transparency
                has_transparency = False
                if img.get_flags() & pygame.SRCALPHA:
                     if img.get_at((0,0)).a == 0: has_transparency = True
                
                if has_transparency:
                    img = img.convert_alpha()
                else:
                    # Force opacity logic
                    img = img.convert() 
                    col = img.get_at((0, 0))
                    img.set_colorkey(col)

                # Scale
                if scale: 
                    img = pygame.transform.scale(img, scale)
                
                # Flip
                if flip: 
                    img = pygame.transform.flip(img, True, False)
                    
                return img
            except Exception as e:
                print(f"Failed to load {name}: {e}")
                s = pygame.Surface(scale if scale else (100, 100))
                s.fill(COLOR_RED)
                return s

        self.bg = load('bg_combat_forest.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Sprites (Scaled Up to 300px+)
        self.spr_player_idle = load('spr_hatchling.png', (300, 300))
        self.spr_player_attack = load('spr_hatchling_attack.png', (350, 300))
        self.spr_player_hit = load('spr_hatchling_hit.png', (300, 300))
        
        # Wolf (Flip logic preserved)
        self.spr_enemy_idle = load('spr_wolf.png', (350, 350), flip=True)
        self.spr_enemy_attack = load('spr_wolf_attack.png', (400, 350), flip=False)
        self.spr_enemy_hit = load('spr_wolf_hit.png', (350, 350), flip=False)

        # Combat Data
        self.state = STATE_INTRO
        self.turn_timer = 0
        self.combat_log = []
        
        self.player = {'hp': 100, 'max_hp': 100, 'charge': 0}
        self.enemy = None
        
        # Animation State
        self.anim_timer = 0
        self.shake_offset = (0, 0)
        self.flash_alpha = 0
        self.victory_selection = 0 

    def start_combat(self, enemy_type="Corrupted Wolf"):
        self.active = True
        self.state = STATE_INTRO
        self.turn_timer = 0
        self.combat_log = [f"{enemy_type} emerges!"]
        
        hp = 60 if enemy_type == "Corrupted Wolf" else 80
        self.enemy = {
            'name': enemy_type,
            'hp': hp,
            'max_hp': hp,
            'charge': 0,
            'speed': 1.0
        }
        self.player['charge'] = 0
        self.victory_selection = 0

    def add_log(self, text):
        self.combat_log.insert(0, text)
        if len(self.combat_log) > 4: self.combat_log.pop()

    def handle_input(self, event):
        if not self.active: return
        
        if self.state == STATE_PLAYER_TURN and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.state = STATE_PLAYER_ACTION
                self.anim_timer = 30
                self.current_action = 'ATTACK'
            elif event.key == pygame.K_d:
                self.state = STATE_PLAYER_ACTION
                self.anim_timer = 30
                self.current_action = 'ABSORB'
                
        elif self.state == STATE_VICTORY_MENU and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.victory_selection = 0
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.victory_selection = 1
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_e:
                 if self.victory_selection == 0: # Consume
                     heal_amount = 30
                     self.player['hp'] = min(self.player['max_hp'], self.player['hp'] + heal_amount)
                     self.add_log(f"Consumed essence. Healed {heal_amount} HP.")
                     self.state = STATE_WIN 
                 else: # Skip
                     self.add_log("Left the essence behind.")
                     self.state = STATE_WIN

    def update(self):
        if not self.active: return None
        
        # Shake Decay
        if self.shake_offset != (0, 0):
            self.shake_offset = (
                int(self.shake_offset[0] * 0.8), 
                int(self.shake_offset[1] * 0.8)
            )
            if abs(self.shake_offset[0]) < 2: self.shake_offset = (0, 0)

        # Flash Decay
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 10)

        # State Machine
        if self.state == STATE_INTRO:
            self.turn_timer += 1
            if self.turn_timer > 60:
                self.state = STATE_PLAYER_TURN
                
        elif self.state == STATE_PLAYER_TURN:
            self.player['charge'] = min(100, self.player['charge'] + 1.0) 
            
        elif self.state == STATE_PLAYER_ACTION:
            self.anim_timer -= 1
            if self.anim_timer == 15: # Impact
                if self.current_action == 'ATTACK':
                    dmg = random.randint(15, 20)
                    self.enemy['hp'] -= dmg
                    self.add_log(f"You hit {self.enemy['name']} for {dmg}!")
                    self.shake_offset = (10, 5)
                    self.flash_alpha = 150
                    
                    if self.enemy['hp'] <= 0:
                        self.state = STATE_VICTORY_MENU 
                        self.anim_timer = 0 
                        return 
                        
                elif self.current_action == 'ABSORB':
                    heal = random.randint(5, 10)
                    self.player['hp'] = min(self.player['max_hp'], self.player['hp'] + heal)
                    self.add_log(f"Absorbed {heal} HP!")
                    self.player['charge'] = 0
            
            if self.anim_timer <= 0:
                self.state = STATE_ENEMY_TURN
                
        elif self.state == STATE_ENEMY_TURN:
            self.enemy['charge'] += self.enemy['speed'] * 1.5
            if self.enemy['charge'] >= 100:
                self.enemy['charge'] = 0
                self.state = STATE_ENEMY_ACTION
                self.anim_timer = 40
                
        elif self.state == STATE_ENEMY_ACTION:
            self.anim_timer -= 1
            if self.anim_timer == 20: # Strike
                dmg = random.randint(5, 12)
                self.player['hp'] -= dmg
                self.add_log(f"{self.enemy['name']} bites you for {dmg}!")
                self.shake_offset = (-10, 5)
                self.flash_alpha = 150
                
                if self.player['hp'] <= 0:
                    self.state = STATE_LOSE
                    return 
            
            if self.anim_timer <= 0:
                self.state = STATE_PLAYER_TURN
        
        elif self.state == STATE_VICTORY_MENU:
             pass 
             
        elif self.state == STATE_WIN:
            return "WIN"

        elif self.state == STATE_LOSE:
            return "LOSE"

        return None

    def draw(self, surface=None):
        target = surface if surface else self.screen
        
        sx, sy = self.shake_offset
        
        # --- LAYER 1: Background ---
        target.blit(self.bg, (0 + sx, 0 + sy))
        
        # --- LAYER 2: Enemy (Right) ---
        if self.state != STATE_WIN and self.enemy['hp'] > 0:
            e_img = self.spr_enemy_idle
            ex, ey = 850, 250 # Adjusted X for 350px width
            
            if self.state == STATE_ENEMY_ACTION:
                 e_img = self.spr_enemy_attack
                 if self.anim_timer > 20:
                      ex -= (40 - self.anim_timer) * 20 # Lunge Left
                 else:
                      ex -= self.anim_timer * 20
            
            if self.state == STATE_PLAYER_ACTION and self.anim_timer < 15 and self.current_action == 'ATTACK':
                 e_img = self.spr_enemy_hit
                 ex += 30 # Knockback Right
            
            target.blit(e_img, (ex + sx, ey + sy))

        # --- LAYER 3: Player (Left) ---
        p_img = self.spr_player_idle
        px, py = 100, 300 # Adjusted X for 300px width
        
        if self.state == STATE_PLAYER_ACTION:
            if self.current_action == 'ATTACK':
                 p_img = self.spr_player_attack
                 if self.anim_timer > 15: # Lunging Right
                      px += (30 - self.anim_timer) * 15
                 else: # Returning
                      px += self.anim_timer * 15
        
        if self.state == STATE_ENEMY_ACTION and self.anim_timer < 20: # Hit reaction
             p_img = self.spr_player_hit
             px -= 20 # Knockback Left
             
        target.blit(p_img, (px + sx, py + sy))

        # --- LAYER 4: UI / Flash ---
        ui_y = 550
        
        # Player Bar
        self.draw_bar(target, 50, ui_y, 250, 20, self.player['hp'], self.player['max_hp'], COLOR_GREEN, "HP")
        self.draw_bar(target, 50, ui_y + 30, 250, 10, self.player['charge'], 100, COLOR_GOLD, "")
        
        # Enemy Bar
        if self.state != STATE_WIN:
             self.draw_bar(target, 800, 100, 250, 20, self.enemy['hp'], self.enemy['max_hp'], COLOR_RED, self.enemy['name'])
             self.draw_bar(target, 800, 130, 250, 10, self.enemy['charge'], 100, COLOR_GOLD, "")

        # Menu / Log
        if self.state == STATE_VICTORY_MENU:
             menu_bg = pygame.Surface((400, 200))
             menu_bg.fill((0, 0, 0))
             menu_bg.set_alpha(200)
             rect = menu_bg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
             target.blit(menu_bg, rect)
             
             title = self.big_font.render("VICTORY", True, COLOR_GOLD)
             target.blit(title, (rect.centerx - title.get_width()//2, rect.top + 20))
             
             opt1_col = COLOR_TEXT_CORRUPTED if self.victory_selection == 0 else COLOR_WHITE
             opt2_col = COLOR_TEXT_CORRUPTED if self.victory_selection == 1 else COLOR_WHITE
             
             t1 = self.font.render("> Consume (+30 HP)" if self.victory_selection == 0 else "  Consume (+30 HP)", True, opt1_col)
             t2 = self.font.render("> Skip" if self.victory_selection == 1 else "  Skip", True, opt2_col)
             
             target.blit(t1, (rect.centerx - 100, rect.top + 80))
             target.blit(t2, (rect.centerx - 100, rect.top + 120))
             
        elif self.state == STATE_PLAYER_TURN:
            menu_text = self.big_font.render("[A] ATTACK    [D] ABSORB", True, COLOR_GOLD)
            target.blit(menu_text, (50, ui_y + 60))

        # Log
        for i, line in enumerate(self.combat_log):
             col = (200, 200, 200)
             txt = self.font.render(line, True, col)
             target.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 20 + i * 25))
             
        # Flash
        if self.flash_alpha > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash.fill((255, 255, 255))
            flash.set_alpha(self.flash_alpha)
            target.blit(flash, (0,0))

    def draw_bar(self, surf, x, y, w, h, val, max_val, color, label=None):
        pygame.draw.rect(surf, (20, 20, 20), (x, y, w, h))
        ratio = max(0, min(1, val / max_val))
        pygame.draw.rect(surf, color, (x, y, w * ratio, h))
        pygame.draw.rect(surf, (100, 100, 100), (x, y, w, h), 2)
        if label:
            l = self.font.render(label, True, (200, 200, 200))
            surf.blit(l, (x, y - 25))
