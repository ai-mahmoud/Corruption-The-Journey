import pygame
import sys
from settings import *
from cutscene import Cutscene
from exploration import Exploration
from dialogue import DialogueSystem
from combat import CombatSystem

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Corruption: The Journey (Vertical Slice)")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # States: 'CUTSCENE', 'EXPLORE', 'DIALOGUE', 'COMBAT'
        self.state = 'CUTSCENE'
        
        # Modules
        self.cutscene = Cutscene(self.screen)
        self.exploration = Exploration(self.screen)
        self.dialogue = DialogueSystem(self.screen)
        self.combat = CombatSystem(self.screen)
        
        # Game Flags
        self.flags = {
            'intro_cutscene_done': False,
            'met_guide': False,
            'first_combat_done': False
        }

    def update(self):
        if self.state == 'CUTSCENE':
            self.cutscene.update()
            if self.cutscene.finished:
                self.state = 'DIALOGUE' 
                self.dialogue.start_dialogue('intro')
                self.flags['intro_cutscene_done'] = True
                
                # Setup
                self.exploration.player.rect.topleft = (400, 300)
                self.exploration.player.hitbox.center = (400, 300)

        elif self.state == 'EXPLORE':
            self.exploration.update()
            
            # Check for triggers
            player_rect = self.exploration.player.hitbox
            
            # Interact with Obstacles
            for obs in self.exploration.obstacles:
                if player_rect.colliderect(obs.hitbox.inflate(20, 20)):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:
                        # Placeholder interaction
                        pass
            
            # Trigger Random Encounter
            if self.exploration.trigger_encounter:
                 self.state = 'DIALOGUE'
                 self.dialogue.start_dialogue('combat_tutorial') # Generic combat intro dialog
                 self.exploration.trigger_encounter = False
                 # Store enemy type for transition
                 self.next_enemy = self.exploration.encounter_type
            
            # Static Tutorial Trigger (Only once)
            if self.exploration.player.rect.x > 1000 and not self.flags['first_combat_done']:
                self.state = 'DIALOGUE'
                self.dialogue.start_dialogue('combat_tutorial')
                self.flags['first_combat_done'] = True 
                self.next_enemy = "Corrupted Wolf"

        elif self.state == 'DIALOGUE':
            pass
            
        elif self.state == 'COMBAT':
            result = self.combat.update()
            if result == "WIN":
                self.state = 'DIALOGUE'
                self.dialogue.start_dialogue('hunger') 
            elif result == "LOSE":
                self.running = False
                print("Game Over")

    def draw(self):
        if self.state == 'CUTSCENE':
            self.cutscene.draw()
            
        elif self.state == 'EXPLORE':
            self.exploration.draw()
            
            # Draw UI overlay for interactions
            keys = pygame.key.get_pressed()
            near_interactable = False
            # Check proximity (optimized)
            p_center = self.exploration.player.rect.center
            for obs in self.exploration.obstacles:
                dist = (p_center[0] - obs.rect.centerx)**2 + (p_center[1] - obs.rect.centery)**2
                if dist < 5000: # approx 70px radius
                    near_interactable = True
                    break
            
            if near_interactable:
                # Text with shadow
                text = get_font(20).render("Press 'E' to Interact", True, COLOR_WHITE)
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT - 50))
                
        elif self.state == 'DIALOGUE':
            # Draw exploration behind it
            self.exploration.draw()
            self.dialogue.draw()
            
        elif self.state == 'COMBAT':
            self.combat.draw()
            
        pygame.display.flip()

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Pass events to active state
                if self.state == 'DIALOGUE':
                    res = self.dialogue.handle_input(event)
                    if res == "END":
                        # Apply State Changes
                        game_updates = self.dialogue.game_state_updates
                        
                        if game_updates.get('trigger_combat'):
                             self.state = 'COMBAT'
                             # Use stored enemy type or default
                             enemy = getattr(self, 'next_enemy', "Corrupted Wolf")
                             self.combat.start_combat(enemy)
                             game_updates['trigger_combat'] = False
                        else:
                             self.state = 'EXPLORE'
                             
                elif self.state == 'COMBAT':
                    self.combat.handle_input(event)

            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
