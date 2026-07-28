"""
generate_heatmap.py
--------------------
Pulls the last 12 months of contribution data straight from GitHub's
GraphQL API and renders a custom hex-dot heatmap SVG (deliberately not
the common github-readme-stats card, per request).

Requires env var GH_TOKEN (a token with read:user scope — the default
GITHUB_TOKEN in Actions works fine for reading the account's own public
contribution calendar).

Usage:
    GH_TOKEN=xxx python scripts/generate_heatmap.py --user kumud1606 --output contrib-heatmap.svg
"""

import argparse
import os
import sys
import json
import urllib.request

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

GREEN_SCALE = ["#0d1117", "#0e4429", "#006d32", "#26a641", "#39d353"]


def fetch_contributions(login: str, token: str):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def level_for(count: int, thresholds=(0, 2, 5, 10)) -> int:
    if count == 0:
        return 0
    for i, t in enumerate(thresholds[1:], start=1):
        if count < t:
            return i
    return len(thresholds)


def build_svg(weeks, cell=11, gap=3) -> str:
    n_weeks = len(weeks)
    width = n_weeks * (cell + gap) + 40
    height = 7 * (cell + gap) + 40

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Consolas, Menlo, monospace">',
        f'<rect width="100%" height="100%" fill="#0d1117" rx="10"/>',
        f'<text x="16" y="20" font-size="12" fill="#7d8590">contribution activity — last 12 months</text>',
    ]

    for w, week in enumerate(weeks):
        for d, day in enumerate(week["contributionDays"]):
            count = day["contributionCount"]
            level = level_for(count)
            x = 20 + w * (cell + gap)
            y = 30 + d * (cell + gap)
            delay = (w * 7 + d) * 0.002
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{GREEN_SCALE[level]}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.4s" fill="freeze"/>'
                f'</rect>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="kumud1606")
    parser.add_argument("--output", default="contrib-heatmap.svg")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN")
    if not token:
        print("GH_TOKEN env var not set — skipping live fetch.", file=sys.stderr)
        sys.exit(1)

    weeks = fetch_contributions(args.user, token)
    svg = build_svg(weeks)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
