import pygame

pygame.init()
clock = pygame.time.Clock()
fps = 60
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Corruption: The Journey")

far_background = pygame.image.load("assets/background/far_background.png").convert_alpha()
bottom_panel_image = pygame.image.load("assets/background/panel.png").convert_alpha()

def draw_bg():
    screen.blit(far_background, (0, 0))

def draw_panel():
    screen.blit(bottom_panel_image, (0, screen_height - bottom_panel))

class Entity:
    def __init__(self, x, y, name, max_hp, strength, mana, image_scaler):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.starter_mana = mana
        self.mana = mana
        self.image_scaler = image_scaler
        self.alive = True
        image = pygame.image.load(f"assets/{self.name}/idle/0.png").convert_alpha()
        self.image = pygame.transform.scale(image, (image.get_width() * image_scaler, image.get_height() * image_scaler))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def draw(self):
        screen.blit(self.image, self.rect)

hatchling = Entity(200, 260, "hatchling", 100, 1, 1, 1.7)
wolf1 = Entity(550, 270, "corrupted_wolf", 50, 1, 0, 3.5)
wolf2 = Entity(700, 270, "corrupted_wolf", 50, 1, 0, 3.5)
wolves = []
wolves.append(wolf1)
wolves.append(wolf2)

run = True
while run:
    clock.tick(fps)
    draw_bg()
    draw_panel()
    hatchling.draw()
    for wolf in wolves:
        wolf.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()

