"""
generate_ascii.py
------------------
Converts a source photo into a hacker-green ASCII-art portrait,
rendered as an SVG (so it scales cleanly on any screen/theme).

Usage:
    python scripts/generate_ascii.py --input data/source-photo.jpg --output ascii-portrait.svg

Steps:
    1. Drop a headshot at data/source-photo.jpg (square-ish photos work best).
    2. Run this script locally once (or trigger the "Update Profile" Action manually).
    3. Commit the generated ascii-portrait.svg — README.md already references it.
"""

import argparse
from PIL import Image

# Characters ordered from "darkest" to "lightest" ink density.
RAMP = "@%#*+=-:. "

# Terminal-green palette to match the info card / heatmap theme.
FG = "#39ff88"
BG = "#0d1117"


def image_to_ascii_rows(path: str, cols: int = 90, font_aspect: float = 0.55):
    img = Image.open(path).convert("L")  # grayscale
    w, h = img.size
    rows = int((h / w) * cols * font_aspect)
    img = img.resize((cols, rows))

    pixels = list(img.getdata())
    ramp_len = len(RAMP) - 1

    ascii_rows = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        row_chars = "".join(
            RAMP[int((255 - p) / 255 * ramp_len)] for p in row_pixels
        )
        ascii_rows.append(row_chars)
    return ascii_rows


def rows_to_svg(rows, char_w: int = 7, char_h: int = 12) -> str:
    cols = len(rows[0]) if rows else 0
    width = cols * char_w + 20
    height = len(rows) * char_h + 20

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Consolas, Menlo, monospace" font-size="{char_h - 1}">',
        f'<rect width="100%" height="100%" fill="{BG}" rx="10"/>',
    ]

    for i, row in enumerate(rows):
        y = 20 + i * char_h
        escaped = (
            row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        lines.append(
            f'<text x="10" y="{y}" xml:space="preserve" fill="{FG}" opacity="0">'
            f'{escaped}'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{i * 0.02:.2f}s" dur="0.4s" fill="freeze"/>'
            f'</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/source-photo.jpg")
    parser.add_argument("--output", default="ascii-portrait.svg")
    parser.add_argument("--cols", type=int, default=90)
    args = parser.parse_args()

    rows = image_to_ascii_rows(args.input, cols=args.cols)
    svg = rows_to_svg(rows)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Wrote {args.output} ({len(rows)} rows x {args.cols} cols)")


if __name__ == "__main__":
    main()
