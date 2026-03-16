#!/usr/bin/env python3
"""
AI Weekly Digest — main entry point.

Usage:
    python main.py              # fetch, curate, render
    python main.py --no-claude  # fetch & render without Claude (first 20 items, no curation)
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fetch import fetch_all
from render import render


def main():
    no_claude = "--no-claude" in sys.argv

    # Step 1: Fetch all news
    items = fetch_all(days=7)

    if not items:
        print("No items fetched. Check your internet connection.")
        sys.exit(1)

    # Step 2: Curate with Claude (or skip)
    if no_claude:
        print("Skipping Claude curation (--no-claude flag). Using first 20 items.")
        curated = items[:20]
        for item in curated:
            item.setdefault("category", "progress")
            item.setdefault("reason", "")
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print(
                "\n[!] ANTHROPIC_API_KEY not set.\n"
                "    Set it in a .env file or environment variable, or run with --no-claude.\n"
                "    Get your key at: https://console.anthropic.com\n"
            )
            sys.exit(1)

        from curate import curate
        curated = curate(items)

    # Step 3: Save raw data (useful for debugging / re-rendering without re-fetching)
    cache_path = Path("last_fetch.json")
    cache_path.write_text(json.dumps(curated, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
    print(f"Cached {len(curated)} curated items to {cache_path}")

    # Step 4: Render HTML
    render(curated, output_path="index.html")
    print("\nDone! Open index.html in your browser.")


if __name__ == "__main__":
    main()
