"""Save/load for GameProgress. Plain JSON, no new dependency.

GameProgress's field names are kept identical to the JSON keys on purpose
so loading is just `GameProgress(**load_game())` -- no separate mapping
layer to keep in sync.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from game_progress import GameProgress

APP_NAME = "CorruptionTheJourney"


def _user_data_dir() -> Path:
    """A proper per-OS user-data location, not next to the source/build --
    writing beside the executable breaks on read-only install locations
    (e.g. Program Files on Windows) and won't survive a reinstall/update."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    # Linux and everything else: XDG Base Directory spec.
    base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(base) / APP_NAME


SAVE_PATH = _user_data_dir() / "savegame.json"


def save_game(progress: GameProgress) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PATH.write_text(json.dumps(asdict(progress), indent=2) + "\n")


def load_game() -> dict | None:
    """Returns the saved dict, or None if there's no save -- also None
    (rather than crashing on startup) if the file exists but doesn't match
    GameProgress's current fields, e.g. after adding/renaming a field in
    a later version. A demo should never fail to launch because of a
    save file from an older build."""
    if not SAVE_PATH.exists():
        return None
    try:
        data = json.loads(SAVE_PATH.read_text())
        GameProgress(**data)  # validates the fields match before trusting it
        return data
    except (json.JSONDecodeError, TypeError):
        return None
