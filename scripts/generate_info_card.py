"""
generate_info_card.py
----------------------
Builds an animated "terminal boot-up" style SVG info card — name, focus,
and a rotating status line. No GitHub stats/graphs live here on purpose;
this is pure identity/bio, kept separate from the heatmap.

Usage:
    python scripts/generate_info_card.py --output info-card.svg
"""

import argparse

BG = "#0d1117"
BORDER = "#21262d"
GREEN = "#39ff88"
WHITE = "#e6edf3"
DIM = "#7d8590"

NAME = "Kumud Mishra"
ROLE = "CSE Undergrad (4th Year)"
FOCUS = "Aspiring AI/ML + Backend Engineer"
STATUS_LINES = [
    "loading model weights...",
    "compiling backend routes...",
    "training on real-world problems...",
    "status: open to opportunities",
]


def build_svg(width=520, height=220) -> str:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Consolas, Menlo, monospace">',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>',

        # fake terminal titlebar dots
        '<circle cx="24" cy="26" r="6" fill="#ff5f56"/>',
        '<circle cx="44" cy="26" r="6" fill="#ffbd2e"/>',
        '<circle cx="64" cy="26" r="6" fill="#27c93f"/>',
        f'<text x="90" y="31" font-size="12" fill="{DIM}">kumud1606@github ~ %</text>',

        f'<line x1="20" y1="46" x2="{width-20}" y2="46" stroke="{BORDER}"/>',

        # name — typing effect
        f'<text x="24" y="80" font-size="24" font-weight="700" fill="{WHITE}">'
        f'<tspan>{NAME}</tspan>'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.6s" fill="freeze"/>'
        f'</text>',

        f'<text x="24" y="106" font-size="14" fill="{GREEN}">{ROLE}</text>',
        f'<text x="24" y="128" font-size="14" fill="{DIM}">{FOCUS}</text>',

        f'<line x1="20" y1="144" x2="{width-20}" y2="144" stroke="{BORDER}"/>',
    ]

    # rotating status line: stack each line at the same spot, fade one in
    # while the others sit at opacity 0, looping forever.
    n = len(STATUS_LINES)
    hold = 1.8   # seconds visible
    fade = 0.3   # seconds fade in/out
    dur = n * (hold + fade)

    for i, line in enumerate(STATUS_LINES):
        start = i * (hold + fade)
        # keyframe times as fractions of total duration, for a single <animate>
        t0 = start / dur
        t1 = (start + fade * 0.3) / dur
        t2 = (start + hold) / dur
        t3 = min((start + hold + fade) / dur, 1)
        lines.append(
            f'<text x="24" y="170" font-size="13" fill="{GREEN}" opacity="0">'
            f'&gt; {line}'
            f'<animate attributeName="opacity" '
            f'keyTimes="0;{t0:.3f};{t1:.3f};{t2:.3f};{t3:.3f};1" '
            f'values="0;0;1;1;0;0" '
            f'dur="{dur:.2f}s" repeatCount="indefinite"/>'
            f'</text>'
        )



    lines.append(
        f'<text x="24" y="196" font-size="12" fill="{DIM}">'
        f'building things that learn, not just run.</text>'
    )

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="info-card.svg")
    args = parser.parse_args()

    svg = build_svg()
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
