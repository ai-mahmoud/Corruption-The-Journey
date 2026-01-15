# Corruption: The Journey (Pre-Act 1 Vertical Slice)

A playable prototype of the "Birth" sequence for *Corruption: The Journey*.

## Overview
You play as the **Hatchling**, a newborn entity in the Corrupted Forest. 
- **Goal**: Explore the forest, learn to communicate, and survive against the corrupted fauna.
- **Key Features**:
    -   **Egg Hatching Cutscene**: Witness the birth of the protagonist.
    -   **Side-View Combat**: Turn-based battles with animated sprites.
    -   **Dynamic Encounters**: Random enemies appear as you explore deeper.
    -   **Dialogue System**: Choices shape her burgeoning consciousness.

## Installation & Running
1.  Ensure you have **Python 3** installed.
2.  Install **Pygame**:
    ```bash
    pip install pygame
    ```
3.  Run the game:
    ```bash
    python3 pre_act1.py
    ```

## Controls
-   **Movement**: Arrow Keys (`WASD` also supported)
-   **Interaction**: `E` (Near trees/rocks)
-   **Combat**:
    -   `A`: Attack (Lunge)
    -   `D`: Absorb (Heal)
-   **Dialogue**:
    -   `UP`/`DOWN`: Select Options
    -   `SPACE`/`ENTER`: Confirm

## File Structure
-   `pre_act1.py`: Main game loop and state manager.
-   `combat.py`: Turn-based combat system logic and rendering.
-   `exploration.py`: Map exploration, player movement, and collision.
-   `dialogue.py`: Narrative engine and UI.
-   `cutscene.py`: Opening sequence animations.
-   `assets/`: Contains all sprite and background images.

## Development Notes
-   Generated assets have been processed with an auto-cropper and transparency cleaner (`combat.py`).
-   Debug mode can be enabled by modifying `settings.py` (if implemented).
