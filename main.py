"""Entry point: `python main.py` from the project root to play.

This just wires up the import path (game code in src/, room data in data/,
kept separate on disk as described in README.md) and hands off to Game.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "data"))

from game import Game  # noqa: E402

if __name__ == "__main__":
    Game().run()
