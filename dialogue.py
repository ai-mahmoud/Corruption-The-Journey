import pygame
import sys
from settings import *

class DialogueSystem:
    def __init__(self, screen=None):
        self.screen = screen if screen else pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.active = False
        self.dialogue_node = None
        self.selected_option = 0
        self.font = get_font(24)
        self.header_font = get_font(28)
        self.game_state_updates = {}
        
        # Current dialogue data
        self.current_text = ""
        self.current_options = []
        self.current_speaker = ""

        self.dialogue_tree = {
            'intro': {
                'speaker': '???',
                'text': '...Light? No. Not light. Something... deeper.',
                'options': [
                    {'text': '(Try to speak)', 'next': 'first_words', 'effect': {}},
                    {'text': '(Listen)', 'next': 'listen', 'effect': {}},
                ]
            },
            'first_words': {
                'speaker': 'Hatchling',
                'text': 'Ma... na? ...Cor... ruption?',
                'options': [
                    {'text': '...I am awake.', 'next': 'awakened', 'effect': {'learned_speak': True}}
                ]
            },
            'listen': {
                'speaker': 'The Forest',
                'text': '*The corrupted roots hum with a discordant song. It welcomes you.*',
                'options': [
                    {'text': '...I hear you.', 'next': 'awakened', 'effect': {'learned_speak': True}}
                ]
            },
            'awakened': {
                'speaker': 'Hatchling',
                'text': 'This hunger... it is a guide. I must find the source.',
                'options': [
                    {'text': '[Begin Journey]', 'next': None, 'effect': {}}
                ]
            },
            'combat_tutorial': {
                 'speaker': 'Instinct',
                 'text': 'A twisted beast blocks the path. It seeks to consume.',
                 'options': [
                     {'text': 'Defend yourself!', 'next': None, 'effect': {'trigger_combat': True}}
                 ]
            },
            'hunger': {
                'speaker': 'Instinct',
                'text': 'The beast falls. Its energy lingers. Absorb it?',
                'options': [
                    {'text': 'Consume (Heal)', 'next': None, 'effect': {'healed': True}}
                ]
            }
        }

    def start_dialogue(self, node_id):
        if node_id in self.dialogue_tree:
            self.active = True
            self.load_node(node_id)
            return True
        return False

    def load_node(self, node_id):
        data = self.dialogue_tree[node_id]
        self.current_speaker = data['speaker']
        self.current_text = data['text']
        self.current_options = data['options']
        self.selected_option = 0

    def handle_input(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = max(0, self.selected_option - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = min(len(self.current_options) - 1, self.selected_option + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.choose_option()
        return None

    def choose_option(self):
        choice = self.current_options[self.selected_option]
        
        # Apply effects
        for k, v in choice['effect'].items():
            self.game_state_updates[k] = v
            
        # Navigate or Close
        if choice['next']:
            self.load_node(choice['next'])
            return "CONTINUE"
        else:
            self.active = False
            return "END"

    def draw(self, surface=None):
        if not self.active:
            return
            
        target_surface = surface if surface else self.screen
        
        # Draw Box Background
        box_height = 200
        pygame.draw.rect(target_surface, (20, 20, 30), (0, SCREEN_HEIGHT - box_height, SCREEN_WIDTH, box_height))
        pygame.draw.rect(target_surface, (100, 100, 120), (0, SCREEN_HEIGHT - box_height, SCREEN_WIDTH, box_height), 3)
        
        # Draw Speaker
        speaker_surf = self.header_font.render(self.current_speaker, True, COLOR_GOLD)
        target_surface.blit(speaker_surf, (20, SCREEN_HEIGHT - box_height + 20))
        
        # Draw Text
        # Simple wrap could be added here, for now assumes short text
        text_surf = self.font.render(self.current_text, True, COLOR_WHITE)
        target_surface.blit(text_surf, (20, SCREEN_HEIGHT - box_height + 60))
        
        # Draw Options
        opt_start_y = SCREEN_HEIGHT - box_height + 100
        for i, option in enumerate(self.current_options):
            color = COLOR_GOLD if i == self.selected_option else (150, 150, 150)
            prefix = "> " if i == self.selected_option else "  "
            opt_surf = self.font.render(prefix + option['text'], True, color)
            target_surface.blit(opt_surf, (40, opt_start_y + i * 30))

    def run_standalone(self):
        # Helper for standalone testing
        self.active = True
        self.start_dialogue('intro')
        clock = pygame.time.Clock()
        while self.active:
            self.screen.fill((50, 50, 50))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                self.handle_input(event)
            self.draw()
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    d = DialogueSystem()
    d.run_standalone()
    pygame.quit()
