# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline (fetch → curate via Claude → render)
python main.py

# Run without Claude (fetch → render first 20 items, no curation)
python main.py --no-claude
```

Requires `ANTHROPIC_API_KEY` in a `.env` file (or environment) unless using `--no-claude`.

## Architecture

The pipeline runs in four sequential steps, all orchestrated by `main.py`:

1. **`fetch.py`** — Pulls articles from RSS feeds and videos from YouTube channel Atom feeds via `feedparser`. Returns a flat list of dicts with keys: `type`, `source`, `title`, `url`, `description`, `published`, `thumbnail`.

2. **`curate.py`** — Sends the fetched items to Claude (`claude-haiku-4-5-20251001`) with a structured prompt. Claude returns a JSON array selecting ~20 items and adding `category` (`progress` | `ethics` | `climate` | `wildcard`) and `reason` fields to each.

3. **`render.py`** — Takes the curated list and writes a self-contained `index.html` using an inline HTML template. Videos embed as iframes; articles show thumbnails if available. Categories control badge color/icon.

4. **`last_fetch.json`** — Cache written after curation; useful for re-rendering without re-fetching or re-calling Claude.

## Deployment

- **Static hosting**: Vercel serves `index.html` directly from the repo root (`vercel.json` sets `outputDirectory: "."`).
- **Automation**: GitHub Actions workflow (`.github/workflows/weekly-update.yml`) runs every Monday at 07:00 UTC, regenerates `index.html` and `last_fetch.json`, and commits them back to the repo. `ANTHROPIC_API_KEY` must be set as a repository secret.
