"""One-time import: crops five frames out of the third-party "The Female
Adventurer - Free" pack into assets/sprites/hatchling.png/json, replacing
the procedurally-generated Hatchling sprite.

Unlike every other tools/*.py generator, this one is NOT self-contained --
it reads directly from the original zip (never extracted or committed
into this repo; see the README's Audio/Art notes on why) and produces
only the small derived crop the game actually uses. Re-run it only if you
have that zip locally:

    python tools/import_female_adventurer_sprite.py [path/to/zip]

Camera-perspective note: this pack is a 3/4 top-down RPG asset (8
directional facings -- Idle_Down, Walk_Left_Up, etc.), not a side-view
platformer sprite like every other character/enemy sprite in this game.
There is no clean way to reconcile that; "Right_Down" was chosen as the
least-mismatched facing (closest to a side profile) and is flipped
horizontally for facing left by the existing Player.draw() code, same as
the previous procedural sprite. This is a deliberate, acknowledged
compromise, not a bug -- see the README for the license caveat too (no
LICENSE/readme ships inside the pack, so its terms are unverified; keep
that in mind before distributing this build beyond a small private
group).
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

from pixel_art import save_sprite

DEFAULT_ZIP_PATH = Path.home() / "Downloads" / "The Female Adventurer - Free.zip"
PACK_ROOT = "The Female Adventurer - Free"

FRAME_SIZE = 64
SCALE = 2

# (pose name, in-pack strip path, frame index within that 6-frame strip)
FRAME_SOURCES = [
    ("idle", f"{PACK_ROOT}/Idle/Idle_Right_Down.png", 0),
    ("run_a", f"{PACK_ROOT}/Walk/walk_Right_Down.png", 0),
    ("run_b", f"{PACK_ROOT}/Walk/walk_Right_Down.png", 3),
    ("jump", f"{PACK_ROOT}/Jump - NEW/Normal/Jump_Right_Down.png", 3),  # airborne, legs tucked
    ("fall", f"{PACK_ROOT}/Jump - NEW/Normal/Jump_Right_Down.png", 0),  # lower, close to ground
]


def _load_frame(zf: zipfile.ZipFile, path: str, index: int) -> Image.Image:
    with zf.open(path) as f:
        strip = Image.open(io.BytesIO(f.read())).convert("RGBA")
    return strip.crop((index * FRAME_SIZE, 0, (index + 1) * FRAME_SIZE, FRAME_SIZE))


def _alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    box = image.getbbox()
    if box is None:
        raise ValueError("frame is fully transparent")
    return box


def main(zip_path: Path) -> None:
    if not zip_path.exists():
        raise SystemExit(
            f"'{zip_path}' not found -- this import needs the original pack zip "
            "locally (it's never stored in this repo). Pass its path as an argument."
        )

    with zipfile.ZipFile(zip_path) as zf:
        raw_frames = {name: _load_frame(zf, path, index) for name, path, index in FRAME_SOURCES}

    # Crop every frame to the SAME shared box (the union of each frame's own
    # opaque bbox) rather than each frame's individual tight bbox -- keeping
    # a shared origin is what stops her from visibly jittering side to side
    # as poses change, since Player.draw() bottom/center-aligns each frame
    # by its own width/height with no separate per-frame offset.
    boxes = [_alpha_bbox(frame) for frame in raw_frames.values()]
    union_box = (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )
    cropped = {name: frame.crop(union_box) for name, frame in raw_frames.items()}

    width = union_box[2] - union_box[0]
    height = union_box[3] - union_box[1]

    sheet = Image.new("RGBA", (width * len(cropped), height), (0, 0, 0, 0))
    frame_boxes: dict[str, list[list[int]]] = {}
    for i, (name, _, _) in enumerate(FRAME_SOURCES):
        sheet.paste(cropped[name], (i * width, 0), cropped[name])
        frame_boxes[name] = [[i * width, 0, width, height]]

    save_sprite(
        sheet,
        name="hatchling",
        scale=SCALE,
        anchor=(width // 2, height),  # bottom-center, i.e. her feet
        frames=frame_boxes,
    )


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ZIP_PATH
    main(path)
