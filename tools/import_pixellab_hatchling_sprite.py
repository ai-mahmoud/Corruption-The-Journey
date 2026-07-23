"""One-time import: crops five frames out of a PixelLab-generated side-view
sprite sheet into assets/sprites/hatchling.png/json, replacing whatever
Hatchling sprite is currently in place (the procedural design, or the
earlier top-down pack import).

Unlike the procedural generators, this reads an external PNG that isn't
part of this repo -- pass its path, or drop it at the default location
below:

    python tools/import_pixellab_hatchling_sprite.py [path/to/sheet.png]

The five frames (idle, run_a, run_b, jump, fall) were hand-picked from a
larger generated sheet -- see the pixel coordinates in FRAME_SOURCES
below. All five are cropped to one shared bounding box (the union of each
frame's own opaque pixels), not each frame's individual tight crop, so
she doesn't visibly jitter side to side as her pose changes -- Player.
draw() bottom/center-aligns each frame by its own width/height with no
separate per-frame offset, so a consistent shared origin is what keeps
that alignment stable across poses.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

from pixel_art import save_sprite

DEFAULT_SOURCE_PATH = (
    Path.home() / "Downloads" / "pixellab--A-2D-side-view-platformer-cha-1784761341837.png"
)

SCALE = 1  # already high-detail native art; upscaling would just blur/blockify it

# (pose name, (x0, y0, x1, y1) box in the source sheet's native pixels)
FRAME_SOURCES = [
    ("idle", (5, 2, 35, 96)),
    ("run_a", (47, 2, 99, 96)),
    ("run_b", (106, 2, 153, 96)),
    ("jump", (179, 2, 217, 96)),
    ("fall", (249, 2, 289, 96)),  # descending/tumble pose, chosen as the fall stand-in
]


def main(source_path: Path) -> None:
    if not source_path.exists():
        raise SystemExit(f"'{source_path}' not found -- pass the sheet's path as an argument.")

    sheet_source = Image.open(source_path).convert("RGBA")
    raw_frames = {name: sheet_source.crop(box) for name, box in FRAME_SOURCES}

    boxes = [frame.getbbox() for frame in raw_frames.values()]
    if any(box is None for box in boxes):
        raise ValueError("one of the chosen frames is fully transparent -- check FRAME_SOURCES")
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
    for i, (name, _) in enumerate(FRAME_SOURCES):
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
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE_PATH
    main(path)
