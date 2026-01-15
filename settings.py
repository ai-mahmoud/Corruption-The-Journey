import pygame

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 64

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 50, 50)
COLOR_GREEN = (50, 200, 50)
COLOR_BLUE = (50, 50, 200)
COLOR_GOLD = (255, 215, 0)

# Narrative Colors (Corruption Theme)
COLOR_BG_CORRUPTED = (20, 10, 30)  # Dark purple/black
COLOR_CORRUPTION_ACCENT = (140, 40, 160) # Bright purple
COLOR_TEXT_NORMAL = (220, 220, 220)
COLOR_TEXT_CORRUPTED = (200, 100, 200)

# Fonts
def get_font(size):
    return pygame.font.SysFont("arial", size)
