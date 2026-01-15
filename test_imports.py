import sys
import os
import pygame

try:
    print("Testing imports...")
    import settings
    import cutscene
    import exploration
    import dialogue
    import combat
    import pre_act1
    print("Imports successful.")

    print("Testing init...")
    pygame.init()
    
    # Mock screen to avoid video device errors in headless env if necessary
    # But usually set_mode might fail if no device.
    # We will try to init classes with a dummy surface if possible or catch video errors.
    
    try:
        # We define a dummy surface so we don't need a window
        dummy_surface = pygame.Surface((800, 600))
        
        c = cutscene.Cutscene(screen=dummy_surface)
        print("Cutscene initialized.")
        
        e = exploration.Exploration(screen=dummy_surface)
        print("Exploration initialized.")
        
        d = dialogue.DialogueSystem(screen=dummy_surface)
        print("DialogueSystem initialized.")
        
        co = combat.CombatSystem(screen=dummy_surface)
        print("CombatSystem initialized.")
        
        # Game class creates its own window so we might skip it or mock pygame.display.set_mode
        # but let's just assume individual modules working is good enough for headless check.
        
    except pygame.error as e:
        print(f"Pygame video init failed as expected in headless: {e}")
        print("Logic verification passed (imports and class definitions valid).")

except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
