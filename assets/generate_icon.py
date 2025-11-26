#!/usr/bin/env python3
"""Generate ICO file from the ear icon design."""

from PIL import Image, ImageDraw
from pathlib import Path


def create_ear_icon(size: int = 64, color: str = "#4CAF50", bg: str = "#1e1e1e") -> Image.Image:
    """Create an ear-shaped icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size / 64  # Scale factor

    # Background circle
    margin = int(2 * s)
    draw.ellipse([margin, margin, size - margin, size - margin],
                 fill=bg, outline=color, width=max(1, int(2 * s)))

    # Ear shape points
    ear_points = [
        (40 * s, 12 * s),
        (50 * s, 20 * s),
        (52 * s, 32 * s),
        (48 * s, 44 * s),
        (40 * s, 50 * s),
        (32 * s, 50 * s),
        (28 * s, 46 * s),
        (30 * s, 40 * s),
        (34 * s, 44 * s),
        (40 * s, 40 * s),
        (44 * s, 32 * s),
        (42 * s, 22 * s),
        (34 * s, 16 * s),
        (26 * s, 20 * s),
        (22 * s, 30 * s),
        (24 * s, 42 * s),
    ]

    # Draw ear
    for i in range(len(ear_points) - 1):
        draw.line([ear_points[i], ear_points[i + 1]], fill=color, width=max(2, int(3 * s)))

    # Sound waves
    draw.arc([int(8 * s), int(24 * s), int(18 * s), int(40 * s)],
             start=60, end=300, fill=color, width=max(1, int(2 * s)))
    draw.arc([int(2 * s), int(20 * s), int(14 * s), int(44 * s)],
             start=60, end=300, fill=color, width=max(1, int(2 * s)))

    return img


def generate_ico(output_path: Path):
    """Generate a multi-size ICO file."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = [create_ear_icon(size) for size in sizes]

    # Save as ICO with multiple sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"Created: {output_path}")


if __name__ == "__main__":
    assets_dir = Path(__file__).parent
    generate_ico(assets_dir / "earhole.ico")

    # Also save a PNG for reference
    icon = create_ear_icon(256)
    icon.save(assets_dir / "earhole.png")
    print(f"Created: {assets_dir / 'earhole.png'}")
