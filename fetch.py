import feedparser
import requests
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

YOUTUBE_CHANNELS = {
    "Matt Wolfe": "UChpleBmo18P08aKCIgti38g",
    "TechWithTim": "UC4JX40jDee_tINbkjycV4Sg",
}

RSS_FEEDS = {
    "TechCrunch AI":       "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge":           "https://www.theverge.com/rss/index.xml",
    "VentureBeat AI":      "https://venturebeat.com/category/ai/feed/",
    "Wired":               "https://www.wired.com/feed/rss",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "The Guardian Tech":   "https://www.theguardian.com/technology/artificialintelligenceai/rss",
    "Future of Life Inst.": "https://futureoflife.org/feed/",
    "Carbon Brief":        "https://www.carbonbrief.org/feed/",
    "AI Now Institute":    "https://ainowinstitute.org/feed",
    "Ars Technica AI":     "https://feeds.arstechnica.com/arstechnica/technology-lab",
}


def _parse_date(entry) -> datetime:
    """Try multiple date fields and return a timezone-aware datetime."""
    for field in ("published", "updated"):
        val = entry.get(field)
        if val:
            try:
                dt = parsedate_to_datetime(val)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass
    return datetime.now(timezone.utc)


def fetch_youtube(channel_name: str, channel_id: str, cutoff: datetime) -> list[dict]:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        published = _parse_date(entry)
        if published < cutoff:
            continue
        thumbnail = ""
        if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
            thumbnail = entry.media_thumbnail[0].get("url", "")
        items.append({
            "type": "video",
            "source": channel_name,
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "description": entry.get("summary", "")[:300],
            "published": published.isoformat(),
            "thumbnail": thumbnail,
        })
    return items


def fetch_rss(source_name: str, url: str, cutoff: datetime) -> list[dict]:
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"  [!] Failed to fetch {source_name}: {e}")
        return []
    items = []
    for entry in feed.entries:
        published = _parse_date(entry)
        if published < cutoff:
            continue
        summary = entry.get("summary", entry.get("description", ""))
        # Strip basic HTML tags from summary
        import re
        summary = re.sub(r"<[^>]+>", "", summary)[:300]
        items.append({
            "type": "article",
            "source": source_name,
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "description": summary.strip(),
            "published": entry.get("published", ""),
            "thumbnail": "",
        })
    return items


def fetch_all(days: int = 7) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    all_items = []

    print("Fetching YouTube channels...")
    for name, cid in YOUTUBE_CHANNELS.items():
        items = fetch_youtube(name, cid, cutoff)
        print(f"  {name}: {len(items)} videos")
        all_items.extend(items)

    print("Fetching RSS feeds...")
    for name, url in RSS_FEEDS.items():
        items = fetch_rss(name, url, cutoff)
        print(f"  {name}: {len(items)} articles")
        all_items.extend(items)

    print(f"\nTotal items fetched: {len(all_items)}")
    return all_items
